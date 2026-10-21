"""Languages a learner can build the project in: which are installed here, and how to install the rest.

    py -P tools/langs.py          list them, with what's installed on this computer

A workbook's project is set up in one language (workbook.json "project"). When a learner wants
another, Claude asks which, checks it here, offers to install what's missing, and sets up a
project in that language (see the blog-to-leetcode skill). The checker also uses parse_errors()
below to point the book at the line of each compiler error.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# key -> label, file extension, and the tools that build or run it (the first one found is used).
LANGUAGES = {
    "c": {"label": "C", "ext": ".c", "tools": ["gcc", "clang", "cc"]},
    "cpp": {"label": "C++", "ext": ".cpp", "tools": ["g++", "clang++", "c++"]},
    "go": {"label": "Go", "ext": ".go", "tools": ["go"]},
    "rust": {"label": "Rust", "ext": ".rs", "tools": ["cargo", "rustc"]},
    "python": {"label": "Python", "ext": ".py", "tools": []},
    "javascript": {"label": "JavaScript", "ext": ".js", "tools": ["node"]},
    "typescript": {"label": "TypeScript", "ext": ".ts", "tools": ["node"], "min": (22, 6)},
    "lua": {"label": "Lua", "ext": ".lua", "tools": ["lua", "lua5.4", "lua54", "luajit"]},
}

# How to install each language's tools, per operating system.
INSTALL = {
    "c": {"windows": "winget install BrechtSanders.WinLibs.POSIX.UCRT", "macos": "xcode-select --install",
          "linux": "sudo apt install build-essential", "url": "https://winlibs.com/"},
    "cpp": {"windows": "winget install BrechtSanders.WinLibs.POSIX.UCRT", "macos": "xcode-select --install",
            "linux": "sudo apt install build-essential", "url": "https://winlibs.com/"},
    "go": {"windows": "winget install GoLang.Go", "macos": "brew install go", "linux": "sudo apt install golang-go",
           "url": "https://go.dev/dl/"},
    "rust": {"windows": "winget install Rustlang.Rustup", "macos": "curl https://sh.rustup.rs -sSf | sh",
             "linux": "curl https://sh.rustup.rs -sSf | sh", "url": "https://rustup.rs/",
             "note": "On Windows without Visual Studio's C++ build tools, run `rustup default stable-x86_64-pc-windows-gnu` afterwards (it links with the MinGW gcc you have for C++)."},
    "python": {"windows": "winget install Python.Python.3.12", "macos": "brew install python", "linux": "sudo apt install python3",
               "url": "https://www.python.org/downloads/"},
    "javascript": {"windows": "winget install OpenJS.NodeJS.LTS", "macos": "brew install node",
                   "linux": "install Node.js from https://nodejs.org/en/download (distribution packages are often old)",
                   "url": "https://nodejs.org/"},
    "typescript": {"windows": "winget install OpenJS.NodeJS.LTS", "macos": "brew install node",
                   "linux": "install Node.js from https://nodejs.org/en/download (distribution packages are often old)",
                   "url": "https://nodejs.org/", "note": "TypeScript runs on Node.js 22.6 or newer; nothing else to install."},
    "lua": {"windows": "winget install DEVCOM.Lua", "macos": "brew install lua", "linux": "sudo apt install lua5.4",
            "url": "https://www.lua.org/download.html"},
}


def platform() -> str:
    return "windows" if os.name == "nt" else "macos" if sys.platform == "darwin" else "linux"


def _version(tool: str) -> tuple:
    try:
        out = subprocess.run([tool, "--version"], capture_output=True, text=True, timeout=10).stdout
        m = re.search(r"(\d+)\.(\d+)", out)
        return (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    except (OSError, subprocess.SubprocessError):
        return (0, 0)


def find_tool(lang: str):
    """(path of the tool to use, or None, problem text or None)."""
    spec = LANGUAGES[lang]
    if lang == "python":
        return sys.executable, None  # the Python running this
    for name in spec["tools"]:
        path = shutil.which(name)
        if path:
            if spec.get("min"):
                have = _version(path)
                if have < spec["min"]:
                    want = ".".join(map(str, spec["min"]))
                    return None, f"{spec['label']} needs Node.js {want} or newer; this computer has {have[0]}.{have[1]}."
            return path, None
    return None, f"{spec['label']} isn't installed (or isn't on PATH): none of {', '.join(spec['tools'])} was found."


def availability(lang: str) -> dict:
    tool, problem = find_tool(lang)
    hint = INSTALL.get(lang, {})
    return {"key": lang, "label": LANGUAGES[lang]["label"], "installed": tool is not None, "problem": problem,
            "install": {"command": hint.get(platform(), ""), "url": hint.get("url", ""), "note": hint.get("note", "")}}


def install_text(lang: str) -> str:
    a = availability(lang)
    lines = [a["problem"] or "", f"Install it with:  {a['install']['command']}", f"or see {a['install']['url']}"]
    if a["install"]["note"]:
        lines.append(a["install"]["note"])
    return "\n".join(lines)


def parse_errors(output: str) -> list:
    """file:line(:column) and message for each error in build output, in any of the languages."""
    found = []

    def add(file, line, col, kind, message):
        found.append({"file": file.replace("\\", "/"), "line": int(line), "column": int(col or 1),
                      "kind": kind, "message": message.strip()})

    for m in re.finditer(r"^(.*?\.(?:c|cc|cpp|cxx|h|hpp)):(\d+):(\d+): (fatal error|error|warning): (.*)$", output, re.M):
        add(m.group(1), m.group(2), m.group(3), "warning" if m.group(4) == "warning" else "error", m.group(5))
    for m in re.finditer(r"^(\S+?\.go):(\d+):(\d+): (.*)$", output, re.M):  # Go
        add(m.group(1), m.group(2), m.group(3), "error", m.group(4))
    for m in re.finditer(r"^(error|warning)(?:\[\w+\])?: (.*)\n\s*--> (.+?):(\d+):(\d+)", output, re.M):  # Rust
        add(m.group(3), m.group(4), m.group(5), m.group(1), m.group(2))
    # Python: a SyntaxError's own location line has no ", in ..." after the line number.
    for m in re.finditer(r'File "(.+?\.py)", line (\d+)\s*$[\s\S]*?^(\w*Error): (.*)$', output, re.M):
        add(m.group(1), m.group(2), None, "error", f"{m.group(3)}: {m.group(4)}")
    for m in re.finditer(r"^(.+?\.(?:js|mjs)):(\d+)\s*$[\s\S]*?^(\w*Error): (.*)$", output, re.M):  # node --check
        add(m.group(1), m.group(2), None, "error", f"{m.group(3)}: {m.group(4)}")
    for m in re.finditer(r"^(\S+?\.ts):(\d+):(\d+): error: (.*)$", output, re.M):  # TS_SYNTAX_CHECK
        add(m.group(1), m.group(2), m.group(3), "error", m.group(4))
    for m in re.finditer(r"(\S+?\.lua):(\d+): (.*)$", output, re.M):  # Lua's loadfile
        add(m.group(1), m.group(2), None, "error", m.group(3))
    # Make paths relative to the workbook, so the book can find the file.
    root = ROOT.as_posix().lower()
    for e in found:
        f = e["file"]
        if f.lower().startswith(root + "/"):
            e["file"] = f[len(root) + 1:]
    return found[:50]


def main() -> int:
    for key in LANGUAGES:
        a = availability(key)
        state = "installed" if a["installed"] else f"not installed - {a['install']['command']}"
        print(f"  {key:<11} {a['label']:<11} {state}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
