"""Test cases for assignment 02 (DOM nodes and props).

React has no counterpart for createDom/updateDom, so the expected lines come from a model written
here from the definition: a node is a map of property slots plus a map of listeners keyed by event
type, and an update is set arithmetic over the old and new prop maps. The model never calls or reads
the reference solution.

    py -P tools/gen_p02.py                                  # tests/02 (seed 1)
    py -P tools/gen_p02.py --seed 777 --out build/fresh/02  # what `.\\check 02 -Fresh` runs
"""

import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reactgen  # noqa: E402
import wbcore  # noqa: E402

SOURCE = "definition-level model in tools/gen_p02.py (property slots, listener map keyed by event type, set arithmetic over prop maps)"

REQUIREMENTS = [
    ("R1", "createDom makes an element whose tag is the element's type"),
    ("R2", "`children` and `key` are never assigned to the node, on create or on update"),
    ("R3", "A TEXT_ELEMENT becomes a text node: created empty, then `nodeValue` is written like any prop"),
    ("R4", "Props are assigned as properties of the node, on create and when they are new on update"),
    ("R5", "A prop whose name starts with `on` becomes a listener of the lower-cased rest of the name, and is not also assigned as a property"),
    ("R6", "updateDom writes only the props that are new or have a different value, falsy values included"),
    ("R7", "A prop that is gone from the new props is written as an empty string"),
    ("R8", "A changed handler loses its old listener and gets a new one, an unchanged one is left alone, a removed one is removed"),
    ("R9", "updateDom on a text node writes a changed `nodeValue`, and clears it when it is gone"),
    ("E2E", "Mixed sequences of create, update, click and ops"),
]

COMPARE = "records dump=n node=depth,label,tag,props text=depth,value ops=create,write,addListener,removeListener log=text"
EXPLAIN = "node:tag=R1"

OPS_NAMES = "create write addListener removeListener"


# ---- the model ------------------------------------------------------------------------------

NEVER_WRITTEN = {"children", "key"}


def is_event(name):
    return name.startswith("on")


def event_type(name):
    return name[2:].lower()


def label_for(index):
    name = ""
    n = index + 1
    while n > 0:
        name = chr(97 + (n - 1) % 26) + name
        n = (n - 1) // 26
    return name


def js_quote(text):
    """encodeURIComponent for the ASCII text the cases use."""
    return quote(text, safe="-_.!~*'()")


class ModelNode:
    def __init__(self, tag):
        self.tag = tag  # None for a text node
        self.slots = {"id": "", "className": "", "title": "", "value": "", "disabled": False, "nodeValue": ""}
        self.listeners = {}  # event type -> handler names, in registration order
        self.label = None


