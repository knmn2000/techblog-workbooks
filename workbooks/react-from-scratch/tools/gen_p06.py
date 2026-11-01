"""Test generator for assignment 06 (reconcile children by position).

    py -P tools/gen_p06.py [--seed N] [--out DIR]

Scenario commands used: tree, render (two or more per scenario, always followed by flush), flush, dump,
click, log. No idle, no ops, no keys: a render is never restarted half way.

Expected lines: real React 19.3.1 on jsdom (tools/oracle). The labels in a dump show identity: the same
label in two dumps is the same DOM node, so "kept" and "replaced" are what React does.

A second, independent opinion: this file also contains a tiny model of the rule the page states
(children of one parent matched by position; same tag keeps the node and updates props and text, another
tag makes a new node, extra old children go, extra new ones are added, a handler is the latest one). It
runs every scenario, with its own labeler, dump writer and event bubbling, and the generator stops if the
model and React disagree on a single line. So the page's rule is proven against React for every case.
"""

import copy
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reactgen  # noqa: E402
import wbcore  # noqa: E402

COMPARE = "records dump=n node=depth,label,tag,props text=depth,value title=value log=text"
EXPLAIN = "node:props=R2 log:text=R6"
SOURCE = ("React 19.3.1 on jsdom 30.1.3 (tools/oracle), cross-checked line by line against "
          "a positional model in tools/gen_p06.py")

REQUIREMENTS = [
    ("R1", "same type at the same position: the DOM node is kept (same label), its props and text are brought up to date"),
    ("R2", "a prop that is gone from the new element is cleared on the kept node"),
    ("R3", "a different type at a position gets a new node, and it stays at that position among its siblings"),
    ("R4", "new children beyond the old ones are added after them"),
    ("R5", "old children beyond the new ones are removed, once each, however many are adjacent, "
           "and also after earlier renders"),
    ("R6", "handlers follow the latest render: a click runs the new handler once, and nothing for a removed one"),
    ("R7", "changes at several depths in one render: kept, replaced, added and removed nodes together"),
    ("R8", "random pairs and triples of trees: the container ends up as the last tree, and the nodes that stay are the ones the positional rule keeps"),
    ("E2E", "whole sessions of renders, clicks and dumps"),
]

SAFE_TAGS = ["div", "span", "section", "em", "b", "i", "ul", "nav", "article", "aside"]
WORDS = reactgen.WORDS


# ---- the model: positional reconciliation, written from the page's rule ---------------------------

ATTR = re.compile(r"""([^\s=]+)(?:=(?:"([^"]*)"|'([^']*)'|(\S+)))?""")


def parse_attrs(raw):
    """name -> True | text | ('h', handler name). Same reading as the harness's markup."""
    out = {}
    for m in ATTR.finditer(raw):
        name = m.group(1)
        value = next((g for g in m.groups()[1:] if g is not None), True)
        if isinstance(value, str) and value.startswith("@"):
            value = ("h", value[1:])
        out[name] = value
    return out


def to_tree(node):
    """reactgen.parse_markup output -> {'el': tag, 'attrs': {...}, 'kids': [...]} or {'text': value}."""
    if node[0] == "text":
        return {"text": node[1]}
    return {"el": node[1], "attrs": parse_attrs(node[2]), "kids": [to_tree(k) for k in node[3]]}


def parse(markup):
    (root,) = reactgen.parse_markup(markup)
    return to_tree(root)


class Live:
    """A node on the model's page: identity (uid) plus what it shows now."""
    counter = 0

    def __init__(self, tree):
        Live.counter += 1
        self.uid = Live.counter
        self.tree = tree
        self.kids = []


def reconcile(old, tree):
    """Positional rule: the same kind of node (same tag, or text) at the same position is kept."""
    same = old is not None and ("el" in tree) == ("el" in old.tree) and (
        "text" in tree or old.tree["el"] == tree["el"])
    live = old if same else Live(tree)
    live.tree = tree
    old_kids = live.kids if same else []
    new_kids = tree.get("kids", [])
    live.kids = [reconcile(old_kids[i] if i < len(old_kids) else None, k) for i, k in enumerate(new_kids)]
    return live


def label_for(index):
    name = ""
    n = index + 1
    while n > 0:
        name = chr(97 + (n - 1) % 26) + name
        n = (n - 1) // 26
    return name


