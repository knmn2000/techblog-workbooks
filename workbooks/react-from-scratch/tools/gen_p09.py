"""Test cases for assignment 09 (function components).

    py -P tools/gen_p09.py                                  # tests/09 (seed 1)
    py -P tools/gen_p09.py --seed 777 --out build/fresh/09  # what `.\\check 09 -Fresh` runs

Dump and log lines come from real React 19 on jsdom (tools/oracle). The `idle` lines of the units cases
come from a formula: one unit for the container's root fiber, one for every element and text node, one
for every function component (the fiber of a component has no node but is a unit of its own). The
component sizes below are read off the catalog in harness/catalog.js.

The catalog components that need `useState` or `useEffect` (Counter, Toggle, Logger, ...) cannot run before
assignments 10 and 11, so these cases use Greeting, Frame, FnA and FnB, plus plain elements whose handlers
(`onClick=@name`) write to the log. Components never return null (out of scope).
"""

import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wbcore  # noqa: E402
from reactgen import WORDS, merge_expected, parse_markup, rng_for, run_oracle_batch  # noqa: E402
from gen_p07 import JSDOM, ORACLE_PACKAGE  # noqa: E402

REACT = ORACLE_PACKAGE["dependencies"]["react"]
SOURCE = f"React {REACT} on jsdom {JSDOM} (tools/oracle)"
SOURCE_UNITS = f"React {REACT} on jsdom {JSDOM} (tools/oracle); idle lines from the fiber count: root, elements, text nodes and components"
COMPARE = "records node=depth,label,tag,props text=depth,value title=value idle=units log=text dump=n"
EXPLAIN = "idle=R9"

REQUIREMENTS = [
    ("R1", "A function component's output is rendered, and the component receives its element's props"),
    ("R2", "Components nest, stand side by side and can be the root of the tree"),
    ("R3", "`props.children` carries the elements, text and components written inside a component"),
    ("R4", "A component of the same type at the same position keeps its nodes and takes new props, text and handlers"),
    ("R5", "Another component, or a plain element, at a position replaces the component's nodes in place"),
    ("R6", "A component that disappears takes its nodes out of the page, and only those"),
    ("R7", "A component mounted in one render can be removed or replaced by the very next render, with or without a render in between"),
    ("R8", "Keys work on components as they do on elements: inserted, removed and reordered components keep their nodes and typed values"),
    ("R9", "A component is a unit of work of its own: it adds one to the unit count and has no node"),
    ("E2E", "Whole sessions with components"),
]


# ---- Units ------------------------------------------------------------------------------------------

def units_of(node):
    """Units of work of one parsed markup node (see reactgen.parse_markup)."""
    if node[0] == "text":
        return 1
    tag, kids = node[1], node[3]
    if tag == "Greeting":
        return 1 + 1 + 2  # the component, its h1, the two texts "Hi " and the name
    if tag in ("FnA", "FnB"):
        return 1 + 1 + 1  # the component, its i or b, its text
    if tag == "Frame":
        return 1 + 1 + 2 + sum(units_of(k) for k in kids)  # the component, section, h2, the title's text, the children
    return 1 + sum(units_of(k) for k in kids)


def units_of_tree(markup):
    (root,) = parse_markup(markup)
    return 1 + units_of(root)  # the container's root fiber, then the tree


# ---- A scenario ------------------------------------------------------------------------------------

class Script:
    def __init__(self):
        self.lines = []
        self.trees = 0
        self.units = {}
        self.final = None

    def render(self, markup, flush=True):
        self.trees += 1
        name = f"t{self.trees}"
        self.units[name] = units_of_tree(markup)
        self.lines += [f"tree {name} {markup}", f"render {name}"]
        if flush:
            self.lines.append("flush")
        return self

    def dump(self):
        self.lines.append("dump")
        return self

    def step(self, markup):
        return self.render(markup).dump()

    def settled(self, markup):
        """Renders the same tree twice, so that what a later render removes or replaces was not mounted
        by the render just before it (that case is assignment 09's R7 and has cases of its own)."""
        return self.render(markup).render(markup).dump()

    def click(self, node_id):
        self.lines.append(f"click #{node_id}")
        return self

    def log(self):
        self.lines.append("log")
        return self

    def idle(self, budget):
        self.lines.append(f"idle {budget}")
        return self

    def text(self):
        return "\n".join(self.lines) + "\n"