class Model:
    def __init__(self):
        self.counts = dict.fromkeys(("create", "write", "addListener", "removeListener"), 0)
        self.node = None
        self.prev = {}
        self.labels = 0
        self.dumps = 0
        self.pending_log = []
        self.out = []

    # the DOM calls the learner's code is allowed to make, as they are counted
    def write(self, name, value):
        self.node.slots[name] = value
        self.counts["write"] += 1

    def add_listener(self, name, handler):
        self.counts["addListener"] += 1
        bucket = self.node.listeners.setdefault(event_type(name), [])
        if handler[1] not in bucket:  # handler is ("@", name); the same name is the same function
            bucket.append(handler[1])

    def remove_listener(self, name, handler):
        self.counts["removeListener"] += 1
        bucket = self.node.listeners.setdefault(event_type(name), [])
        if handler[1] in bucket:
            bucket.remove(handler[1])

    # what createDom and updateDom have to achieve
    def apply(self, old, new):
        old_names, new_names = set(old), set(new)
        gone = old_names - new_names
        fresh = new_names - old_names
        changed = {name for name in old_names & new_names if old[name] != new[name]}
        events_off = sorted(name for name in gone | changed if is_event(name))
        events_on = sorted(name for name in fresh | changed if is_event(name))
        plain_gone = sorted(name for name in gone if not is_event(name) and name not in NEVER_WRITTEN)
        plain_set = sorted(name for name in fresh | changed if not is_event(name) and name not in NEVER_WRITTEN)
        for name in events_off:
            self.remove_listener(name, old[name])
        for name in plain_gone:
            self.write(name, "")
        for name in plain_set:
            self.write(name, new[name])
        for name in events_on:
            self.add_listener(name, new[name])

    # scenario commands
    def create(self, kind, props):
        self.counts["create"] += 1
        if kind == "text":
            self.node = ModelNode(None)
        else:
            self.node = ModelNode(kind)
        self.apply({}, props)
        self.prev = props

    def update(self, props):
        self.apply(self.prev, props)
        self.prev = props

    def click(self, element_id):
        node = self.node
        assert node.tag is not None and node.slots["id"] == element_id, f"model: no clickable node with id {element_id}"
        for handler in list(node.listeners.get("click", [])):
            self.pending_log.append(handler)

    def dump(self):
        self.dumps += 1
        self.out.append(f"dump {self.dumps}")
        node = self.node
        if node.tag is None:
            if node.slots["nodeValue"] != "":
                self.out.append(f'text 0 "{encode_text(str(node.slots["nodeValue"]))}"')
            return
        if node.label is None:
            node.label = label_for(self.labels)
            self.labels += 1
        self.out.append(f'node 0 {node.label} {node.tag} "{describe(node)}"')

    def ops(self):
        names = OPS_NAMES.split()
        self.out.append("ops " + " ".join(str(self.counts[name]) for name in names))
        for name in names:
            self.counts[name] = 0

    def log(self):
        self.out += [f"log {entry}" for entry in self.pending_log]
        self.pending_log = []


def encode_text(text):
    return text.replace("%", "%25").replace('"', "%22").replace("\r", "%0D").replace("\n", "%0A")


def describe(node):
    slots, tag, parts = node.slots, node.tag, []

    def show(name, value):
        if value is True:
            parts.append(f"{name}=true")
        else:
            text = str(value)
            parts.append(f"{name}={js_quote(text) if re.search(chr(34) + r'|%|\s', text) else text}")

    if slots["className"] != "":
        show("className", slots["className"])
    if tag in ("button", "input", "textarea") and slots["disabled"]:
        show("disabled", True)
    if slots["id"] != "":
        show("id", slots["id"])
    if slots["title"] != "":
        show("title", slots["title"])
    if tag in ("input", "textarea") and slots["value"] != "":
        show("value", slots["value"])
    return " ".join(parts)


# ---- scenario steps -------------------------------------------------------------------------

def H(name):
    return ("@", name)


def create(kind, props=None):
    return ("create", kind, props or {})


def update(props=None):
    return ("update", props or {})


def click(element_id):
    return ("click", element_id)


DUMP, OPS, LOG = ("dump",), ("ops",), ("log",)


def attr(name, value):
    if value is True:
        return name
    if isinstance(value, tuple):
        return f"{name}=@{value[1]}"
    if re.fullmatch(r"[A-Za-z0-9_.:%-]+", value):
        return f"{name}={value}"
    return f'{name}="{value}"' if '"' not in value else f"{name}='{value}'"


def scenario_lines(steps):
    lines = []
    for step in steps:
        word = step[0]
        if word == "create":
            lines.append(" ".join(["create", step[1], *[attr(n, v) for n, v in step[2].items()]]))
        elif word == "update":
            lines.append(" ".join(["update", *[attr(n, v) for n, v in step[1].items()]]).rstrip())
        elif word == "click":
            lines.append(f"click #{step[1]}")
        elif word == "ops":
            lines.append("ops " + OPS_NAMES)
        else:
            lines.append(word)
    return lines


def expected_lines(steps):
    model = Model()
    for step in steps:
        word = step[0]
        if word == "create":
            model.create(step[1], step[2])
        elif word == "update":
            model.update(step[1])
        else:
            getattr(model, word)(*step[1:])
    return model.out


# ---- hand-made cases ------------------------------------------------------------------------

