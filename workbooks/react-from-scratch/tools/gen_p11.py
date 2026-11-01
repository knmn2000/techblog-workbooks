"""Test generator for assignment 11 (useEffect).

    py -P tools/gen_p11.py [--seed N] [--out DIR]

Expected output comes from real React 19 on jsdom (tools/oracle). The orders it prints are pinned in
_source/react-observed.md (section 1); the generator only uses the rows recorded there, and stays out of
the rows that mix a deletion with an update in one commit (M1, M10, M12).

Two independent checks stand between the oracle and the case file:
  * every hand-written case lists the `log` lines that the observed rules give (written here from the
    rules, not read from the oracle) and the generator stops if React prints something else;
  * the scripted and the random sessions are described as operations on a small model of a scene, in
    plain Python, that computes the log lines from the rules; the generator stops if React disagrees.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wbcore  # noqa: E402
from reactgen import rng_for, run_oracle_batch  # noqa: E402

NN = "11"
SOURCE = "React 19.3.1 (react-dom 19.3.1) on jsdom 30.1.3, run by tools/oracle with the harness catalog; orders pinned in _source/react-observed.md"

# `log` has no field names on purpose: a difference is reported as the whole expected and actual line.
COMPARE = "records dump=n node=depth,label,tag,props text=depth,value"

REQUIREMENTS = [
    ("R1", "An effect runs once per mount, and only after the render that created it has been committed"),
    ("R2", "An effect with an empty deps array runs once: re-renders, new props and clicks elsewhere do not run it again"),
    ("R3", "With a deps array the effect runs again only when a dependency changed, and its previous cleanup runs first"),
    ("R4", "An effect without a deps array runs after every render, cleanup first"),
    ("R5", "When a component is removed its cleanup runs, also for components nested in it: a parent's before its children's"),
    ("R6", "On mount, effects run children before parents and siblings in order"),
    ("R7", "In one commit every cleanup runs before any effect"),
    ("R8", "An effect and its cleanup keep the closure of the render that ran them"),
    ("E2E", "Long sessions that mix all of the above"),
]


# ---- hand-written cases: steps with the log lines the observed rules give ----------------------

def render(markup, *logs):
    return ("render", markup, list(logs))


def click(button, *logs):
    return ("click", button, list(logs))


def partial(markup, budget, units, *logs):
    """A first step that only gets `budget` units of work (an idle period) before the log is read and the
    page is dumped: no effect may have run yet and the page is still empty. `units` is the number of fibers of the tree: the container's root, every
    element, every text node and every function component, the catalog's own output included."""
    return ("partial", markup, budget, units, list(logs))


def build_case(cid, req, title, steps, dump=True):
    """Every step ends with `log` and `dump`: the dump is the boundary between two steps, so an effect
    that runs one step late shows up (the log lines alone would still be in the same order)."""
    lines, oracle, expected, prefix = [], [], [], []
    for step in steps:
        if step[0] == "partial":
            _, markup, budget, units, logs = step
            assert not lines, "a partial step has to be the first one"
            assert 3 <= budget < units, f"{cid}: idle {budget} must leave work over ({units} units)"
            lines += [f"tree t {markup}", "render t", f"idle {budget}", "log", "dump", "flush", "log", "dump"]
            oracle += [f"tree t {markup}", "render t", "flush", "log", "dump"]
            prefix = [f"idle {budget}", "dump 1"]  # nothing is on the page yet, and nothing was logged
            expected += logs
        elif step[0] == "render":
            lines += [f"tree t {step[1]}", "render t", "flush", "log", "dump"]
            oracle += [f"tree t {step[1]}", "render t", "flush", "log", "dump"]
            expected += step[2]
        elif step[0] == "log":
            lines += ["log", "dump"]
            oracle += ["log", "dump"]
        else:
            lines += [f"click #{step[1]}", "log", "dump"]
            oracle += [f"click #{step[1]}", "log", "dump"]
            expected += step[2]
    return {"id": cid, "req": req, "title": title, "lines": lines, "oracle": oracle, "prefix": prefix, "flat": expected}