def dump_blocks(lines):
    blocks = []
    for line in lines:
        if line.startswith("dump "):
            blocks.append([])
        elif blocks and line.split(" ", 1)[0] in ("node", "text"):
            blocks[-1].append(line)
    return blocks


def shape(block):
    """The (depth, tag) of every element in a dump."""
    out = []
    for line in block:
        words = line.split(" ", 4)
        if words[0] == "node":
            out.append((int(words[1]), words[3]))
    return out


def label_at(block, index):
    elements = [line.split(" ", 4) for line in block if line.startswith("node ")]
    return elements[index][2]


class Book:
    def __init__(self):
        self.entries = []

    def add(self, case_id, req, title, script, final=None, same=(), different=(), units=False):
        """final: the (depth, tag) list the last dump must have; same / different: (dump, element, dump,
        element) tuples of nodes that must have equal / different labels. These only check that a
        hand-made scenario does what its author meant: the expected lines come from React either way."""
        assert title.isascii(), case_id
        self.entries.append((case_id, req, title, script, final, same, different, units))

    def save(self, args):
        results = run_oracle_batch([entry[3].text() for entry in self.entries])
        cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, EXPLAIN, source=SOURCE)
        for (case_id, req, title, script, final, same, different, units), lines in zip(self.entries, results):
            blocks = dump_blocks(lines)
            if final is not None:
                assert shape(blocks[-1]) == final, f"{case_id}: React shows {shape(blocks[-1])}, expected {final}"
            for a, i, b, j in same:
                assert label_at(blocks[a], i) == label_at(blocks[b], j), f"{case_id}: node {i} of dump {a + 1} should be kept"
            for a, i, b, j in different:
                assert label_at(blocks[a], i) != label_at(blocks[b], j), f"{case_id}: node {i} of dump {a + 1} should be new"
            if units:
                lines = merge_expected(script.lines, lines, script.units)
                source = SOURCE_UNITS
            else:
                source = None
            cases.add(case_id, req, title, script.lines, expected=lines, source=source)
        cases.save()


# ---- Hand-made cases ---------------------------------------------------------------------------------

