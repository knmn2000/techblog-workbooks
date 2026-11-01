"""Test cases for assignment 07 (match children by key).

    py -P tools/gen_p07.py                                  # tests/07 (seed 1)
    py -P tools/gen_p07.py --seed 777 --out build/fresh/07  # what `.\\check 07 -Fresh` runs

What a correct program prints for every dump line comes from real React 19 on jsdom (tools/oracle).
React cannot count the learner's DOM calls, so the `ops create remove` lines come from a model written
here: it matches the children of every parent by key (or by position when there is no key) with a lookup
table, the way the definition reads, and adds up the nodes that have to be built and the children that
have to go. The reference program walks linked fibers instead; the two only meet in the numbers.

Rules the scenarios follow, from the React notes (_source/react-observed.md):
  - every `render` is followed by `flush` before the next one;
  - keys are unique among siblings, and in this assignment the keys two renders share keep their order
    (reordering is assignment 08);
  - a list never mixes keyed and unkeyed children (React matches an unkeyed child by its index, a
    program that walks the old list in step does not always agree);
  - inputs are uncontrolled (no `value=` in the markup) and carry an id, so `type` can find them.

This module is also imported by gen_p08.py (the script builder, the model, the random lists).
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reactgen  # noqa: E402
import wbcore  # noqa: E402
from reactgen import parse_markup, rng_for, run_oracle_batch  # noqa: E402

ORACLE_PACKAGE = json.loads((wbcore.ROOT / "tools" / "oracle" / "package.json").read_text(encoding="utf-8"))
REACT = ORACLE_PACKAGE["dependencies"]["react"]
JSDOM = ORACLE_PACKAGE["dependencies"]["jsdom"]
SOURCE = f"React {REACT} on jsdom {JSDOM} (tools/oracle); ops lines from a model of the matching rules in tools/gen_p07.py"
COMPARE = "records node=depth,label,tag,props text=depth,value title=value ops=create,remove dump=n"
EXPLAIN = "ops=R9"


# ---- The model behind `ops create remove` ---------------------------------------------------------

KEY_ATTR = re.compile(r"""\bkey=(?:"([^"]*)"|'([^']*)'|(\S+))""")


class Node:
    """An element or a text node of a markup tree: what the model needs to know about it."""

    def __init__(self, tag, key, kids):
        self.tag, self.key, self.kids = tag, key, kids


def to_nodes(parsed):
    nodes = []
    for item in parsed:
        if item[0] == "text":
            nodes.append(Node("#text", None, []))
            continue
        _, tag, attrs, kids = item
        found = KEY_ATTR.search(attrs)
        key = None if found is None else next(g for g in found.groups() if g is not None)
        nodes.append(Node(tag, key, to_nodes(kids)))
    return nodes


def subtree_size(node):
    return 1 + sum(subtree_size(kid) for kid in node.kids)


def slot(node, index):
    """Where a child can be found again: by its key, or by its position when it has none."""
    return ("key", node.key) if node.key is not None else ("position", index)


def edit_cost(old, new):
    """(nodes created, children removed) when the child list `old` on the page becomes `new`.
    A new child continues the old child that has its slot and its tag, and the pair is compared below.
    Otherwise it is built from scratch (every element and text node counts as one creation) and the old
    child in that slot, if there is one, goes. Old children nobody continues go. A removed child costs one
    removal, whatever it holds."""
    table = {slot(child, i): child for i, child in enumerate(old)}
    assert len(table) == len(old), "duplicate keys among siblings"
    created = removed = 0
    claimed = set()
    for i, child in enumerate(new):
        wanted = slot(child, i)
        partner = table.get(wanted)
        if partner is not None:
            claimed.add(wanted)
            if partner.tag == child.tag:
                inner_created, inner_removed = edit_cost(partner.kids, child.kids)
                created += inner_created
                removed += inner_removed
                continue
            removed += 1
        created += subtree_size(child)
    removed += len(table) - len(claimed)
    return created, removed


# ---- A scenario with its model --------------------------------------------------------------------

