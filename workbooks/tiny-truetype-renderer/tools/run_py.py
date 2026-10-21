"""Runs a Python project for the checker and the book.

    python -P tools/run_py.py <project> <id> <input> <output>   assignment <id>'s program
    python -P tools/run_py.py <project> -m <module> [args...]    the finished program (python -m)
    python -P tools/run_py.py --compile <project>                the "build": every .py checked for syntax

<project> is solutions/ (yours) or a snapshot of the reference. Its src/ folder goes on the import
path, so assignments/assignment_07_x.py can say `from mypackage.x509 import certificate`, the same
way it would after `pip install -e .`.

A NotImplementedError ends the program with exit code 99 and "not implemented: <what>", which the
checker reports as "Not implemented yet": the Boilerplate raises it from every function left TODO.
"""

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOT_IMPLEMENTED_EXIT = 99


def compile_all(folder: Path) -> int:
    """Checks every .py under `folder` for syntax errors and prints each one the way a Python
    traceback does (the checker and the book read file and line from it). Writes no .pyc files."""
    errors = 0
    for path in sorted(folder.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except SyntaxError as e:
            errors += 1
            shown = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
            print(f'  File "{shown}", line {e.lineno}')
            if e.text:
                print(f"    {e.text.rstrip()}")
            print(f"{type(e).__name__}: {e.msg}")
        except (UnicodeDecodeError, ValueError) as e:
            errors += 1
            print(f'  File "{path.relative_to(ROOT).as_posix()}", line 1\nSyntaxError: {e}')
    return 1 if errors else 0


def missing_module(error: ImportError, project: Path):
    """When an import failed because a project module doesn't exist yet: which file, and which
    assignment creates it. None for any other import error."""
    import re
    name = error.name or ""
    m = re.search(r"cannot import name '(\w+)'", str(error))
    candidates = [f"{name}.{m.group(1)}"] if m else []
    candidates.append(name)
    if (m := re.search(r"No module named '?([\w.]+)'?", str(error))):  # python -m pkg, no __main__.py yet
        candidates.append(m.group(1))
    for dotted in candidates:
        rel = "src/" + dotted.replace(".", "/") + ".py"
        if dotted and not (project / rel).exists() and not (project / rel).with_suffix("").is_dir():
            try:
                sys.path.insert(0, str(ROOT / "tools"))
                import project as layout  # tools/project.py: which assignment owns a file
                owner = layout.owner(layout.load_config(), rel)
            except Exception:
                owner = None
            return f"{rel} is missing: do assignment {owner} first" if owner else f"{rel} is missing"
    return None


def run(target, project: Path) -> int:
    """Runs `target()` and turns NotImplementedError into the checker's exit code."""
    try:
        target()
    except NotImplementedError as e:
        print(f"not implemented: {e or 'a function'}", file=sys.stderr)
        return NOT_IMPLEMENTED_EXIT
    except ImportError as e:
        message = missing_module(e, project)
        if not message:
            raise
        print(message, file=sys.stderr)
        return 1
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
    return 0


def main(argv: list) -> int:
    if argv[:1] == ["--compile"] and len(argv) == 2:
        return compile_all(ROOT / argv[1])
    if len(argv) < 2:
        sys.exit(__doc__)
    project = (ROOT / argv[0]).resolve()
    sys.path.insert(0, str(project / "src"))
    if argv[1] == "-m":
        module, args = argv[2], argv[3:]
        sys.argv = [module, *args]
        return run(lambda: runpy.run_module(module, run_name="__main__", alter_sys=True), project)
    cid, rest = argv[1], argv[2:]
    matches = sorted((project / "assignments").glob(f"assignment_{cid}_*.py"))
    if len(matches) != 1:
        print(f"expected one assignments/assignment_{cid}_*.py in {argv[0]}, found {len(matches)}", file=sys.stderr)
        return 2
    sys.argv = [str(matches[0]), *rest]
    return run(lambda: runpy.run_path(str(matches[0]), run_name="__main__"), project)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