def handwritten():
    c = []
    add = lambda *a, **k: c.append(build_case(*a, **k))

    # R1: mount
    add("11-R1-nothing-runs-before-the-commit", "R1", "two Loggers in a div: after 4 units of work no effect has run, after the flush both have",
        [partial("<div><Logger name=a/><Logger name=b/></div>", 4, 8, "mount a", "mount b")])
    add("11-R1-nothing-runs-before-the-commit-outer", "R1", "an Outer: after 5 of its 6 units no effect has run",
        [partial("<Outer name=o/>", 5, 6, "mount o.inner", "mount o")])
    add("11-R1-logger-mounts", "R1", "one Logger: its effect runs once the page is built",
        [render("<Logger name=a/>", "mount a")])
    add("11-R1-deps-effect-mounts", "R1", "a LoggerDeps with dep=1 runs on mount",
        [render("<LoggerDeps name=x dep=1/>", "run x 1")])
    add("11-R1-every-render-effect-mounts", "R1", "a LoggerEvery runs on mount",
        [render("<LoggerEvery name=e/>", "run e")])
    add("11-R1-inside-a-div-and-nothing-after", "R1", "a Logger in a div; a second log command prints nothing",
        [render("<div><Logger name=a/></div>", "mount a"), ("log", None, [])])

    # R2: [] runs once
    add("11-R2-same-tree-again", "R2", "the same Logger tree rendered three times",
        [render("<Logger name=a/>", "mount a"), render("<Logger name=a/>"), render("<Logger name=a/>")])
    add("11-R2-new-name-ignored", "R2", "a Logger rendered again, then with a new name: nothing runs",
        [render("<Logger name=a/>", "mount a"), render("<Logger name=a/>"), render("<Logger name=q/>")])
    add("11-R2-parent-class-changes", "R2", "the div around a Logger gets a class",
        [render("<div><Logger name=a/></div>", "mount a"), render("<div className=k><Logger name=a/></div>")])
    add("11-R2-a-neighbour-is-clicked", "R2", "a Logger beside a Counter that is clicked twice",
        [render("<div><Logger name=a/><Counter/></div>", "mount a"), click("c-inc"), click("c-inc")])
    add("11-R2-frame-title-changes", "R2", "the Frame around a Logger gets a new title",
        [render("<Frame title=A><Logger name=x/></Frame>", "mount x"), render("<Frame title=B><Logger name=x/></Frame>")])

    # R3: deps
    add("11-R3-dep-changes", "R3", "dep 1 then 2: cleanup of the first run, then the second run",
        [render("<LoggerDeps name=x dep=1/>", "run x 1"), render("<LoggerDeps name=x dep=2/>", "clean x 1", "run x 2")])
    add("11-R3-dep-same-twice", "R3", "dep=1 rendered three times",
        [render("<LoggerDeps name=x dep=1/>", "run x 1"), render("<LoggerDeps name=x dep=1/>"),
         render("<LoggerDeps name=x dep=1/>")])
    add("11-R3-dep-back-and-forth", "R3", "dep 1, 2, 2, 1",
        [render("<LoggerDeps name=x dep=1/>", "run x 1"), render("<LoggerDeps name=x dep=2/>", "clean x 1", "run x 2"),
         render("<LoggerDeps name=x dep=2/>"), render("<LoggerDeps name=x dep=1/>", "clean x 2", "run x 1")])
    add("11-R3-only-one-sibling-changes", "R3", "two siblings, only the second gets a new dep",
        [render("<div><LoggerDeps name=a dep=1/><LoggerDeps name=b dep=1/></div>", "run a 1", "run b 1"),
         render("<div><LoggerDeps name=a dep=1/><LoggerDeps name=b dep=2/></div>", "clean b 1", "run b 2")])
    add("11-R3-props-change-same-dep", "R3", "a new name with the same dep runs nothing",
        [render("<LoggerDeps name=a dep=1/>", "run a 1"), render("<LoggerDeps name=b dep=1/>")])

    # R4: no deps array
    add("11-R4-click-twice", "R4", "a LoggerEvery clicked twice",
        [render("<LoggerEvery name=e/>", "run e"), click("e-btn", "clean e", "run e"), click("e-btn", "clean e", "run e")])
    add("11-R4-render-again", "R4", "a LoggerEvery clicked, then the same tree rendered again",
        [render("<LoggerEvery name=e/>", "run e"), click("e-btn", "clean e", "run e"),
         render("<LoggerEvery name=e/>", "clean e", "run e")])
    add("11-R4-parent-changes-then-click", "R4", "the div around a LoggerEvery gets a class, then a click",
        [render("<div><LoggerEvery name=e/></div>", "run e"), render("<div className=k><LoggerEvery name=e/></div>", "clean e", "run e"),
         click("e-btn", "clean e", "run e")])
    add("11-R4-beside-a-deps-effect", "R4", "a LoggerEvery beside a LoggerDeps: the click reruns only the first",
        [render("<div><LoggerEvery name=e/><LoggerDeps name=d dep=1/></div>", "run e", "run d 1"),
         click("e-btn", "clean e", "run e")])

    # R5: unmount
    add("11-R5-two-loggers-removed", "R5", "two Loggers in a div, replaced by a p",
        [render("<div><Logger name=a/><Logger name=b/></div>", "mount a", "mount b"), render("<p>x</p>", "cleanup a", "cleanup b")])
    add("11-R5-outer-removed", "R5", "an Outer replaced by a p: its cleanup, then its Logger's",
        [render("<Outer name=o/>", "mount o.inner", "mount o"), render("<p>x</p>", "cleanup o", "cleanup o.inner")])
    add("11-R5-outer-and-logger-removed", "R5", "an Outer and a Logger side by side, replaced by a p",
        [render("<div><Outer name=o/><Logger name=l/></div>", "mount o.inner", "mount o", "mount l"),
         render("<p>x</p>", "cleanup o", "cleanup o.inner", "cleanup l")])
    add("11-R5-removed-after-clicks", "R5", "a LoggerEvery clicked once and a LoggerDeps, then everything removed",
        [render("<div><LoggerEvery name=e/><LoggerDeps name=d dep=1/></div>", "run e", "run d 1"),
         click("e-btn", "clean e", "run e"), render("<p>gone</p>", "clean e", "clean d 1")])
    add("11-R5-second-logger-removed", "R5", "the second of two Loggers disappears, the first stays",
        [render("<div><Logger name=a/><Logger name=b/></div>", "mount a", "mount b"), render("<div><Logger name=a/></div>", "cleanup b")])
    add("11-R5-second-deps-removed", "R5", "the second of two LoggerDeps disappears",
        [render("<div><LoggerDeps name=a dep=1/><LoggerDeps name=b dep=1/></div>", "run a 1", "run b 1"),
         render("<div><LoggerDeps name=b dep=1/></div>", "clean b 1")])

    # R6: mount order
    add("11-R6-outer-inner-first", "R6", "an Outer: its Logger mounts before it does",
        [render("<Outer name=o/>", "mount o.inner", "mount o")])
    add("11-R6-siblings-in-order", "R6", "two Loggers side by side",
        [render("<div><Logger name=a/><Logger name=b/></div>", "mount a", "mount b")])
    add("11-R6-outer-then-logger", "R6", "an Outer followed by a Logger",
        [render("<div><Outer name=o/><Logger name=l/></div>", "mount o.inner", "mount o", "mount l")])
    add("11-R6-two-outers-in-a-frame", "R6", "two Outers inside a Frame",
        [render("<Frame title=T><Outer name=o/><Outer name=p/></Frame>", "mount o.inner", "mount o", "mount p.inner", "mount p")])

    # R7: cleanups before effects
    add("11-R7-both-siblings-change", "R7", "two siblings change dep together, then only the second changes again",
        [render("<div><LoggerDeps name=a dep=1/><LoggerDeps name=b dep=1/></div>", "run a 1", "run b 1"),
         render("<div><LoggerDeps name=a dep=2/><LoggerDeps name=b dep=2/></div>", "clean a 1", "clean b 1", "run a 2", "run b 2"),
         render("<div><LoggerDeps name=a dep=2/><LoggerDeps name=b dep=3/></div>", "clean b 2", "run b 3")])
    add("11-R7-positions-swapped", "R7", "two LoggerDeps trade places",
        [render("<div><LoggerDeps name=a dep=1/><LoggerDeps name=b dep=2/></div>", "run a 1", "run b 2"),
         render("<div><LoggerDeps name=b dep=2/><LoggerDeps name=a dep=1/></div>", "clean a 1", "clean b 2", "run b 2", "run a 1")])
    add("11-R7-subtree-replaced", "R7", "a div with a Logger becomes a section with another Logger",
        [render("<div><Logger name=a/></div>", "mount a"), render("<section><Logger name=b/></section>", "cleanup a", "mount b")])
    add("11-R7-outer-becomes-logger", "R7", "an Outer at the root becomes a Logger",
        [render("<Outer name=o/>", "mount o.inner", "mount o"), render("<Logger name=l/>", "cleanup o", "cleanup o.inner", "mount l")])
    add("11-R7-root-component-swapped", "R7", "a Logger at the root becomes a LoggerDeps",
        [render("<Logger name=a/>", "mount a"), render("<LoggerDeps name=b dep=1/>", "cleanup a", "run b 1")])
    add("11-R7-two-gone-one-new", "R7", "two components removed with their div, one new one in a section",
        [render("<div><Logger name=x/><LoggerDeps name=a dep=1/></div>", "mount x", "run a 1"),
         render("<section><LoggerDeps name=b dep=1/></section>", "cleanup x", "clean a 1", "run b 1")])
    add("11-R7-key-changes", "R7", "a Logger whose key changes",
        [render('<div><Logger key=a name=a/></div>', "mount a"), render('<div><Logger key=b name=b/></div>', "cleanup a", "mount b")])

    # R8: closures
    add("11-R8-cleanup-after-props-change", "R8", "new name with the same dep, then removal: the cleanup logs the first name",
        [render("<LoggerDeps name=a dep=1/>", "run a 1"), render("<LoggerDeps name=b dep=1/>"),
         render("<p>x</p>", "clean a 1")])
    add("11-R8-reused-position-keeps-name", "R8", "the first of two LoggerDeps goes, the second moves up and keeps the first one's closure",
        [render("<div><LoggerDeps name=a dep=1/><LoggerDeps name=b dep=1/></div>", "run a 1", "run b 1"),
         render("<div><LoggerDeps name=b dep=1/></div>", "clean b 1")])
    add("11-R8-outer-keeps-first-name", "R8", "an Outer renamed twice and then removed: the cleanups use the first name",
        [render("<Outer name=o/>", "mount o.inner", "mount o"), render("<Outer name=o/>"), render("<Outer name=q/>"),
         render("<p>x</p>", "cleanup o", "cleanup o.inner")])
    add("11-R8-run-uses-new-closure", "R8", "dep 1 to 2 to 3 with a new name each time: each run logs the name of its own render",
        [render("<LoggerDeps name=a dep=1/>", "run a 1"), render("<LoggerDeps name=b dep=2/>", "clean a 1", "run b 2"),
         render("<LoggerDeps name=c dep=3/>", "clean b 2", "run c 3")])
    return c


