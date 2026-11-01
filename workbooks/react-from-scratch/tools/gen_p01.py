"""Test cases for assignment 01 (create elements).

The expected lines come from an independent model written here with plain dicts and loops (nothing
borrowed from the reference solution). Every case whose shapes coincide with React's is also run
through React.createElement (tools/oracle's react package): the type, the props and the children
must agree with the model, and the model's text must equal what the harness's stableJson prints.

    py -P tools/gen_p01.py                                  # tests/01 (seed 1)
    py -P tools/gen_p01.py --seed 777 --out build/fresh/01  # what `.\\check 01 -Fresh` runs
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reactgen  # noqa: E402
import wbcore  # noqa: E402

ROOT = wbcore.ROOT
ORACLE = ROOT / "tools" / "oracle"
REACT_VERSION = json.loads((ORACLE / "node_modules" / "react" / "package.json").read_text(encoding="utf-8"))["version"]
SOURCE = f"independent dict model in tools/gen_p01.py, cross-checked with React {REACT_VERSION} createElement"

REQUIREMENTS = [
    ("R1", "An element is an object with exactly `type` and `props`; `type` is the first argument and `props` holds every given prop"),
    ("R2", "`props.children` is always an array of the children in order: empty for none, one entry for one child"),
    ("R3", "A string or number child becomes a text element with `nodeValue` as given (a number stays a number)"),
    ("R4", "An element given as a child is placed in `children` unchanged, at its position"),
    ("R5", "Props of `null` behave like an empty object"),
    ("R6", "The props object you were given is never modified"),
    ("R7", "`key` is an ordinary prop and stays in `props`"),
    ("E2E", "Whole trees built from several calls"),
]

EXPLAIN = "_lines=R1"
COMPARE = "records element=n,json props=name,json"


# ---- stableJson, as the harness prints it ---------------------------------------------------

def js_string(text):
    out = json.dumps(text, ensure_ascii=True)
    return out.replace("\x7f", "\\u007f").replace(" ", "\\u0020")


def js_number(value):
    if isinstance(value, float) and value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return repr(value)


def sjson(value):
    """Compact JSON, sorted keys, spaces in strings as \\u0020, non-ASCII as \\u escapes."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return js_number(value)
    if isinstance(value, str):
        return js_string(value)
    if isinstance(value, list):
        return "[" + ",".join(sjson(v) for v in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(js_string(k) + ":" + sjson(value[k]) for k in sorted(value)) + "}"
    raise TypeError(value)


# ---- case specs -----------------------------------------------------------------------------
# A case is a list of steps:
#   ("props", name, obj)                        defines a props object
#   ("call", type, props, children)             props: None, a dict or ("@", name); a child is a str,
#                                               a number or ("$", k) (the result of the k-th call)
#   ("show", name)

def ref(k):
    return ("$", k)


def named(name):
    return ("@", name)


def scenario_lines(steps):
    lines = []
    for step in steps:
        if step[0] == "props":
            lines.append(f"props {step[1]} {json.dumps(step[2], separators=(',', ':'))}")
        elif step[0] == "show":
            lines.append(f"show {step[1]}")
        else:
            _, type_, props, children = step
            if props is None:
                props_text = "null"
            elif isinstance(props, tuple):
                props_text = "@" + props[1]
            else:
                props_text = json.dumps(props, separators=(",", ":"))
            kids = []
            for child in children:
                kids.append(f"${child[1]}" if isinstance(child, tuple) else json.dumps(child))
            lines.append(" ".join(["call", type_, props_text, *kids]))
    return lines


def model(steps):
    """What a correct createElement prints, worked out with plain dicts."""
    defined, elements, out = {}, [], []
    for step in steps:
        if step[0] == "props":
            defined[step[1]] = step[2]
        elif step[0] == "show":
            out.append(f"props {step[1]} {sjson(defined[step[1]])}")
        else:
            _, type_, props, children = step
            given = defined[props[1]] if isinstance(props, tuple) else (props or {})
            result_props = {}
            for name in given:
                result_props[name] = given[name]
            kids = []
            for child in children:
                if isinstance(child, tuple):
                    kids.append(elements[child[1] - 1])
                else:
                    kids.append({"type": "TEXT_ELEMENT", "props": {"nodeValue": child, "children": []}})
            result_props["children"] = kids
            element = {"type": type_, "props": result_props}
            elements.append(element)
            out.append(f"element {len(elements)} {sjson(element)}")
    return out


# ---- the React cross-check ------------------------------------------------------------------

NODE_CHECK = r"""
import { pathToFileURL } from "node:url";
const { stableJson } = await import(pathToFileURL(process.argv[1]).href);
const React = (await import("react")).default;
const chunks = [];
for await (const c of process.stdin) chunks.push(c);
const jobs = JSON.parse(Buffer.concat(chunks).toString("utf8"));

// React keeps primitives as they are and `key` outside props: put them back into the plain shape.
function plain(node) {
  if (typeof node === "string" || typeof node === "number") {
    return { type: "TEXT_ELEMENT", props: { nodeValue: node, children: [] } };
  }
  const { children, ...rest } = node.props;
  const list = children === undefined ? [] : Array.isArray(children) ? children : [children];
  const props = { ...rest };
  if (node.key !== null) props.key = node.key;
  props.children = list.map(plain);
  return { type: node.type, props };
}

const results = [];
for (const steps of jobs) {
  const defined = new Map(), made = [], lines = [];
  for (const step of steps) {
    if (step[0] === "props") defined.set(step[1], step[2]);
    else if (step[0] === "show") lines.push(`props ${step[1]} ${stableJson(defined.get(step[1]))}`);
    else {
      const [, type, props, children] = step;
      const given = props !== null && typeof props === "object" && "$props" in props ? defined.get(props.$props) : props;
      const kids = children.map((c) => (c !== null && typeof c === "object" ? made[c.$ref - 1] : c));
      made.push(React.createElement(type, given, ...kids));
      lines.push(`element ${made.length} ${stableJson(plain(made[made.length - 1]))}`);
    }
  }
  results.push(lines);
}
process.stdout.write(JSON.stringify(results));
"""


def react_lines(case_steps):
    node = shutil.which("node")
    if not node:
        sys.exit("node is not on PATH (the cross-check needs Node.js 26 or newer)")
    jobs = []
    for steps in case_steps:
        job = []
        for step in steps:
            if step[0] == "call":
                _, type_, props, children = step
                if isinstance(props, tuple):
                    props = {"$props": props[1]}
                children = [{"$ref": c[1]} if isinstance(c, tuple) else c for c in children]
                job.append(["call", type_, props, children])
            else:
                job.append(list(step))
        jobs.append(job)
    proc = subprocess.run([node, "--input-type=module", "-e", NODE_CHECK, str(ROOT / "harness" / "scenario.js")],
                          input=json.dumps(jobs), capture_output=True, text=True, encoding="utf-8", cwd=ORACLE)
    if proc.returncode != 0:
        sys.exit(f"the React cross-check failed:\n{proc.stderr.strip()}")
    return json.loads(proc.stdout)


# ---- the cases ------------------------------------------------------------------------------

def call(type_, props=None, *children):
    return ("call", type_, props, list(children))


HAND = []  # (id, requirement, title, steps, crosscheck)


def hand(case_id, req, title, steps, crosscheck=True):
    HAND.append((case_id, req, title, steps, crosscheck))


# R1: shape
hand("01-R1-bare-div", "R1", "div with null props and no children", [call("div")])
hand("01-R1-two-props", "R1", "div with id and className", [call("div", {"id": "main", "className": "wide"})])
hand("01-R1-types", "R1", "five different types, the type string is kept as given",
     [call("h1"), call("span"), call("my-widget"), call("Panel"), call("input", {"disabled": True})])
hand("01-R1-value-kinds", "R1", "prop values of every JSON kind pass through untouched",
     [call("div", {"count": 3, "ratio": 0.5, "on": True, "off": False, "none": None, "text": "a b",
                   "obj": {"a": [1, 2, {"b": None}], "c": "d"}, "list": [1, "two", [3]]})])
hand("01-R1-many-props", "R1", "ten props, sorted by name in the output",
     [call("section", {"id": "s", "className": "c", "title": "t", "role": "main", "lang": "en", "dir": "ltr",
                       "tabIndex": 0, "key": "m", "draggable": True, "slot": "x"})])

# R2: children array
hand("01-R2-none", "R2", "no children gives an empty array", [call("div", {"id": "a"}), call("p")])
hand("01-R2-one-text", "R2", "one child is still an array of one", [call("h1", None, "Title")])
hand("01-R2-one-element", "R2", "one element child is still an array of one",
     [call("b", None, "x"), call("p", None, ref(1))])
hand("01-R2-three", "R2", "three text children keep their order", [call("p", None, "a", "b", "c")])
hand("01-R2-order-mixed", "R2", "children in order, texts and elements mixed",
     [call("i", None, "one"), call("em", None, "two"), call("div", None, "before", ref(1), "between", ref(2), "after")])
hand("01-R2-children-key", "R2", "a children key in the given props is replaced by the children array",
     [call("div", {"children": "junk"}, "x"), call("div", {"children": ["a", "b"]}),
      call("div", {"children": 5, "id": "k"}, "p", "q")], crosscheck=False)

# R3: text
hand("01-R3-string", "R3", "one string child", [call("span", None, "hello world")])
hand("01-R3-number", "R3", "a number child keeps its number type", [call("span", None, 42), call("span", None, 3.5)])
hand("01-R3-zero-empty", "R3", "0 and the empty string are children too",
     [call("span", None, 0), call("span", None, ""), call("span", None, "", 0, "")])
hand("01-R3-numeric-string", "R3", "the string \"42\" stays a string, the number 42 stays a number",
     [call("p", None, "42", 42, "4.0", 4.0, "-7", -7)])
hand("01-R3-spaces-unicode", "R3", "text with spaces, quotes, a backslash and non-ASCII characters",
     [call("p", None, "  leading and trailing  ", "say \"hi\"", "back\\slash", "caf\u00e9 \u2603", "tab\there")])
hand("01-R3-mixed-order", "R3", "strings and numbers interleaved keep their order",
     [call("p", None, "a", 1, "b", 2, 3, "c")])
hand("01-R3-text-shape", "R3", "a text element has type TEXT_ELEMENT, nodeValue and an empty children array",
     [call("li", {"id": "t"}, "x")])
hand("01-R3-negative-float", "R3", "negative and fractional numbers",
     [call("td", None, -1, 0.25, -0.5, 1000000)])

# R4: nested elements
hand("01-R4-one-level", "R4", "an element inside an element",
     [call("span", None, "x"), call("div", None, ref(1))])
hand("01-R4-interleaved", "R4", "text, element, text",
     [call("b", None, "bold"), call("p", None, "a ", ref(1), " b")])
hand("01-R4-three-levels", "R4", "four calls, each the child of the next",
     [call("i", None, "deep"), call("em", {"id": "e"}, ref(1)), call("span", None, ref(2)), call("div", None, ref(3))])
hand("01-R4-siblings", "R4", "three element children in order, each with its own text",
     [call("li", None, "one"), call("li", None, "two"), call("li", None, "three"),
      call("ul", {"id": "list"}, ref(1), ref(2), ref(3))])
hand("01-R4-same-twice", "R4", "the same element used as two children",
     [call("br"), call("p", None, ref(1), "x", ref(1))])

# R5: null props
hand("01-R5-null-no-children", "R5", "null props, no children", [call("div", None)])
hand("01-R5-null-text", "R5", "null props with a text child", [call("p", None, "text")])
hand("01-R5-null-elements", "R5", "null props with two element children",
     [call("i"), call("b", None, "x"), call("p", None, ref(1), ref(2))])
hand("01-R5-empty-object", "R5", "an empty props object and null give the same element",
     [call("p", {}, "x"), call("p", None, "x"), call("div", {})])

# R6: props are not modified
hand("01-R6-show-after-call", "R6", "a props object after one call",
     [("props", "a", {"id": "x"}), call("div", named("a"), "t"), ("show", "a")])
hand("01-R6-reuse", "R6", "one props object used for two elements with different children",
     [("props", "p", {"className": "box", "title": "t"}), call("div", named("p"), "one"),
      call("div", named("p"), "two", "three"), call("div", named("p")), ("show", "p")])
hand("01-R6-children-key", "R6", "a props object that has a children key stays as it was",
     [("props", "q", {"children": ["old"], "id": "z"}), call("div", named("q"), "new"), ("show", "q")], crosscheck=False)
hand("01-R6-key-stays", "R6", "a props object with a key is not stripped of it",
     [("props", "k", {"key": "item-1", "id": "x"}), call("li", named("k"), "a"), call("li", named("k"), "b"),
      ("show", "k")])
hand("01-R6-nested-values", "R6", "nested prop values are not touched either",
     [("props", "n", {"data": {"x": 1, "y": [1, 2]}, "list": [3, 4]}), call("div", named("n"), "t"),
      ("show", "n")])

# R7: key
hand("01-R7-key", "R7", "key is a prop", [call("li", {"key": "a"}, "x")])
hand("01-R7-key-and-props", "R7", "key next to other props and children",
     [call("li", {"id": "i", "key": "k-2", "className": "row"}, "one", "two")])
hand("01-R7-key-values", "R7", "keys of different kinds are kept as given (empty string, 0, number)",
     [call("li", {"key": ""}, "a"), call("li", {"key": 0}, "b"), call("li", {"key": 7}, "c")], crosscheck=False)
hand("01-R7-key-on-parent-and-child", "R7", "key on both the parent and its children",
     [call("li", {"key": "x"}, "one"), call("li", {"key": "y"}, "two"),
      call("ul", {"key": "list"}, ref(1), ref(2))])

# E2E
hand("01-E2E-page", "E2E", "a small page: heading, paragraph with a link, list of three",
     [call("h1", {"id": "top"}, "Notes"),
      call("a", {"href": "#more", "title": "more notes"}, "more"),
      call("p", {"className": "lead"}, "See ", ref(2), " for details, section ", 2, "."),
      call("li", {"key": "a"}, "first"), call("li", {"key": "b"}, "second"), call("li", {"key": "c"}, "third"),
      call("ul", None, ref(4), ref(5), ref(6)),
      call("div", {"id": "page"}, ref(1), ref(3), ref(7))])
hand("01-E2E-reused-props", "E2E", "props defined once, used in a chain of calls, shown at the end",
     [("props", "base", {"className": "card", "key": "c"}),
      call("span", named("base"), "x", 1), call("span", named("base"), ref(1)), call("div", named("base"), ref(2), ref(1)),
      ("show", "base")])


# ---- random cases ---------------------------------------------------------------------------

PROP_NAMES = ["id", "className", "title", "key", "data", "hidden", "tabIndex", "role", "lang", "value", "href", "name"]
WORDS = reactgen.WORDS


def rand_value(rng, depth=0):
    kind = rng.randint(0, 7 if depth < 2 else 5)
    if kind == 0:
        return rng.choice(WORDS)
    if kind == 1:
        return rng.choice(WORDS) + " " + rng.choice(WORDS)
    if kind == 2:
        return rng.randint(-50, 5000)
    if kind == 3:
        return rng.choice([0.5, 2.25, -3.75, 100.5])
    if kind == 4:
        return rng.choice([True, False])
    if kind == 5:
        return None
    if kind == 6:
        return [rand_value(rng, depth + 1) for _ in range(rng.randint(0, 3))]
    return {rng.choice(WORDS): rand_value(rng, depth + 1) for _ in range(rng.randint(0, 3))}


def rand_props(rng, simple=False):
    """Random props, or None. `simple` keeps them small (a couple of scalar props) so that the
    cases about children print short lines."""
    if rng.random() < 0.25:
        return None
    props = {}
    for name in rng.sample(PROP_NAMES, rng.randint(0, 2 if simple else 5)):
        if name == "key":
            props[name] = rng.choice(WORDS) + str(rng.randint(1, 9))
        elif simple:
            props[name] = rng.choice([rng.choice(WORDS), rng.randint(0, 99), rng.choice([True, False])])
        else:
            props[name] = rand_value(rng)
    return props


def rand_text(rng):
    kind = rng.randint(0, 5)
    if kind == 0:
        return rng.choice(WORDS)
    if kind == 1:
        return rng.choice(WORDS) + " " + rng.choice(WORDS) + "  " + rng.choice(WORDS)
    if kind == 2:
        return rng.randint(-20, 999)
    if kind == 3:
        return rng.choice([0, 0.5, 12.75, -4.5])
    if kind == 4:
        return rng.choice(["", " ", "42", "a\"b", "50%", "caf\u00e9"])
    return str(rng.randint(0, 99))


TYPES = ["div", "span", "p", "ul", "li", "h1", "button", "section", "my-tag", "Item"]


def random_flat(rng):
    steps = []
    for _ in range(5):
        kids = [rand_text(rng) for _ in range(rng.choice([0, 1, 1, 2, 3, 4, 6]))]
        steps.append(call(rng.choice(TYPES), rand_props(rng, simple=True), *kids))
    return steps


def random_nested(rng):
    steps = []
    for k in range(1, 8):
        kids = [rand_text(rng) for _ in range(rng.choice([0, 1, 2]))]
        if k > 1:  # every call after the first holds at least one earlier element, wherever it lands
            for _ in range(rng.choice([1, 1, 2, 3])):
                kids.insert(rng.randint(0, len(kids)), ref(rng.randint(1, k - 1)))
        steps.append(call(rng.choice(TYPES), rand_props(rng, simple=True), *kids))
    return steps


def random_reuse(rng):
    steps = [("props", "p1", rand_props(rng) or {"id": "p1"}), ("props", "p2", rand_props(rng) or {})]
    made = 0
    for _ in range(6):
        pick = rng.choice(["p1", "p2", None])
        kids = [rand_text(rng) for _ in range(rng.choice([0, 1, 2, 3]))]
        if made and rng.random() < 0.4:
            kids.insert(rng.randint(0, len(kids)), ref(rng.randint(1, made)))
        steps.append(call(rng.choice(TYPES), named(pick) if pick else None, *kids))
        made += 1
        if rng.random() < 0.3:
            steps.append(("show", rng.choice(["p1", "p2"])))
    steps += [("show", "p1"), ("show", "p2")]
    return steps


def main():
    args = wbcore.parse_args("01")
    cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, EXPLAIN, source=SOURCE)

    planned = [(cid, req, title, steps, cross) for cid, req, title, steps, cross in HAND]
    for k in range(1, 4):
        planned.append((f"01-R3-random-s{args.seed}-{k}", "R3", f"random flat elements with random texts, seed {args.seed}",
                        random_flat(reactgen.rng_for(args.seed, f"flat{k}")), True))
    for k in range(1, 4):
        planned.append((f"01-R4-random-s{args.seed}-{k}", "R4", f"random trees of calls that refer to earlier calls, seed {args.seed}",
                        random_nested(reactgen.rng_for(args.seed, f"nest{k}")), True))
    for k in range(1, 4):
        planned.append((f"01-R6-random-s{args.seed}-{k}", "R6", f"random reuse of two props objects, shown during and after, seed {args.seed}",
                        random_reuse(reactgen.rng_for(args.seed, f"reuse{k}")), True))

    crossed = [steps for _, _, _, steps, cross in planned if cross]
    from_react = iter(react_lines(crossed))
    for cid, req, title, steps, cross in planned:
        expected = model(steps)
        if cross:
            theirs = next(from_react)
            if theirs != expected:
                for mine, react in zip(expected, theirs):
                    if mine != react:
                        sys.exit(f"{cid}: the model and React disagree\n  model: {mine}\n  react: {react}")
                sys.exit(f"{cid}: the model and React print a different number of lines")
        cases.add(cid, req, title, scenario_lines(steps), expected=expected)
    cases.save()


if __name__ == "__main__":
    main()