def encode_prop(value):
    text = str(value)
    return quote(text, safe="-_.!~*'()") if re.search(r'[\s"%]', text) else text


def props_text(tree):
    attrs, tag = tree["attrs"], tree["el"]
    shown = []
    for name in ("className", "disabled", "id", "title", "value"):
        value = attrs.get(name)
        if value is None or value == "" or isinstance(value, tuple):
            continue
        if name == "disabled" and tag not in ("button", "input", "textarea"):
            continue
        if name == "value" and tag not in ("input", "textarea"):
            continue
        shown.append(f"{name}=true" if value is True else f"{name}={encode_prop(value)}")
    return " ".join(shown)


def encode_text(text):
    return text.replace("%", "%25").replace('"', "%22").replace("\r", "%0D").replace("\n", "%0A")


class Model:
    def __init__(self):
        self.root = None
        self.labels = {}
        self.dumps = 0
        self.log = []

    def render(self, tree):
        self.root = reconcile(self.root, tree)

    def dump(self):
        self.dumps += 1
        lines = [f"dump {self.dumps}"]

        def walk(live, depth):
            if "text" in live.tree:
                if live.tree["text"] != "":
                    lines.append(f'text {depth} "{encode_text(live.tree["text"])}"')
                return
            label = self.labels.setdefault(live.uid, label_for(len(self.labels)))
            lines.append(f'node {depth} {label} {live.tree["el"]} "{props_text(live.tree)}"')
            for k in live.kids:
                walk(k, depth + 1)

        if self.root is not None:
            walk(self.root, 0)
        return lines

    def click(self, element_id):
        path = []

        def find(live, trail):
            if "text" in live.tree:
                return None
            here = trail + [live]
            if live.tree["attrs"].get("id") == element_id:
                return here
            for k in live.kids:
                found = find(k, here)
                if found:
                    return found
            return None

        found = find(self.root, [])
        assert found, f"model: no element with id {element_id}"
        for live in reversed(found):  # target first, then each ancestor
            handler = live.tree["attrs"].get("onClick")
            if isinstance(handler, tuple):
                self.log.append(handler[1])


def run_model(trees, steps):
    """The output lines of a scenario according to the model."""
    Live.counter = 0
    model, out = Model(), []
    parsed = {name: parse(m) for name, m in trees.items()}
    for step in steps:
        word, _, arg = step.partition(" ")
        if word == "render":
            model.render(copy.deepcopy(parsed[arg]))
        elif word == "dump":
            out += model.dump()
        elif word == "click":
            model.click(arg.lstrip("#"))
        elif word == "log":
            out += [f"log {entry}" for entry in model.log]
            model.log = []
        elif word == "flush":
            pass
        else:
            raise AssertionError(f"model: unknown command {step}")
    return out


# ---- scenarios -----------------------------------------------------------------------------------

class Scenario:
    def __init__(self, case_id, req, title, trees, steps):
        self.case_id, self.req, self.title = case_id, req, title
        self.trees, self.steps = trees, steps

    def lines(self):
        return [f"tree {name} {m}" for name, m in self.trees.items()] + self.steps


def session(case_id, req, title, markups):
    """Renders each markup in turn (flush, dump after each). Trees are named a, b, c, ..."""
    names = [chr(97 + i) for i in range(len(markups))]
    steps = []
    for n in names:
        steps += [f"render {n}", "flush", "dump"]
    return Scenario(case_id, req, title, dict(zip(names, markups)), steps)


def clicking(case_id, req, title, rounds):
    """rounds: [(markup, [ids to click])]. After each render: dump, then every click followed by log."""
    names = [chr(97 + i) for i in range(len(rounds))]
    steps = []
    for n, (markup, clicks) in zip(names, rounds):
        steps += [f"render {n}", "flush", "dump"]
        for element_id in clicks:
            steps += [f"click #{element_id}", "log"]
    return Scenario(case_id, req, title, {n: r[0] for n, r in zip(names, rounds)}, steps)


def ul(*items, attrs=""):
    a = f" {attrs}" if attrs else ""
    return f"<ul{a}>" + "".join(f"<li>{t}</li>" for t in items) + "</ul>"


