"""The workbook's primer: what a learner needs to know before an assignment, in one place.

primer/*.md holds the entries, one file per group (the file's `# ` heading names the group). Each
entry is a `## ` heading, an optional comment block, and its text:

    ## `static_assert`
    <!--
    id: static-assert
    also: static assertion; compile-time check
    code: \\bstatic_assert\\b
    -->
    What it is, in a few sentences, with a small example, where the workbook uses it,
    and a "Learn more" list of links.

  id     the anchor (#primer/<id>); defaults to the heading made into a slug
  also   other names for the entry, separated by ";" (the book's search finds them)
  code   a regular expression (multiline: ^ and $ match at each line); an assignment whose
         Boilerplate files match it uses the entry

Problem pages link to entries as [text](#primer/<id>): in their tags, and in a "What you need"
section that lists the entries with a note on how the assignment uses them. An entry belongs to
the first assignment that lists it; later assignments that use it show it as known from earlier.
tools/primer_check.py checks that every entry an assignment uses is listed by then.
"""

import re
from pathlib import Path

import project

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "primer"
LINK = re.compile(r"\]\(#primer/([a-z0-9-]+)\)")
META = re.compile(r"^(\w+):\s*(.*)$")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"[`*]", "", text).lower()).strip("-")


def load() -> list:
    """The groups, in file-name order: [{"title", "intro" (lines), "entries": [entry]}], where an
    entry is {"id", "title", "also", "code" (compiled or None), "lines" (its Markdown body),
    "file", "line"}."""
    groups = []
    for path in sorted(DIR.glob("*.md")) if DIR.is_dir() else []:
        lines = path.read_text(encoding="utf-8").replace("\r\n", "\n").split("\n")
        group = {"title": path.stem, "intro": [], "entries": [], "file": path.relative_to(ROOT).as_posix()}
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("# ") and not group["entries"]:
                group["title"] = line[2:].strip()
            elif line.startswith("## "):
                entry = {"title": line[3:].strip(), "also": [], "code": None, "lines": [],
                         "file": group["file"], "line": i + 1}
                entry["id"] = slug(entry["title"])
                if i + 1 < len(lines) and lines[i + 1].strip() == "<!--":
                    j = i + 2
                    while j < len(lines) and lines[j].strip() != "-->":
                        if m := META.match(lines[j].strip()):
                            key, value = m.group(1), m.group(2).strip()
                            if key == "id":
                                entry["id"] = value
                            elif key == "also":
                                entry["also"] = [a.strip() for a in value.split(";") if a.strip()]
                            elif key == "code":
                                entry["code"] = re.compile(value, re.M)  # ^ and $ match at each line
                        j += 1
                    i = j
                group["entries"].append(entry)
            elif group["entries"]:
                group["entries"][-1]["lines"].append(line)
            else:
                group["intro"].append(line)
            i += 1
        groups.append(group)
    return groups


def entries(groups: list) -> dict:
    return {e["id"]: e for g in groups for e in g["entries"]}


def strip_comments(text: str, path: str) -> str:
    """The code without its comments, so an entry's pattern doesn't match a word in a comment.
    Include and import lines keep their code (only the comment after them goes)."""
    if path.endswith(".py"):
        return re.sub(r"(?m)#.*$", "", text)
    if path.endswith((".lua",)):
        return re.sub(r"(?m)--.*$", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"(?m)//.*$", "", text)


def assignment_code(config: dict, cid: str) -> dict:
    """{path: text} of the code the learner reads in assignment cid: the Boilerplate of its own
    files. The reference solution doesn't count: it is one way to write the answer, and what the
    learner needs beyond the Boilerplate is what the page asks for, which its tags link."""
    meta = config["checkpoints"][cid]
    texts = {}
    for path in [project.entry(config, cid), *meta.get("files", [])]:
        starter = project.starter("boilerplate", path)
        if starter.exists():
            texts["boilerplate/" + path] = starter.read_text(encoding="utf-8")
    return texts


def page_links(problem_text: str) -> dict:
    """{"tags": ids linked from the tag lines, "need": [(id, item text)] from "What you need",
    "all": every id linked anywhere on the page}."""
    lines = problem_text.replace("\r\n", "\n").split("\n")
    tags, need, section = [], [], None
    for line in lines:
        if line.startswith("## "):
            section = line[3:].strip().lower()
            continue
        if section is None and re.match(r"- \*\w+:\*", line):
            tags += LINK.findall(line)
        elif section == "what you need" and re.match(r"\s*[-*]\s+", line):
            ids = LINK.findall(line)
            if ids:
                need.append((ids[0], line))
    return {"tags": tags, "need": need, "all": LINK.findall("\n".join(lines))}


def usage(config: dict, groups: list) -> dict:
    """For each assignment, in order: {"listed": ids its "What you need" lists, "used": ids its
    code or tags use, "first": {id: the assignment that introduces it}}."""
    known = entries(groups)
    out, first = {}, {}
    for cid, meta in sorted(config["checkpoints"].items()):
        problem = ROOT / meta["problem"]
        if not problem.exists():
            continue
        links = page_links(problem.read_text(encoding="utf-8"))
        listed = [i for i, _ in links["need"]]
        used = set(links["tags"])
        for path, text in assignment_code(config, cid).items():
            code = strip_comments(text, path)
            used |= {i for i, e in known.items() if e["code"] and e["code"].search(code)}
        for i in listed:
            first.setdefault(i, cid)
        out[cid] = {"listed": listed, "used": used, "links": links}
    return {"assignments": out, "first": first}