# ---- the model: a scene of effect components, and the log lines the rules give -------------------

class Item:
    """One component under the scene's root: L Logger, D LoggerDeps, O Outer, E LoggerEvery."""

    def __init__(self, kind, name, dep=None):
        self.kind, self.name, self.dep = kind, name, dep
        self.ran_name, self.ran_dep = name, dep  # the closure of the effect run that is live

    def markup(self):
        return {"L": f"<Logger name={self.name}/>", "D": f"<LoggerDeps name={self.name} dep={self.dep}/>",
                "O": f"<Outer name={self.name}/>", "E": f"<LoggerEvery name={self.name}/>"}[self.kind]

    def mount_logs(self):
        return {"L": [f"mount {self.name}"], "D": [f"run {self.name} {self.dep}"],
                "O": [f"mount {self.name}.inner", f"mount {self.name}"], "E": [f"run {self.name}"]}[self.kind]

    def unmount_logs(self):
        n = self.ran_name
        return {"L": [f"cleanup {n}"], "D": [f"clean {n} {self.ran_dep}"],
                "O": [f"cleanup {n}", f"cleanup {n}.inner"], "E": [f"clean {n}"]}[self.kind]

    def due(self, previous):
        """Does this render's effect run, given the item at the same position before?"""
        if self.kind == "E":
            return True
        return self.kind == "D" and self.dep != previous.ran_dep

    def copy_closure(self, previous):
        self.ran_name, self.ran_dep = previous.ran_name, previous.ran_dep