def handwritten():
    cases = []
    add = cases.append

    # R1: same type, same position: kept and updated
    add(session("06-R1-text-changes", "R1", "one paragraph, new text", ["<p>one</p>", "<p>two</p>"]))
    add(session("06-R1-props-change", "R1", "a div gets another id and a class",
                ["<div id=x>hi</div>", "<div id=y className=k>hi</div>"]))
    add(session("06-R1-every-node-kept", "R1", "three paragraphs, each with new text",
                ["<div><p>a</p><p>b</p><p>c</p></div>", "<div><p>A</p><p>B</p><p>C</p></div>"]))
    page = "<section id=s><h1>Title</h1><p className=lead>Lead <b>bold</b></p></section>"
    add(session("06-R1-same-tree-twice", "R1", "the same tree rendered twice and a third time", [page, page, page]))
    add(session("06-R1-three-renders", "R1", "a list through three different renders",
                [ul("one", "two"), ul("1", "2"), ul("x", "y", attrs="title=t")]))
    add(session("06-R1-inline-text-pieces", "R1", "two text pieces and an inline element all change",
                ["<p>a <b>b</b> c</p>", "<p>x <b>y</b> z</p>"]))

    # R2: props that disappear
    add(session("06-R2-all-props-removed", "R2", "id, className and title all go",
                ["<div id=x className=k title=t>hi</div>", "<div>hi</div>"]))
    add(session("06-R2-disabled-removed", "R2", "a disabled button is enabled again",
                ["<button disabled id=b>go</button>", "<button id=b>go</button>"]))
    add(session("06-R2-one-out-one-in", "R2", "className removed, title added, id kept",
                ["<p id=a className=c>x</p>", "<p id=a title=t>x</p>"]))
    add(session("06-R2-set-then-cleared", "R2", "a prop that appears and goes again",
                ["<button>go</button>", "<button disabled className=hot>go</button>", "<button>go</button>"]))

    # R3: another type at a position
    add(session("06-R3-root-changes-type", "R3", "div becomes p at the root", ["<div id=a>x</div>", "<p id=a>x</p>"]))
    add(session("06-R3-middle-child", "R3", "the middle of three children changes tag",
                ["<div><p>A</p><b>B</b><i>C</i></div>", "<div><p>A</p><u>B</u><i>C</i></div>"]))
    add(session("06-R3-first-child", "R3", "the first of three changes tag",
                ["<div><p>A</p><p>B</p><p>C</p></div>", "<div><h3>A</h3><p>B</p><p>C</p></div>"]))
    add(session("06-R3-last-child", "R3", "the last of three changes tag",
                ["<div><p>A</p><p>B</p><p>C</p></div>", "<div><p>A</p><p>B</p><h3>C</h3></div>"]))
    add(session("06-R3-two-of-five", "R3", "children 1 and 4 of five change tag",
                ["<div><p>1</p><p>2</p><p>3</p><p>4</p><p>5</p></div>",
                 "<div><h3>1</h3><p>2</p><p>3</p><span>4</span><p>5</p></div>"]))
    add(session("06-R3-subtree-replaced", "R3", "a section becomes an article, its children are new nodes",
                ["<div><section><p>x</p><p>y</p></section><b>z</b></div>",
                 "<div><article><p>x</p><p>y</p></article><b>z</b></div>"]))
    add(session("06-R3-text-and-element", "R3", "text becomes an element at the same position and back",
                ["<p>hello</p>", "<p><b>hello</b></p>", "<p>hello</p>"]))
    add(session("06-R3-there-and-back", "R3", "the middle child changes tag and then changes back",
                ["<div><p>A</p><b>B</b><i>C</i></div>", "<div><p>A</p><u>B</u><i>C</i></div>",
                 "<div><p>A</p><b>B</b><i>C</i></div>"]))

    # R4: more children
    add(session("06-R4-list-grows", "R4", "one item becomes three", [ul("a"), ul("a", "b", "c")]))
    add(session("06-R4-empty-gets-children", "R4", "an empty div gets two paragraphs",
                ["<div></div>", "<div><p>a</p><p>b</p></div>"]))
    add(session("06-R4-nested-list-grows", "R4", "the inner list grows, the paragraph after it stays last",
                ["<div><ul><li>a</li></ul><p>x</p></div>", "<div><ul><li>a</li><li>b</li></ul><p>x</p></div>"]))
    add(session("06-R4-text-then-element", "R4", "a paragraph with text gets an element after the text",
                ["<p>a</p>", "<p>a<b>b</b></p>"]))

    # R5: fewer children
    add(session("06-R5-three-to-two", "R5", "one trailing item removed", [ul("a", "b", "c"), ul("a", "b")]))
    add(session("06-R5-four-to-two", "R5", "two adjacent trailing items removed", [ul("a", "b", "c", "d"), ul("a", "b")]))
    add(session("06-R5-three-to-none", "R5", "all three items removed", [ul("a", "b", "c"), "<ul></ul>"]))
    add(session("06-R5-five-to-three-with-updates", "R5", "two adjacent removed while the others change",
                [ul("a", "b", "c", "d", "e"), ul("A", "B", "C", attrs="id=u")]))
    add(session("06-R5-nested-adjacent", "R5", "three adjacent items removed from an inner list",
                ["<div><ul><li>a</li><li>b</li><li>c</li><li>d</li></ul><p>after</p></div>",
                 "<div><ul><li>a</li></ul><p>after</p></div>"]))
    add(session("06-R5-removals-in-two-renders", "R5", "5 items, then 3, then 1",
                [ul("a", "b", "c", "d", "e"), ul("a", "b", "c"), ul("a")]))
    add(session("06-R5-there-and-back", "R5", "3 items, then 1, then 3 again",
                [ul("a", "b", "c"), ul("a"), ul("a", "b", "c")]))
    add(session("06-R5-unkeyed-middle-removal", "R5", "A, B, C becomes A, C: the second node takes the text C",
                [ul("A", "B", "C"), ul("A", "C")]))
    add(session("06-R5-element-and-text-removed", "R5", "an element and the text after it are removed",
                ["<p>a<b>b</b>c</p>", "<p>a</p>"]))
    add(session("06-R5-replaced-and-removed", "R5", "one child replaced and two removed in one render",
                ["<div><p>a</p><b>b</b><i>c</i><u>d</u></div>", "<div><p>a</p><s>b</s></div>"]))

    # R6: handlers
    btn = lambda h, text="x": f"<button id=b onClick=@{h}>{text}</button>" if h else f"<button id=b>{text}</button>"
    add(clicking("06-R6-handler-replaced", "R6", "the handler changes from one to two",
                 [(btn("one"), ["b"]), (btn("two"), ["b"])]))
    add(clicking("06-R6-same-function-again", "R6", "the same handler in every render still runs once per click",
                 [(btn("one"), ["b"]), (btn("one"), ["b"]), (btn("one"), ["b", "b"])]))
    add(clicking("06-R6-handler-removed", "R6", "the second render has no handler",
                 [(btn("one"), ["b"]), (btn(None), ["b"])]))
    add(clicking("06-R6-handler-added", "R6", "the first render has no handler, the second has one",
                 [(btn(None), ["b"]), (btn("one"), ["b"])]))
    add(clicking("06-R6-new-node-has-handler", "R6", "a replaced element carries the new handler",
                 [("<div><button id=b onClick=@one>x</button></div>", ["b"]),
                  ("<div><a id=b onClick=@two>x</a></div>", ["b"])]))
    add(clicking("06-R6-parent-and-child", "R6", "a parent's and a child's handler change in turn",
                 [("<div id=p onClick=@p><button id=c onClick=@c>x</button></div>", ["c"]),
                  ("<div id=p onClick=@p2><button id=c onClick=@c>x</button></div>", ["c"]),
                  ("<div id=p onClick=@p><button id=c onClick=@c2>x</button></div>", ["c"])]))
    add(clicking("06-R6-alternating", "R6", "one, two, one, two over four renders",
                 [(btn("one"), ["b"]), (btn("two"), ["b"]), (btn("one"), ["b"]), (btn("two"), ["b"])]))
    add(clicking("06-R6-handler-moves-by-position", "R6", "the handler moves from the first button to the second",
                 [("<div><button id=x onClick=@one>x</button><button id=y>y</button></div>", ["x", "y"]),
                  ("<div><button id=x>x</button><button id=y onClick=@one>y</button></div>", ["x", "y"])]))

    # R7: changes at several depths
    add(session("06-R7-deep-edit", "R7", "text, an added item and a changed item four levels down",
                ["<div><section><ul><li>a</li><li>b</li></ul></section></div>",
                 "<div><section><ul><li>a</li><li>B</li><li>c</li></ul></section></div>"]))
    add(session("06-R7-page-edit", "R7", "a page with a new class, a shorter nav, a replaced paragraph in the middle and a new one",
                ["<main id=app><header><h1>Title</h1><nav><a>one</a><a>two</a></nav></header>"
                 "<section className=body><p>First</p><p>Second</p><p>Third</p></section><footer>bye</footer></main>",
                 "<main id=app className=dark><header><h1>New title</h1><nav><a>one</a></nav></header>"
                 "<section className=body><p>First</p><div>Second</div><p>Third</p><p>Fourth</p></section>"
                 "<footer title=f>bye</footer></main>"]))
    add(session("06-R7-replaced-then-updated", "R7", "a replaced subtree is kept by the render after it",
                ["<div><section><h2>t</h2><p>x</p></section></div>", "<div><article><h2>t</h2><p>x</p></article></div>",
                 "<div><article><h2>T</h2><p>X</p></article></div>"]))
    add(session("06-R7-list-edits", "R7", "six items: one edited, two removed, a class added",
                [ul("a", "b", "c", "d", "e", "f"), ul("a", "b", "C", "d", attrs="className=short")]))

    # E2E
    add(clicking("06-E2E-add-and-remove", "E2E", "a small app: a button and a list through five renders",
                 [("<div id=app><button id=go onClick=@add>add</button><ul><li>one</li></ul></div>", ["go"]),
                  ("<div id=app><button id=go onClick=@add>add</button><ul><li>one</li><li>two</li></ul></div>", ["go"]),
                  ("<div id=app><button id=go onClick=@add>add</button><ul><li>one</li><li>two</li><li>three</li></ul></div>", []),
                  ("<div id=app className=full><button id=go onClick=@stop>stop</button><ul><li>one</li></ul></div>", ["go"]),
                  ("<div id=app><p>done</p></div>", [])]))
    add(session("06-E2E-section-swap", "E2E", "a layout that swaps its sidebar and shrinks its main area",
                ["<div id=root><aside><ul><li>a</li><li>b</li></ul></aside><main><p>one</p><p>two</p><p>three</p></main></div>",
                 "<div id=root><nav><ul><li>a</li><li>b</li></ul></nav><main><p>one</p></main></div>",
                 "<div id=root><nav><ul><li>a</li></ul></nav><main><p>one</p><p>two</p></main><footer>f</footer></div>"]))
    return cases