class Script:
    """Builds the scenario text and, next to it, the `ops` lines the model expects."""

    def __init__(self):
        self.lines = []
        self.model = []
        self.created = self.removed = 0
        self.expected_ops = []
        self.trees = 0

    def render(self, markup):
        nodes = to_nodes(parse_markup(markup))
        assert len(nodes) == 1, "one root element per render"
        made, gone = edit_cost(self.model, nodes)
        self.created += made
        self.removed += gone
        self.model = nodes
        self.trees += 1
        name = f"t{self.trees}"
        self.lines += [f"tree {name} {markup}", f"render {name}", "flush"]
        return self

    def dump(self):
        self.lines.append("dump")
        return self

    def ops(self):
        self.lines.append("ops create remove")
        self.expected_ops.append(f"ops {self.created} {self.removed}")
        self.created = self.removed = 0
        return self

    def type(self, node_id, text):
        self.lines.append(f"type #{node_id} {text}")
        return self

    def step(self, markup, *, ops=True):
        """render, flush, dump and (unless told not to) ops."""
        self.render(markup).dump()
        return self.ops() if ops else self

    def text(self):
        return "\n".join(self.lines) + "\n"


def fill_ops(oracle_lines, script):
    """The oracle's lines with every `ops ?` placeholder replaced by the model's line, in order."""
    expected = iter(script.expected_ops)
    out = [next(expected) if line == "ops ?" else line for line in oracle_lines]
    assert next(expected, None) is None, "the oracle printed fewer ops lines than the model has"
    return out


# ---- Reading the oracle's dumps (only to check that a hand-made case does what its author meant) ----

def dump_blocks(lines):
    blocks = []
    for line in lines:
        if line.startswith("dump "):
            blocks.append([])
        elif blocks and line.split(" ", 1)[0] in ("node", "text"):
            blocks[-1].append(line)
    return blocks


def labels_by_item(block):
    """{text or id of a depth-1 node: its label} for a dump of a list."""
    found = {}
    for i, line in enumerate(block):
        words = line.split(" ", 4)
        if words[0] != "node" or words[1] != "1":
            continue
        name = None
        for below in block[i + 1:]:
            parts = below.split(" ", 4)
            if parts[0] == "node" and int(parts[1]) <= 1:
                break
            if parts[0] == "text" and name is None:
                name = below.split(" ", 2)[2].strip('"')
            if parts[0] == "node" and name is None:
                m = re.search(r"\bid=(\S+?)[ \"]", parts[4] + '"')
                if m:
                    name = m.group(1)
        if name is None:
            m = re.search(r"\bid=(\S+?)[ \"]", words[4] + '"')
            name = m.group(1) if m else f"#{len(found)}"
        found[name] = words[2]
    return found


def check_identity(case_id, lines, kept=(), fresh=(), gone=(), between=(-2, -1)):
    """Between two dumps (the last two unless `between` names others): items in `kept` keep their label, `fresh` ones have a new label,
    `gone` ones are no longer listed. Items are named by their text (or their input's id)."""
    blocks = dump_blocks(lines)
    before, after = labels_by_item(blocks[between[0]]), labels_by_item(blocks[between[1]])
    for name in kept:
        assert before.get(name) is not None and before[name] == after.get(name), f"{case_id}: {name!r} should be kept"
    for name in fresh:
        assert name in after and after[name] != before.get(name) and after[name] not in before.values(), \
            f"{case_id}: {name!r} should be a new node"
    for name in gone:
        assert name in before and name not in after, f"{case_id}: {name!r} should be gone"


# ---- Markup helpers --------------------------------------------------------------------------------

def word(key):
    return "item empty" if key == "" else f"item {key}"


def li(key, text=None, attrs=""):
    return f'<li key="{key}"{attrs}>{word(key) if text is None else text}</li>'


def ul(*items):
    return "<ul>" + "".join(items) + "</ul>"


def keyed(*keys, **kw):
    return ul(*[li(k, **kw) for k in keys])