HAND = []


def hand(case_id, req, title, steps):
    HAND.append((case_id, req, title, steps))


# R1: element creation (dump only)
hand("02-R1-div", "R1", "one div, dumped", [create("div"), DUMP])
hand("02-R1-tags", "R1", "five tags, each dumped with its own label",
     [create("button"), DUMP, create("input"), DUMP, create("h1"), DUMP, create("section"), DUMP, create("my-widget"), DUMP])
hand("02-R1-labels", "R1", "the same node dumped twice keeps its label, a new node gets the next one",
     [create("span"), DUMP, DUMP, create("span"), DUMP, DUMP])

# R2: children and key are never assigned
hand("02-R2-create-ops", "R2", "creating a bare div writes nothing (children is never assigned)",
     [create("div"), OPS, create("span"), OPS])
hand("02-R2-key-on-create", "R2", "key given at creation is not written",
     [create("li", {"key": "k1"}), OPS, create("li", {"key": "k2", "id": "x"}), OPS])
hand("02-R2-key-on-update", "R2", "key changes on update are not written, the id change next to it is",
     [create("li", {"id": "a", "key": "k1"}), OPS, update({"id": "b", "key": "k2"}), OPS,
      update({"id": "c", "key": "k3"}), OPS])
hand("02-R2-key-removed", "R2", "a key that disappears is not cleared",
     [create("li", {"id": "a", "key": "k"}), OPS, update({"id": "b"}), DUMP, OPS])

# R3: text nodes
hand("02-R3-text", "R3", "a text node: one create, one write, text in the dump",
     [create("text", {"nodeValue": "hello"}), DUMP, OPS])
hand("02-R3-text-spaces", "R3", "text with inner and trailing spaces and a percent sign",
     [create("text", {"nodeValue": "two  spaces, one trailing  and 100%"}), DUMP, OPS])
hand("02-R3-text-quotes", "R3", "text with double quotes",
     [create("text", {"nodeValue": 'say "hi" now'}), DUMP])
hand("02-R3-text-digits", "R3", "text that looks like a number, and text with a leading space",
     [create("text", {"nodeValue": "0"}), DUMP, OPS, create("text", {"nodeValue": " padded "}), DUMP, OPS])

# R4: props are properties
hand("02-R4-id-class-title", "R4", "id, className and a title with a space",
     [create("div", {"id": "a", "className": "big", "title": "hello world"}), DUMP, OPS])
hand("02-R4-input", "R4", "an input with a value that has a space, and disabled",
     [create("input", {"id": "i", "value": "x y", "disabled": True}), DUMP, OPS])
hand("02-R4-unseen-props", "R4", "props the dump does not show are still written, one write each",
     [create("div", {"lang": "en", "hidden": True, "data-role": "main", "tabIndex": "3"}), DUMP, OPS])
hand("02-R4-update-new", "R4", "a prop added by an update, then a changed one next to a new one",
     [create("div"), update({"id": "a"}), DUMP, update({"id": "b", "className": "c"}), DUMP, OPS])
hand("02-R4-encoded", "R4", "class with spaces, title with a percent sign and quotes",
     [create("div", {"className": "a b c", "title": '5% "off"'}), DUMP])

# R5: listeners
hand("02-R5-click", "R5", "onClick becomes a click listener, not a property",
     [create("button", {"id": "b", "onClick": H("one")}), OPS, click("b"), LOG])
hand("02-R5-click-twice", "R5", "two clicks, two calls of the handler",
     [create("button", {"id": "b", "onClick": H("tap")}), click("b"), click("b"), LOG])
hand("02-R5-lowercase-name", "R5", "onclick in lower case is a click listener as well",
     [create("div", {"id": "d", "onclick": H("low")}), click("d"), LOG, OPS])
hand("02-R5-types", "R5", "three handlers for three event types, only the click one runs on a click",
     [create("div", {"id": "a", "onClick": H("c"), "onMouseDown": H("m"), "onInput": H("i")}), OPS,
      click("a"), LOG])

