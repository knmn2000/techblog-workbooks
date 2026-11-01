"""Helpers shared by the test generators (tools/gen_pNN.py) of this workbook.

    from reactgen import run_oracle, count_units, merge_expected, rand_tree, ...

The expected output of a scenario comes from real React 19 running on jsdom (tools/oracle), never from
the reference solution. React can't answer two things, and the generators model them:
  `idle <k>`   units of work per idle period: derived from the fiber count (count_units)
  `ops ...`    statistics of the learner's DOM writes: modelled per assignment
The oracle prints the placeholders `idle ?` and `ops ?` for them, and merge_expected() fills them in.
"""

import json
import math
import random
import re
import shutil
import subprocess
import sys

import wbcore

ROOT = wbcore.ROOT
ORACLE = ROOT / "tools" / "oracle"


# ---- Running the oracle ---------------------------------------------------------------------

def run_oracle_batch(scenarios, todo=False):
    """Runs scenario texts (strings or line lists) against React in one Node process.
    Returns one list of output lines per scenario. Stops the generator on the first error."""
    node = shutil.which("node")
    if not node:
        sys.exit("node is not on PATH (the oracle needs Node.js 26 or newer)")
    jobs = [{"text": s if isinstance(s, str) else "\n".join(s) + "\n", "todo": todo} for s in scenarios]
    proc = subprocess.run([node, str(ORACLE / "batch.mjs")], input=json.dumps(jobs), capture_output=True,
                          text=True, encoding="utf-8", cwd=ROOT)
    if proc.returncode != 0:
        sys.exit(f"the oracle failed:\n{proc.stderr.strip()}")
    results = json.loads(proc.stdout)
    out = []
    for job, result in zip(jobs, results):
        if "error" in result:
            sys.exit(f"the oracle rejected a scenario: {result['error']}\n{job['text']}")
        if result.get("warnings"):
            sys.exit("React warned while running a scenario (avoid the construct, or fix the scenario):\n"
                     + "\n".join(result["warnings"])[:1500] + "\n" + job["text"])
        out.append(result["lines"])
    return out


def run_oracle(scenario, todo=False):
    return run_oracle_batch([scenario], todo=todo)[0]


# ---- Markup, fibers, units ------------------------------------------------------------------

TAG = re.compile(r"<(/?)([A-Za-z][A-Za-z0-9]*)((?:\s+[^<>]*?)?)\s*(/?)>")
VOID = {"input", "br", "hr", "img"}


def parse_markup(src):
    """A small parser for the harness's markup: returns a list of nodes, each ('el', tag, attrs, children)
    or ('text', value). Only what the generators need (attributes are kept as the raw text)."""
    pos, stack = 0, [("root", None, "", [])]
    for m in TAG.finditer(src):
        text = src[pos:m.start()]
        if text.strip():
            stack[-1][3].append(("text", text))
        pos = m.end()
        closing, tag, attrs, selfclose = m.group(1), m.group(2), m.group(3).strip(), m.group(4)
        if closing:
            node = stack.pop()
            assert node[1] == tag, f"markup: </{tag}> closes <{node[1]}>"
            stack[-1][3].append(("el", node[1], node[2], node[3]))
        elif selfclose or tag.lower() in VOID:
            stack[-1][3].append(("el", tag, attrs, []))
        else:
            stack.append(("open", tag, attrs, []))
    tail = src[pos:]
    if tail.strip():
        stack[-1][3].append(("text", tail))
    assert len(stack) == 1, "markup: unclosed tag"
    return stack[0][3]


def count_nodes(nodes):
    total = 0
    for n in nodes:
        total += 1
        if n[0] == "el":
            total += count_nodes(n[3])
    return total


def count_units(markup, components=0):
    """Units of work to render a plain tree: the container's root fiber, one per element and one per text
    node. `components` adds one unit for each function component in the tree (assignment 09 on)."""
    return 1 + count_nodes(parse_markup(markup)) + components


def periods(units, budget):
    """The `idle` lines a tree of `units` units needs with a fixed budget until it is done, plus one
    more period that finds nothing to do."""
    lines, left = [], units
    while left > 0:
        run = min(budget, left)
        lines.append(f"idle {run}")
        left -= run
    lines.append("idle 0")
    return lines


# ---- Filling in what React can't answer -----------------------------------------------------