def plain(*texts):
    """A list whose children have no key."""
    return ul(*[f"<li>{t}</li>" for t in texts])


def field_item(key, input_id):
    return f'<li key="{key}"><input id="{input_id}"/></li>'


def fields(*pairs):
    """A list of list items that each hold an uncontrolled input: pairs are (key, input id)."""
    return ul(*[field_item(k, i) for k, i in pairs])


# ---- The cases --------------------------------------------------------------------------------------

REQUIREMENTS = [
    ("R1", "Rendering a list again with the same keys in the same order keeps every node and writes the changed props and text into it"),
    ("R2", "A new keyed child is built and placed where the new list has it: at the front, in the middle or at the end"),
    ("R3", "A child whose key is still in the list keeps its node (and everything below it) while others are added and removed around it"),
    ("R4", "A child whose key is missing from the new list is removed, that child only, wherever it stood"),
    ("R5", "A new key, or the same key on a different tag, gives a new node in the old child's place"),
    ("R6", "An input keeps what was typed into it for as long as its key stays in the list, and a new input starts empty"),
    ("R7", "A key is an exact string: the empty string is a key, and \"0\", \"00\", \"1\" and \"01\" are different keys"),
    ("R8", "Children without a key match by position, and a keyed child never matches an unkeyed one"),
    ("R9", "`ops create remove` counts a node for every element and text node of a new child and one removal for every removed child"),
    ("E2E", "Whole sessions on keyed lists"),
]


class Book:
    """Collects scenarios, runs them against the oracle in one go and writes the case file."""

    def __init__(self):
        self.entries = []

    def add(self, case_id, req, title, script, **identity):
        assert title.isascii(), case_id
        self.entries.append((case_id, req, title, script, identity))

    def save(self, args, requirements=REQUIREMENTS, compare=COMPARE, explain=EXPLAIN, source=SOURCE):
        results = run_oracle_batch([entry[3].text() for entry in self.entries])
        cases = wbcore.Cases(args.out, args.seed, compare, requirements, explain, source=source)
        for (case_id, req, title, script, identity), lines in zip(self.entries, results):
            if identity:
                check_identity(case_id, lines, **identity)
            cases.add(case_id, req, title, script.lines, expected=fill_ops(lines, script))
        cases.save()


