"""Writes every assignment's starters: the blank ones, and the header of the boilerplate ones.

    py -P tools/blank_starters.py            # write missing blank starters, refresh every header
    py -P tools/blank_starters.py --force    # rewrite every blank starter too

An assignment's files (workbook.json) are its program the checker runs ("solution") and the
project files it creates ("files"). Each has two starters, at the same path under:
  starters/blank/        the header below, then nothing (an empty main in a program): the
                         learner writes everything else
  starters/boilerplate/  the same header, then the declarations named as the author names them,
                         TODO bodies, and the program's input/output done (authors write these;
                         this script only replaces their header)
Every header says which assignment the file belongs to, why the file exists (project.purposes),
what the learner's job in it is (the assignment's "jobs"), and how to start: blank or Boilerplate.
Starting an assignment copies its blank starters into the project (tools/project.py).
"""

import argparse
import re
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project  # noqa: E402

# Extension -> (line comment, empty program).
SHAPES = {
    ".cpp": ("//", "int main(int argc, char** argv) {\n}\n"),
    ".cc": ("//", "int main(int argc, char** argv) {\n}\n"),
    ".c": ("//", "int main(int argc, char** argv) {\n  return 0;\n}\n"),
    ".h": ("//", ""),
    ".hpp": ("//", ""),
    ".py": ("#", "def main():\n    pass\n\n\nif __name__ == \"__main__\":\n    main()\n"),
    ".js": ("//", "function main() {\n}\n\nmain();\n"),
    ".ts": ("//", "function main(): void {\n}\n\nmain();\n"),
    ".rs": ("//", "fn main() {\n}\n"),
    ".go": ("//", "package main\n\nfunc main() {\n}\n"),
    ".lua": ("--", ""),
}
RULE = "=" * 86


def wrap(text: str, indent: str = "  ") -> list:
    return textwrap.wrap(text, 88 - len(indent), break_long_words=False, break_on_hyphens=False) or [""]


def listing(paths: list) -> str:
    return paths[0] if len(paths) == 1 else ", ".join(paths[:-1]) + " and " + paths[-1]


def header(path: str, cid: str, meta: dict, config: dict, kind: str, todo: bool = True) -> str:
    """The comment block at the top of one of an assignment's files."""
    note = SHAPES.get(Path(path).suffix.lower(), ("//", ""))[0]
    entry = project.entry(config, cid)
    jobs = meta.get("jobs", {})
    sections = [[f"Assignment {cid}: {meta['title']}",
                 f"Problem: {meta['problem']} (and in the problem book, with its Start here card)"]]
    if path == entry:
        run = config["run"].replace("{id}", cid).replace("{input}", "<input-file>").replace("{output}", "<output-file>")
        check = config.get("book", {}).get("checkCommand", ".\\check {id}").replace("{id}", cid)
        why = (f"The checker runs this program for assignment {cid} as `{run}`. It reads a test input, "
               f"calls your code and writes the answer to the output file, and the checker compares that "
               f"answer with the expected one. Run `{check}`, or use Run and Submit in the book.")
    else:
        why = config["project"].get("purposes", {}).get(path, "")
        later = sorted(c for c, m in config["checkpoints"].items() if path in m.get("extends", []))
        # Say which later assignments add to the file, unless the purpose already names them.
        if later and not all(re.search(rf"\b0?{int(c)}\b", why) for c in later):
            why += f" Later, assignment{'s' if len(later) > 1 else ''} {listing(later)} add{'' if len(later) > 1 else 's'} to this file."
    sections.append(["Why this file exists:", *("  " + l for l in wrap(why))])
    # A post with code: the Boilerplate keeps its author's names for things.
    names = ", with the author's names" if config["project"].get("author") else ""
    job = jobs.get(path) or "See this assignment's Start here card in the problem book."
    if kind == "boilerplate" and path == entry:
        job = "The Boilerplate gives you this program finished. You fill in the TODOs in this assignment's other files."
    elif kind == "boilerplate" and todo:
        job += " The Boilerplate gives you the declarations; fill in each TODO."
    elif kind == "boilerplate":
        job = (f"The Boilerplate gives you this file finished: the declarations{names}. "
               "You fill in the TODOs in this assignment's other files.")
    sections.append(["Your job:", *("  " + l for l in wrap(job))])
    if path == entry:
        others = [p for p in meta.get("files", [])]
        lines = []
        if others:
            lines += wrap(f"You also write {listing(others)} in this assignment; each one gives its job at the top.")
        for p in meta.get("extends", []):
            lines += wrap(f"It adds to {p}, which you started earlier: {jobs.get(p, 'see the Start here card.')}")
        if meta.get("buildsOn"):
            lines += wrap(f"Earlier files you can use: {listing(meta['buildsOn'])}.")
        headers = [p for p in others + meta.get("extends", []) if p.endswith((".h", ".hpp"))]
        if headers and path.endswith((".cpp", ".cc", ".c")):
            lines += wrap(f'Include them by their path under src/, e.g. #include "{headers[0].removeprefix("src/")}".')
        modules = [p for p in others + meta.get("extends", []) if p.endswith(".py") and p.startswith("src/")]
        if modules and path.endswith(".py"):
            dotted = modules[0].removeprefix("src/").removesuffix(".py").replace("/", ".")
            package, _, name = dotted.rpartition(".")
            lines += wrap(f"Import them as modules of your package, e.g. `from {package} import {name}`.")
        if lines:
            sections.append(["The other files of this assignment:", *("  " + l for l in lines)])
    how = ("This is the Boilerplate. To start from an empty file instead, choose From scratch in the "
           "book (the empty files are in starters/blank/)." if kind == "boilerplate" else
           "Write it yourself from here, or press Boilerplate in the book's editor to get the "
           f"input/output code and the declarations{names} (the same files are in "
           "starters/boilerplate/).")
    sections.append(["How to start:", *("  " + l for l in wrap(how))])
    body = []
    for k, section in enumerate(sections):
        if k:
            body.append("")
        body += section
    return "\n".join([f"{note} {RULE}", *(f"{note} {line}".rstrip() for line in body), f"{note} {RULE}"]) + "\n"


