"""Your project: the program the post builds, written by you one assignment at a time.

    py -P tools/project.py setup [language]   create the project folder (build file, README, .gitignore)
    py -P tools/project.py start 07           create assignment 07's files (existing files are never touched)
    py -P tools/project.py status             the project's files, and which assignment each belongs to

The layout is set in workbook.json: "project" says where the project lives and what it starts
with, and each assignment lists the files it creates ("files") and the earlier files it adds to
("extends"). Each assignment also has a program the checker runs ("solution", e.g.
assignments/assignment_07_simple_glyph.cpp) that reads a test input, calls the project and writes the
output. Starting an assignment copies its starters: the boilerplate by default
(project.starter in workbook.json), or the blank ones.
"""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STARTERS = ROOT / "starters"


class NoProject(Exception):
    """The project folder hasn't been set up yet."""


def load_config() -> dict:
    return json.loads((ROOT / "workbook.json").read_text(encoding="utf-8"))


def home(config: dict) -> Path:
    """The project folder, e.g. solutions/."""
    return ROOT / config["project"]["dir"]


def exists(config: dict) -> bool:
    return home(config).is_dir()


def rel(config: dict, path: Path) -> str:
    """A path inside the project, relative to the project folder."""
    return path.resolve().relative_to(home(config).resolve()).as_posix()


def entry(config: dict, cid: str) -> str:
    """The checkpoint's entry program, relative to the project folder."""
    return rel(config, ROOT / config["checkpoints"][cid]["solution"])


def own_files(config: dict, cid: str) -> list:
    """What starting the checkpoint creates: its entry program, then the project files it adds."""
    return [entry(config, cid)] + list(config["checkpoints"][cid].get("files", []))


def touched_files(config: dict, cid: str) -> list:
    """Every file the checkpoint has you write in: its own, then the earlier ones it adds to."""
    return own_files(config, cid) + list(config["checkpoints"][cid].get("extends", []))


def owner(config: dict, path: str):
    """The checkpoint that creates a project file (or whose entry program it is), or None."""
    for cid in config["checkpoints"]:
        if path in own_files(config, cid):
            return cid
    return None


def starter(kind: str, path: str) -> Path:
    """A file's starter: kind is "blank" or "boilerplate"."""
    return STARTERS / kind / path


def lines(path: Path) -> list:
    return [line.rstrip() for line in path.read_text(encoding="utf-8", errors="replace").splitlines()]


def still_blank(config: dict, path: str) -> bool:
    """True while a project file is unchanged from its blank starter (line endings ignored)."""
    mine, blank = home(config) / path, starter("blank", path)
    return mine.exists() and blank.exists() and lines(mine) == lines(blank)


def setup(config: dict, language: str = "") -> list:
    """Creates the project folder with what it starts with. Returns the files created."""
    spec = config["project"]
    if language and language.lower() not in (spec["language"], *spec.get("aliases", [])):
        raise ValueError(f"this workbook's project is set up for {spec['languageLabel']}; "
                         "to work in another language, ask Claude to set it up")
    created = []
    skeleton = STARTERS / "project"
    sources = {p.relative_to(skeleton).as_posix(): p for p in sorted(skeleton.rglob("*")) if p.is_file()}
    sources.update({dest: ROOT / src for dest, src in spec.get("copy", {}).items()})
    for dest, src in sources.items():
        target = home(config) / dest
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, target)
            created.append(dest)
    return created


def start(config: dict, cid: str, kind: str = "") -> list:
    """Creates the assignment's files, and any earlier file it adds to that's missing, from their
    starters: `kind` ("boilerplate" or "blank"), else workbook.json's project.starter, else the
    boilerplate. A file without that starter gets its blank one. Never touches an existing file."""
    if not exists(config):
        raise NoProject(config["project"]["dir"])
    kind = kind or config["project"].get("starter", "boilerplate")
    created = []
    for path in touched_files(config, cid):
        target, source = home(config) / path, starter(kind, path)
        if not source.exists():
            source = starter("blank", path)
        if not target.exists() and source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            created.append(path)
    return created


def use_starter(config: dict, cid: str, kind: str) -> list:
    """Replaces the checkpoint's own files with its blank or boilerplate starters (the book asks
    first). Earlier files it only adds to are left alone. Returns the files written."""
    written = []
    for path in own_files(config, cid):
        source = starter(kind, path)
        if source.exists():
            target = home(config) / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            written.append(path)
    return written


# ---- The reference project, as it stands after each checkpoint --------------------------
#
# A reference file that later checkpoints add to is split into sections by marker lines such
# as `// ---- Checkpoint 11: curves ----`. Everything before the first marker belongs to the
# checkpoint that creates the file. "The reference after checkpoint N" leaves out the sections
# of later checkpoints and the files they create: that's what -Ref builds and proves for N,
# and what the Editorial for N shows, so it never gives away a later checkpoint.

