"""Test generator for assignment 10 (useState).

    py -P tools/gen_p10.py [--seed N] [--out DIR]

Every expected output comes from real React 19 on jsdom (tools/oracle), never from the reference solution.
The scenarios use the catalog components Counter, MultiCounter, Toggle and Keeper. The hand-written cases
carry a `must` list: lines the oracle's answer has to contain, written down here from the definition of
the case (a counter that was clicked three times shows 3), so a scenario that does not test what its
title says stops the generator.
"""

import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wbcore  # noqa: E402
from reactgen import rng_for, run_oracle_batch  # noqa: E402

NN = "10"
SOURCE = "React 19.3.1 (react-dom 19.3.1) on jsdom 30.1.3, run by tools/oracle with the harness catalog"

COMPARE = "records dump=n node=depth,label,tag,props text=depth,value"

REQUIREMENTS = [
    ("R1", "useState(initial) returns [state, setState]; the first render shows the initial value"),
    ("R2", "A setter call (an updater function) re-renders the component and the page shows the new state"),
    ("R3", "Every component instance has state of its own"),
    ("R4", "Several useState calls in one component keep separate slots, in call order, and slots never leak between components"),
    ("R5", "Several updater calls before the next render are all applied, in the order they were called"),
    ("R6", "State survives a re-render that comes from above or from another component"),
    ("R7", "State belongs to the fiber at a position (or key): a new type or a new position starts from the initial value"),
    ("R8", "A setter from an earlier render still works: nothing is lost when it is called later"),
    ("R9", "A component whose root tag changes keeps its state, and its new nodes are live"),
    ("E2E", "Long sessions that mix all of the above"),
]


def count_lines(n):
    return f'{n}'


def case(cid, req, title, lines, must=()):
    return {"id": cid, "req": req, "title": title, "lines": lines, "must": list(must)}