def hand_made(book):
    # R1 ---------------------------------------------------------------------------------------------
    book.add("09-R1-greeting-at-root", "R1", "a Greeting is the whole tree",
             Script().step("<Greeting name=Ann/>"), final=[(0, "h1")])
    book.add("09-R1-greeting-in-div", "R1", "a Greeting with a two-word name inside a div",
             Script().step('<div><Greeting name="Mary Jo"/></div>'), final=[(0, "div"), (1, "h1")])
    book.add("09-R1-fn-components", "R1", "FnA and FnB inside a div: an i and a b",
             Script().step("<div><FnA/><FnB/></div>"), final=[(0, "div"), (1, "i"), (1, "b")])
    book.add("09-R1-frame-title", "R1", "a Frame with a title and nothing inside",
             Script().step("<Frame title=Menu></Frame>"), final=[(0, "section"), (1, "h2")])

    # R2 ---------------------------------------------------------------------------------------------
    book.add("09-R2-nested-frames", "R2", "a Frame inside a Frame inside a div",
             Script().step("<div><Frame title=Outer><Frame title=Inner><p>deep</p></Frame></Frame></div>"),
             final=[(0, "div"), (1, "section"), (2, "h2"), (2, "section"), (3, "h2"), (3, "p")])
    book.add("09-R2-side-by-side", "R2", "four components next to each other in a div",
             Script().step("<div><Greeting name=A/><FnA/><Greeting name=B/><FnB/></div>"),
             final=[(0, "div"), (1, "h1"), (1, "i"), (1, "h1"), (1, "b")])

    # R3 ---------------------------------------------------------------------------------------------
    book.add("09-R3-frame-children", "R3", "a Frame around two paragraphs",
             Script().step("<Frame title=Menu><p>one</p><p>two</p></Frame>"),
             final=[(0, "section"), (1, "h2"), (1, "p"), (1, "p")])
    book.add("09-R3-frame-text-child", "R3", "a Frame whose only child is text",
             Script().step("<Frame title=Note>just text</Frame>"), final=[(0, "section"), (1, "h2")])
    book.add("09-R3-frame-mixed-children", "R3", "a Frame around a component, an element and text",
             Script().step("<Frame title=Mix><Greeting name=A/><FnB/><em>e</em>tail</Frame>"),
             final=[(0, "section"), (1, "h2"), (1, "h1"), (1, "b"), (1, "em")])
    book.add("09-R3-children-appear-and-go", "R3", "a Frame gets children, loses one, then loses all",
             Script().step("<Frame title=T></Frame>").step("<Frame title=T><p>x</p><p>y</p></Frame>").step("<Frame title=T><p>x</p></Frame>")
                     .step("<Frame title=T></Frame>"),
             final=[(0, "section"), (1, "h2")], same=[(0, 0, 3, 0)])

    # R4 ---------------------------------------------------------------------------------------------
    book.add("09-R4-greeting-name-changes", "R4", "a Greeting is given another name, twice",
             Script().step("<div><Greeting name=Ann/></div>").step("<div><Greeting name=Bo/></div>").step("<div><Greeting name=Bo/></div>"),
             same=[(0, 1, 1, 1), (1, 1, 2, 1)])
    book.add("09-R4-frame-title-and-children", "R4", "a Frame changes its title, one child's text, and gains a child",
             Script().step("<Frame title=First><p>one</p></Frame>").step("<Frame title=Second><p>ONE</p><p>two</p></Frame>"),
             same=[(0, 0, 1, 0), (0, 2, 1, 2)])
    book.add("09-R4-handler-in-component", "R4", "a button inside a Frame: click, swap the handler, click again",
             Script().step("<Frame title=Go><button id=go onClick=@first>go</button></Frame>").click("go").log()
                     .step("<Frame title=Go><button id=go onClick=@second>go</button></Frame>").click("go").log().click("go").log(),
             same=[(0, 2, 1, 2)])
    book.add("09-R4-around-a-component", "R4", "the div and the paragraph around a Greeting change props, the Greeting keeps its h1",
             Script().step('<div className=x><Greeting name=A/><p title=t>1</p></div>')
                     .step('<div className=y><Greeting name=B/><p>2</p></div>'),
             same=[(0, 0, 1, 0), (0, 1, 1, 1), (0, 2, 1, 2)])

    # R5 ---------------------------------------------------------------------------------------------
    book.add("09-R5-fn-swap-in-div", "R5", "FnA is replaced by FnB inside a div",
             Script().settled("<div><FnA/></div>").step("<div><FnB/></div>"), final=[(0, "div"), (1, "b")],
             same=[(0, 0, 1, 0)], different=[(0, 1, 1, 1)])
    book.add("09-R5-fn-swap-at-root", "R5", "FnA is replaced by FnB as the whole tree",
             Script().settled("<FnA/>").step("<FnB/>"), final=[(0, "b")], different=[(0, 0, 1, 0)])
    book.add("09-R5-fn-to-element-and-back", "R5", "FnA, then a plain i, then FnA again",
             Script().settled("<div><FnA/></div>").settled("<div><i>a</i></div>").step("<div><FnA/></div>"), final=[(0, "div"), (1, "i")],
             same=[(0, 0, 2, 0)], different=[(0, 1, 1, 1), (1, 1, 2, 1)])
    book.add("09-R5-swap-between-siblings", "R5", "FnA in the middle of two paragraphs becomes FnB",
             Script().settled("<div><p>1</p><FnA/><p>2</p></div>").step("<div><p>1</p><FnB/><p>2</p></div>"),
             final=[(0, "div"), (1, "p"), (1, "b"), (1, "p")], same=[(0, 1, 1, 1), (0, 3, 1, 3)], different=[(0, 2, 1, 2)])
    book.add("09-R5-swap-before-a-component", "R5", "FnA in front of a Greeting becomes FnB: the new node must stay in front",
             Script().settled("<div><FnA/><Greeting name=g/></div>").step("<div><FnB/><Greeting name=g/></div>"),
             final=[(0, "div"), (1, "b"), (1, "h1")], same=[(0, 2, 1, 2)], different=[(0, 1, 1, 1)])
    book.add("09-R5-greeting-and-frame", "R5", "a Greeting and a Frame swap types at the same position, and back",
             Script().settled("<div><Greeting name=A/></div>").settled("<div><Frame title=A><p>x</p></Frame></div>").step("<div><Greeting name=A/></div>"),
             final=[(0, "div"), (1, "h1")])

    # R6 ---------------------------------------------------------------------------------------------
    book.add("09-R6-remove-between-siblings", "R6", "a component between two paragraphs is removed, after a render in between",
             Script().step("<div><p>a</p><FnA/><p>b</p></div>").step("<div><p>a</p><FnA/><p>b</p></div>").step("<div><p>a</p><p>b</p></div>"),
             final=[(0, "div"), (1, "p"), (1, "p")], same=[(0, 1, 2, 1)])
    book.add("09-R6-remove-frame-with-content", "R6", "a Frame with nested content is removed, the paragraph after it stays",
             Script().step("<div><Frame title=T><p>x</p><Greeting name=g/></Frame><p>after</p></div>")
                     .step("<div><Frame title=T><p>x</p><Greeting name=g/></Frame><p>after</p></div>").step("<div><p>after</p></div>")
                     .step("<div></div>"),
             final=[(0, "div")])
    book.add("09-R6-remove-all-components", "R6", "a div of two components is emptied",
             Script().step("<div><FnA/><FnB/></div>").step("<div><FnA/><FnB/></div>").step("<div></div>"), final=[(0, "div")])
    book.add("09-R6-root-component-to-element", "R6", "a Greeting as the whole tree is replaced by a paragraph",
             Script().step("<Greeting name=x/>").step("<Greeting name=x/>").step("<p>y</p>"), final=[(0, "p")])
    book.add("09-R6-deep", "R6", "a component three levels down is removed",
             Script().step("<div><section><Frame title=T><FnA/></Frame></section></div>")
                     .step("<div><section><Frame title=T><FnA/></Frame></section></div>").step("<div><section></section></div>"),
             final=[(0, "div"), (1, "section")])

    # R7 ---------------------------------------------------------------------------------------------
    book.add("09-R7-mount-then-remove", "R7", "FnA is mounted and removed by the very next render",
             Script().step("<div><p>a</p><FnA/></div>").step("<div><p>a</p></div>"), final=[(0, "div"), (1, "p")])
    book.add("09-R7-mount-then-swap", "R7", "FnA is mounted and replaced by FnB by the very next render",
             Script().step("<div><p>a</p><FnA/></div>").step("<div><p>a</p><FnB/></div>"), final=[(0, "div"), (1, "p"), (1, "b")])
    book.add("09-R7-mount-render-then-remove", "R7", "FnA is mounted, rendered once more, then removed",
             Script().step("<div><p>a</p><FnA/></div>").step("<div><p>a</p><FnA/></div>").step("<div><p>a</p></div>"), final=[(0, "div"), (1, "p")])
    book.add("09-R7-frame-mount-then-remove", "R7", "a Frame with content is mounted and removed by the next render",
             Script().step("<div><p>a</p><Frame title=T><p>x</p><Greeting name=g/></Frame></div>").step("<div><p>a</p></div>"),
             final=[(0, "div"), (1, "p")])
    book.add("09-R7-nested-removed", "R7", "components inside components are mounted and then all removed",
             Script().step("<div><Frame title=A><Frame title=B><FnA/></Frame></Frame></div>").step("<div></div>"), final=[(0, "div")])
    book.add("09-R7-root-swap", "R7", "the whole tree is FnA, then FnB, then a paragraph",
             Script().step("<FnA/>").step("<FnB/>").step("<p>end</p>"), final=[(0, "p")])

    # R8 ---------------------------------------------------------------------------------------------
    book.add("09-R8-insert-in-front", "R8", "a keyed Greeting is added in front of two others",
             Script().step('<div><Greeting key=a name=A/><Greeting key=b name=B/></div>').step('<div><Greeting key=z name=Z/><Greeting key=a name=A/><Greeting key=b name=B/></div>'),
             same=[(0, 1, 1, 2), (0, 2, 1, 3)], different=[(0, 1, 1, 1)])
    book.add("09-R8-frames-with-inputs-reverse", "R8", "keyed Frames with an input each are reversed; the typed text moves with them",
             Script().step("<div><Frame key=a title=A><input id=ia/></Frame><Frame key=b title=B><input id=ib/></Frame><Frame key=c title=C><input id=ic/></Frame></div>")
                     .lines_add("type #ia first").lines_add("type #ib second").lines_add("type #ic third").dump()
                     .step("<div><Frame key=c title=C><input id=ic/></Frame><Frame key=b title=B><input id=ib/></Frame><Frame key=a title=A><input id=ia/></Frame></div>"),
             final=[(0, "div"), (1, "section"), (2, "h2"), (2, "input"), (1, "section"), (2, "h2"), (2, "input"), (1, "section"), (2, "h2"), (2, "input")])
    book.add("09-R8-remove-middle", "R8", "the middle one of three keyed components is removed",
             Script().settled('<div><Greeting key=a name=A/><FnA key=b/><Greeting key=c name=C/></div>').step('<div><Greeting key=a name=A/><Greeting key=c name=C/></div>'),
             same=[(0, 1, 1, 1), (0, 3, 1, 2)])
    book.add("09-R8-mixed-edit", "R8", "keyed components: one new, one gone, two swapped",
             Script().settled('<div><Greeting key=a name=A/><Greeting key=b name=B/><Greeting key=c name=C/><Greeting key=d name=D/></div>')
                     .step('<div><Greeting key=d name=D/><Greeting key=x name=X/><Greeting key=a name=A/><Greeting key=c name=C/></div>'),
             same=[(0, 4, 1, 1), (0, 1, 1, 3), (0, 3, 1, 4)], different=[(0, 2, 1, 2)])

    # R9 ---------------------------------------------------------------------------------------------
    def units_case(case_id, title, markup, budget):
        script = Script()
        total = units_of_tree(markup)
        periods_needed = math.ceil(total / budget)
        script.render(markup, flush=False).dump()
        for index in range(periods_needed):
            script.idle(budget)
            if index == periods_needed - 2:
                script.dump()  # one period is still to come: the page is still empty
        script.dump()
        script.idle(budget)
        book.add(case_id, "R9", f"{title} ({total} units, {budget} per idle period)", script, units=True)

    units_case("09-R9-units-greeting", "one Greeting as the whole tree", "<Greeting name=Ann/>", 2)
    units_case("09-R9-units-frame", "a Frame with a paragraph and a component inside a div", "<div><Frame title=T><p>one</p><FnA/></Frame></div>", 3)
    units_case("09-R9-units-side-by-side", "four components side by side", "<div><Greeting name=A/><FnA/><Greeting name=B/><FnB/></div>", 4)

    # E2E ----------------------------------------------------------------------------------------------
    page = Script()
    page.step("<div><Greeting name=Ann/><Frame title=News><p>none</p></Frame><button id=more onClick=@more>more</button></div>")
    page.click("more").log()
    page.step("<div><Greeting name=Ann/><Frame title=News><p>one</p><p>two</p></Frame><button id=more onClick=@more>more</button></div>")
    page.step("<div><Greeting name=Bo/><Frame title=News><p>one</p></Frame><FnA/><button id=more onClick=@again>more</button></div>")
    page.click("more").log()
    page.step("<div><Greeting name=Bo/><FnB/><button id=more onClick=@again>more</button></div>")
    page.step("<div><Greeting name=Bo/><button id=more onClick=@again>more</button></div>")
    page.click("more").log()
    book.add("09-E2E-page", "E2E", "a page of components: names change, a Frame grows and shrinks, FnA comes and goes, a handler is swapped", page)

    shell = Script()
    shell.step("<Frame title=App><Frame title=Header><Greeting name=Ann/></Frame><Frame title=Body><p>loading</p></Frame></Frame>")
    shell.step("<Frame title=App><Frame title=Header><Greeting name=Ann/></Frame><Frame title=Body><FnA/><FnB/></Frame></Frame>")
    shell.step("<Frame title=App><Frame title=Body><FnA/><FnB/></Frame></Frame>")
    shell.step("<Frame title=App2><Frame title=Header><FnB/></Frame><Frame title=Body><FnA/></Frame></Frame>")
    book.add("09-E2E-app-shell", "E2E", "Frames nested three deep, with sections that come and go", shell)


