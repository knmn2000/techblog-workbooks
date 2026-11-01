"""Test generator for assignment 12 (the todo app).

    py -P tools/gen_p12.py [--seed N] [--out DIR]

Expected output comes from real React 19 on jsdom running tools/oracle/todoApp.mjs (`run_oracle(..., todo=True)`).
Every session is also described to a small model of the application in plain Python (a list of items, a
draft, the next id); the generator stops if a dump that React printed differs from what the model says the
page looks like, label-free, or if a node that should have been kept changed its label.

Scenarios type only text that has no trailing space (the case file strips them) and, in one case, a draft
with leading spaces, which the app has to trim.
"""

import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wbcore  # noqa: E402
from reactgen import rng_for, run_oracle_batch  # noqa: E402

NN = "12"
SOURCE = "React 19.3.1 (react-dom 19.3.1) on jsdom 30.1.3 running tools/oracle/todoApp.mjs; every dump also checked against a model of the app in the generator"

COMPARE = "records dump=n node=depth,label,tag,props text=depth,value title=value"
EXPLAIN = "title:value=R8 title=R8"

REQUIREMENTS = [
    ("R1", "The page starts as the contract says: the form, an empty list, `0 left`, and the title `0 left`"),
    ("R2", "Typing in the input stores the draft, and the input shows it as its value"),
    ("R3", "Submitting a non-empty draft adds an item at the front of the list: the trimmed text, the next id counting from 1, a todo button, and the input is cleared"),
    ("R4", "Submitting an empty draft adds nothing"),
    ("R5", "The toggle button flips one item between todo and done, and puts the class done on its label while it is done"),
    ("R6", "The remove button deletes one item, and an id is never used twice"),
    ("R7", "The count paragraph reads `<n> left`, n being the number of items that are not done"),
    ("R8", "document.title is `<n> left` after every step"),
    ("R9", "Items are keyed by id: nodes of items that stay are kept (same nodes) when others are added, toggled or removed"),
    ("E2E", "Long sessions: scripted, and seeded random ones"),
]


# ---- the model of the page -----------------------------------------------------------------------

def prop(value):
    """A prop value as dump.js prints it: percent-encoded when it holds a space, a quote or a percent sign."""
    return quote(value, safe="-_.!~*'()") if re.search(r'[\s"%]', value) else value


def text(value):
    return value.replace("%", "%25").replace('"', "%22")


class Todo:
    def __init__(self):
        self.items = []  # {"id", "text", "done"}, newest first
        self.draft = ""
        self.next_id = 1

    @property
    def left(self):
        return sum(not item["done"] for item in self.items)

    def type(self, value):
        self.draft = value

    def submit(self):
        trimmed = self.draft.strip()
        if trimmed == "":
            return
        self.items.insert(0, {"id": self.next_id, "text": trimmed, "done": False})
        self.next_id += 1
        self.draft = ""

    def toggle(self, item_id):
        for item in self.items:
            if item["id"] == item_id:
                item["done"] = not item["done"]
                return
        raise AssertionError(f"no item {item_id}")

    def remove(self, item_id):
        before = len(self.items)
        self.items = [item for item in self.items if item["id"] != item_id]
        assert len(self.items) == before - 1, f"no item {item_id}"

    def lines(self, head=(), offset=0):
        """The dump of the page, without labels (a `node` line is `node <depth> <tag> "<props>"`)."""
        d = offset
        out = list(head)
        out.append(f'node {d} div "id=todo"')
        out.append(f'node {d + 1} form "id=todo-form"')
        value = f" value={prop(self.draft)}" if self.draft else ""
        out.append(f'node {d + 2} input "id=todo-input{value}"')
        out += [f'node {d + 2} button "id=todo-add"', f'text {d + 3} "Add"']
        out.append(f'node {d + 1} ul "id=todo-list"')
        for item in self.items:
            n = item["id"]
            done = "className=done " if item["done"] else ""
            out += [f'node {d + 2} li "id=item-{n}"',
                    f'node {d + 3} button "id=toggle-{n}"', f'text {d + 4} "{"done" if item["done"] else "todo"}"',
                    f'node {d + 3} span "{done}id=label-{n}"', f'text {d + 4} "{text(item["text"])}"',
                    f'node {d + 3} button "id=remove-{n}"', f'text {d + 4} "x"']
        out += [f'node {d + 1} p "id=todo-count"', f'text {d + 2} "{self.left} left"', f'title "{self.left} left"']
        return out