def build_handwritten():
    c = []
    add = lambda *a, **k: c.append(case(*a, **k))

    # ---- R1: initial state ----
    add("10-R1-counter-default", "R1", "a Counter with no start prop shows 0",
        ["tree t <Counter/>", "render t", "flush", "dump"], [count_lines(0)])
    add("10-R1-counter-start", "R1", "a Counter with start=5 shows 5",
        ["tree t <Counter start=5/>", "render t", "flush", "dump"], [count_lines(5)])
    add("10-R1-two-initial-values", "R1", "two Counters start from their own start prop",
        ["tree t <div><Counter id=a start=3/><Counter id=b start=40/></div>", "render t", "flush", "dump"],
        ['3', '40'])
    add("10-R1-every-component", "R1", "Counter, MultiCounter, Keeper and Toggle in one tree, before any click",
        ["tree t <div><Frame title=all><Counter/><MultiCounter/><Keeper/></Frame><Toggle/></div>",
         "render t", "flush", "dump"], ['off'])

    # ---- R2: a click shows up ----
    add("10-R2-one-click", "R2", "one click on + takes 0 to 1",
        ["tree t <Counter/>", "render t", "flush", "click #c-inc", "dump"], [count_lines(1)])
    add("10-R2-dump-after-each-click", "R2", "three clicks, a dump after each: the same nodes show 1, 2, 3",
        ["tree t <Counter/>", "render t", "flush",
         "click #c-inc", "dump", "click #c-inc", "dump", "click #c-inc", "dump"],
        [count_lines(1), count_lines(2), count_lines(3)])
    add("10-R2-start-then-clicks", "R2", "start=5, two clicks",
        ["tree t <Counter start=5/>", "render t", "flush", "click #c-inc", "click #c-inc", "dump"], [count_lines(7)])
    add("10-R2-inside-frame", "R2", "a Counter inside a Frame",
        ["tree t <Frame title=box><Counter id=k/></Frame>", "render t", "flush",
         "click #k-inc", "click #k-inc", "dump"], ['2'])

    # ---- R3: separate instances ----
    add("10-R3-two-counters", "R3", "two Counters: a is clicked twice, b once",
        ["tree t <div><Counter id=a/><Counter id=b/></div>", "render t", "flush",
         "click #a-inc", "click #a-inc", "click #b-inc", "dump"], ['2', '1'])
    add("10-R3-three-counters-nested", "R3", "three Counters, one of them inside a Frame",
        ["tree t <div><Counter id=a/><Frame title=f><Counter id=b/></Frame><Counter id=c/></div>", "render t", "flush",
         "click #b-inc", "click #c-inc", "click #c-inc", "click #a-inc", "dump"], ['1', '1', '2'])
    add("10-R3-same-start-different-clicks", "R3", "two Counters with start=10, only b is clicked (three times)",
        ["tree t <div><Counter id=a start=10/><Counter id=b start=10/></div>", "render t", "flush",
         "click #b-inc", "click #b-inc", "click #b-inc", "dump"], ['10', '13'])

    # ---- R4: hook order ----
    add("10-R4-multicounter", "R4", "MultiCounter: a, b, a, a, b",
        ["tree t <MultiCounter/>", "render t", "flush",
         "click #mc-a", "click #mc-b", "click #mc-a", "click #mc-a", "click #mc-b", "dump"],
        ['3', '2'])
    add("10-R4-counter-multicounter-counter", "R4", "a MultiCounter between two Counters",
        ["tree t <div><Counter id=a/><MultiCounter/><Counter id=b/></div>", "render t", "flush",
         "click #a-inc", "click #mc-b", "click #b-inc", "click #mc-a", "click #mc-b", "click #a-inc", "dump"], [])
    add("10-R4-multicounter-first", "R4", "a MultiCounter followed by a Counter that starts at 9",
        ["tree t <div><MultiCounter/><Counter id=z start=9/></div>", "render t", "flush",
         "click #mc-b", "click #z-inc", "click #mc-b", "click #mc-a", "dump"], ['10'])
    add("10-R4-keeper-between-others", "R4", "a Keeper between a Counter and a MultiCounter, poked once, then clicks all round",
        ["tree t <div><Counter id=a/><Keeper/><MultiCounter/></div>", "render t", "flush",
         "poke", "click #a-inc", "click #mc-a", "click #mc-b", "click #a-inc", "click #mc-b", "dump"], ["1", "1", "2", "2"])

    # ---- R5: queued updaters ----
    add("10-R5-d-one-click", "R5", "the d Counter adds 2 on one click",
        ["tree t <Counter id=d/>", "render t", "flush", "click #d-inc", "dump"], [count_lines(2)])
    add("10-R5-d-three-clicks", "R5", "the d Counter after each of three clicks",
        ["tree t <Counter id=d/>", "render t", "flush",
         "click #d-inc", "dump", "click #d-inc", "dump", "click #d-inc", "dump"],
        [count_lines(2), count_lines(4), count_lines(6)])
    add("10-R5-d-next-to-c", "R5", "c adds 1 and d adds 2, interleaved",
        ["tree t <div><Counter id=c/><Counter id=d start=10/></div>", "render t", "flush",
         "click #d-inc", "click #c-inc", "click #d-inc", "dump"], ['1', '14'])

    # ---- R6: survives re-renders from outside ----
    add("10-R6-render-again", "R6", "click twice, then render the same tree again",
        ["tree t <Counter/>", "render t", "flush", "click #c-inc", "click #c-inc", "render t", "flush", "dump"],
        [count_lines(2)])
    add("10-R6-frame-title-changes", "R6", "the Frame around a clicked Counter gets a new title",
        ["tree a <Frame title=A><Counter/></Frame>", "tree b <Frame title=B><Counter/></Frame>",
         "render a", "flush", "click #c-inc", "render b", "flush", "dump"], ['B', '1'])
    add("10-R6-wrapper-class-changes", "R6", "the div around two clicked Counters gets a class",
        ["tree a <div><Counter id=a/><Counter id=b/></div>", "tree b <div className=k><Counter id=a/><Counter id=b/></div>",
         "render a", "flush", "click #a-inc", "click #b-inc", "click #b-inc", "render b", "flush", "dump"],
        ['1', '2'])
    add("10-R6-start-ignored-later", "R6", "start only matters on the first render: 5, click, render with start=9",
        ["tree a <Counter start=5/>", "tree b <Counter start=9/>",
         "render a", "flush", "click #c-inc", "render b", "flush", "dump"], [count_lines(6)])
    add("10-R6-render-between-clicks", "R6", "click, render again, click, render again, click",
        ["tree t <div><Counter id=a/><Counter id=d/></div>", "render t", "flush",
         "click #a-inc", "render t", "flush", "click #d-inc", "render t", "flush", "click #a-inc", "dump"],
        ['2'])

    # ---- R7: position and type ----
    add("10-R7-type-change-resets", "R7", "Counter, then FnA, then a Counter again at the same position",
        ["tree a <div><Counter/></div>", "tree b <div><FnA/></div>",
         "render a", "flush", "click #c-inc", "click #c-inc", "render b", "flush", "render a", "flush", "dump"],
        [count_lines(0)])
    add("10-R7-root-type-change-resets", "R7", "a Counter at the root, replaced by a div and then by a Counter",
        ["tree a <Counter/>", "tree b <div>other</div>",
         "render a", "flush", "click #c-inc", "render b", "flush", "render a", "flush", "dump"], ['0'])
    add("10-R7-position-shift-resets", "R7", "a p is put in front of a clicked Counter",
        ["tree a <div><Counter/></div>", "tree b <div><p>x</p><Counter/></div>",
         "render a", "flush", "click #c-inc", "click #c-inc", "render b", "flush", "dump"], ['0'])
    add("10-R7-reset-to-start", "R7", "start=4, clicked to 6, removed, added again: 4",
        ["tree a <div><Counter start=4/></div>", "tree b <div><p>gone</p></div>",
         "render a", "flush", "click #c-inc", "click #c-inc", "render b", "flush", "render a", "flush", "dump"],
        [count_lines(4)])
    add("10-R7-swap-positions", "R7", "Counters a and b swap places in the tree: the count stays with the position",
        ["tree a <div><Counter id=a/><Counter id=b/></div>", "tree b <div><Counter id=b/><Counter id=a/></div>",
         "render a", "flush", "click #a-inc", "click #a-inc", "click #a-inc", "click #b-inc",
         "dump", "render b", "flush", "dump", "click #b-inc", "dump"], [])
    add("10-R7-keyed-reverse", "R7", "keyed Counters are reversed: the count follows the key",
        ["tree a <div><Counter key=a id=a/><Counter key=b id=b/></div>",
         "tree b <div><Counter key=b id=b/><Counter key=a id=a/></div>",
         "render a", "flush", "click #a-inc", "click #a-inc", "click #b-inc", "render b", "flush", "dump",
         "click #a-inc", "dump"], [])
    add("10-R7-keyed-remove-first", "R7", "the first of three keyed Counters is removed",
        ["tree a <div><Counter key=a id=a/><Counter key=b id=b/><Counter key=c id=c/></div>",
         "tree b <div><Counter key=b id=b/><Counter key=c id=c/></div>",
         "render a", "flush", "click #a-inc", "click #b-inc", "click #b-inc", "click #c-inc", "click #c-inc", "click #c-inc",
         "render b", "flush", "dump"], [])

    # ---- R8: stale setter ----
    add("10-R8-poke-once", "R8", "Keeper, one poke",
        ["tree t <Keeper/>", "render t", "flush", "poke", "dump"], ['1'])
    add("10-R8-poke-four-times", "R8", "Keeper, four pokes, a dump after each",
        ["tree t <Keeper/>", "render t", "flush",
         "poke", "dump", "poke", "dump", "poke", "dump", "poke", "dump"],
        ['1', '2', '3', '4'])
    add("10-R8-poke-after-render", "R8", "poke, render again, poke twice",
        ["tree t <div><Keeper/></div>", "render t", "flush", "poke", "render t", "flush", "poke", "poke", "dump"],
        ['3'])
    add("10-R8-poke-among-clicks", "R8", "pokes and clicks on a neighbour take turns",
        ["tree t <div><Keeper/><Counter/></div>", "render t", "flush",
         "poke", "click #c-inc", "poke", "click #c-inc", "poke", "click #c-inc", "dump"], ['3'])

    # ---- R9: Toggle ----
    add("10-R9-toggle-once", "R9", "Toggle after one click: a section with class on",
        ["tree t <Toggle/>", "render t", "flush", "dump", "click #t-btn", "dump"], ['on'])
    add("10-R9-toggle-three-times", "R9", "Toggle clicked three times, a dump after each",
        ["tree t <Toggle/>", "render t", "flush",
         "click #t-btn", "dump", "click #t-btn", "dump", "click #t-btn", "dump"], [])
    add("10-R9-toggle-after-a-sibling", "R9", "a paragraph before the Toggle",
        ["tree t <div><p>before</p><Toggle/></div>", "render t", "flush",
         "click #t-btn", "dump", "click #t-btn", "dump"], [])
    add("10-R9-toggle-and-counter", "R9", "a Counter keeps counting while the Toggle after it flips",
        ["tree t <div><Counter/><Toggle/></div>", "render t", "flush",
         "click #c-inc", "click #t-btn", "click #c-inc", "click #t-btn", "click #t-btn", "click #c-inc", "dump"],
        ['3'])
    add("10-R9-toggle-in-frame", "R9", "a Toggle as the last child of a Frame, clicked twice, then once more",
        ["tree t <Frame title=f><Toggle/></Frame>", "render t", "flush",
         "click #t-btn", "dump", "click #t-btn", "click #t-btn", "dump"], [])

    # ---- E2E ----
    add("10-E2E-dashboard", "E2E", "a dashboard of every stateful component, 40 steps",
        dashboard_session(), [])
    add("10-E2E-rerenders-and-resets", "E2E", "clicks, outside re-renders, a reset and a swap",
        mixed_session(), [])
    return c