def lines_add(self, line):
    self.lines.append(line)
    return self


Script.lines_add = lines_add


# ---- Random cases ------------------------------------------------------------------------------------

CONTAINERS = ["div", "span", "section", "b", "em"]


def random_tree(rng, depth):
    """Markup of a random tree of plain elements and components. Adjacent texts never occur (they would
    merge into one text node in the markup), no element mixes keyed and unkeyed children, names and
    titles are single words."""
    pick = rng.random()
    if depth <= 0 or pick < 0.2:
        kind = rng.choice(["Greeting", "FnA", "FnB", "p"])
        return leaf(rng, kind)
    if pick < 0.55:
        return container(rng, depth, rng.choice(CONTAINERS))
    if pick < 0.8:
        title = rng.choice(WORDS)
        return f"<Frame title={title}>{children(rng, depth - 1)}</Frame>"
    return leaf(rng, rng.choice(["Greeting", "FnA", "FnB"]))


def leaf(rng, kind):
    if kind == "Greeting":
        return f"<Greeting name={rng.choice(WORDS)}/>"
    if kind in ("FnA", "FnB"):
        return f"<{kind}/>"
    return f"<p>{rng.choice(WORDS)}</p>"


def container(rng, depth, tag):
    return f"<{tag}>{children(rng, depth - 1)}</{tag}>"