class Scene:
    def __init__(self):
        self.tag, self.items = "p", []
        self.lines, self.steps, self.n = [], [], 0

    def tree(self, tag, items, cls=""):
        self.n += 1
        attr = f" className={cls}" if cls else ""
        self.lines += [f"tree s{self.n} <{tag}{attr}>{''.join(i.markup() for i in items)}</{tag}>", f"render s{self.n}", "flush"]

    def finish_step(self, logs):
        self.lines += ["log", "dump"]
        self.steps.append(logs)

    # whole tree replaced (the root tag changes) or first mount
    def replace(self, tag, items):
        assert tag != self.tag
        logs = [l for item in self.items for l in item.unmount_logs()]
        logs += [l for item in items for l in item.mount_logs()]
        self.tree(tag, items)
        self.tag, self.items = tag, items
        self.finish_step(logs)

    def unmount(self):
        logs = [l for item in self.items for l in item.unmount_logs()]
        self.lines += ["tree s0 <p>x</p>", "render s0", "flush"]
        self.tag, self.items = "p", []
        self.finish_step(logs)

    # same shapes, new props
    def rerender(self, items, cls=""):
        assert [i.kind for i in items] == [i.kind for i in self.items]
        due = [(new, old) for new, old in zip(items, self.items) if new.due(old)]
        logs = [f"clean {old.ran_name} {old.ran_dep}" if old.kind == "D" else f"clean {old.ran_name}" for new, old in due]
        logs += [(f"run {new.name} {new.dep}" if new.kind == "D" else f"run {new.name}") for new, old in due]
        for new, old in zip(items, self.items):
            new.copy_closure(old)
        for new, _ in due:
            new.ran_name, new.ran_dep = new.name, new.dep
        self.tree(self.tag, items, cls)
        self.items = items
        self.finish_step(logs)

    def click(self):
        (e,) = [i for i in self.items if i.kind == "E"]
        self.lines.append(f"click #{e.name}-btn")
        self.finish_step([f"clean {e.ran_name}", f"run {e.name}"])

    def removable(self, keep):
        """Trailing items can be removed or added when no surviving item has an effect that is due."""
        return all(i.kind != "E" for i in self.items[:keep])

    def resize(self, items):
        """Same leading items, a different number of trailing ones (no survivor's effect is due)."""
        keep = min(len(items), len(self.items))
        assert self.removable(keep)
        assert all(a.kind == b.kind and a.name == b.name and a.dep == b.dep for a, b in zip(items, self.items))
        logs = [l for item in self.items[keep:] for l in item.unmount_logs()]
        logs += [l for item in items[keep:] for l in item.mount_logs()]
        for new, old in zip(items, self.items):
            new.copy_closure(old)
        self.tree(self.tag, items)
        self.items = items
        self.finish_step(logs)