# ---- the random section --------------------------------------------------------------------------

def gen_el(rng, depth, width):
    attrs = {}
    if rng.random() < 0.35:
        attrs["id"] = f"{rng.choice(WORDS)}{rng.randint(1, 99)}"
    if rng.random() < 0.25:
        attrs["className"] = rng.choice(WORDS)
    if rng.random() < 0.15:
        attrs["title"] = rng.choice(WORDS)
    kids = []
    if depth > 0:
        for _ in range(rng.randint(0, width)):
            if rng.random() < 0.3 and not (kids and "text" in kids[-1]):
                kids.append({"text": rng.choice(WORDS)})
            else:
                kids.append(gen_el(rng, depth - 1, width))
    return {"el": rng.choice(SAFE_TAGS), "attrs": attrs, "kids": kids}


def elements(tree, found=None):
    found = [] if found is None else found
    if "el" in tree:
        found.append(tree)
        for k in tree["kids"]:
            elements(k, found)
    return found


def mutate(rng, tree, forced=None):
    """A random edit of 1 to 4 places: texts, props, tags, children added, removed or inserted. `forced`
    names an edit that has to happen first: 'tag-nonlast' (a child with later siblings changes tag) or
    'remove-two' (the last two children of some element go). ValueError if the tree has no place for it."""
    tree = copy.deepcopy(tree)
    for n in range(rng.randint(1, 4)):
        els = elements(tree)
        el = rng.choice(els)
        op = rng.choice(["text", "prop", "prop", "tag", "append", "remove-tail", "remove-one", "insert-front"])
        texts = [(parent, i) for parent in els for i, k in enumerate(parent["kids"]) if "text" in k]
        if n == 0 and forced == "tag-nonlast":
            spots = [k for parent in els for k in parent["kids"][:-1] if "el" in k]
            if not spots:
                raise ValueError(forced)
            target = rng.choice(spots)
            target["el"] = rng.choice([t for t in SAFE_TAGS if t != target["el"]])
        elif n == 0 and forced == "remove-two":
            spots = [parent for parent in els if len(parent["kids"]) >= 2]
            if not spots:
                raise ValueError(forced)
            del rng.choice(spots)["kids"][-2:]
        elif op == "text" and texts:
            parent, i = rng.choice(texts)
            parent["kids"][i]["text"] = rng.choice(WORDS) + " " + rng.choice(WORDS)
        elif op == "prop":
            name = rng.choice(["id", "className", "title"])
            if name in el["attrs"] and rng.random() < 0.5:
                del el["attrs"][name]
            else:
                el["attrs"][name] = f"{rng.choice(WORDS)}{rng.randint(1, 9)}"
        elif op == "tag":
            el["el"] = rng.choice([t for t in SAFE_TAGS if t != el["el"]])
        elif op == "append" and len(el["kids"]) < 6:
            new = gen_el(rng, 1, 2) if rng.random() < 0.7 else {"text": rng.choice(WORDS)}
            if "text" in new and el["kids"] and "text" in el["kids"][-1]:
                new = gen_el(rng, 1, 2)
            el["kids"].append(new)
        elif op == "remove-tail" and el["kids"]:
            del el["kids"][-rng.randint(1, min(3, len(el["kids"]))):]
        elif op == "remove-one" and el["kids"]:
            i = rng.randrange(len(el["kids"]))
            del el["kids"][i]
            # two texts that became neighbours would merge in the markup: drop the second one
            for j in range(len(el["kids"]) - 1, 0, -1):
                if "text" in el["kids"][j] and "text" in el["kids"][j - 1]:
                    del el["kids"][j]
        elif op == "insert-front" and len(el["kids"]) < 6:
            if not (el["kids"] and "text" in el["kids"][0]):
                el["kids"].insert(0, gen_el(rng, 1, 2))
    return tree