def dashboard_session():
    s = ["tree t <div><Counter id=a start=2/><Counter id=d/><Frame title=multi><MultiCounter/></Frame><Keeper/><Toggle/></div>",
         "render t", "flush", "dump"]
    steps = ["a-inc", "d-inc", "mc-a", "poke", "t-btn", "d-inc", "mc-b", "mc-b", "poke", "a-inc",
             "t-btn", "mc-a", "d-inc", "poke", "a-inc", "t-btn", "t-btn", "mc-b", "d-inc", "poke"]
    for i, step in enumerate(steps):
        s.append("poke" if step == "poke" else f"click #{step}")
        if i % 4 == 3:
            s.append("dump")
    s += ["render t", "flush", "click #d-inc", "poke", "dump"]
    return s


def mixed_session():
    return [
        "tree a <div><Counter id=a/><Counter id=b start=7/><Keeper/></div>",
        "tree b <div className=wide><Counter id=a/><Counter id=b start=1/><Keeper/></div>",
        "tree c <div><Counter id=b/><Counter id=a/><Keeper/></div>",
        "tree d <section><Counter id=a/><Counter id=b/><Keeper/></section>",
        "render a", "flush", "click #a-inc", "click #b-inc", "poke", "dump",
        "render b", "flush", "click #b-inc", "poke", "dump",
        "render c", "flush", "dump", "click #b-inc", "click #a-inc", "poke", "dump",
        "render d", "flush", "dump", "click #a-inc", "dump",
    ]


