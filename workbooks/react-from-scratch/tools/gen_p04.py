"""Test generator for assignment 04 (work in units: fibers).

    py -P tools/gen_p04.py [--seed N] [--out DIR]

Scenario commands used: tree, render, idle, flush, dump.

Where the expected lines come from:
  dump lines   real React 19.3.1 on jsdom (tools/oracle), run on the same scenario text. A dump taken
               before any unit has run is replaced by an empty dump (render() must leave the page alone).
  idle lines   the unit formula: U = 1 (the container's root fiber) + elements + text nodes, and an idle
               period with budget k reports min(k, units left). reactgen.merge_expected applies it; this
               file also counts the units itself, in another way (a regex over the markup), checks the
               count against the oracle's own final dump, and checks every idle line against a second
               tiny model written here.

The generator never dumps between two idle periods: in assignment 04 the page may fill up progressively
while units run (assignment 05 forbids it), so only the empty page before the first idle period and the
finished page after `flush` are pinned down. Each case is aimed at one requirement and ends where that
requirement has been looked at, so that a bug in another requirement does not fail it as well.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reactgen  # noqa: E402
import wbcore  # noqa: E402

COMPARE = "records idle=units dump=n node=depth,label,tag,props text=depth,value title=value"
# node:props and text:value can only differ when the lines are aligned: they point at the content rule.
# idle and the structure lines serve several requirements, so they are not mapped: the checker then
# names the requirement the failing case is aimed at.
EXPLAIN = "node:props=R6 text:value=R6"
SOURCE = ("React 19.3.1 on jsdom 30.1.3 for the dumps; the unit formula (1 root fiber + elements + text nodes) "
          "for the idle lines")

REQUIREMENTS = [
    ("R1", "render only schedules the work: right after it the container is still empty and no unit has run"),
    ("R2", "one unit of work per fiber: the root fiber, every element and every text node, and nothing else"),
    ("R3", "the loop reads timeRemaining() once after each unit: idle k reports min(k, units left)"),
    ("R4", "the walk reaches every fiber, depth first (child, then sibling, then the parent's sibling and so on up), "
           "so after flush the container holds the whole tree in order"),
    ("R5", "with no work left a period reads nothing and reports 0: before any render and after the tree is done"),
    ("R6", "every node carries the props and the text of its element"),
    ("E2E", "whole scenarios: empty page, uneven periods, finished page"),
]

SAFE_TAGS = ["div", "span", "section", "em", "b", "i", "ul", "nav", "article", "aside"]


# ---- the independent unit counter ---------------------------------------------------------------

OPEN_TAG = re.compile(r"<[A-Za-z][^<>]*>")
ANY_TAG = re.compile(r"</?[A-Za-z][^<>]*>")


def units_by_regex(markup):
    """U counted in a different way than reactgen.count_units: opening tags are elements, every
    non-blank piece of text between tags is a text node, plus the root fiber."""
    elements = len(OPEN_TAG.findall(markup))
    texts = sum(1 for piece in ANY_TAG.split(markup) if piece.strip())
    return 1 + elements + texts


def my_idle_model(units, commands):
    """The idle lines a scenario must print: `render` queues `units` units, `idle k` does up to k of them
    (all of them for inf), `flush` does the rest."""
    left, out = 0, []
    for command in commands:
        word, _, arg = command.partition(" ")
        if word == "render":
            left = units
        elif word == "flush":
            left = 0
        elif word == "idle":
            n = left if arg == "inf" else min(int(arg), left)
            out.append(f"idle {n}")
            left -= n
    return out


# ---- scenario builders --------------------------------------------------------------------------

def periods_for(units, budget):
    """Budgets (as scenario words) for idle periods of one size until done, plus one that finds no work."""
    return [str(budget)] * (len(reactgen.periods(units, budget)))


class Scenario:
    def __init__(self, case_id, req, title, markup, steps):
        self.case_id, self.req, self.title = case_id, req, title
        self.markup = markup
        self.steps = steps

    def lines(self):
        return [f"tree a {self.markup}"] + self.steps


def idles(*budgets):
    return [f"idle {b}" for b in budgets]


FINISH = ["flush", "dump"]  # the finished page: the only dump 04 allows after a unit has run


# ---- the handwritten trees ----------------------------------------------------------------------

LEAF = "<br>"
PLAIN = "<p>hello</p>"
POST_SHAPE = "<div><h1><p></p><a></a></h1><h2></h2></div>"  # the post's example: root, div, h1, p, a, h2
POST_TEXT = "<div><h1>title<p>para</p><a>link</a></h1><h2>sub</h2></div>"
WIDE = "<ul>" + "".join(f"<li>item {i}</li>" for i in range(1, 13)) + "</ul>"
DEEP = "<div>" * 10 + "bottom" + "</div>" * 10
UNCLE = "<div><div><div><p>x</p></div></div><span>y</span></div>"
MIXED = "<p>one <b>two</b> three <i>four</i> five</p>"
VOIDS = "<div><input id=i1 className=field><br><hr></div>"
SPECIAL = '<p>50% off, "today" only</p>'
STAIRS = "<div><div><div><p>a</p><p>b</p></div><p>c</p></div><p>d</p></div>"
NESTED_LISTS = ("<ul><li>one<ul><li>one.a</li><li>one.b</li></ul></li><li>two</li>"
                "<li>three<ul><li>three.a</li></ul></li></ul>")
LAST_CHAIN = "<div><span>first</span><span><em><b>last</b></em></span></div>"
ONLY_CHILDREN = "<section><div><span><em>solo</em></span></div></section>"
# the same shapes without text or props, for the walk requirement: nothing but the structure can fail them
UNCLE_E = "<div><div><div><p></p></div></div><span></span></div>"
STAIRS_E = "<div><div><div><p></p><p></p></div><p></p></div><p></p></div>"
NESTED_E = "<ul><li><ul><li></li><li></li></ul></li><li></li><li><ul><li></li></ul></li></ul>"
LAST_E = "<div><span></span><span><em><b></b></em></span></div>"
ONLY_E = "<section><div><span><em></em></span></div></section>"
PAGE_E = ("<main><header><h1></h1><nav><a></a><a></a><a></a></nav></header><section><article><h2></h2>"
          "<p><b></b><i></i></p><p></p></article><aside><ul><li></li><li></li><li></li></ul></aside></section>"
          "<footer></footer></main>")
ATTRS = ('<section id="main" className="wide" title="the page"><h1 id=head className=big>Hi</h1>'
         '<button disabled id=go className="btn primary" title="go on">Go</button><span title=t>x</span></section>')
TEXT_ODDITIES = '<div><p>  padded  </p><p>100% done</p><p>say "hi"</p><p>a, b; c</p></div>'
BIG = ("<main id=app><header><h1>Title</h1><nav><a>one</a><a>two</a><a>three</a></nav></header>"
       "<section className=body><article><h2>Story</h2><p>First <b>bold</b> and <i>italic</i> words.</p>"
       "<p>Second paragraph.</p></article><aside><ul><li>a</li><li>b</li><li>c</li></ul></aside></section>"
       "<footer title=end>bye</footer></main>")


def handwritten():
    cases = []

    def add(case_id, req, title, markup, steps):
        cases.append(Scenario(case_id, req, title, markup, steps))

    # R1: render() leaves the page alone and runs no unit. Each case only looks at the page right after
    # render, so nothing else can make it fail.
    add("04-R1-dump-after-render-leaf", "R1", "one paragraph: the page is empty right after render",
        PLAIN, ["render a", "dump"])
    add("04-R1-dump-after-render-nested", "R1", "a nested tree with text: empty right after render",
        POST_TEXT, ["render a", "dump"])
    add("04-R1-dump-after-render-wide", "R1", "a list of 12 items: empty right after render",
        WIDE, ["render a", "dump", "dump"])
    add("04-R1-dump-after-render-props", "R1", "elements with props: empty right after render",
        ATTRS, ["render a", "dump"])

    # R2: units are fibers
    for slug, title, m in [
        ("leaf", "a lone <br>: root fiber plus one element", LEAF),
        ("element-and-text", "<p>hello</p>: root, p, one text node", PLAIN),
        ("post-shape", "div > (h1 > (p, a), h2): six units without text", POST_SHAPE),
        ("post-with-text", "the same shape with four text nodes", POST_TEXT),
        ("wide-list", "a list with 12 items (26 units)", WIDE),
        ("deep-chain", "ten nested divs around one text node", DEEP),
        ("mixed-text", "text pieces around two inline elements", MIXED),
        ("void-elements", "input, br and hr have no children", VOIDS),
    ]:
        add(f"04-R2-units-{slug}", "R2", title, m, ["render a"] + idles("inf", "inf"))

    # R3: period sizes
    for k in (1, 2, 3, 5):
        add(f"04-R3-budget-{k}-post-text", "R3", f"10 units in periods of {k}", POST_TEXT,
            ["render a"] + idles(*periods_for(reactgen.count_units(POST_TEXT), k)))
    add("04-R3-budget-7-wide", "R3", "26 units in periods of 7: the last one is short", WIDE,
        ["render a"] + idles(*periods_for(reactgen.count_units(WIDE), 7)))
    add("04-R3-budget-equals-units", "R3", "a budget of exactly the 9 units there are", MIXED,
        ["render a"] + idles(9, 3))
    add("04-R3-budget-larger-than-units", "R3", "a budget of 50 for 6 units", POST_SHAPE,
        ["render a"] + idles(50, 50))
    add("04-R3-mixed-budgets", "R3", "budgets 2, 5, 1, 4, then unlimited", BIG,
        ["render a"] + idles(2, 5, 1, 4, "inf", 3))
    add("04-R3-budget-1-leaf", "R3", "budget 1 for a tree of 2 units", LEAF, ["render a"] + idles(1, 1, 1))

    # R4: the walk. Flush alone, on trees with no text and no props: only the structure can make them fail.
    add("04-R4-uncle", "R4", "a leaf at the end of a branch: the next unit is the parent's sibling",
        POST_SHAPE, ["render a"] + FINISH)
    add("04-R4-climb-three-levels", "R4", "from the only leaf, three levels up to a sibling",
        UNCLE_E, ["render a"] + FINISH)
    add("04-R4-staircase", "R4", "siblings at every level of a left-leaning tree", STAIRS_E, ["render a"] + FINISH)
    add("04-R4-nested-lists", "R4", "lists inside list items", NESTED_E, ["render a"] + FINISH)
    add("04-R4-last-branch", "R4", "the walk ends by climbing from the last leaf to the root",
        LAST_E, ["render a"] + FINISH)
    add("04-R4-only-children", "R4", "a chain with no siblings at all", ONLY_E, ["render a"] + FINISH)
    add("04-R4-page-shape", "R4", "a page-sized tree of bare elements", PAGE_E, ["render a"] + FINISH)
    add("04-R4-text-leaf-then-uncle", "R4", "the leaf is a text node and the next unit is its parent's sibling",
        UNCLE, ["render a"] + FINISH)

    # R5: nothing left to do. These scenarios end on an idle line: a library that reads the clock when it
    # has no work can't get through flush, and the case should point at R5, not at a timeout.
    add("04-R5-idle-before-render", "R5", "idle before any render reports 0, then a normal render", PLAIN,
        idles(3, "inf") + ["render a"] + idles("inf", 2))
    add("04-R5-idle-after-done", "R5", "after the work is done, budgets 1, 5 and unlimited all report 0",
        POST_TEXT, ["render a"] + idles("inf", 1, 5, "inf"))
    add("04-R5-idle-after-flush", "R5", "idle after flush reports 0", WIDE, ["render a", "flush"] + idles(4, "inf"))
    add("04-R5-small-periods-then-more", "R5", "periods of 3 to the end, then three more", UNCLE,
        ["render a"] + idles(*periods_for(reactgen.count_units(UNCLE), 3), 3, 3, 3))
    add("04-R5-idle-only", "R5", "idle with nothing ever rendered", PLAIN, idles(1, "inf", 2))

    # R6: content
    add("04-R6-attributes", "R6", "id, className, title and disabled on several elements", ATTRS,
        ["render a"] + FINISH)
    add("04-R6-text-oddities", "R6", "padded text, a percent sign, quotes and punctuation", TEXT_ODDITIES,
        ["render a"] + FINISH)
    add("04-R6-special-characters", "R6", "percent sign and quotes in text", SPECIAL, ["render a"] + FINISH)
    add("04-R6-input-and-voids", "R6", "an input with props between void elements", VOIDS, ["render a"] + FINISH)

    # E2E
    add("04-E2E-page", "E2E", "a page-sized tree: empty page, uneven periods, finished page", BIG,
        ["render a", "dump"] + idles(3, 6, 2, "inf") + FINISH + idles(1))
    add("04-E2E-nested-lists", "E2E", "a nested list rendered with budget 2 until done", NESTED_LISTS,
        ["render a", "dump"] + idles(*periods_for(reactgen.count_units(NESTED_LISTS), 2)) + FINISH)
    add("04-E2E-resume-after-periods", "E2E", "periods of 4 and 1 leave work for flush to finish", STAIRS,
        ["render a"] + idles(4, 1) + FINISH)
    return cases


def random_tree(rng):
    """A random tree of 8 to 60 units (a tree of two or three units says nothing about the walk)."""
    while True:
        markup = reactgen.rand_markup(rng, depth=rng.randint(2, 4), width=rng.randint(2, 4), tags=SAFE_TAGS)
        if 8 <= reactgen.count_units(markup) <= 60:
            return markup


def random_cases(seed):
    cases = []
    for i in range(1, 7):
        rng = reactgen.rng_for(seed, f"p04-{i}")
        markup = random_tree(rng)
        u = reactgen.count_units(markup)
        if i <= 3:  # whole trees finished by flush, some after a few periods
            steps = ["render a"] + idles(*[rng.choice([1, 2, 3, 5]) for _ in range(rng.randint(0, 3))]) + FINISH
            cases.append(Scenario(f"04-E2E-random-s{seed}-{i}", "E2E", f"random tree of {u} units", markup, steps))
        else:  # period sizes on random trees: a few random budgets, then until done
            budgets = [rng.choice([1, 2, 3, 5, 8]) for _ in range(rng.randint(2, 8))]
            steps = ["render a"] + idles(*budgets, "inf", "inf")
            cases.append(Scenario(f"04-R3-random-s{seed}-{i}", "R3", f"random tree of {u} units, random budgets",
                                  markup, steps))
    return cases


# ---- expected output -----------------------------------------------------------------------------

def final_dump_counts(oracle_lines):
    """(node lines, text lines) of the last dump block of the oracle's output."""
    start = max(i for i, line in enumerate(oracle_lines) if line.startswith("dump "))
    block = oracle_lines[start + 1:]
    return (sum(1 for l in block if l.startswith("node ")), sum(1 for l in block if l.startswith("text ")))


