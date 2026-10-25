"""Checks the primer against the assignments, the way requirement coverage is checked.

    py -P tools/primer_check.py            # coverage, links inside the book, commented includes
    py -P tools/primer_check.py --links    # also fetch every outside link in the primer

It reports:
  - an entry an assignment's Boilerplate or tags use that neither it nor an earlier assignment lists
    in "Learning material" (so the learner meets it unexplained)
  - a link to #primer/<id> that names no entry, and duplicate ids
  - an entry that no page lists and no other entry links to (nothing leads a learner to it)
  - an entry without text, or without a "Learn more" link, or a link with ( ) in its URL
  - an include or import line in a Boilerplate starter without a comment saying why it's there
  - with --links, an outside link that doesn't answer
Exit status 1 when anything is reported.
"""

import argparse
import json
import re
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import primer  # noqa: E402
import project  # noqa: E402

ROOT = primer.ROOT
URL = re.compile(r"\]\((https?://[^)\s]+)\)")
# An include or import line, by file extension, and the comment that must follow it.
IMPORTS = {
    (".c", ".cc", ".cpp", ".cxx", ".h", ".hpp"): (re.compile(r"^\s*#\s*include\b"), "//"),
    (".py",): (re.compile(r"^\s*(import\s+\w|from\s+\S+\s+import\b)"), "#"),
    (".js", ".mjs", ".ts"): (re.compile(r"^\s*import\b.*\bfrom\b|^\s*import\s+['\"]"), "//"),
    (".rs",): (re.compile(r"^\s*use\s+\w"), "//"),
}


def fetch(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (workbook primer link check)"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return url, response.status
    except Exception as e:  # noqa: BLE001 - any failure is a report, not a crash
        return url, getattr(e, "code", None) or type(e).__name__


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--links", action="store_true", help="fetch every outside link in the primer")
    args = ap.parse_args()
    config = json.loads((ROOT / "workbook.json").read_text(encoding="utf-8"))
    groups = primer.load()
    problems = []
    if not groups:
        print("no primer/ folder: nothing to check")
        return 0

    known, seen = primer.entries(groups), {}
    for e in (e for g in groups for e in g["entries"]):
        where = f"{e['file']}:{e['line']}"
        if e["id"] in seen:
            problems.append(f"{where}: id '{e['id']}' is already used at {seen[e['id']]}")
        seen[e["id"]] = where
        text = "\n".join(e["lines"])
        if len(text.split()) < 25:
            problems.append(f"{where}: '{e['id']}' has almost no text")
        if not URL.search(text):
            problems.append(f"{where}: '{e['id']}' has no outside link to learn more")
        for bad in re.findall(r"\]\((https?://[^\s)]*\()", text):  # the link would end at its ')'
            problems.append(f"{where}: write ( and ) in a link as %28 and %29: {bad}")
        for target in primer.LINK.findall(text):
            if target not in known:
                problems.append(f"{where}: links to #primer/{target}, which isn't an entry")

    use = primer.usage(config, groups)
    first = use["first"]
    order = sorted(use["assignments"])
    for cid in order:
        a = use["assignments"][cid]
        for target in a["links"]["all"]:
            if target not in known:
                problems.append(f"{cid}: links to #primer/{target}, which isn't an entry")
        for i in sorted(a["used"]):
            if i in known and (i not in first or first[i] > cid):
                why = "its tags link it" if i in a["links"]["tags"] else "its code uses it"
                problems.append(f"{cid}: {why}, but no assignment lists '{i}' in Learning material by then")
        if not a["listed"]:
            problems.append(f"{cid}: the page has no Learning material")
    # An entry no page lists is still fine when another entry links to it: the primer is also
    # a reference to browse (a technique a solution may use, a term inside another entry).
    linked = {t for e in known.values() for t in primer.LINK.findall("\n".join(e["lines"])) if t != e["id"]}
    for i in known:
        if i not in first and i not in linked:
            problems.append(f"{known[i]['file']}:{known[i]['line']}: no page lists '{i}' and no entry links to it")

    for cid in order:
        meta = config["checkpoints"][cid]
        for path in [project.entry(config, cid), *meta.get("files", [])]:
            starter = project.starter("boilerplate", path)
            rule = next((r for exts, r in IMPORTS.items() if path.endswith(exts)), None)
            if not starter.exists() or not rule:
                continue
            pattern, mark = rule
            for n, line in enumerate(starter.read_text(encoding="utf-8").splitlines(), 1):
                if pattern.match(line) and mark not in line:
                    problems.append(f"{starter.relative_to(ROOT).as_posix()}:{n}: say why it's here: {line.strip()}")

    if args.links:
        urls = sorted({u for g in groups for e in g["entries"] for u in URL.findall("\n".join(e["lines"]))})
        with ThreadPoolExecutor(8) as pool:
            for url, status in pool.map(fetch, urls):
                if status != 200:
                    problems.append(f"link {url}: {status}")
        print(f"fetched {len(urls)} outside links")

    total = sum(len(g["entries"]) for g in groups)
    for p in problems:
        print(p)
    print(f"{total} entries in {len(groups)} groups, {len(order)} assignments: "
          + (f"{len(problems)} problems" if problems else "all covered"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