class Session:
    """A scenario and the model's answer for every dump in it."""

    def __init__(self, tree="<TodoApp/>", head=(), offset=0):
        self.model = Todo()
        self.lines = [f"tree t {tree}", "render t", "flush"]
        self.head, self.offset = list(head), offset
        self.dumps = []

    def type(self, value):
        assert value == value.rstrip(), "the case file strips trailing spaces"
        self.lines.append(f"type #todo-input {value}" if value else "type #todo-input")
        self.model.type(value)

    def submit(self):
        self.lines.append("submit #todo-form")
        self.model.submit()

    def press_add(self):
        self.lines.append("click #todo-add")
        self.model.submit()

    def add(self, value, how="submit"):
        self.type(value)
        self.submit() if how == "submit" else self.press_add()

    def toggle(self, item_id):
        self.lines.append(f"click #toggle-{item_id}")
        self.model.toggle(item_id)

    def remove(self, item_id):
        self.lines.append(f"click #remove-{item_id}")
        self.model.remove(item_id)

    def dump(self):
        self.lines.append("dump")
        self.dumps.append(self.model.lines(self.head, self.offset))
        return self


def dump_blocks(lines):
    blocks, current = [], None
    for l in lines:
        if l.startswith("dump "):
            current = []
            blocks.append(current)
        elif current is not None:
            current.append(l)
    return blocks


def strip_label(line):
    m = re.match(r"^(node \d+) ([a-z]+) (.*)$", line)
    return f"{m.group(1)} {m.group(3)}" if m else line


def check_against_model(cid, lines, session):
    blocks = dump_blocks(lines)
    assert len(blocks) == len(session.dumps), f"{cid}: {len(blocks)} dumps, the model expects {len(session.dumps)}"
    for n, (block, expected) in enumerate(zip(blocks, session.dumps), 1):
        got = [strip_label(l) for l in block]
        assert got == expected, (f"{cid}: dump {n} differs from the model\n  React: {got}\n  model: {expected}")
    # nodes that stay are the same nodes: the label of an element with a given id never changes
    seen = {}
    for block in blocks:
        for l in block:
            m = re.match(r'^node \d+ ([a-z]+) [a-z]+ "(?:[^"]*? )?id=([\w-]+)', l)
            if not m:
                continue
            label, ident = m.group(1), m.group(2)
            if ident in seen:
                assert seen[ident] == label, f"{cid}: the node {ident} was rebuilt ({seen[ident]} -> {label})"
            seen[ident] = label
    assert len(set(seen.values())) == len(seen), f"{cid}: two nodes share a label"


# ---- the cases -----------------------------------------------------------------------------------