def item(kind, name, dep=None):
    return Item(kind, name, dep)


def scripted_one():
    s = Scene()
    s.replace("div", [item("E", "e"), item("D", "x", 1), item("O", "o"), item("L", "l")])
    s.click()
    s.rerender([item("E", "e"), item("D", "x", 2), item("O", "o"), item("L", "l")])
    s.rerender([item("E", "e"), item("D", "x", 2), item("O", "o"), item("L", "l")], cls="same")
    s.click()
    s.rerender([item("E", "e"), item("D", "y", 2), item("O", "p"), item("L", "m")], cls="renamed")
    s.rerender([item("E", "e"), item("D", "y", 3), item("O", "p"), item("L", "m")])
    s.replace("section", [item("D", "z", 7), item("O", "q"), item("E", "f")])
    s.rerender([item("D", "z", 8), item("O", "q"), item("E", "f")])
    s.click()
    s.unmount()
    s.replace("div", [item("L", "a"), item("L", "b")])
    s.resize([item("L", "a"), item("L", "b"), item("D", "c", 1), item("O", "d")])
    s.resize([item("L", "a"), item("L", "b"), item("D", "c", 1)])
    s.rerender([item("L", "a"), item("L", "b"), item("D", "c", 2)])
    s.unmount()
    return s


def scripted_two():
    s = Scene()
    s.replace("section", [item("D", "a", 1), item("D", "b", 1), item("D", "c", 1)])
    s.rerender([item("D", "a", 2), item("D", "b", 1), item("D", "c", 2)])
    s.rerender([item("D", "b", 2), item("D", "a", 2), item("D", "c", 2)])
    s.rerender([item("D", "a", 1), item("D", "b", 1), item("D", "c", 1)])
    s.resize([item("D", "a", 1), item("D", "b", 1)])
    s.replace("div", [item("O", "o"), item("E", "e"), item("D", "d", 4)])
    s.click()
    s.click()
    s.rerender([item("O", "o"), item("E", "e"), item("D", "d", 5)])
    s.unmount()
    s.replace("section", [item("O", "r"), item("O", "s")])
    s.resize([item("O", "r"), item("O", "s"), item("L", "t")])
    s.resize([item("O", "r")])
    s.unmount()
    return s


NAMES = ["a", "b", "c", "d", "g", "k", "m", "n", "r", "s", "t", "u", "w", "x", "y", "z"]