def children(rng, depth):
    parts = []
    for _ in range(rng.randint(0, 3)):
        if rng.random() < 0.2 and not (parts and not parts[-1].startswith("<")):
            parts.append(rng.choice(WORDS))
        else:
            parts.append(random_tree(rng, depth))
    return "".join(parts)


def random_cases(book, seed):
    for req, n, steps in (("R2", 0, 4), ("R2", 1, 5), ("R7", 0, 5), ("R7", 1, 6)):
        rng = rng_for(seed, f"09-{req}-{n}")
        script = Script()
        # R7 trees are small so that components are often mounted and gone again in the next render
        depth = 3 if req == "R2" else 2
        tree = f"<div>{children(rng, depth)}</div>"
        show = script.settled if req == "R2" else script.step  # R2 trees are rendered twice, see Script.settled
        show(tree)
        for _ in range(steps):
            tree = mutate_root(rng, depth, tree)
            show(tree)
        what = "random trees of elements and components, changing" if req == "R2" else "random small trees where components come and go quickly"
        book.add(f"09-{req}-random-s{seed}-{n}", req, f"{what} (seed {seed}, {steps + 1} renders)", script)

    rng = rng_for(seed, "09-R8-random")
    keys = list("abcdef")
    script = Script()
    order = rng.sample(keys, 4)
    for step in range(5):
        items = []
        for k in order:
            kind = rng.choice(["Greeting", "FnA", "FnB"]) if step == 0 else kinds.get(k, "Greeting")
            items.append(kind_markup(kind, k, rng))
        if step == 0:
            kinds = {k: re.match(r"<(\w+)", item).group(1) for k, item in zip(order, items)}
        script.settled(f"<div>{''.join(items)}</div>")
        kept = [k for k in order if rng.random() < 0.8]
        rng.shuffle(kept)
        unused = [k for k in keys if k not in order]
        for k in rng.sample(unused, min(len(unused), rng.choice([0, 1, 1]))):
            kept.insert(rng.randint(0, len(kept)), k)
            kinds[k] = rng.choice(["Greeting", "FnA", "FnB"])
        order = kept or rng.sample(keys, 2)
        for k in order:
            kinds.setdefault(k, "Greeting")
    book.add(f"09-R8-random-s{seed}-0", "R8", f"random shuffles of keyed components (seed {seed}, 5 renders)", script)