def make_cases():
    c = []

    def case(cid, req, title, session):
        c.append((cid, req, title, session))

    # R1
    s = Session().dump()
    case("12-R1-empty-app", "R1", "the app just rendered", s)
    s = Session("<div><p>top</p><TodoApp/></div>", head=['node 0 div ""', 'node 1 p ""', 'text 2 "top"'], offset=1).dump()
    case("12-R1-inside-another-tree", "R1", "the app as the second child of a div, after a paragraph", s)

    # R2
    s = Session()
    s.type("milk")
    s.dump()
    case("12-R2-type-one-word", "R2", "type milk", s)
    s = Session()
    s.type("a")
    s.dump()
    s.type("buy some milk")
    s.dump()
    case("12-R2-type-replaces-the-draft", "R2", "type a, then buy some milk: the input holds the last text", s)
    s = Session()
    s.type('say "hi" to 100% of them')
    s.dump()
    case("12-R2-type-quotes-and-percent", "R2", "a draft with quotes and a percent sign", s)
    s = Session()
    s.type("abc")
    s.dump()
    s.type("")
    s.dump()
    case("12-R2-type-then-erase", "R2", "type abc, then type nothing: the input is empty again", s)

    # R3
    s = Session()
    s.add("buy milk")
    s.dump()
    case("12-R3-add-one-item", "R3", "type buy milk and submit the form", s)
    s = Session()
    s.add("buy milk", how="click")
    s.dump()
    case("12-R3-add-with-the-button", "R3", "type buy milk and click the Add button", s)
    s = Session()
    for word in ("one", "two", "three"):
        s.add(word)
    s.dump()
    case("12-R3-ids-and-front-insert", "R3", "three items added: ids 1, 2, 3, newest first", s)
    s = Session()
    s.add("   walk the dog")
    s.dump()
    case("12-R3-text-is-trimmed", "R3", "a draft that starts with spaces is stored without them", s)
    s = Session()
    s.add('write "tests" for 100% of it')
    s.dump()
    case("12-R3-quotes-and-percent-kept", "R3", "quotes and a percent sign inside the text stay", s)

    # R4
    s = Session()
    s.submit()
    s.dump()
    case("12-R4-submit-with-nothing-typed", "R4", "submit right away", s)
    s = Session()
    s.press_add()
    s.dump()
    case("12-R4-add-button-with-nothing-typed", "R4", "click Add right away", s)
    s = Session()
    s.add("first")
    s.submit()
    s.add("second")
    s.dump()
    case("12-R4-empty-submit-between-adds", "R4", "an empty submit after an add changes nothing, and the next id is 2", s)
    s = Session()
    s.type("regret")
    s.type("")
    s.submit()
    s.dump()
    case("12-R4-typed-then-erased", "R4", "type regret, erase it, submit", s)

    # R5
    s = Session()
    s.add("a")
    s.toggle(1)
    s.dump()
    case("12-R5-toggle-one-item", "R5", "add an item, toggle it", s)
    s = Session()
    s.add("a")
    s.toggle(1)
    s.toggle(1)
    s.dump()
    case("12-R5-toggle-twice", "R5", "toggle twice: back to todo", s)
    s = Session()
    for word in ("one", "two", "three"):
        s.add(word)
    s.toggle(2)
    s.dump()
    s.toggle(3)
    s.dump()
    case("12-R5-toggle-only-that-item", "R5", "three items, toggle the second and then the third", s)

    # R6
    s = Session()
    for word in ("one", "two", "three"):
        s.add(word)
    s.remove(2)
    s.dump()
    case("12-R6-remove-the-middle-item", "R6", "three items, remove the one with id 2", s)
    s = Session()
    for word in ("one", "two", "three", "four"):
        s.add(word)
    s.remove(4)
    s.remove(1)
    s.dump()
    case("12-R6-remove-first-and-last", "R6", "four items, remove ids 4 and 1 (the first and the last in the list)", s)
    s = Session()
    s.add("one")
    s.add("two")
    s.remove(1)
    s.remove(2)
    s.dump()
    case("12-R6-remove-everything", "R6", "two items, both removed", s)
    s = Session()
    s.add("one")
    s.add("two")
    s.remove(2)
    s.add("three")
    s.remove(1)
    s.add("four")
    s.dump()
    case("12-R6-ids-never-reused", "R6", "two items, remove id 2 and add one, remove id 1 and add one: the new ids are 3 and 4", s)

    # R7
    s = Session()
    for word in ("one", "two", "three"):
        s.add(word)
    s.dump()
    case("12-R7-count-after-adds", "R7", "three adds: 3 left", s)
    s = Session()
    s.add("one")
    s.add("two")
    s.toggle(1)
    s.toggle(2)
    s.dump()
    case("12-R7-count-all-done", "R7", "two items, both toggled: 0 left", s)
    s = Session()
    for word in ("one", "two", "three", "four"):
        s.add(word)
    s.toggle(4)
    s.dump()
    case("12-R7-count-one-done-of-four", "R7", "four items, the newest done: 3 left", s)
    s = Session()
    for word in ("one", "two", "three"):
        s.add(word)
    s.toggle(1)
    s.dump()
    s.toggle(3)
    s.dump()
    s.toggle(1)
    s.dump()
    case("12-R7-count-with-done-items", "R7", "three items, toggles change the count", s)
    s = Session()
    for word in ("one", "two", "three"):
        s.add(word)
    s.toggle(2)
    s.remove(2)
    s.dump()
    s.remove(1)
    s.dump()
    case("12-R7-count-after-removing", "R7", "removing a done item keeps the count, removing a todo item lowers it", s)

    # R8
    s = Session()
    s.dump()
    s.add("one")
    s.add("two")
    s.dump()
    s.toggle(1)
    s.dump()
    case("12-R8-title-follows-the-count", "R8", "the title after the first render, two adds and a toggle", s)
    s = Session()
    for word in ("one", "two", "three", "four"):
        s.add(word)
    s.toggle(1)
    s.remove(2)
    s.dump()
    case("12-R8-title-after-toggles-and-removals", "R8", "four items, a toggle and a removal: 2 left in the title", s)
    s = Session()
    s.add("one")
    s.add("two")
    s.remove(1)
    s.remove(2)
    s.dump()
    case("12-R8-title-back-to-zero", "R8", "two items added and removed: the title is 0 left again", s)

    # R9
    s = Session()
    s.add("one")
    s.dump()
    s.add("two")
    s.dump()
    s.add("three")
    s.dump()
    case("12-R9-front-insert-keeps-nodes", "R9", "adding at the front keeps the older items' nodes", s)
    s = Session()
    for word in ("one", "two", "three"):
        s.add(word)
    s.dump()
    s.remove(2)
    s.dump()
    s.remove(3)
    s.dump()
    case("12-R9-remove-keeps-the-others", "R9", "removing from the middle and the front keeps the other nodes", s)
    s = Session()
    s.add("one")
    s.add("two")
    s.dump()
    s.toggle(1)
    s.dump()
    s.toggle(2)
    s.dump()
    case("12-R9-toggle-keeps-nodes", "R9", "toggling only rewrites the item's button and label", s)
    s = Session()
    s.dump()
    for part in ("b", "bu", "buy"):
        s.type(part)
        s.dump()
    case("12-R9-typing-keeps-the-input", "R9", "typing letter by letter keeps the input node", s)

    # E2E
    s = Session()
    s.dump()
    s.add("buy milk")
    s.dump()
    s.submit()
    s.dump()
    s.add('write "tests" 100%')
    s.dump()
    s.toggle(1)
    s.dump()
    s.remove(2)
    s.dump()
    case("12-E2E-short-session", "E2E", "buy milk, an empty submit, a text with quotes, toggle 1, remove 2", s)
    s = long_session()
    case("12-E2E-long-session", "E2E", "a scripted session of about 50 steps: adds from the form and from the button, toggles, removals", s)
    return c