def random_scene(seed, index):
    rng = rng_for(seed, f"p11-session-{index}")
    s = Scene()
    pool = list(NAMES)

    def fresh_items(count):
        out, have_e = [], False
        for _ in range(count):
            kind = rng.choice("LLDDDOE")
            if kind == "E" and have_e:
                kind = "D"
            have_e = have_e or kind == "E"
            name = rng.choice(pool)
            out.append(item(kind, name, rng.randint(1, 3) if kind == "D" else None))
        return out

    def next_props(items):
        out = []
        for it in items:
            name = it.name if it.kind == "E" else rng.choice(pool)
            dep = rng.randint(1, 3) if it.kind == "D" else None
            out.append(item(it.kind, name, dep))
        return out

    def copies(items):
        return [item(i.kind, i.name, i.dep) for i in items]

    def grown(count):
        return [i for i in fresh_items(count) if i.kind != "E"]

    s.replace(rng.choice(["div", "section"]), fresh_items(rng.randint(2, 5)))
    for _ in range(rng.randint(10, 18)):
        roll = rng.random()
        has_e = any(i.kind == "E" for i in s.items)
        if not s.items:
            if s.tag == "p":
                s.replace("div", fresh_items(rng.randint(2, 5)))
            else:
                s.resize(grown(rng.randint(1, 3)))
        elif roll < 0.25 and has_e:
            s.click()
        elif roll < 0.55:
            s.rerender(next_props(s.items), cls=rng.choice(["", "k", "wide"]))
        elif roll < 0.62:
            s.rerender(copies(s.items))
        elif roll < 0.74:
            s.replace("section" if s.tag == "div" else "div", fresh_items(rng.randint(1, 5)))
        elif roll < 0.82:
            s.unmount()
        elif roll < 0.91 and len(s.items) > 0 and s.removable(len(s.items) - 1):
            keep = rng.randint(0, len(s.items) - 1)
            if s.removable(keep):
                s.resize(copies(s.items[:keep]))
            else:
                s.rerender(next_props(s.items))
        elif s.removable(len(s.items)):
            s.resize(copies(s.items) + grown(rng.randint(1, 2)))
        elif has_e:
            s.click()
        else:
            s.rerender(next_props(s.items))
    if s.items:
        s.unmount()
    return s


def split_steps(lines):
    """The oracle's lines grouped by step: each step ends with a `dump`, and its log lines come first."""
    groups, current = [], []
    for l in lines:
        if l.startswith("log "):
            current.append(l[4:])
        elif l.startswith("dump "):
            groups.append(current)
            current = []
    return groups


def main():
    args = wbcore.parse_args(NN)
    cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, source=SOURCE)

    hand = handwritten()
    specs = []
    for h in hand:
        specs.append({"id": h["id"], "req": h["req"], "title": h["title"], "lines": h["lines"], "flat": h["flat"], "model": None,
                      "oracle": h["oracle"], "prefix": h["prefix"]})
    for cid, title, scene in (("11-E2E-everything-in-turn", "five kinds of step on four components, then a regrown list", scripted_one()),
                              ("11-E2E-swaps-and-nesting", "dep swaps over three siblings, then Outers growing and shrinking", scripted_two())):
        specs.append({"id": cid, "req": "E2E", "title": title, "lines": scene.lines, "flat": None, "model": scene.steps})
    for k in range(5):
        scene = random_scene(args.seed, k)
        specs.append({"id": f"11-E2E-random-s{args.seed}-{k}", "req": "E2E",
                      "title": f"seeded random session {k} (seed {args.seed}): props, clicks, regrowth, replacement, removal",
                      "lines": scene.lines, "flat": None, "model": scene.steps})

    outputs = run_oracle_batch([s.get("oracle", s["lines"]) for s in specs])
    for spec, lines in zip(specs, outputs):
        logs = [l[4:] for l in lines if l.startswith("log ")]
        later = [re.sub(r"^dump (\d+)$", lambda m: f"dump {int(m[1]) + 1}", l) for l in lines] if spec.get("prefix") else lines
        expected = spec.get("prefix", []) + later
        if spec["flat"] is not None:
            assert logs == spec["flat"], f"{spec['id']}: the rules give {spec['flat']}, React printed {logs}"
        else:
            assert split_steps(lines) == spec["model"], (
                f"{spec['id']}: the model gives {spec['model']}, React printed {split_steps(lines)}")
        cases.add(spec["id"], spec["req"], spec["title"], spec["lines"], expected=expected)
    cases.save()


if __name__ == "__main__":
    main()