def hand_made(book):
    # R1 ---------------------------------------------------------------------------------------------
    book.add("07-R1-same-list-twice", "R1", "a list of three keyed items rendered twice, unchanged",
             Script().step(keyed("a", "b", "c")).step(keyed("a", "b", "c")),
             kept=["item a", "item b", "item c"])
    book.add("07-R1-props-and-text-in-place", "R1", "same keys, but class, title and text change; one title disappears",
             Script().step(ul(li("a", "alpha", ' className="x" title="t"'), li("b", "beta", ' id="bb"')))
                     .step(ul(li("a", "ALPHA", ' className="y"'), li("b", "beta", ' id="bb" title="new"'))),
             kept=["beta"])
    book.add("07-R1-nested-update", "R1", "items hold nested elements; their text changes between renders",
             Script().step(ul('<li key="a"><b>one</b><i>x</i></li>', '<li key="b"><b>two</b><i>y</i></li>'))
                     .step(ul('<li key="a"><b>one</b><i>X</i></li>', '<li key="b"><b>TWO</b><i>y</i></li>')))

    # R2 ---------------------------------------------------------------------------------------------
    book.add("07-R2-front", "R2", "a keyed item is added in front of two others",
             Script().step(keyed("a", "b")).step(keyed("z", "a", "b")),
             kept=["item a", "item b"], fresh=["item z"])
    book.add("07-R2-front-two", "R2", "two keyed items are added in front of one",
             Script().step(keyed("a")).step(keyed("x", "y", "a")),
             kept=["item a"], fresh=["item x", "item y"])
    book.add("07-R2-middle", "R2", "a keyed item is added between two others",
             Script().step(keyed("a", "c")).step(keyed("a", "b", "c")),
             kept=["item a", "item c"], fresh=["item b"])
    book.add("07-R2-end", "R2", "a keyed item is added after the last one",
             Script().step(keyed("a", "b")).step(keyed("a", "b", "c")),
             kept=["item a", "item b"], fresh=["item c"])
    book.add("07-R2-everywhere", "R2", "five items from two: new ones in front, between and after",
             Script().step(keyed("b", "d")).step(keyed("a", "b", "c", "d", "e")),
             kept=["item b", "item d"], fresh=["item a", "item c", "item e"])
    book.add("07-R2-front-after-removal", "R2", "the first item goes and a new one takes the front: [a, b] to [x, b]",
             Script().step(keyed("a", "b")).step(keyed("x", "b")),
             kept=["item b"], fresh=["item x"], gone=["item a"])
    book.add("07-R2-into-empty-list", "R2", "items are added to an empty list, then one more in front",
             Script().step("<ul></ul>").step(keyed("b", "c")).step(keyed("a", "b", "c")),
             kept=["item b", "item c"], fresh=["item a"])

    # R3 ---------------------------------------------------------------------------------------------
    book.add("07-R3-insert-and-remove", "R3", "[a, b, c, d] becomes [x, b, y, d]: two new, two gone, two kept",
             Script().step(keyed("a", "b", "c", "d")).step(keyed("x", "b", "y", "d")),
             kept=["item b", "item d"], fresh=["item x", "item y"], gone=["item a", "item c"])
    book.add("07-R3-four-renders", "R3", "four renders in a row, each adding and dropping some items",
             Script().step(keyed("a", "b", "c")).step(keyed("b", "c", "d")).step(keyed("x", "c", "d", "y"))
                     .step(keyed("c")),
             kept=["item c"])
    book.add("07-R3-subtrees-kept", "R3", "a new item in front: the nested nodes of the kept items stay too",
             Script().step(ul('<li key="a"><span><b>A</b> tail</span></li>', '<li key="b"><span><b>B</b> tail</span></li>'))
                     .step(ul('<li key="z"><span><b>Z</b> tail</span></li>', '<li key="a"><span><b>A</b> tail</span></li>',
                              '<li key="b"><span><b>B</b> tail</span></li>')))
    book.add("07-R3-two-lists", "R3", "two lists in one tree reuse the keys a and b; each list is edited on its own",
             Script().step('<div><ul><li key="a">u-a</li><li key="b">u-b</li></ul><ol><li key="a">o-a</li><li key="b">o-b</li></ol></div>')
                     .step('<div><ul><li key="n">u-n</li><li key="a">u-a</li></ul><ol><li key="b">o-b</li><li key="c">o-c</li></ol></div>'))

    # R4 ---------------------------------------------------------------------------------------------
    book.add("07-R4-middle", "R4", "the middle one of three is removed",
             Script().step(keyed("a", "b", "c")).step(keyed("a", "c")),
             kept=["item a", "item c"], gone=["item b"])
    book.add("07-R4-first", "R4", "the first one of three is removed",
             Script().step(keyed("a", "b", "c")).step(keyed("b", "c")),
             kept=["item b", "item c"], gone=["item a"])
    book.add("07-R4-last", "R4", "the last one of three is removed",
             Script().step(keyed("a", "b", "c")).step(keyed("a", "b")),
             kept=["item a", "item b"], gone=["item c"])
    book.add("07-R4-adjacent", "R4", "three adjacent items in the middle of five are removed: [a, e] stays",
             Script().step(keyed("a", "b", "c", "d", "e")).step(keyed("a", "e")),
             kept=["item a", "item e"], gone=["item b", "item c", "item d"])
    book.add("07-R4-all-then-some", "R4", "the list is emptied, then two items come back",
             Script().step(keyed("a", "b", "c")).step("<ul></ul>").step(keyed("a", "b")),
             fresh=["item a", "item b"])

    # R5 ---------------------------------------------------------------------------------------------
    book.add("07-R5-key-change", "R5", "the key of the middle item changes from b to x",
             Script().step(keyed("a", "b", "c")).step(keyed("a", "x", "c")),
             kept=["item a", "item c"], fresh=["item x"], gone=["item b"])
    book.add("07-R5-same-key-other-tag", "R5", "the item with key b becomes a section, the key stays",
             Script().step('<div><p key="a">A</p><p key="b">B</p><p key="c">C</p></div>')
                     .step('<div><p key="a">A</p><section key="b">B</section><p key="c">C</p></div>'),
             kept=["A", "C"], fresh=["B"])

    # R6 ---------------------------------------------------------------------------------------------
    book.add("07-R6-front-insert", "R6", "text typed into two inputs, then a new input comes in front",
             Script().step(fields(("a", "ia"), ("b", "ib"))).type("ia", "hello").type("ib", "two words").dump()
                     .step(fields(("z", "iz"), ("a", "ia"), ("b", "ib"))).type("iz", "new").dump(),
             kept=["ia", "ib"], fresh=["iz"], between=(1, 2))
    book.add("07-R6-remove-middle", "R6", "three inputs with text, the middle one is removed",
             Script().step(fields(("a", "ia"), ("b", "ib"), ("c", "ic"))).type("ia", "one").type("ib", "two").type("ic", "three")
                     .step(fields(("a", "ia"), ("c", "ic"))),
             kept=["ia", "ic"], gone=["ib"])
    book.add("07-R6-key-change-resets", "R6", "an input gets a new key and starts empty; its neighbour keeps its text",
             Script().step(fields(("a", "ia"), ("b", "ib"))).type("ia", "typed").type("ib", "kept")
                     .step(fields(("a2", "ia"), ("b", "ib"))),
             kept=["ib"], fresh=["ia"])
    book.add("07-R6-typing-after-edits", "R6", "typing into a kept input after edits around it, twice",
             Script().step(fields(("a", "ia"), ("b", "ib"))).type("ib", "x")
                     .step(fields(("n", "in"), ("a", "ia"), ("b", "ib"))).type("ib", "xy").type("in", "q")
                     .step(fields(("n", "in"), ("b", "ib"))),
             kept=["in", "ib"], gone=["ia"])
    book.add("07-R6-bare-inputs", "R6", "inputs directly under a div, keyed, one added in the middle",
             Script().step('<div><input key="a" id="ia"/><input key="c" id="ic"/></div>').type("ia", "A!").type("ic", "C!").dump()
                     .step('<div><input key="a" id="ia"/><input key="b" id="ib"/><input key="c" id="ic"/></div>'),
             kept=["ia", "ic"], fresh=["ib"], between=(1, 2))

    # R7 ---------------------------------------------------------------------------------------------
    book.add("07-R7-empty-key-front-removal", "R7", "[x, \"\", y] loses x: the child with the empty key must stay",
             Script().step(keyed("x", "", "y")).step(keyed("", "y")),
             kept=["item empty", "item y"], gone=["item x"])
    book.add("07-R7-empty-key-insert", "R7", "a new item in front of one with the empty key, and one after it",
             Script().step(keyed("", "a")).step(keyed("b", "", "a", "c")),
             kept=["item empty", "item a"], fresh=["item b", "item c"])
    book.add("07-R7-zero-and-empty", "R7", "keys \"0\" and \"\" side by side: dropping \"0\" must keep the empty key",
             Script().step(keyed("0", "", "a")).step(keyed("", "a")),
             kept=["item empty", "item a"], gone=["item 0"])
    book.add("07-R7-look-alike-keys", "R7", "keys \"1\", \"01\" and \"001\" are three keys; the first one goes",
             Script().step(keyed("1", "01", "001")).step(keyed("01", "001")),
             kept=["item 01", "item 001"], gone=["item 1"])

    # R8 ---------------------------------------------------------------------------------------------
    book.add("07-R8-unkeyed-front", "R8", "no keys: Z is put in front of A and B, so the first two nodes are reused",
             Script().step(plain("A", "B")).step(plain("Z", "A", "B")))
    book.add("07-R8-unkeyed-shrink", "R8", "no keys: four items become two",
             Script().step(plain("one", "two", "three", "four")).step(plain("one", "two")))
    book.add("07-R8-unkeyed-grow", "R8", "no keys: two items become four",
             Script().step(plain("one", "two")).step(plain("one", "two", "three", "four")))
    book.add("07-R8-keyed-to-unkeyed", "R8", "the same two items, first with keys, then without: both are rebuilt",
             Script().step(keyed("a", "b")).step(plain("item a", "item b")).step(keyed("a", "b")))
    book.add("07-R8-unkeyed-inside-keyed", "R8", "keyed items with unkeyed content: a new item in front, content changes",
             Script().step(ul('<li key="a"><b>1</b><i>2</i></li>', '<li key="b"><b>3</b><i>4</i></li>'))
                     .step(ul('<li key="z"><b>0</b></li>', '<li key="a"><b>1</b><i>two</i><u>!</u></li>', '<li key="b"><b>3</b></li>')))

    # R9 ---------------------------------------------------------------------------------------------
    book.add("07-R9-first-render", "R9", "ops after the first render of three items, then after an identical one",
             Script().step(keyed("a", "b", "c")).step(keyed("a", "b", "c")))
    book.add("07-R9-nested-counts", "R9", "a new item with nested content costs every node; a removed one costs one",
             Script().step(ul('<li key="a"><b>x</b></li>')).step(ul('<li key="n"><span><i>p</i><i>q</i></span></li>', '<li key="a"><b>x</b></li>'))
                     .step(ul('<li key="n"><span><i>p</i><i>q</i></span></li>')))
    book.add("07-R9-tag-change", "R9", "the item with key b turns from p into section: new subtree, one removal",
             Script().step('<div><p key="a">A</p><p key="b"><i>B</i> text</p></div>')
                     .step('<div><p key="a">A</p><section key="b"><i>B</i> text</section></div>'))

    # E2E ----------------------------------------------------------------------------------------------
    todo = Script()
    todo.step("<ul></ul>")
    todo.step(ul(todo_item("1", "buy milk")))
    todo.type("n1", "2 litres").dump()
    todo.step(ul(todo_item("2", "write tests"), todo_item("1", "buy milk")))
    todo.step(ul(todo_item("3", "call home"), todo_item("2", "write tests"), todo_item("1", "buy milk")))
    todo.type("n3", "tonight").type("n2", "friday").dump()
    todo.step(ul(todo_item("3", "call home"), todo_item("1", "buy milk")))
    todo.step(ul(todo_item("4", "water plants"), todo_item("3", "call home"), todo_item("1", "buy milk (done)")))
    todo.step(ul(todo_item("4", "water plants")))
    book.add("07-E2E-todo-session", "E2E", "a todo-style list: add in front, type, remove from the middle and the end", todo)

    inbox = Script()
    inbox.step('<div><h2>inbox</h2><ul><li key="m1">first</li><li key="m2">second</li></ul><p>2 messages</p></div>')
    inbox.step('<div><h2>inbox</h2><ul><li key="m3">third</li><li key="m1">first</li><li key="m2">second</li></ul><p>3 messages</p></div>')
    inbox.step('<div><h2>inbox</h2><ul><li key="m3">third</li><li key="m2">second (read)</li></ul><p>2 messages</p></div>')
    inbox.step('<div><h2>inbox</h2><ul><li key="m4">fourth</li><li key="m3">third</li><li key="m2">second (read)</li><li key="m5">fifth</li></ul><p>4 messages</p></div>')
    book.add("07-E2E-inbox", "E2E", "a list between a heading and a counter: items come and go, the siblings stay put", inbox)