def merge_expected(scenario, oracle_lines, units, ops_lines=()):
    """Combines the oracle's lines with the modelled ones for a scenario (a list of command lines) that
    renders trees and runs idle periods.

    units      {tree name: units of work}; the pending render of a tree needs that many units
    ops_lines  the `ops ...` lines, in order, for the `ops` commands

    Simulates the idle periods (`idle k` runs up to k units, `idle inf` and `flush` finish the pending
    render) and, for a `dump` taken while a first render is still pending, prints the empty container,
    because nothing may be on the page before the commit (assignment 05). Re-renders are not modelled:
    use it for scenarios with one render in flight at a time, onto an empty container."""
    commands = [c.strip() for c in scenario if c.strip() and not c.strip().startswith("#")]
    out, o, ops_iter = [], 0, iter(ops_lines)
    pending = 0
    committed_dump = None
    n_dump = 0

    def take_block(i):
        """The oracle's lines from i up to the next line that starts another command's output."""
        j = i + 1
        while j < len(oracle_lines) and oracle_lines[j].split(" ", 1)[0] in ("node", "text", "title"):
            j += 1
        return oracle_lines[i:j], j

    for cmd in commands:
        word = cmd.split(None, 1)[0]
        rest = cmd.split(None, 1)[1] if " " in cmd else ""
        if word == "render":
            pending = units[rest.strip()]
            committed_dump = None
        elif word == "flush":
            pending = 0
        elif word == "idle":
            arg = rest.strip()
            budget = math.inf if arg in ("inf", "infinity") else int(arg)
            run = min(budget, pending)
            pending -= run
            assert oracle_lines[o] == "idle ?", f"expected the idle placeholder at line {o}: {oracle_lines[o]!r}"
            o += 1
            out.append(f"idle {int(run)}")
        elif word == "ops":
            assert oracle_lines[o] == "ops ?", f"expected the ops placeholder at line {o}: {oracle_lines[o]!r}"
            o += 1
            out.append(next(ops_iter))
        elif word == "dump":
            block, o = take_block(o)
            n_dump += 1
            out.extend([f"dump {n_dump}"] if pending > 0 else block)
        elif word in ("click", "type", "submit", "poke", "tree"):
            pass
        elif word == "log":
            while o < len(oracle_lines) and oracle_lines[o].startswith("log "):
                out.append(oracle_lines[o])
                o += 1
    assert o == len(oracle_lines), f"{len(oracle_lines) - o} oracle lines left over"
    return out


# ---- Random trees (for the seeded part of every assignment from 03 on) ----------------------

# Tags that can nest in any order without React warning about invalid HTML nesting
# (no p, ul/li, headings, tables): random trees mix them freely.
TAGS = ["div", "span", "section", "article", "em", "b", "i"]
WORDS = ["alpha", "beta", "gamma", "delta", "kiwi", "plum", "fig", "oak", "elm", "ash", "reed", "moss"]


def rand_attrs(rng, handlers=False):
    attrs = []
    if rng.random() < 0.35:
        attrs.append(f'id="{rng.choice(WORDS)}{rng.randint(1, 99)}"')
    if rng.random() < 0.25:
        attrs.append(f'className="{rng.choice(WORDS)}"')
    if rng.random() < 0.15:
        attrs.append(f'title="{rng.choice(WORDS)}"')
    return attrs


def rand_markup(rng, depth=3, width=3, tags=TAGS, keyed=None):
    """One random element as markup. `keyed` is None (no keys) or a list of keys to give the children of
    the outer element's lists (the caller decides). Ids are not unique: don't `click #id` on them."""
    tag = rng.choice(tags)
    attrs = rand_attrs(rng)
    kids = []
    if depth > 0:
        for _ in range(rng.randint(0, width)):
            if rng.random() < 0.3:
                kids.append(rng.choice(WORDS) + rng.choice(["", " " + rng.choice(WORDS)]))
            else:
                kids.append(rand_markup(rng, depth - 1, width, tags))
    elif rng.random() < 0.5:
        kids.append(rng.choice(WORDS))
    # adjacent text pieces would merge into one text node in the markup parser: keep texts apart
    cleaned = []
    for k in kids:
        if cleaned and not k.startswith("<") and not cleaned[-1].startswith("<"):
            cleaned.append(f"<b>{k}</b>")
        else:
            cleaned.append(k)
    a = (" " + " ".join(attrs)) if attrs else ""
    return f"<{tag}{a}>{''.join(cleaned)}</{tag}>"


def rng_for(seed, label):
    """A random generator tied to a seed and a label, so cases keep their content when others change."""
    return random.Random(f"{seed}:{label}")
