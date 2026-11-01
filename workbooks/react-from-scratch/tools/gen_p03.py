"""Test cases for assignment 03 (render a tree).

Every expected line comes from real React 19 running on jsdom (tools/oracle): the same markup is
rendered with React.createElement into a jsdom container and dumped the way the harness dumps the
learner's minidom tree. The scenarios avoid what React and a library built from the posts do
differently (see _source/react-observed.md): one render per scenario, always followed by `flush`,
no `onChange`, no clicks on disabled controls, an input `value` only together with `readOnly`.

    py -P tools/gen_p03.py                                  # tests/03 (seed 1)
    py -P tools/gen_p03.py --seed 777 --out build/fresh/03  # what `.\\check 03 -Fresh` runs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reactgen  # noqa: E402
import wbcore  # noqa: E402

SOURCE = "React 19.3.1 + react-dom 19.3.1 on jsdom 30.1.3 (tools/oracle)"

REQUIREMENTS = [
    ("R1", "An element with no children becomes one node of its tag as the container's only child; nothing is in the container before `render`"),
    ("R2", "Children become nodes inside their parent's node, at every depth"),
    ("R3", "Siblings keep their order and none is dropped"),
    ("R4", "String children become text nodes, in order among the elements, with their spaces kept"),
    ("R5", "Props are set on the nodes (id, className, title, input value, disabled)"),
    ("R6", "Handlers are attached: a click runs the handler of the element and then those of its ancestors"),
    ("E2E", "Whole pages and random trees"),
]

COMPARE = "records dump=n node=depth,label,tag,props text=depth,value title=value log=text"
EXPLAIN = ""

# Tags that React accepts nested in any order without a validateDOMNesting warning.
SAFE_TAGS = ["div", "span", "section", "em", "b", "i", "main", "article"]

HAND = []  # (id, requirement, title, markup, extra commands, dump before render, dump after render)


def hand(case_id, req, title, markup, *extra, before=False, nodump=False):
    HAND.append((case_id, req, title, markup, list(extra), before, not nodump))


def scenario(markup, extra=(), dump_before=False, dump=True):
    lines = [f"tree t {markup}"]
    if dump_before:
        lines.append("dump")
    lines += ["render t", "flush"]
    if dump:
        lines.append("dump")
    lines += list(extra)
    return lines


# Each group isolates its own requirement, so a failure points at the right one: R2 and R3 use
# structure only (no text, no props, symmetric where order would not matter), R5 keeps props on a
# single root or a chain, and R6 clicks without dumping the tree.

# R1: one element
hand("03-R1-div", "R1", "one empty div", "<div></div>")
hand("03-R1-heading", "R1", "one empty h1", "<h1></h1>")
hand("03-R1-void", "R1", "a void element, an input with no props", "<input>")
hand("03-R1-br", "R1", "a br", "<br>")
hand("03-R1-before-render", "R1", "the container is empty until render, then holds one node", "<section></section>", before=True)

# R2: nesting
hand("03-R2-two-levels", "R2", "a p inside a div", "<div><p></p></div>")
hand("03-R2-six-levels", "R2", "a chain of six elements",
     "<div><section><div><span><em><b></b></em></span></div></section></div>")
hand("03-R2-ten-levels", "R2", "a chain of ten elements",
     "<main><article><section><div><span><em><b><i><u><s></s></u></i></b></em></span></div></section></article></main>")
hand("03-R2-two-equal-branches", "R2", "two identical branches of three levels",
     "<div><section><span><i></i><i></i></span></section><section><span><i></i><i></i></span></section></div>")
hand("03-R2-lists-in-lists", "R2", "ul in li in ul",
     "<ul><li><ul><li></li></ul></li></ul>")

# R3: siblings
hand("03-R3-three-tags", "R3", "h1, h2, h3 in a div", "<div><h1></h1><h2></h2><h3></h3></div>")
hand("03-R3-seven-tags", "R3", "seven different tags in order",
     "<div><h1></h1><p></p><span></span><em></em><b></b><i></i><section></section></div>")
hand("03-R3-twelve-tags", "R3", "twelve different tags in order",
     "<div><h1></h1><h2></h2><h3></h3><p></p><span></span><em></em><b></b><i></i><u></u><s></s><code></code><small></small></div>")
hand("03-R3-last-is-deep", "R3", "the last child has children of its own",
     "<div><h1></h1><h2></h2><section><h3></h3><h4></h4></section></div>")
hand("03-R3-first-is-deep", "R3", "the first child has children of its own",
     "<div><section><h3></h3><h4></h4></section><h1></h1><h2></h2></div>")

# R4: text
hand("03-R4-one-text", "R4", "a p with one text", "<p>hello</p>")
hand("03-R4-text-element-text", "R4", "text, an element, text", "<p>hello <b>big</b> world</p>")
hand("03-R4-spaces", "R4", "inner spaces and leading and trailing spaces are kept",
     "<div><p>a  b   c</p><p> padded </p></div>")
hand("03-R4-quotes-percent", "R4", "double quotes and a percent sign in text", '<p>say "hi" to 100% of them</p>')
hand("03-R4-interleaved", "R4", "texts and elements alternating",
     "<div>one<span>two</span>three<span>four</span>five</div>")
hand("03-R4-numbers", "R4", "text that looks like numbers", "<ul><li>1</li><li>22</li><li>0</li></ul>")
hand("03-R4-list", "R4", "three li with text in a ul", "<ul><li>a</li><li>b</li><li>c</li></ul>")

# R5: props
hand("03-R5-id-class-title", "R5", "id, className and a title with spaces",
     '<div id="a" className="box" title="hello there"></div>')
hand("03-R5-nested-props", "R5", "props on three nested elements",
     '<div id="a" className="x"><section id="b" title="t"><p id="c" className="y z"></p></section></div>')
hand("03-R5-input-value", "R5", "an input with a value (read only, so React does not warn)",
     '<input id="q" value="typed text" readOnly>')
hand("03-R5-input-disabled", "R5", "a disabled read-only input",
     '<input id="r" value="x" readOnly disabled>')
hand("03-R5-disabled-button", "R5", "a disabled button", '<button id="go" disabled></button>')
hand("03-R5-unseen-props", "R5", "props the dump does not show",
     '<div lang="en" data-role="main" hidden><span tabIndex="2"></span></div>')
hand("03-R5-class-spaces", "R5", "a class list with spaces and a title with a percent sign",
     '<p className="a b c" title="5% off"></p>')
hand("03-R5-key", "R5", "key on a list item does not show up as a property",
     '<ul><li key="a" id="la"></li></ul>')

# R6: handlers (no dump: only what the clicks do)
hand("03-R6-click", "R6", "one button with a handler, clicked once",
     '<button id="b" onClick=@hit></button>', "click #b", "log", nodump=True)
hand("03-R6-click-twice", "R6", "clicked twice",
     '<button id="b" onClick=@tap></button>', "click #b", "click #b", "log", nodump=True)
hand("03-R6-bubbling", "R6", "inner click reaches the outer handler, outer click does not reach the inner one",
     '<div id="outer" onClick=@outer><button id="inner" onClick=@inner></button></div>',
     "click #inner", "log", "click #outer", "log", nodump=True)
hand("03-R6-two-buttons", "R6", "two buttons with their own handlers",
     '<div><button id="a" onClick=@first></button><button id="b" onClick=@second></button></div>',
     "click #b", "log", "click #a", "log", nodump=True)
hand("03-R6-same-handler", "R6", "one handler on two elements, only the clicked one fires it",
     '<div><button id="a" onClick=@one></button><button id="b" onClick=@one></button></div>',
     "click #a", "log", nodump=True)
hand("03-R6-child-without-handler", "R6", "a click on a child that has no handler bubbles to the parent",
     '<div id="p" onClick=@parent><span id="c"><b id="d"></b></span></div>',
     "click #c", "log", "click #d", "log", nodump=True)
hand("03-R6-handler-and-props", "R6", "a handler next to other props, the node dumped after the click",
     '<button id="go" className="primary" title="run it" onClick=@go></button>', "click #go", "log")

# E2E
hand("03-E2E-page", "E2E", "a small page with text, a list, props and two handlers",
     '<div id="app" className="page"><h1 id="title">Notes</h1><ul id="list" className="items">'
     '<li id="n1">first note</li><li id="n2" className="done">second note</li><li id="n3">third  note</li></ul>'
     '<p>Total: <b>3</b> notes, <i>all</i> shown.</p><button id="add" onClick=@add>Add</button>'
     '<button id="del" disabled onClick=@del>Delete</button></div>',
     "click #add", "log")
hand("03-E2E-nested-handlers", "E2E", "handlers on three levels, clicked from the inside out",
     '<section id="s" onClick=@section><div id="d" onClick=@div><p id="p" onClick=@para>one <em id="e">two</em></p>'
     '<p id="q">three</p></div></section>',
     "click #e", "log", "click #q", "log", "click #d", "log")


def random_markup(seed, label, depth, width):
    rng = reactgen.rng_for(seed, label)
    return reactgen.rand_markup(rng, depth=depth, width=width, tags=SAFE_TAGS)


def rand_structure(rng, depth, width):
    """A random element tree of tags only: no text, no props."""
    tag = rng.choice(SAFE_TAGS)
    kids = ""
    if depth > 0:
        kids = "".join(rand_structure(rng, depth - 1, width) for _ in range(rng.randint(0, width)))
    return f"<{tag}>{kids}</{tag}>"


def wrapped(seed, label):
    """Two random subtrees and a button, under two nested handlers."""
    a = random_markup(seed, label + "a", 3, 3)
    b = random_markup(seed, label + "b", 2, 3)
    return ('<div id="top" onClick=@top><div id="mid" onClick=@mid>' + a + b +
            '<button id="hit" onClick=@hit>x</button></div></div>')


def main():
    args = wbcore.parse_args("03")
    cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, EXPLAIN, source=SOURCE)

    planned = []
    for case_id, req, title, markup, extra, before, dump in HAND:
        planned.append((case_id, req, title, scenario(markup, extra, before, dump)))
    for k in range(1, 3):
        markup = rand_structure(reactgen.rng_for(args.seed, f"structure{k}"), 4, 3)
        planned.append((f"03-R3-random-s{args.seed}-{k}", "R3", f"random tree {k} of tags only, no text and no props, seed {args.seed}",
                        scenario(markup)))
    for k in range(1, 4):
        markup = random_markup(args.seed, f"tree{k}", 3, 3 + k % 2)
        planned.append((f"03-E2E-random-s{args.seed}-{k}", "E2E", f"random tree {k} of nested elements, texts and props, seed {args.seed}",
                        scenario(markup)))
    for k in range(1, 3):
        planned.append((f"03-R6-random-s{args.seed}-{k}", "R6", f"random tree under handlers, clicks from three depths, seed {args.seed}",
                        scenario(wrapped(args.seed, f"wrap{k}"),
                                 ["click #hit", "log", "click #mid", "log", "click #top", "log"], dump=False)))
    expected = reactgen.run_oracle_batch([lines for _, _, _, lines in planned])
    for (case_id, req, title, lines), out in zip(planned, expected):
        cases.add(case_id, req, title, lines, expected=out)
    cases.save()


if __name__ == "__main__":
    main()
