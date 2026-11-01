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
import os
import posixpath
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STARTERS = ROOT / "starters"

# This computer's names for the commands the tools tell you to type, and what a built program's
# file name ends in. workbook.json writes program names as e.g. build/solutions/assignment_{id}{exe}.
WINDOWS = os.name == "nt"
EXE = ".exe" if WINDOWS else ""
CHECK = ".\\check" if WINDOWS else "./check.sh"
STUDY = ".\\study" if WINDOWS else "./study.sh"
PY = "py" if WINDOWS else "python3"
OLD_EXE = re.compile(r'^("?[^\s"]+?)\.exe(?="?(?:\s|$))', re.I)  # a command's program, named with .exe


def native(command: str) -> str:
    """A command from workbook.json as this computer runs it: {exe} becomes .exe on Windows and
    nothing on macOS or Linux, so one workbook.json serves all three. Workbooks made before {exe}
    wrote .exe after the program's name itself; on macOS and Linux that is left out too."""
    command = command.replace("{exe}", EXE)
    return command if WINDOWS else OLD_EXE.sub(r"\1", command)


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
                         "to work in another language, ask your coding assistant to set it up")
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
#
# A section can also be replaced later: `// ---- Assignment 04, until 06: a fiber for every child ----`
# is assignment 04's section, and it is left out as of assignment 06 and every later one (06 has
# a section of its own that takes its place). The line shown for it before 06 doesn't say "until",
# so an earlier Editorial doesn't name the assignment that replaces it.

# Folders at the top of the reference project that are never part of it: installed packages and
# build output.
REFERENCE_SKIP = {"node_modules", "build"}

SECTION = re.compile(r"^[ \t]*(?://|#|--)[ \t]*-{2,}[ \t]*(?:Assignment|Checkpoint)[ \t]+(\d+)\b"
                     r"(?:[ \t]*[,;]?[ \t]*until[ \t]+(\d+)\b)?.*$", re.M)
UNTIL = re.compile(r"\b((?:Assignment|Checkpoint)[ \t]+\d+)\b[ \t]*[,;]?[ \t]*until[ \t]+\d+\b")


def as_of(text: str, upto: str) -> str:
    """A reference file's text after checkpoint `upto`: later checkpoints' sections left out, and
    so are the sections an earlier checkpoint marked `until` a checkpoint that has now come."""
    kept, start, keep = [], 0, True
    for m in SECTION.finditer(text):
        if keep:
            kept.append(text[start:m.start()])
        start = m.start()
        keep = int(m.group(1)) <= int(upto) and not (m.group(2) and int(upto) >= int(m.group(2)))
        if keep and m.group(2):  # still in force at `upto`: show its marker without the end
            kept.append(UNTIL.sub(r"\1", m.group(0), count=1))
            start = m.end()
    if keep:
        kept.append(text[start:])
    return "".join(kept).rstrip() + "\n"


def reference_as_of(config: dict, upto: str) -> dict:
    """{path: text} of the reference project after checkpoint `upto`: the files created by it and
    the checkpoints before it, each without later sections, plus the files no checkpoint owns
    (the build file, a Python package's __init__.py files) and the third-party files the
    learner's project gets too ("copy")."""
    base = ROOT / config["project"]["reference"]
    owned = {p for cid in config["checkpoints"] for p in own_files(config, cid)}
    files = {}
    for p in sorted(base.rglob("*")):
        path = p.relative_to(base).as_posix()
        if path.split("/")[0] in REFERENCE_SKIP or "__pycache__" in p.parts:
            continue
        if p.is_file() and path not in owned:
            files[path] = p.read_text(encoding="utf-8")  # CMakeLists.txt, pyproject.toml, package.json, __init__.py
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
PY_IMPORT = re.compile(r"^[ \t]*(?:from[ \t]+(\.*)([\w.]*)[ \t]+import[ \t]+(?:\(([^)]*)\)|([\w ,*]+))"
                       r"|import[ \t]+([\w., ]+))", re.M)


def py_module(files: dict, dotted: str, include_dirs) -> list:
    """The files that importing `dotted` (e.g. pkiaudit.ecc.curve) runs: each package's
    __init__.py on the way, and the module itself, found under an include folder."""
    parts = [p for p in dotted.split(".") if p]
    for base in include_dirs:
        prefix = f"{base}/" if base else ""
        found = [f"{prefix}{'/'.join(parts[:i])}/__init__.py" for i in range(1, len(parts) + 1)]
        found = [f for f in found if f in files]
        module = f"{prefix}{'/'.join(parts)}.py"
        if module in files:
            return found + [module]
        if found and found[-1] == f"{prefix}{'/'.join(parts)}/__init__.py":
            return found
    return []


