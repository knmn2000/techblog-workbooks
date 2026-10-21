"""Writes the blank starters for every checkpoint's files.

    py -P tools/blank_starters.py            # write the blank starters that are missing
    py -P tools/blank_starters.py --force    # rewrite every blank starter

A checkpoint's files (workbook.json) are its entry program ("solution") and the project files it
creates ("files"). Each has two starters, at the same path under:
  starters/blank/        a comment saying what belongs in the file (and an empty main in the
                         entry program): the learner writes everything else
  starters/boilerplate/  the entry program's input/output done, and the project files'
                         declarations named as the author names them, with TODO bodies
                         (authors write these; see docs/authoring-guide.md)
The comment for a project file is its line in "purposes" (workbook.json's "project").
Starting a checkpoint copies its blank starters into the project (tools/project.py).
"""

import argparse
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


def wrap(text: str) -> list:
    return textwrap.wrap(text, 88, break_long_words=False, break_on_hyphens=False)


def listing(paths: list) -> str:
    return paths[0] if len(paths) == 1 else ", ".join(paths[:-1]) + " and " + paths[-1]


def entry_starter(cid: str, meta: dict, config: dict) -> str:
    path = project.entry(config, cid)
    note, program = SHAPES.get(Path(path).suffix.lower(), ("//", ""))
    run = (config["run"].replace("{id}", cid).replace("{input}", "<input-file>")
           .replace("{output}", "<output-file>"))
    check = config.get("book", {}).get("checkCommand", ".\\check {id}").replace("{id}", cid)
    own, extends = meta.get("files", []), meta.get("extends", [])
    work = []
    if own:
        work.append(f"This checkpoint's work goes in {listing(own)}.")
    if extends:
        started = sorted({project.owner(config, p) for p in extends} - {None})
        work.append(f"{'It' if own else 'This checkpoint'} adds to {listing(extends)}, which you "
                    f"started in checkpoint {listing(started)}.")
    if meta.get("buildsOn"):
        work.append(f"Earlier files you can build on: {listing(meta['buildsOn'])}.")
    headers = [p for p in own + extends if p.endswith((".h", ".hpp"))]
    if headers and path.endswith((".cpp", ".cc", ".c")):
        work.append(f'Include project files by their path under src/, e.g. #include "{headers[0].removeprefix("src/")}".')
    lines = [
        f"Checkpoint {cid} ({meta['title']}): the program the checker runs.",
        "",
        f"Problem:  {meta['problem']} (also in the web problem book)",
        f"Check:    {check}",
        "",
        "The checker runs this program from the workbook folder as",
        "",
        f"    {run}",
        "",
        *wrap("Read the input file, use your project to work out the answer, and write it to the "
              "output file; only that file is checked. The includes, the parsing and the structure "
              "are up to you."),
        "",
        *wrap(" ".join(work)),
        "",
        *wrap("For ready-made input/output code, use the book's Boilerplate button (the files are "
              "in starters/boilerplate/)."),
    ]
    header = "\n".join(f"{note} {line}".rstrip() for line in lines)
    return header + "\n" + ("\n" + program if program else "")


def file_starter(path: str, cid: str, meta: dict, config: dict) -> str:
    note, program = SHAPES.get(Path(path).suffix.lower(), ("//", ""))
    purpose = config["project"].get("purposes", {}).get(path, "")
    lines = [f"Checkpoint {cid} - {meta['title']}.", *wrap(purpose), f"Problem: {meta['problem']}"]
    text = "\n".join(f"{note} {line}".rstrip() for line in lines) + "\n"
    if path.endswith((".h", ".hpp")):
        return "#pragma once\n" + text
    is_main = Path(path).stem == "main" and program
    return text + ("\n" + program if is_main else "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="rewrite blank starters that already exist")
    args = ap.parse_args()
    config = project.load_config()
    written = 0
    for cid, meta in config["checkpoints"].items():
        texts = {project.entry(config, cid): entry_starter(cid, meta, config)}
        texts.update({p: file_starter(p, cid, meta, config) for p in meta.get("files", [])})
        for path, text in texts.items():
            target = project.starter("blank", path)
            if args.force or not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8", newline="\n")
                written += 1
    print(f"blank starters written: {written}")


if __name__ == "__main__":
    main()