SECTION = re.compile(r"^[ \t]*(?://|#|--)[ \t]*-{2,}[ \t]*(?:Assignment|Checkpoint)[ \t]+(\d+)\b.*$", re.M)


def as_of(text: str, upto: str) -> str:
    """A reference file's text after checkpoint `upto`: later checkpoints' sections left out."""
    kept, start, keep = [], 0, True
    for m in SECTION.finditer(text):
        if keep:
            kept.append(text[start:m.start()])
        start, keep = m.start(), int(m.group(1)) <= int(upto)
    if keep:
        kept.append(text[start:])
    return "".join(kept).rstrip() + "\n"


def reference_as_of(config: dict, upto: str) -> dict:
    """{path: text} of the reference project after checkpoint `upto`: the files created by it and
    the checkpoints before it, each without later sections, plus the build file and the
    third-party files the learner's project gets too ("copy")."""
    base = ROOT / config["project"]["reference"]
    files = {p.name: p.read_text(encoding="utf-8") for p in base.iterdir() if p.is_file()}  # CMakeLists.txt
    files.update({dest: (ROOT / src).read_text(encoding="utf-8")
                  for dest, src in config["project"].get("copy", {}).items()})
    for cid in config["checkpoints"]:
        if int(cid) > int(upto):
            break
        for path in own_files(config, cid):
            if (base / path).exists():
                files[path] = as_of((base / path).read_text(encoding="utf-8"), upto)
    return files


def write_tree(files: dict, dest: Path):
    """Makes `dest` hold exactly `files`. Unchanged files keep their timestamps, so a build there
    only recompiles what changed."""
    dest.mkdir(parents=True, exist_ok=True)
    for path, text in files.items():
        target = dest / path
        if not target.exists() or target.read_text(encoding="utf-8") != text:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8", newline="\n")
    for p in sorted(dest.rglob("*"), reverse=True):
        if p.is_file() and p.relative_to(dest).as_posix() not in files:
            p.unlink()
        elif p.is_dir() and not any(p.iterdir()):
            p.rmdir()


LOCAL_INCLUDE = re.compile(r'^\s*#\s*include\s+"([^"]+)"', re.M)


def closure(files: dict, first: str, include_dirs=("src",)) -> list:
    """The files a program is built from, out of {path: text}: `first`, every file it includes
    with #include "..." (found next to the including file or in an include folder), and the
    .cpp next to each header."""
    found, queue = [], [first]
    while queue:
        path = queue.pop(0)
        if path in found or path not in files:
            continue
        found.append(path)
        stem, _, ext = path.rpartition(".")
        if ext in ("h", "hpp"):
            queue += [f"{stem}.cpp", f"{stem}.cc"]
        folder = path.rpartition("/")[0]
        for name in LOCAL_INCLUDE.findall(files[path]):
            for base in (folder, *include_dirs):
                candidate = f"{base}/{name}" if base else name
                if candidate in files:
                    queue.append(candidate)
                    break
    return found


def status(config: dict) -> list:
    """(path, checkpoint, state) for every file the layout has, in checkpoint order."""
    rows = []
    for cid in config["checkpoints"]:
        for path in own_files(config, cid):
            target = home(config) / path
            state = "missing" if not target.exists() else ("blank" if still_blank(config, path) else "written")
            rows.append((path, cid, state))
    return rows


def main(argv: list) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    config = load_config()
    command = argv[0] if argv else "status"
    if command == "setup":
        try:
            created = setup(config, argv[1] if len(argv) > 1 else "")
        except ValueError as e:
            print(f"Not set up: {e}.")
            return 2
        folder = config["project"]["dir"]
        print(f"Your project is in {folder}/." + (f" Created: {', '.join(created)}." if created else " (Nothing new to create.)"))
        print("Each assignment's files appear when you start it, in the book or with .\\check NN.")
        return 0
    if command == "start" and len(argv) > 1:
        cid = f"{int(argv[1]):02d}"
        if cid not in config["checkpoints"]:
            print(f"There is no assignment {cid}.")
            return 2
        try:
            created = start(config, cid)
        except NoProject:
            print("Set up the project first:  py -P tools/project.py setup")
            return 2
        print("Created: " + ", ".join(created) if created else f"Assignment {cid}'s files are already there.")
        return 0
    if command == "status":
        if not exists(config):
            print("No project yet. Set it up with:  py -P tools/project.py setup")
            return 0
        for path, cid, state in status(config):
            if state != "missing":
                print(f"  {cid}  {state:<8} {config['project']['dir']}/{path}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
