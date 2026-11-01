"""Runs a JavaScript project for the checker and the book.

    python -P tools/run_js.py <project> <id> <input> <output>   assignment <id>'s program
    python -P tools/run_js.py <project> -m <file> [args...]      a project file, e.g. src/main.js
    python -P tools/run_js.py --compile <project>                the "build": every .js checked for syntax

<project> is solutions/ (yours) or a snapshot of the reference. Programs are ES modules, run with
the first `node` on PATH (this workbook needs Node.js 26 or newer), from the workbook folder.

A program that exits with code 99 ("not implemented: <what>") passes straight through: the checker
reports it as "Not implemented yet". So does a program that dies on an uncaught
`Error: not implemented ...`, as the Boilerplate's TODO functions do outside the harness.

When a program can't start because a project file doesn't exist yet (or is still an empty
starter), the message says which file and which assignment writes it.
"""

import os
import re
import shutil
import signal
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote, urlparse
from urllib.request import url2pathname

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import langs  # noqa: E402  (tools/langs.py: which node, and how old)

NOT_IMPLEMENTED_EXIT = 99
SKIP_DIRS = {"node_modules", "tools"}  # folders --compile leaves alone (dot folders too)
_job = None  # the Windows job that keeps node tied to this process (see contain)


# ---- Finding node ---------------------------------------------------------------------

def find_node():
    """The node to run, or None after printing why there is none (not installed, or too old)."""
    path, problem = langs.find_tool("javascript")
    if path:
        return path
    print(install_message(problem), file=sys.stderr)
    return None


def install_message(problem: str) -> str:
    hint = langs.availability("javascript")["install"]
    return f"{problem} Install it with: {hint['command']} (or see {hint['url']})."


def too_old():
    """A message when the node on PATH is older than this workbook needs, else None."""
    path, problem = langs.find_tool("javascript")
    return None if path or "needs Node.js" not in (problem or "") else install_message(problem)


# ---- The build: a syntax check -----------------------------------------------------------

def shown(path: Path) -> str:
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def syntax_error(path: Path, stderr: str) -> str:
    """One failed `node --check` as the checker and the book read it: `file:line`, the source line
    and `SyntaxError: message`."""
    lines = stderr.splitlines()
    at = next((i for i, l in enumerate(lines) if re.search(r"\.(?:c|m)?js:\d+\s*$", l)), None)
    row = int(re.search(r":(\d+)\s*$", lines[at]).group(1)) if at is not None else 1
    source = lines[at + 1].strip() if at is not None and at + 1 < len(lines) else ""
    found = next((l for l in lines if re.match(r"\w*Error: ", l)), None)
    return "\n".join([f"{shown(path)}:{row}", *([f"    {source}"] if source else []),
                      found or (lines[-1] if lines else "SyntaxError: the file can't be parsed")])


def compile_all(folder: Path) -> int:
    """Checks every .js and .mjs under `folder` for syntax errors with `node --check` and prints
    each failure. Nothing is written."""
    node = find_node()
    if node is None:
        return 1
    files = sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix in (".js", ".mjs")
                   and not any(part in SKIP_DIRS or part.startswith(".") for part in p.relative_to(folder).parts[:-1]))

    def check(path: Path):
        return path, subprocess.run([node, "--check", str(path)], capture_output=True, text=True,
                                    encoding="utf-8", errors="replace")

    with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 4)) as pool:
        failed = [(p, proc) for p, proc in pool.map(check, files) if proc.returncode != 0]
    for path, proc in failed:
        print(syntax_error(path, proc.stderr))
    return 1 if failed else 0


# ---- Running a program ---------------------------------------------------------------------