def kind_markup(kind, key, rng):
    if kind == "Greeting":
        return f"<Greeting key={key} name={rng.choice(WORDS)}/>"
    return f"<{kind} key={key}/>"


def mutate_root(rng, depth, markup):
    """A new tree that resembles `markup`: some of its top-level children kept, dropped, replaced or added."""
    (root,) = parse_markup(markup)
    kids = [to_markup(k) for k in root[3]]
    out = []
    for kid in kids:
        roll = rng.random()
        if roll < 0.15:
            continue
        if roll < 0.35:
            out.append(random_tree(rng, depth - 1))
        elif roll < 0.55:
            out.append(tweak(rng, kid))
        else:
            out.append(kid)
        if rng.random() < 0.15:
            out.append(random_tree(rng, depth - 1))
    if rng.random() < 0.3:
        out.insert(rng.randint(0, len(out)), random_tree(rng, depth - 1))
    return "<div>" + separate(out) + "</div>"


def tweak(rng, markup):
    """Another word in the first name, title or text of a subtree."""
    return re.sub(r"(name=|title=|>)(" + "|".join(WORDS) + r")", lambda m: m.group(1) + rng.choice(WORDS), markup, count=1)


def separate(parts):
    """Joins markup pieces; two texts in a row become one piece wrapped in <b>."""
    out = []
    for part in parts:
        if out and not part.startswith("<") and not out[-1].startswith("<"):
            part = f"<b>{part}</b>"
        out.append(part)
    return "".join(out)


def to_markup(node):
    if node[0] == "text":
        return node[1]
    _, tag, attrs, kids = node
    attrs = f" {attrs}" if attrs else ""
    if not kids and tag in ("Greeting", "FnA", "FnB"):
        return f"<{tag}{attrs}/>"
    return f"<{tag}{attrs}>" + "".join(to_markup(k) for k in kids) + f"</{tag}>"


def main():
    args = wbcore.parse_args("09")
    book = Book()
    hand_made(book)
    random_cases(book, args.seed)
    book.save(args)


if __name__ == "__main__":
    main()