def main():
    args = wbcore.parse_args("04")
    all_cases = handwritten() + random_cases(args.seed)
    scenarios = [c.lines() for c in all_cases]
    oracle = reactgen.run_oracle_batch(scenarios)
    # React alone shows how many nodes each tree has: the check on the unit formula
    shapes = reactgen.run_oracle_batch([[f"tree a {c.markup}", "render a", "dump"] for c in all_cases])

    cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, EXPLAIN, source=SOURCE)
    for case, lines, oracle_lines, shape in zip(all_cases, scenarios, oracle, shapes):
        units = {"a": reactgen.count_units(case.markup)}
        elements, texts = final_dump_counts(shape)
        by_oracle = 1 + elements + texts
        assert units["a"] == units_by_regex(case.markup) == by_oracle,             (f"{case.case_id}: unit counts disagree: formula {units['a']}, regex {units_by_regex(case.markup)}, "
             f"oracle dump {by_oracle}")
        expected = reactgen.merge_expected(lines, oracle_lines, units)
        # the second model must give the same idle lines
        got = [l for l in expected if l.startswith("idle ")]
        want = my_idle_model(units["a"], lines)
        assert got == want, f"{case.case_id}: idle lines differ between the two models: {got} vs {want}"
        cases.add(case.case_id, case.req, case.title, lines, expected)
    cases.save()


if __name__ == "__main__":
    main()