def todo_item(key, text):
    return f'<li key="{key}"><input id="n{key}"/><span>{text}</span></li>'


# ---- Random cases ------------------------------------------------------------------------------------

PLAIN_POOL = list("abcdefgh")
ODD_POOL = ["", "0", "00", "1", "01", "a", "b", "c", "d", "x"]


class Lists:
    """A random sequence of keyed lists. Keys are unique, new keys never come from the previous list
    (a key that is dropped and added in one render would count as shared, and shared keys keep their
    order here), and the keys two lists share stay in the same order."""

    def __init__(self, rng, pool, kind):
        self.rng, self.pool, self.kind = rng, pool, kind
        self.ids = {}
        self.counter = 0
        self.keys = []
        self.version = 0

    def fresh_key(self, avoid):
        options = [k for k in self.pool if k not in avoid]
        if options:
            return self.rng.choice(options)
        self.counter += 1
        return f"n{self.counter}"

    def first(self):
        count = self.rng.randint(2, 5)
        self.keys = []
        for _ in range(count):
            self.keys.append(self.fresh_key(self.keys))
        return self.keys

    def next(self):
        old = self.keys
        kept = [k for k in old if self.rng.random() < 0.7]
        new = list(kept)
        banned = set(old)
        for _ in range(self.rng.choice([0, 1, 1, 2, 3])):
            key = self.fresh_key(banned | set(new))
            banned.add(key)
            new.insert(self.rng.randint(0, len(new)), key)
        self.keys = new
        return new

    def input_id(self, key):
        return self.ids.setdefault(key, f"in{len(self.ids) + 1}")

    def markup(self):
        self.version += 1
        items = []
        for k in self.keys:
            if self.kind == "input":
                items.append(field_item(k, self.input_id(k)))
            elif self.kind == "nested":
                items.append(f'<li key="{k}"><b>{word(k)}</b><i>{self.rng.choice(["x", "y"])}</i></li>')
            else:
                label = word(k) if self.rng.random() < 0.7 else f"{word(k)} v{self.version}"
                items.append(li(k, label))
        return ul(*items)

    def type_somewhere(self, script):
        """Types into a few of the inputs on the page (only for the `input` kind)."""
        for k in self.keys:
            if self.rng.random() < 0.6:
                script.type(self.input_id(k), self.rng.choice(["a", "two words", "x1", "hello"]))