def py_imports(files: dict, path: str, include_dirs) -> list:
    """The project files a Python file imports, relative imports included."""
    out = []
    # The file's own package, as a dotted name under its include folder (for relative imports).
    package = None
    for base in include_dirs:
        prefix = f"{base}/" if base else ""
        if path.startswith(prefix):
            package = path[len(prefix):].rpartition("/")[0].replace("/", ".")
            break
    for dots, module, grouped, names, plain in PY_IMPORT.findall(files[path]):
        names = grouped or names
        if plain:
            for name in plain.split(","):
                out += py_module(files, name.split()[0] if name.split() else "", include_dirs)
            continue
        if dots:
            if package is None:
                continue
            up = package.split(".") if package else []
            up = up[:len(up) - (len(dots) - 1)] if len(dots) > 1 else up
            module = ".".join([*up, module] if module else up)
        out += py_module(files, module, include_dirs)
        for name in re.sub(r"#.*", "", names).split(","):
            name = name.split()[0] if name.split() else ""
            if name and name != "*":  # `from pkg import module` imports a submodule
                out += py_module(files, f"{module}.{name}", include_dirs)
    return out


# JavaScript: the module specifiers a file names. Line-anchored, so a commented-out import isn't
# followed; an import list may span lines. A specifier that doesn't start with "." (react, node:fs)
# is a package, not a project file.
JS_FROM = re.compile(r"""^[ \t]*(?:import|export)\b(?:[^;'"`/]|/(?![/*])|//[^\n]*|/\*[\s\S]*?\*/)*?"""
                     r"""\bfrom[ \t]*['"]([^'"\n]+)['"]""", re.M)
JS_BARE_IMPORT = re.compile(r"""^[ \t]*import[ \t]*['"]([^'"\n]+)['"]""", re.M)
JS_DYNAMIC = re.compile(r"""\bimport[ \t]*\([ \t]*['"]([^'"\n]+)['"][ \t]*\)""")


def js_module(files: dict, importer: str, spec: str):
    """The project file a relative specifier names, or None. `./x.js` is what ES modules write;
    `./x` and `./dir` (for dir/index.js) are found too."""
    if not spec.startswith("."):
        return None
    base = posixpath.normpath(posixpath.join(posixpath.dirname(importer), spec))
    for candidate in (base, f"{base}.js", f"{base}.mjs", f"{base}/index.js"):
        if candidate in files:
            return candidate
    return None


def js_imports(files: dict, path: str) -> list:
    """The project files a JavaScript file imports: import ... from, import '...', export ... from
    and import('...'), with relative specifiers resolved against the importing file."""
    text = files[path]
    specs = JS_FROM.findall(text) + JS_BARE_IMPORT.findall(text) + JS_DYNAMIC.findall(text)
    return [found for spec in specs if (found := js_module(files, path, spec))]


def closure(files: dict, first: str, include_dirs=("src",)) -> list:
    """The files a program is built from, out of {path: text}: `first` and everything it uses.
    C and C++: every file it includes with #include "..." (found next to the including file or
    in an include folder), and the .cpp next to each header. Python: every project module it
    imports, with the packages' __init__.py files. JavaScript: every project file it imports
    (import ... from, import '...', export ... from, import('...')), found from the importing
    file's own folder."""
    found, queue = [], [first]
    while queue:
        path = queue.pop(0)
        if path in found or path not in files:
            continue
        found.append(path)
        stem, _, ext = path.rpartition(".")
        if ext == "py":
            queue += py_imports(files, path, include_dirs)
            continue
        if ext in ("js", "mjs"):
            queue += js_imports(files, path)
            continue
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
        print(f"Each assignment's files appear when you start it, in the book or with {CHECK} NN.")
        return 0
    if command == "start" and len(argv) > 1:
        cid = f"{int(argv[1]):02d}"
        if cid not in config["checkpoints"]:
            print(f"There is no assignment {cid}.")
            return 2
        try:
            created = start(config, cid)
        except NoProject:
            print(f"Set up the project first:  {PY} -P tools/project.py setup")
            return 2
        print("Created: " + ", ".join(created) if created else f"Assignment {cid}'s files are already there.")
        return 0
    if command == "status":
        if not exists(config):
            print(f"No project yet. Set it up with:  {PY} -P tools/project.py setup")
            return 0
        for path, cid, state in status(config):
            if state != "missing":
                print(f"  {cid}  {state:<8} {config['project']['dir']}/{path}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
