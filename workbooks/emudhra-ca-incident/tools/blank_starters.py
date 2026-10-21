"""Writes the blank starters and puts them in solutions/.

    py -P tools/blank_starters.py            # write missing blank starters, install where safe
    py -P tools/blank_starters.py --force    # rewrite every blank starter

Each checkpoint has two starters:
  starters/blank/<file>        a header comment and an empty main: the learner writes the
                               includes, the input parsing and the output themselves
  starters/boilerplate/<file>  the full starter: input/output code done, functions marked TODO

Authors write the boilerplate as solutions/<file> (that's what the stub checks run on). This
script keeps a copy of it in starters/boilerplate/, writes starters/blank/<file>, and copies the
blank starter into solutions/ when the solution file is missing or is still the untouched
boilerplate. A solution file the learner has changed is never overwritten.
"""

import argparse
import json
import re
import shutil
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Extension -> (line comment, empty program).
SHAPES = {
    ".cpp": ("//", "int main(int argc, char** argv) {\n}\n"),
    ".cc": ("//", "int main(int argc, char** argv) {\n}\n"),
    ".c": ("//", "int main(int argc, char** argv) {\n  return 0;\n}\n"),
    ".py": ("#", "def main():\n    pass\n\n\nif __name__ == \"__main__\":\n    main()\n"),
    ".js": ("//", "function main() {\n}\n\nmain();\n"),
    ".ts": ("//", "function main(): void {\n}\n\nmain();\n"),
    ".rs": ("//", "fn main() {\n}\n"),
    ".go": ("//", "package main\n\nfunc main() {\n}\n"),
    ".java": ("//", "public class Main {\n  public static void main(String[] args) {\n  }\n}\n"),
}


def blank_starter(cid: str, meta: dict, config: dict) -> str:
    solution = Path(meta["solution"])
    note, program = SHAPES.get(solution.suffix.lower(), ("//", ""))
    run = (config["run"].replace("{id}", cid).replace("{input}", "<input-file>")
           .replace("{output}", "<output-file>"))
    check = config.get("book", {}).get("checkCommand", ".\\check {id}").replace("{id}", cid)
    header = (ROOT / meta["cases"]).read_text(encoding="utf-8").split("\ncase ", 1)[0]
    picture = re.search(r"^compare\s+image", header, re.M) is not None
    answer = ("your picture (a PNG or a binary PPM, see the problem page)" if picture
              else "your answer")
    wrap = lambda text: textwrap.wrap(text, 84, break_long_words=False, break_on_hyphens=False)
    lines = [
        f"Checkpoint {cid} - {meta['title']}",
        "",
        f"Problem:  {meta['problem']} (also in the web problem book)",
        f"Check:    {check}",
        "",
        "The checker runs your program from the workbook folder as",
        "",
        f"    {run}",
        "",
        *wrap(f"Read the input file and write {answer} to the output file; only that file is "
              "checked. The includes, the parsing and the structure are up to you."),
        "",
        *wrap("Code you want to share between checkpoints can go in solutions/common/ (see the "
              "README there). To start from ready-made input/output code instead, copy "
              f"starters/boilerplate/{solution.name} over this file."),
    ]
    header = "\n".join(f"{note} {line}".rstrip() for line in lines)
    return header + "\n" + ("\n" + program if program else "")


def same(a: Path, b: Path) -> bool:
    text = lambda p: [line.rstrip() for line in p.read_text(encoding="utf-8", errors="replace").splitlines()]
    return a.exists() and b.exists() and text(a) == text(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="rewrite blank starters that already exist")
    args = ap.parse_args()
    config = json.loads((ROOT / "workbook.json").read_text(encoding="utf-8"))
    kept = written = installed = 0
    for cid, meta in sorted(config["checkpoints"].items()):
        solution = ROOT / meta["solution"]
        boilerplate = ROOT / "starters" / "boilerplate" / solution.name
        blank = ROOT / "starters" / "blank" / solution.name
        if not boilerplate.exists() and solution.exists():
            boilerplate.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(solution, boilerplate)
            kept += 1
        untouched = not solution.exists() or same(solution, boilerplate) or same(solution, blank)
        if args.force or not blank.exists():
            blank.parent.mkdir(parents=True, exist_ok=True)
            blank.write_text(blank_starter(cid, meta, config), encoding="utf-8", newline="\n")
            written += 1
        if untouched and not same(solution, blank):
            solution.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(blank, solution)
            installed += 1
    (ROOT / "solutions" / "common").mkdir(parents=True, exist_ok=True)
    print(f"boilerplate copies kept: {kept}, blank starters written: {written}, "
          f"installed in solutions/: {installed}")


if __name__ == "__main__":
    main()