def to_markup(tree):
    if "text" in tree:
        return tree["text"]
    a = "".join(f' {k}="{v}"' for k, v in tree["attrs"].items())
    return f"<{tree['el']}{a}>" + "".join(to_markup(k) for k in tree["kids"]) + f"</{tree['el']}>"


def size(tree):
    return 1 + sum(size(k) for k in tree.get("kids", []))


def random_first(rng):
    """A random tree of 10 to 80 nodes."""
    while True:
        tree = gen_el(rng, rng.randint(2, 4), rng.randint(2, 4))
        if 10 <= size(tree) <= 80:
            return tree


def random_cases(seed):
    cases = []
    for i in range(1, 9):
        rng = reactgen.rng_for(seed, f"p06-{i}")
        first = random_first(rng)
        if i <= 4:      # related trees: B is an edit of A; the first two replace a child that has later
            #             siblings, the next two remove the last two children of an element
            forced = ["tag-nonlast", "tag-nonlast", "remove-two", "remove-two"][i - 1]
            while True:
                try:
                    trees = [first, mutate(rng, first, forced)]
                    break
                except ValueError:
                    first = random_first(rng)
            kind = "an edit of the first tree"
        elif i <= 6:    # three renders, each an edit of the one before
            second = mutate(rng, first)
            trees = [first, second, mutate(rng, second)]
            kind = "two edits in a row"
        else:           # unrelated trees from the shared generator
            trees = [first, reactgen.rand_markup(rng, depth=3, width=3, tags=SAFE_TAGS)]
            kind = "two unrelated random trees"
        markups = [t if isinstance(t, str) else to_markup(t) for t in trees]
        assert all(reactgen.count_nodes(reactgen.parse_markup(m)) < 190 for m in markups)
        cases.append(session(f"06-R8-random-s{seed}-{i}", "R8", f"random trees ({kind}), {len(markups)} renders",
                             markups))
    return cases


# ---- expected output -----------------------------------------------------------------------------

def main():
    args = wbcore.parse_args("06")
    all_cases = handwritten() + random_cases(args.seed)
    scenarios = [c.lines() for c in all_cases]
    oracle = reactgen.run_oracle_batch(scenarios)

    cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, EXPLAIN, source=SOURCE)
    for case, lines, expected in zip(all_cases, scenarios, oracle):
        modelled = run_model(case.trees, case.steps)
        if modelled != expected:
            for n, (m, e) in enumerate(zip(modelled + [None] * 3, expected + [None] * 3), 1):
                if m != e:
                    raise SystemExit(f"{case.case_id}: model and React differ at output line {n}:\n"
                                     f"  model: {m}\n  React: {e}\n" + "\n".join(lines))
        cases.add(case.case_id, case.req, case.title, lines, expected)
    cases.save()


if __name__ == "__main__":
    main()
