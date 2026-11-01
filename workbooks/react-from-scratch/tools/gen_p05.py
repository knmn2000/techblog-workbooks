"""Test generator for assignment 05 (render phase, then commit).

    py -P tools/gen_p05.py [--seed N] [--out DIR]

Scenario commands used: tree, render, idle, flush, dump, ops (always `ops insert move remove`).
Every scenario renders one tree onto the empty container and never renders again.

Where the expected lines come from:
  node/text lines   real React 19.3.1 on jsdom (tools/oracle). A dump taken while work is still pending is
                    printed as an empty container: nothing may reach the page before the last unit.
  idle lines        the unit formula (U = 1 root fiber + elements + text nodes; idle k reports min(k, left)),
                    applied by reactgen.merge_expected and re-checked here with a second model.
  ops lines         modelled here: `insert` counts the nodes the commit attaches (U - 1, every element and
                    text node, once) and is 0 in every period that leaves work undone; `move` and `remove`
                    are always 0 for a first render. The counters reset at each `ops`.

The ops lines only use insert, move and remove. `create` and `write` are left out on purpose: whether the
nodes are made in the units or in the commit is not part of the assignment.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reactgen  # noqa: E402
import wbcore  # noqa: E402

COMPARE = ("records idle=units dump=n node=depth,label,tag,props text=depth,value title=value "
           "ops=insert,move,remove")
EXPLAIN = "node:props=R5 text:value=R5"
SOURCE = ("React 19.3.1 on jsdom 30.1.3 for the dumps; the unit formula for the idle lines; "
          "a model in tools/gen_p05.py for the ops lines")

REQUIREMENTS = [
    ("R1", "while units run the container stays empty: a dump after a period that leaves work undone shows no node"),
    ("R2", "the period that runs the last unit also commits: a dump right after it shows the whole tree"),
    ("R3", "the commit adds no unit and no timeRemaining() read: idle k still reports min(k, units left), then 0"),
    ("R4", "every node is inserted once, by the commit: ops insert move remove is 0 0 0 while work is pending, "
           "N 0 0 in the period of the last unit (N = elements + text nodes), and 0 0 0 after that"),
    ("R5", "the committed tree has the right shape: nesting, sibling order, props and text"),
    ("E2E", "whole scenarios: periods, dumps and ops mixed"),
]

SAFE_TAGS = ["div", "span", "section", "em", "b", "i", "ul", "nav", "article", "aside"]

OPEN_TAG = re.compile(r"<[A-Za-z][^<>]*>")
ANY_TAG = re.compile(r"</?[A-Za-z][^<>]*>")


def units_by_regex(markup):
    elements = len(OPEN_TAG.findall(markup))
    texts = sum(1 for piece in ANY_TAG.split(markup) if piece.strip())
    return 1 + elements + texts


# ---- the model written here (a second opinion on idle lines, and the source of ops lines) -------------

def my_model(units, commands):
    """Walks a scenario and returns (idle lines, ops lines, dump states) where a dump state is 'empty'
    or 'full'. One render, onto an empty container; the commit happens in the period that finishes it."""
    pending, rendered, inserted = 0, False, 0
    idles, opses, dumps = [], [], []

    def run(budget):
        nonlocal pending, inserted
        done = pending if budget == "inf" else min(int(budget), pending)
        pending -= done
        if done and pending == 0:
            inserted += units - 1
        return done

    for command in commands:
        word, _, arg = command.partition(" ")
        if word == "render":
            pending, rendered = units, True
        elif word == "idle":
            idles.append(f"idle {run(arg)}")
        elif word == "flush":
            run("inf")
        elif word == "ops":
            names = arg.split()
            values = {"insert": inserted, "move": 0, "remove": 0}
            opses.append("ops " + " ".join(str(values[n]) for n in names))
            inserted = 0
        elif word == "dump":
            dumps.append("full" if rendered and pending == 0 else "empty")
    return idles, opses, dumps


def dump_states(expected):
    """'empty' or 'full' for each dump block of an expected output."""
    states, current = [], None
    for line in expected:
        if line.startswith("dump "):
            if current is not None:
                states.append(current)
            current = "empty"
        elif line.startswith(("node ", "text ")):
            current = "full"
    if current is not None:
        states.append(current)
    return states


# ---- scenario builders --------------------------------------------------------------------------

class Scenario:
    def __init__(self, case_id, req, title, markup, steps):
        self.case_id, self.req, self.title = case_id, req, title
        self.markup = markup
        self.steps = steps

    def lines(self):
        return [f"tree a {self.markup}"] + self.steps


def idles(*budgets):
    return [f"idle {b}" for b in budgets]


OPS = "ops insert move remove"


def partial(units, k):
    """Periods of size k that leave work undone: as many as fit while at least one unit remains."""
    return [k] * ((units - 1) // k)


def to_the_end(units, k):
    """Periods of size k up to and including the one that runs the last unit."""
    return [k] * (-(-units // k))


def with_dumps(budgets, after_each=("dump",)):
    steps = []
    for b in budgets:
        steps += [f"idle {b}", *after_each]
    return steps


LEAF = "<br>"
PLAIN = "<p>hello</p>"
POST_SHAPE = "<div><h1><p></p><a></a></h1><h2></h2></div>"
POST_TEXT = "<div><h1>title<p>para</p><a>link</a></h1><h2>sub</h2></div>"
WIDE = "<ul>" + "".join(f"<li>item {i}</li>" for i in range(1, 13)) + "</ul>"
UNCLE = "<div><div><div><p>x</p></div></div><span>y</span></div>"
MIXED = "<p>one <b>two</b> three <i>four</i> five</p>"
VOIDS = "<div><input id=i1 className=field><br><hr></div>"
STAIRS = "<div><div><div><p>a</p><p>b</p></div><p>c</p></div><p>d</p></div>"
NESTED_LISTS = ("<ul><li>one<ul><li>one.a</li><li>one.b</li></ul></li><li>two</li>"
                "<li>three<ul><li>three.a</li></ul></li></ul>")
ATTRS = ('<section id="main" className="wide" title="the page"><h1 id=head className=big>Hi</h1>'
         '<button disabled id=go className="btn primary" title="go on">Go</button><span title=t>x</span></section>')
TEXT_ODDITIES = '<div><p>  padded  </p><p>100% done</p><p>say "hi"</p><p>a, b; c</p></div>'
BIG = ("<main id=app><header><h1>Title</h1><nav><a>one</a><a>two</a><a>three</a></nav></header>"
       "<section className=body><article><h2>Story</h2><p>First <b>bold</b> and <i>italic</i> words.</p>"
       "<p>Second paragraph.</p></article><aside><ul><li>a</li><li>b</li><li>c</li></ul></aside></section>"
       "<footer title=end>bye</footer></main>")


def chain(depth):
    """depth nested elements, nothing else: depth + 1 units."""
    tags = ["div", "section", "article", "span", "em", "b"]
    names = [tags[i % len(tags)] for i in range(depth)]
    return "".join(f"<{n}>" for n in names) + "".join(f"</{n}>" for n in reversed(names))


def U(markup):
    return reactgen.count_units(markup)


def handwritten():
    cases = []

    def add(case_id, req, title, markup, steps):
        cases.append(Scenario(case_id, req, title, markup, steps))

    # R1: dumps while work is pending. Every case ends with work left, so every dump has to be empty.
    add("05-R1-empty-between-periods", "R1", "10 units in periods of 3, a dump after each: empty every time",
        POST_TEXT, ["render a"] + with_dumps(partial(U(POST_TEXT), 3)))
    add("05-R1-one-unit-at-a-time", "R1", "three units, one per period: empty after the first two",
        PLAIN, ["render a"] + with_dumps(partial(U(PLAIN), 1)))
    add("05-R1-one-unit-left", "R1", "25 of 26 units done: still empty", WIDE,
        ["render a"] + with_dumps(partial(U(WIDE), 25)))
    add("05-R1-uneven-periods", "R1", "periods of 2, 5, 3 and 1 on a page-sized tree",
        BIG, ["render a"] + with_dumps([2, 5, 3, 1]))
    add("05-R1-elements-with-props", "R1", "props and text on the way: still nothing on the page", ATTRS,
        ["render a"] + with_dumps(partial(U(ATTRS), 2)))
    add("05-R1-nested-lists-by-fours", "R1", "periods of 4 on nested lists, dumping twice after each",
        NESTED_LISTS, ["render a"] + with_dumps(partial(U(NESTED_LISTS), 4), ("dump", "dump")))

    # R2: the period of the last unit commits. Only the dump after that period is looked at, and the trees
    # are single chains (no siblings, no text), so a commit that forgets siblings or text can't fail them.
    c8, c6, c13, c4, c10, c5 = chain(7), chain(5), chain(12), chain(3), chain(9), chain(4)
    add("05-R2-last-period-of-three", "R2", "8 units in periods of 3: the third one runs the last two and commits",
        c8, ["render a"] + idles(*to_the_end(U(c8), 3)) + ["dump"])
    add("05-R2-budget-equals-units", "R2", "a budget of exactly the 6 units there are", c6,
        ["render a", "idle 6", "dump"])
    add("05-R2-one-unlimited-period", "R2", "one unlimited period does everything", c13,
        ["render a", "idle inf", "dump"])
    add("05-R2-one-unit-periods", "R2", "periods of 1 on a two-unit tree", LEAF,
        ["render a"] + idles(*to_the_end(U(LEAF), 1)) + ["dump"])
    add("05-R2-budget-larger-than-units", "R2", "a budget of 50 for 4 units", c4,
        ["render a", "idle 50", "dump"])
    add("05-R2-short-last-period", "R2", "periods of 4 on 10 units: the last one has 2", c10,
        ["render a"] + idles(*to_the_end(U(c10), 4)) + ["dump"])
    add("05-R2-periods-of-one", "R2", "five units, one per period", c5,
        ["render a"] + idles(*to_the_end(U(c5), 1)) + ["dump"])

    # R3: unit counts with the commit in the picture (no dumps: only the idle lines are looked at)
    for k in (1, 2, 3, 5):
        add(f"05-R3-budget-{k}-post-text", "R3", f"10 units in periods of {k}, then one more period",
            POST_TEXT, ["render a"] + idles(*to_the_end(U(POST_TEXT), k), k))
    add("05-R3-budget-equals-units", "R3", "a budget of exactly 9: no tenth unit for the commit", MIXED,
        ["render a", "idle 9", "idle 3", "idle inf"])
    add("05-R3-unlimited-reports-units", "R3", "an unlimited period reports 26, not 27", WIDE,
        ["render a", "idle inf", "idle inf"])
    add("05-R3-one-short-of-done", "R3", "a budget of 5 on 6 units, then 1, then 1", POST_SHAPE,
        ["render a", "idle 5", "idle 1", "idle 1"])
    add("05-R3-mixed-budgets", "R3", "budgets 4, 1, 6, 2, 50", BIG, ["render a"] + idles(4, 1, 6, 2, 50, 3))

    # R4: ops. No dumps here, so a bug in what the page shows can't fail these.
    add("05-R4-insert-at-commit", "R4", "10 units: periods of 4, nothing inserted until the third",
        POST_TEXT, ["render a", "idle 4", OPS, "idle 4", OPS, "idle 4", OPS])
    add("05-R4-one-period", "R4", "one unlimited period inserts the 9 nodes", POST_TEXT,
        ["render a", "idle inf", OPS])
    add("05-R4-nothing-after-commit", "R4", "periods after the commit insert, move and remove nothing", MIXED,
        ["render a", "idle inf", OPS, "idle 3", "idle inf", "flush", OPS])
    add("05-R4-leaf", "R4", "two units, one per period", LEAF, ["render a", "idle 1", OPS, "idle 1", OPS])
    add("05-R4-wide-list", "R4", "25 nodes inserted once", WIDE, ["render a", "idle 20", OPS, "idle 20", OPS])
    add("05-R4-every-period", "R4", "a reading of ops after every period of 3", POST_TEXT,
        ["render a"] + [s for _ in range(5) for s in ("idle 3", OPS)])
    add("05-R4-commit-once-over-many-periods", "R4", "five more periods after the commit: still one insert per node",
        STAIRS, ["render a", "idle inf"] + idles(1, 1, 1, 1, 1) + [OPS])

    # R5: the committed tree
    for slug, title, m in [
        ("post-shape", "div > (h1 > (p, a), h2)", POST_SHAPE),
        ("uncle-and-text", "text leaves and three levels to climb", UNCLE),
        ("staircase", "siblings at every level", STAIRS),
        ("nested-lists", "lists inside list items", NESTED_LISTS),
        ("attributes", "id, className, title and disabled", ATTRS),
        ("text-oddities", "padded text, a percent sign and quotes", TEXT_ODDITIES),
        ("mixed-text", "text pieces around two inline elements", MIXED),
        ("voids", "input, br and hr", VOIDS),
        ("page", "a page-sized tree", BIG),
    ]:
        add(f"05-R5-shape-{slug}", "R5", title, m, ["render a", "flush", "dump"])

    # E2E
    add("05-E2E-watch-it-build", "E2E", "dump and ops after every period of 4 on a page-sized tree", BIG,
        ["render a"] + [s for _ in range(6) for s in ("idle 4", "dump", OPS)] + ["flush", "dump", OPS])
    add("05-E2E-uneven", "E2E", "uneven periods ending in flush", NESTED_LISTS,
        ["render a", "dump", "idle 2", "dump", OPS, "idle 7", "dump", OPS, "idle 3", "dump", OPS, "flush", "dump", OPS])
    return cases


def random_tree(rng):
    """A random tree of 8 to 60 units (a tree of two or three units says nothing about the walk)."""
    while True:
        markup = reactgen.rand_markup(rng, depth=rng.randint(2, 4), width=rng.randint(2, 4), tags=SAFE_TAGS)
        if 8 <= reactgen.count_units(markup) <= 60:
            return markup


def random_cases(seed):
    cases = []
    for i in range(1, 6):
        rng = reactgen.rng_for(seed, f"p05-{i}")
        markup = random_tree(rng)
        u = U(markup)
        if i <= 2:  # dumps while work is pending
            k = rng.choice([1, 2, 3, 4, 6])
            budgets = partial(u, k)[:12] or [1]
            if sum(budgets) >= u:  # keep at least one unit pending
                budgets = budgets[:-1] or [1]
            cases.append(Scenario(f"05-R1-random-s{seed}-{i}", "R1", f"random tree of {u} units, a dump after each period",
                                  markup, ["render a"] + with_dumps(budgets)))
        else:  # everything: periods, dumps, ops
            steps = ["render a"]
            pending = u
            for _ in range(rng.randint(2, 6)):
                b = rng.choice([1, 2, 3, 5, 8, "inf"])
                steps.append(f"idle {b}")
                pending -= pending if b == "inf" else min(b, pending)
                if rng.random() < 0.7:
                    steps.append("dump")
                if rng.random() < 0.6:
                    steps.append(OPS)
            steps += ["flush", "dump", OPS]
            cases.append(Scenario(f"05-E2E-random-s{seed}-{i}", "E2E", f"random tree of {u} units, random periods",
                                  markup, steps))
    return cases


# ---- expected output -----------------------------------------------------------------------------

def final_dump_counts(oracle_lines):
    start = max(i for i, line in enumerate(oracle_lines) if line.startswith("dump "))
    block = oracle_lines[start + 1:]
    return (sum(1 for l in block if l.startswith("node ")), sum(1 for l in block if l.startswith("text ")))


def main():
    args = wbcore.parse_args("05")
    all_cases = handwritten() + random_cases(args.seed)
    scenarios = [c.lines() for c in all_cases]
    oracle = reactgen.run_oracle_batch(scenarios)
    shapes = reactgen.run_oracle_batch([[f"tree a {c.markup}", "render a", "dump"] for c in all_cases])

    cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, EXPLAIN, source=SOURCE)
    for case, lines, oracle_lines, shape in zip(all_cases, scenarios, oracle, shapes):
        units = U(case.markup)
        elements, texts = final_dump_counts(shape)
        assert units == units_by_regex(case.markup) == 1 + elements + texts, \
            f"{case.case_id}: unit counts disagree: formula {units}, regex {units_by_regex(case.markup)}, oracle {1 + elements + texts}"
        idle_lines, ops_lines, states = my_model(units, lines)
        expected = reactgen.merge_expected(lines, oracle_lines, {"a": units}, ops_lines)
        # the second model must agree on the idle lines, the ops lines and which dumps are empty
        assert [l for l in expected if l.startswith("idle ")] == idle_lines, f"{case.case_id}: idle lines differ"
        assert [l for l in expected if l.startswith("ops ")] == ops_lines, f"{case.case_id}: ops lines differ"
        assert dump_states(expected) == states, f"{case.case_id}: dump states differ: {dump_states(expected)} vs {states}"
        cases.add(case.case_id, case.req, case.title, lines, expected)
    cases.save()


if __name__ == "__main__":
    main()