def contain(proc: subprocess.Popen):
    """Makes node die with this process. The checker stops a program that runs too long by killing
    this script, and without this node would go on running (in a loop, perhaps) after it."""
    try:
        if os.name == "nt":
            windows_job(proc)
        elif sys.platform != "linux":  # Linux sets this before node starts (parent_dies)
            subprocess.Popen([sys.executable, "-c", REAPER, str(os.getpid()), str(proc.pid)], start_new_session=True,
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:  # noqa: BLE001 - only a safety net: the run itself never depends on it
        pass


REAPER = """
import os, signal, sys, time
parent, child = int(sys.argv[1]), int(sys.argv[2])
def alive(pid):
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except OSError:
        return True
    return True
while alive(parent) and alive(child):
    time.sleep(0.2)
if alive(child) and not alive(parent):
    try:
        os.kill(child, signal.SIGKILL)
    except OSError:
        pass
"""


def parent_dies():
    """For Linux, run in the new process before node starts: SIGKILL it when this process goes."""
    try:
        import ctypes
        ctypes.CDLL("libc.so.6", use_errno=True).prctl(1, signal.SIGKILL)  # PR_SET_PDEATHSIG
    except Exception:  # noqa: BLE001
        pass


def windows_job(proc: subprocess.Popen):
    """Puts the process in a job object that kills it when the job's last handle closes, which
    happens when this process ends, however it ends."""
    import ctypes
    from ctypes import wintypes

    class Basic(ctypes.Structure):
        _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                    ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                    ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                    ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                    ("SchedulingClass", wintypes.DWORD)]

    class Counters(ctypes.Structure):
        _fields_ = [(n, ctypes.c_uint64) for n in ("ReadOps", "WriteOps", "OtherOps", "ReadBytes", "WriteBytes", "OtherBytes")]

    class Extended(ctypes.Structure):
        _fields_ = [("Basic", Basic), ("Io", Counters), ("ProcessMemoryLimit", ctypes.c_size_t),
                    ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                    ("PeakJobMemoryUsed", ctypes.c_size_t)]

    global _job
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateJobObjectW.restype = wintypes.HANDLE
    kernel32.CreateJobObjectW.argtypes = [wintypes.LPVOID, wintypes.LPCWSTR]
    kernel32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD]
    kernel32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    job = kernel32.CreateJobObjectW(None, None)
    info = Extended()
    info.Basic.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    if job and kernel32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
        if kernel32.AssignProcessToJobObject(job, int(proc._handle)):  # noqa: SLF001
            _job = job  # never closed by hand: Windows closes it when this process ends


def project_file(project: Path, path: Path):
    """A path inside the project folder as the project names it (src/didact/dom.js), else None."""
    try:
        return path.resolve().relative_to(project).as_posix()
    except ValueError:
        return None


def file_url_path(text: str) -> Path:
    """A file:// URL or a plain path, as a Path."""
    return Path(url2pathname(unquote(urlparse(text).path))) if text.startswith("file:") else Path(text)


def missing_file(stderr: str, project: Path, current):
    """When node couldn't start because of a project file an assignment hasn't written yet: which
    file and which assignment writes it. None for any other failure (a typo in the learner's own
    import, a package that isn't installed), where node's own message is the useful one."""
    gone = re.search(r"Cannot find module '([^']+)' imported from ", stderr)
    export = re.search(r"The requested module '([^']+)' does not provide an export named", stderr)
    importer = re.search(r"^(file:///\S+?\.m?js):\d+\s*$", stderr, re.M)
    if gone:
        target = file_url_path(gone.group(1))
    elif export and importer and export.group(1).startswith("."):
        target = file_url_path(importer.group(1)).parent / export.group(1)
    else:
        return None
    rel = project_file(project, target)
    if rel is None:
        return None
    here = project / rel
    # A file that exists but exports nothing is a starter nobody has written yet.
    if export and here.exists() and re.search(r"^\s*export\b", here.read_text(encoding="utf-8", errors="replace"), re.M):
        return None
    try:
        import project as layout  # tools/project.py: which assignment owns a file
        owner = layout.owner(layout.load_config(), rel)
    except Exception:  # noqa: BLE001
        owner = None
    if owner is None or (current is not None and owner.isdigit() and current.isdigit() and int(owner) == int(current)):
        return None  # not one of the layout's files, or the learner's own file for this very assignment
    return f"{rel} is missing: do assignment {owner} first"