# ---- the seeded part -----------------------------------------------------------------------------

def random_session(seed, index):
    """A tree of catalog components in a div and 14-26 operations on it. Only valid operations: a click
    names a button that is on the page, `poke` is used while the first Keeper is still the one on the
    page, and a Toggle is always the last child (what follows a replaced root is assignment 06's
    business)."""
    rng = rng_for(seed, f"p10-session-{index}")
    ids = ["a", "b", "c"]
    rng.shuffle(ids)

    def new_items():
        kinds = ["counter", "counter", "counter", "frame-counter", "multi", "keeper", "d"]
        picked, used_ids = [], set()
        for _ in range(rng.randint(3, 6)):
            kind = rng.choice(kinds)
            if kind in ("multi", "keeper") and any(p[0] == kind for p in picked):
                continue
            if kind in ("counter", "frame-counter"):
                free = [i for i in ids if i not in used_ids]
                if not free:
                    continue
                cid = rng.choice(free)
                used_ids.add(cid)
                picked.append((kind, cid, rng.randint(0, 9)))
            elif kind == "d":
                if "d" in used_ids:
                    continue
                used_ids.add("d")
                picked.append(("d", "d", rng.randint(0, 5)))
            else:
                picked.append((kind, None, 0))
        if rng.random() < 0.5:
            picked.append(("toggle", None, 0))
        return picked

    def markup(items, wrapper_class="", title="t"):
        parts = []
        for kind, cid, start in items:
            if kind in ("counter", "d"):
                parts.append(f"<Counter id={cid} start={start}/>")
            elif kind == "frame-counter":
                parts.append(f"<Frame title={title}><Counter id={cid} start={start}/></Frame>")
            elif kind == "multi":
                parts.append("<MultiCounter/>")
            elif kind == "keeper":
                parts.append("<Keeper/>")
            else:
                parts.append("<Toggle/>")
        attr = f" className={wrapper_class}" if wrapper_class else ""
        return f"<div{attr}>{''.join(parts)}</div>"

    def buttons(items):
        out = []
        for kind, cid, _ in items:
            if kind in ("counter", "d", "frame-counter"):
                out.append(f"click #{cid}-inc")
            elif kind == "multi":
                out += ["click #mc-a", "click #mc-b"]
            elif kind == "toggle":
                out.append("click #t-btn")
        return out

    items = new_items()
    if not items:
        items = [("counter", "a", 0)]
    trees = {}
    lines = []
    tree_no = 0

    def put_tree(its, **kw):
        nonlocal tree_no
        tree_no += 1
        name = f"t{tree_no}"
        lines.append(f"tree {name} {markup(its, **kw)}")
        return name

    # the Keeper that `poke` reaches is the first one that ever rendered; it stays valid while a Keeper
    # sits at the same index in every later tree
    keeper_alive = False
    keeper_index = None

    def note_keeper(its, first):
        nonlocal keeper_alive, keeper_index
        idx = next((i for i, it in enumerate(its) if it[0] == "keeper"), None)
        if first:
            keeper_alive, keeper_index = idx is not None, idx
        elif keeper_alive and idx != keeper_index:
            keeper_alive = False

    name = put_tree(items)
    lines += [f"render {name}", "flush"]
    note_keeper(items, True)
    for step in range(rng.randint(14, 26)):
        roll = rng.random()
        if roll < 0.5 and buttons(items):
            lines.append(rng.choice(buttons(items)))
        elif roll < 0.62 and keeper_alive:
            lines.append("poke")
        elif roll < 0.76:
            # the same shape, new outside props: the wrapper's class, the Frame titles, the start props
            same = [(k, cid, rng.randint(0, 9) if k != "d" else s) for k, cid, s in items]
            name = put_tree(same, wrapper_class=rng.choice(["k", "wide", "box"]), title=rng.choice(["x", "y", "z"]))
            lines += [f"render {name}", "flush"]
        elif roll < 0.88:
            items = new_items() or [("counter", "a", 0)]
            note_keeper(items, False)
            name = put_tree(items)
            lines += [f"render {name}", "flush"]
        elif lines[-1] != "dump":
            lines.append("dump")
        if rng.random() < 0.3 and lines[-1] != "dump":
            lines.append("dump")
    if lines[-1] != "dump":
        lines.append("dump")
    return lines


def main():
    args = wbcore.parse_args(NN)
    cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, source=SOURCE)

    specs = build_handwritten()
    for k in range(5):
        specs.append(case(f"10-E2E-random-s{args.seed}-{k}", "E2E",
                          f"seeded random session {k} (seed {args.seed}): clicks, pokes, outside re-renders, new shapes",
                          random_session(args.seed, k)))
    outputs = run_oracle_batch([s["lines"] for s in specs])
    for spec, lines in zip(specs, outputs):
        text = "\n".join(lines)
        shown = Counter(m.group(1) for m in (re.fullmatch(r'text \d+ "(.*)"', l) for l in lines) if m)
        for value, times in Counter(spec["must"]).items():
            assert shown[value] >= times, (f"{spec['id']}: the oracle shows the text {value!r} {shown[value]} times, "
                                           f"wanted {times}\n{text}")
        assert any(l.startswith("dump ") for l in lines), f"{spec['id']}: no dump"
        cases.add(spec["id"], spec["req"], spec["title"], spec["lines"], expected=lines)
    cases.save()


if __name__ == "__main__":
    main()