def blank_text(path: str, cid: str, meta: dict, config: dict) -> str:
    _, program = SHAPES.get(Path(path).suffix.lower(), ("//", ""))
    top = "#pragma once\n" if path.endswith((".h", ".hpp")) else ""
    is_program = path == project.entry(config, cid) or Path(path).stem == "main"
    return top + header(path, cid, meta, config, "blank") + ("\n" + program if is_program and program else "")


def restamp(text: str, block: str, is_program: bool) -> str:
    """The boilerplate's text with its header replaced by `block`."""
    lines = text.split("\n")
    top = []
    if lines and lines[0].strip() == "#pragma once":
        top, lines = [lines[0]], lines[1:]
    if lines and lines[0].endswith(RULE):  # a header this script wrote before
        end = next(i for i in range(1, len(lines)) if lines[i].endswith(RULE))
        lines = lines[end + 1:]
    elif is_program:  # an older header: the whole leading comment block
        while lines and lines[0].lstrip().startswith(("//", "#", "--")):
            lines = lines[1:]
    elif lines and re.match(r"\s*(//|#|--)\s*(Assignment|Checkpoint) \d+", lines[0]):
        lines = lines[1:]  # the one-line "Assignment NN: ..." comment
        if lines and lines[0].strip() in ("//", "#", "--"):
            lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    return "\n".join(top) + ("\n" if top else "") + block + "\n" + "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="rewrite blank starters that already exist")
    args = ap.parse_args()
    config = project.load_config()
    written = stamped = 0
    for cid, meta in config["checkpoints"].items():
        for path in project.own_files(config, cid):
            target = project.starter("blank", path)
            if args.force or not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(blank_text(path, cid, meta, config), encoding="utf-8", newline="\n")
                written += 1
            boiler = project.starter("boilerplate", path)
            if boiler.exists():
                old = boiler.read_text(encoding="utf-8")
                block = header(path, cid, meta, config, "boilerplate", todo="TODO" in old.split(RULE)[-1])
                new = restamp(old, block, path == project.entry(config, cid))
                if new != old:
                    boiler.write_text(new, encoding="utf-8", newline="\n")
                    stamped += 1
    print(f"blank starters written: {written}, boilerplate headers refreshed: {stamped}")


if __name__ == "__main__":
    main()