def random_lists(book, seed):
    plans = [("R3", "text", PLAIN_POOL, 0, "random edits on keyed text items"),
             ("R3", "nested", PLAIN_POOL, 1, "random edits on keyed items with nested content"),
             ("R6", "input", PLAIN_POOL, 0, "random edits on keyed inputs, typing between renders"),
             ("R6", "input", PLAIN_POOL, 1, "random edits on keyed inputs, typing between renders"),
             ("R7", "text", ODD_POOL, 0, "random edits with the keys \"\", \"0\", \"00\", \"1\", \"01\" in play"),
             ("R7", "input", ODD_POOL, 1, "random edits on inputs with the odd keys in play")]
    for req, kind, pool, n, what in plans:
        rng = rng_for(seed, f"07-{req}-{kind}-{n}")
        lists = Lists(rng, pool, kind)
        script = Script()
        steps = rng.randint(4, 6) + (2 if n == 2 else 0)
        lists.first()
        script.step(lists.markup())
        for _ in range(steps):
            if kind == "input":
                lists.type_somewhere(script)
            lists.next()
            script.step(lists.markup())
        book.add(f"07-{req}-random-s{seed}-{n}", req, f"{what} (seed {seed}, {steps + 1} renders)", script)

    # no keys at all: positions decide
    rng = rng_for(seed, "07-R8-random")
    script = Script()
    count = rng.randint(2, 5)
    steps = rng.randint(3, 5)
    for step in range(steps + 1):
        texts = [f"{rng.choice(['red', 'green', 'blue', 'grey'])} {i}" for i in range(count)]
        script.step(plain(*texts))
        count = max(0, count + rng.randint(-2, 3))
    book.add(f"07-R8-random-s{seed}-0", "R8", f"random lengths of an unkeyed list, texts change (seed {seed}, {steps + 1} renders)", script)


def main():
    args = wbcore.parse_args("07")
    book = Book()
    hand_made(book)
    random_lists(book, args.seed)
    book.save(args)


if __name__ == "__main__":
    main()