# R6: only changed props are written
hand("02-R6-unchanged", "R6", "an update with the same props writes nothing",
     [create("div", {"id": "a", "className": "c"}), OPS, update({"id": "a", "className": "c"}), OPS,
      update({"id": "a", "className": "c"}), OPS])
hand("02-R6-one-changed", "R6", "one of three props changes",
     [create("div", {"id": "a", "className": "c", "title": "t"}), OPS,
      update({"id": "a", "className": "d", "title": "t"}), DUMP, OPS])
hand("02-R6-added", "R6", "an unchanged prop and a new one",
     [create("div", {"id": "a"}), OPS, update({"id": "a", "title": "t"}), DUMP, OPS])
hand("02-R6-empty-string", "R6", "a prop set to the empty string is written, so the title goes away",
     [create("div", {"title": "x"}), DUMP, update({"title": ""}), DUMP, OPS, create("div", {"title": ""}), OPS])
hand("02-R6-disabled-twice", "R6", "disabled stays true across updates: written once",
     [create("button", {"disabled": True, "id": "b"}), OPS, update({"disabled": True, "id": "b"}), OPS,
      update({"disabled": True, "id": "c"}), DUMP, OPS])
hand("02-R6-flip-flop", "R6", "id goes a, b, a, a: three writes in total after creation",
     [create("div", {"id": "a"}), OPS, update({"id": "b"}), OPS, update({"id": "a"}), OPS, update({"id": "a"}), OPS])

# R7: removed props are cleared
hand("02-R7-id-removed", "R7", "id disappears, className stays",
     [create("div", {"id": "a", "className": "c"}), DUMP, update({"className": "c"}), DUMP, OPS])
hand("02-R7-all-removed", "R7", "three props disappear in one update",
     [create("div", {"id": "a", "className": "c", "title": "t"}), OPS, update(), DUMP, OPS])
hand("02-R7-input", "R7", "an input loses its value and its disabled flag",
     [create("input", {"id": "i", "value": "v", "disabled": True}), DUMP, update({"id": "i"}), DUMP, OPS])
hand("02-R7-unseen", "R7", "a prop the dump does not show is cleared with one write",
     [create("div", {"lang": "en", "id": "a"}), OPS, update({"id": "a"}), OPS])
hand("02-R7-back-again", "R7", "a prop that disappears and comes back is written both times",
     [create("div", {"id": "a"}), OPS, update(), DUMP, OPS, update({"id": "a"}), DUMP, OPS])

# R8: handler changes
hand("02-R8-swap", "R8", "onClick goes from @a to @b: one removal, one addition, only b runs",
     [create("button", {"id": "b", "onClick": H("a")}), click("b"), LOG, OPS, update({"id": "b", "onClick": H("b")}), OPS,
      click("b"), LOG])
hand("02-R8-same-handler", "R8", "the same handler again: no listener calls, it still runs once",
     [create("button", {"id": "b", "onClick": H("a")}), OPS, update({"id": "b", "onClick": H("a")}), OPS,
      click("b"), LOG])
hand("02-R8-removed", "R8", "a removed handler stops running",
     [create("button", {"id": "b", "onClick": H("a")}), OPS, update({"id": "b"}), OPS, click("b"), LOG])
hand("02-R8-added-later", "R8", "a handler added by an update",
     [create("div", {"id": "d"}), OPS, update({"id": "d", "onClick": H("late")}), OPS, click("d"), LOG])
hand("02-R8-swap-three-times", "R8", "a, b, c, a: each click runs exactly the current handler",
     [create("div", {"id": "d", "onClick": H("a")}), click("d"), LOG,
      update({"id": "d", "onClick": H("b")}), click("d"), LOG,
      update({"id": "d", "onClick": H("c")}), click("d"), LOG,
      update({"id": "d", "onClick": H("a")}), click("d"), LOG, OPS])
hand("02-R8-other-prop-moves", "R8", "the handler moves from onClick to onInput: removed for click, added for input",
     [create("div", {"id": "d", "onClick": H("a")}), OPS, update({"id": "d", "onInput": H("a")}), OPS, click("d"), LOG])