def not_implemented(stderr: str):
    """The text after `Error: not implemented` when a program died on that error, else None."""
    found = re.search(r"^\w*Error: not implemented[:\s]*(.*)$", stderr, re.M)
    return None if found is None else found.group(1).strip() or "a function"


def with_summary(stderr: str) -> str:
    """What node printed about a crash, without its closing "Node.js v26" line, and ending with the
    error's own line: the checker shows the last line of stderr next to "Runtime Error"."""
    lines = stderr.rstrip().splitlines()
    while lines and (not lines[-1].strip() or lines[-1].startswith("Node.js v")):
        lines.pop()
    error = next((l for l in lines if re.match(r"(?:\w+ )?\w*Error(?: \[\w+\])?: ", l)), None)
    if error and lines[-1] != error:
        lines.append(error)
    return "\n".join(lines)


def run(node: str, args: list, project: Path, current) -> int:
    """Runs node on the program, passes its output through and returns its exit code, turning the
    "not started yet" situations into the messages above."""
    spawn = {"preexec_fn": parent_dies} if sys.platform == "linux" else {}
    try:
        proc = subprocess.Popen([node, *args], stderr=subprocess.PIPE, text=True, encoding="utf-8",
                                errors="replace", **spawn)
    except OSError as e:
        print(f"could not start node: {e}", file=sys.stderr)
        return 1
    contain(proc)
    try:
        _, stderr = proc.communicate()
    except KeyboardInterrupt:  # Ctrl+C in a terminal reaches node as well; just stop quietly
        proc.kill()
        return 130
    code = proc.returncode
    if code == 0 or code == NOT_IMPLEMENTED_EXIT:
        sys.stderr.write(stderr)
        return code
    if (what := not_implemented(stderr)) is not None:
        print(f"not implemented: {what}", file=sys.stderr)
        return NOT_IMPLEMENTED_EXIT
    if (message := missing_file(stderr, project, current)) is not None:
        print(message, file=sys.stderr)
        return 1
    if (text := with_summary(stderr)):
        print(text, file=sys.stderr)
    if (old := too_old()) is not None:  # the failure may be a feature this node doesn't have
        print(old, file=sys.stderr)
    if code < 0 and os.name != "nt":  # stopped by a signal: stop the same way, so the checker can say which
        try:
            signal.signal(-code, signal.SIG_DFL)
            os.kill(os.getpid(), -code)
        except (OSError, ValueError):
            pass
    return code


def main(argv: list) -> int:
    if argv[:1] == ["--compile"] and len(argv) == 2:
        return compile_all(ROOT / argv[1])
    if len(argv) < 2:
        sys.exit(__doc__)
    project = (ROOT / argv[0]).resolve()
    if argv[1] == "-m":
        if len(argv) < 3:
            sys.exit(__doc__)
        target, current, rest = project / argv[2], None, argv[3:]
        if not target.is_file():
            print(f"{argv[2]} is not in {argv[0]}", file=sys.stderr)
            return 2
    else:
        current, rest = argv[1], argv[2:]
        matches = sorted((project / "assignments").glob(f"assignment_{current}_*.js"))
        if len(matches) != 1:
            print(f"expected one assignments/assignment_{current}_*.js in {argv[0]}, found {len(matches)}", file=sys.stderr)
            return 2
        target = matches[0]
    # The build (--compile) has already checked node's version. Each run only looks for node, which
    # costs nothing; a failed run asks whether the node is too old (see run).
    node = shutil.which("node") or find_node()
    if node is None:
        return 1
    return run(node, [str(target), *rest], project, current)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