def long_session():
    s = Session()
    s.dump()
    words = ["milk", "eggs", "bread", "call mum", "pay rent", "water plants", "read a chapter", "file taxes", "walk", "cook"]
    for i, w in enumerate(words[:6]):
        s.add(w, how="click" if i % 3 == 2 else "submit")
        if i % 2:
            s.dump()
    s.toggle(2)
    s.toggle(5)
    s.dump()
    s.remove(3)
    s.submit()
    s.dump()
    s.toggle(2)
    s.remove(6)
    s.add(words[6])
    s.dump()
    s.type("half-typed")
    s.dump()
    s.toggle(7)
    s.dump()
    s.submit()
    s.dump()
    s.remove(1)
    s.remove(4)
    s.add(words[7], how="click")
    s.toggle(9)
    s.dump()
    s.remove(5)
    s.remove(7)
    s.remove(8)
    s.remove(9)
    s.dump()
    s.add(words[8])
    s.add(words[9], how="click")
    s.toggle(10)
    s.dump()
    return s


WORDS = ["milk", "eggs", "bread", "tea", "call mum", "pay rent", "plants", "taxes", "write 5 tests", "a & b", 'say "hi"',
         "100%", "x", "buy 2 apples", "fix the bike", "email Sam"]


def random_session(seed, index):
    rng = rng_for(seed, f"p12-session-{index}")
    s = Session()
    s.dump()
    for _ in range(rng.randint(18, 34)):
        roll = rng.random()
        ids = [item["id"] for item in s.model.items]
        if roll < 0.30:
            s.add(rng.choice(WORDS), how=rng.choice(["submit", "click"]))
        elif roll < 0.42 and ids:
            s.toggle(rng.choice(ids))
        elif roll < 0.52 and ids:
            s.remove(rng.choice(ids))
        elif roll < 0.60:
            s.type(rng.choice(WORDS))
        elif roll < 0.68:
            s.type("")
            s.submit() if rng.random() < 0.5 else s.press_add()
        elif roll < 0.76:
            s.add(("   " + rng.choice(WORDS)), how=rng.choice(["submit", "click"]))
        else:
            s.add(rng.choice(WORDS))
        if rng.random() < 0.35:
            s.dump()
    s.dump()
    return s


def main():
    args = wbcore.parse_args(NN)
    cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, explain=EXPLAIN, source=SOURCE)
    specs = make_cases()
    for k in range(5):
        specs.append((f"12-E2E-random-s{args.seed}-{k}", "E2E",
                      f"seeded random session {k} (seed {args.seed}): adds, toggles, removals, empty submits", random_session(args.seed, k)))
    outputs = run_oracle_batch([s[3].lines for s in specs], todo=True)
    for (cid, req, title, session), lines in zip(specs, outputs):
        check_against_model(cid, lines, session)
        cases.add(cid, req, title, session.lines, expected=lines)
    cases.save()


if __name__ == "__main__":
    main()