hand("02-R8-handler-and-prop", "R8", "a changed id and a changed handler in one update",
     [create("div", {"id": "x", "onClick": H("a")}), OPS, update({"id": "y", "onClick": H("b")}), OPS, click("y"), LOG])
hand("02-R8-one-of-two", "R8", "two handlers, only the mouse one changes, the click one stays",
     [create("div", {"id": "d", "onClick": H("a"), "onMouseDown": H("m1")}), OPS,
      update({"id": "d", "onClick": H("a"), "onMouseDown": H("m2")}), OPS, click("d"), LOG])

# R9: text updates
hand("02-R9-change", "R9", "text changes from a to b",
     [create("text", {"nodeValue": "a"}), OPS, update({"nodeValue": "b"}), DUMP, OPS])
hand("02-R9-same", "R9", "the same text again writes nothing",
     [create("text", {"nodeValue": "same text"}), OPS, update({"nodeValue": "same text"}), DUMP, OPS])
hand("02-R9-cleared", "R9", "the text prop disappears and the node is empty",
     [create("text", {"nodeValue": "bye"}), DUMP, update(), DUMP, OPS])

# E2E
hand("02-E2E-button", "E2E", "a button through its life: created, clicked, re-labelled, disabled, stripped",
     [create("button", {"id": "go", "className": "primary", "onClick": H("start")}), DUMP, OPS,
      click("go"), LOG,
      update({"id": "go", "className": "primary", "title": "running", "onClick": H("pause")}), DUMP, OPS,
      click("go"), LOG,
      update({"id": "go", "className": "muted", "disabled": True, "title": "running", "onClick": H("pause")}), DUMP, OPS,
      update({"id": "go"}), DUMP, OPS, click("go"), LOG])
hand("02-E2E-input", "E2E", "an input: value and disabled change, handler swapped, text node follows",
     [create("input", {"id": "q", "value": "first", "onInput": H("typed"), "key": "k"}), DUMP, OPS,
      update({"id": "q", "value": "second try", "onInput": H("typed"), "key": "k"}), DUMP, OPS,
      update({"id": "q", "value": "second try", "disabled": True, "onInput": H("other")}), DUMP, OPS,
      create("text", {"nodeValue": "label"}), DUMP, update({"nodeValue": "label 2"}), DUMP, OPS])


# ---- random cases ---------------------------------------------------------------------------

POOL = {
    "id": ["a", "b", "c"],
    "className": ["x", "y z", "x y"],
    "title": ["t1", "t 2", ""],
    "value": ["v1", "v 2"],
    "disabled": [True],
    "lang": ["en", "fr"],
    "tabIndex": ["1", "2"],
    "key": ["k1", "k2"],
}
HANDLERS = ["a", "b", "c", "d"]


HANDLER_PROPS = ["onClick", "onMouseDown", "onInput"]


def plain_props(rng, tag):
    names = [n for n in POOL if (n != "value" or tag in ("input", "textarea")) and (n != "disabled" or tag in ("button", "input"))]
    return names


def random_values(rng):
    """Props only change or get added, never disappear (requirement R6)."""
    tag = rng.choice(["div", "button", "input", "span"])
    names = plain_props(rng, tag)
    current = {n: rng.choice(POOL[n]) for n in names if rng.random() < 0.5}
    steps = [create(tag, current), DUMP, OPS]
    for _ in range(rng.randint(4, 7)):
        nxt = {}
        for name in names:
            if name in current:
                nxt[name] = current[name] if rng.random() < 0.5 else rng.choice(POOL[name])
            elif rng.random() < 0.3:
                nxt[name] = rng.choice(POOL[name])
        current = nxt
        steps += [update(current), DUMP, OPS]
    return steps


def random_removals(rng):
    """Props disappear and come back (requirement R7)."""
    tag = rng.choice(["div", "button", "input", "span"])
    names = plain_props(rng, tag)
    current = {n: rng.choice(POOL[n]) for n in names if rng.random() < 0.7}
    steps = [create(tag, current), DUMP, OPS]
    for _ in range(rng.randint(4, 7)):
        nxt = {}
        for name in names:
            if name in current and rng.random() < 0.6:
                nxt[name] = current[name]
            elif name not in current and rng.random() < 0.3:
                nxt[name] = rng.choice(POOL[name])
        current = nxt
        steps += [update(current), DUMP, OPS]
    return steps


def random_handlers(rng):
    """One node with a fixed id; its handlers are swapped, dropped and added (requirement R8)."""
    handlers = {n: H(rng.choice(HANDLERS)) for n in HANDLER_PROPS if rng.random() < 0.5}
    steps = [create("div", {"id": "d", **handlers}), OPS, click("d"), LOG]
    current = handlers
    for _ in range(rng.randint(4, 7)):
        nxt = {}
        for name in HANDLER_PROPS:
            roll = rng.random()
            if name in current and roll < 0.4:
                nxt[name] = current[name]
            elif roll < 0.8 and (name in current or rng.random() < 0.5):
                nxt[name] = H(rng.choice(HANDLERS))
        current = nxt
        steps += [update({"id": "d", **current}), OPS, click("d"), LOG]
    return steps


def random_mixed(rng):
    """Everything at once: plain props, handlers, clicks (end to end)."""
    tag = rng.choice(["div", "button", "input"])
    names = plain_props(rng, tag)
    props = {"id": "m"}
    props.update({n: rng.choice(POOL[n]) for n in names if n != "id" and rng.random() < 0.4})
    props.update({n: H(rng.choice(HANDLERS)) for n in HANDLER_PROPS if rng.random() < 0.4})
    steps = [create(tag, props), DUMP, OPS]
    current = props
    for _ in range(rng.randint(4, 7)):
        nxt = {"id": "m"}
        for name in names:
            if name == "id":
                continue
            if name in current and rng.random() < 0.6:
                nxt[name] = current[name] if rng.random() < 0.6 else rng.choice(POOL[name])
            elif name not in current and rng.random() < 0.3:
                nxt[name] = rng.choice(POOL[name])
        for name in HANDLER_PROPS:
            if name in current and rng.random() < 0.5:
                nxt[name] = current[name]
            elif rng.random() < 0.35:
                nxt[name] = H(rng.choice(HANDLERS))
        current = nxt
        steps += [update(current), DUMP, OPS]
        if rng.random() < 0.8:
            steps += [click("m"), LOG]
    return steps


def random_text(rng):
    values = ["a", "b", "two words", "0", " padded ", "50%", 'q "uoted"', "same", "same"]
    steps = [create("text", {"nodeValue": rng.choice(values)}), DUMP, OPS]
    for _ in range(rng.randint(3, 6)):
        steps.append(update({"nodeValue": rng.choice(values)} if rng.random() < 0.85 else {}))
        steps += [DUMP, OPS]
    return steps


def main():
    args = wbcore.parse_args("02")
    cases = wbcore.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, EXPLAIN, source=SOURCE)
    planned = list(HAND)
    seed = args.seed

    def add(req, kind, make, count, what):
        for k in range(1, count + 1):
            planned.append((f"02-{req}-random-s{seed}-{k}", req, f"{what}, seed {seed}",
                            make(reactgen.rng_for(seed, f"{kind}{k}"))))

    add("R6", "values", random_values, 1, "random prop values changing and appearing, dump and ops after every update")
    add("R7", "removals", random_removals, 1, "random props disappearing and coming back, dump and ops after every update")
    add("R8", "handlers", random_handlers, 2, "random handler swaps, removals and additions with a click and log after every update")
    add("R9", "text", random_text, 1, "random text updates")
    add("E2E", "mixed", random_mixed, 1, "random mix of props, handlers and clicks")
    for case_id, req, title, steps in planned:
        cases.add(case_id, req, title, scenario_lines(steps), expected=expected_lines(steps))
    cases.save()


if __name__ == "__main__":
    main()
