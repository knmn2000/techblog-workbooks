"""The languages a learner can solve checkpoints in: how to find, build, run and install each.

Only a program's output is checked, so any language works. This file lets the checker and the
book build and run each one without the learner writing build files. The workbook's own language
(workbook.json "language", or the solution files' extension) keeps using workbook.json's build
and run commands; every other language is built here, from its file in solutions/:
solutions/p07_simple_glyph.cpp -> solutions/p07_simple_glyph.go, .py, ...

To add a language: an entry in LANGUAGES (and INSTALL), and its branches in build() and run().
"""

import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXE = ".exe" if os.name == "nt" else ""

# key -> label, file extension, line comment, CodeMirror MIME type, the tools that can build or run
# it (first found wins), an empty program, and how shared code in solutions/common/ is used.
LANGUAGES = {
    "c": {"label": "C", "ext": ".c", "comment": "//", "mime": "text/x-csrc", "tools": ["gcc", "clang", "cc"],
          "program": "int main(int argc, char** argv) {\n  return 0;\n}\n",
          "shared": 'put .c and .h files in solutions/common/ and #include "common/name.h"; every .c there is compiled in.'},
    "cpp": {"label": "C++", "ext": ".cpp", "comment": "//", "mime": "text/x-c++src", "tools": ["g++", "clang++", "c++"],
            "program": "int main(int argc, char** argv) {\n}\n",
            "shared": 'put .cpp and .h files in solutions/common/ and #include "common/name.h"; every .cpp there is compiled in.'},
    "go": {"label": "Go", "ext": ".go", "comment": "//", "mime": "text/x-go", "tools": ["go"],
           "program": "package main\n\nfunc main() {\n}\n",
           "shared": "every .go file in solutions/common/ is built with this one: start it with `package main` and call its functions directly."},
    "rust": {"label": "Rust", "ext": ".rs", "comment": "//", "mime": "text/x-rustsrc", "tools": ["rustc"],
             "program": "fn main() {\n}\n",
             "shared": 'add `#[path = "common/name.rs"] mod name;` here, then call `name::f()`.'},
    "python": {"label": "Python", "ext": ".py", "comment": "#", "mime": "text/x-python", "tools": [],
               "program": 'def main():\n    pass\n\n\nif __name__ == "__main__":\n    main()\n',
               "shared": "`from common.name import f`, with the code in solutions/common/name.py."},
    "javascript": {"label": "JavaScript", "ext": ".js", "comment": "//", "mime": "text/javascript", "tools": ["node"],
                   "program": "function main() {\n}\n\nmain();\n",
                   "shared": '`const { f } = require("./common/name.js");`, and `module.exports = { f };` in that file.'},
    "typescript": {"label": "TypeScript", "ext": ".ts", "comment": "//", "mime": "text/typescript", "tools": ["node"],
                   "min": (22, 6),
                   "program": "function main(): void {\n}\n\nmain();\n",
                   "shared": '`import { f } from "./common/name.ts";`, with `export function f` in that file. Node runs it directly; types are erased, not checked.'},
    "lua": {"label": "Lua", "ext": ".lua", "comment": "--", "mime": "text/x-lua", "tools": ["lua", "lua5.4", "lua54", "luajit"],
            "program": "local function main()\nend\n\nmain()\n",
            "shared": 'add `package.path = "solutions/?.lua;" .. package.path`, then `local name = require("common.name")`; end that file with `return { f = f }`.'},
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

TS_SYNTAX_CHECK = r"""
const { stripTypeScriptTypes } = require("node:module");
const fs = require("fs");
let bad = 0;
if (typeof stripTypeScriptTypes === "function") {
  for (const file of process.argv.slice(1)) {
    try { stripTypeScriptTypes(fs.readFileSync(file, "utf8")); }
    catch (e) {
      bad = 1;
      const at = /,-\[(\d+):(\d+)\]/.exec(e.message) || [0, 1, 1];
      const why = e.message.split("\n")[0].replace(/^\s*x\s*/, "");
      console.error(`${file}:${at[1]}:${at[2]}: error: ${why}`);
    }
  }
}
process.exit(bad);
"""

EXT_TO_LANG = {spec["ext"]: key for key, spec in LANGUAGES.items()}
EXT_TO_LANG.update({".cc": "cpp", ".cxx": "cpp", ".mjs": "javascript"})


def platform() -> str:
    return "windows" if os.name == "nt" else "macos" if sys.platform == "darwin" else "linux"


def native(config: dict) -> str:
    """The workbook's own language: the one its starters, boilerplate and reference are in."""
    if config.get("language") in LANGUAGES:
        return config["language"]
    first = next(iter(config["checkpoints"].values()), {"solution": "x.cpp"})
    return EXT_TO_LANG.get(Path(first["solution"]).suffix.lower(), "cpp")


def solution_path(meta: dict, lang: str, config: dict) -> Path:
    if lang == native(config):
        return ROOT / meta["solution"]
    return ROOT / Path(meta["solution"]).with_suffix(LANGUAGES[lang]["ext"])


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
        return sys.executable, None  # the Python running the checker
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
    lines.append("Then close and reopen the book (study.cmd) or the terminal so the new tool is found. "
                 "Or ask Claude to install it for you.")
    return "\n".join(lines)


def blank_starter(lang: str, cid: str, meta: dict, config: dict) -> str:
    """The empty starter for a checkpoint in a language other than the workbook's own."""
    spec = LANGUAGES[lang]
    path = solution_path(meta, lang, config).relative_to(ROOT).as_posix()
    check = config.get("book", {}).get("checkCommand", ".\\check {id}").replace("{id}", cid) + f" -Lang {lang}"
    wrap = lambda text: textwrap.wrap(text, 84, break_long_words=False, break_on_hyphens=False)
    lines = [f"Checkpoint {cid} - {meta['title']} ({spec['label']})", "",
             f"Problem:  {meta['problem']} (also in the web problem book)", f"Check:    {check}", "",
             *wrap(f"The checker runs this file as a program from the workbook folder, with two arguments: "
                   f"the input file to read and the output file to write. Only the output is checked."),
             "", *wrap("Shared code: " + spec["shared"]), "", f"File: {path}"]
    header = "\n".join(f"{spec['comment']} {line}".rstrip() for line in lines)
    return header + "\n\n" + spec["program"]


def _common(*exts) -> list:
    common = ROOT / "solutions" / "common"
    return sorted(p for p in common.rglob("*") if p.suffix.lower() in exts) if common.is_dir() else []


def _rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def build(lang: str, cid: str, meta: dict, config: dict):
    """Builds (or syntax-checks) the learner's file. Returns (ok, output)."""
    src = solution_path(meta, lang, config)
    tool, problem = find_tool(lang)
    if tool is None:
        return False, problem
    out_dir = ROOT / "build" / "lang" / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"p{cid}{EXE}"
    static = ["-static"] if os.name == "nt" else []
    if lang == "c":
        steps = [[tool, "-std=c17", "-O2", "-Wall", "-Wextra", "-Wno-unused-parameter", "-Iinclude", "-Isolutions",
                  _rel(src), *map(_rel, _common(".c")), "-o", _rel(out), "-lm", *static]]
    elif lang == "cpp":
        third = [f"-I{_rel(d)}" for d in sorted((ROOT / "third_party").glob("*")) if d.is_dir()] if (ROOT / "third_party").is_dir() else []
        steps = [[tool, "-std=c++20", "-O2", "-Wall", "-Wextra", "-Wno-unused-parameter", "-Iinclude", "-Isolutions", *third,
                  _rel(src), *map(_rel, _common(".cpp", ".cc", ".cxx")), "-o", _rel(out), *static]]
    elif lang == "go":
        # Go builds the named files only when they're in one folder: copy them into one, keeping
        # names that map back to the real files in error messages.
        work = out_dir / f"p{cid}"
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        names = {src.name: _rel(src)}
        shutil.copyfile(src, work / src.name)
        for f in _common(".go"):
            name = "common__" + "__".join(f.relative_to(ROOT / "solutions" / "common").parts)
            shutil.copyfile(f, work / name)
            names[name] = _rel(f)
        proc = subprocess.run([tool, "build", "-o", str(out), *names], cwd=work, capture_output=True, text=True)
        output = (proc.stdout + proc.stderr).strip()
        for name, real in names.items():
            output = output.replace("./" + name, real).replace(name, real)
        return proc.returncode == 0, output
    elif lang == "rust":
        steps = [[tool, "-O", "--edition", "2021", "--crate-name", f"p{cid}", _rel(src), "-o", _rel(out)]]
    elif lang == "python":
        files = [_rel(src), *map(_rel, _common(".py"))]
        steps = [[tool, "-B", "-c", "import ast, sys\nfor f in sys.argv[1:]: ast.parse(open(f, encoding='utf-8').read(), f)", *files]]
    elif lang == "javascript":
        steps = [[tool, "--check", f] for f in [_rel(src), *map(_rel, _common(".js"))]]
    elif lang == "typescript":
        # `node --check` doesn't look inside .ts files, so strip the types of each file ourselves: the
        # stripper parses the whole file and names the line of any syntax error. (Node 22.13+; older
        # versions skip this and report syntax errors when the tests run.)
        steps = [[tool, "--disable-warning=ExperimentalWarning", "-e", TS_SYNTAX_CHECK,
                  _rel(src), *map(_rel, _common(".ts"))]]
    elif lang == "lua":
        files = ", ".join(f'"{_rel(f)}"' for f in [src, *_common(".lua")])
        steps = [[tool, "-e", f"for _, f in ipairs({{{files}}}) do local ok, err = loadfile(f) "
                              f"if not ok then io.stderr:write(err, '\\n') os.exit(1) end end"]]
    else:
        return False, f"don't know how to build {lang}"
    output = []
    for step in steps:
        proc = subprocess.run(step, cwd=ROOT, capture_output=True, text=True)
        output.append((proc.stdout + proc.stderr).strip())
        if proc.returncode != 0:
            return False, "\n".join(filter(None, output))
    return True, "\n".join(filter(None, output))


def run_command(lang: str, cid: str, meta: dict, config: dict) -> str:
    """The checker's run template ({input} and {output} are filled in per case)."""
    src = _rel(solution_path(meta, lang, config))
    tool, _ = find_tool(lang)
    if lang in ("c", "cpp", "go", "rust"):
        return f"build/lang/{lang}/p{cid}{EXE} {{input}} {{output}}"
    if lang == "python":
        return f'"{tool}" -B {src} {{input}} {{output}}'
    if lang == "javascript":
        return f"node {src} {{input}} {{output}}"
    if lang == "typescript":
        return f"node --experimental-strip-types --disable-warning=ExperimentalWarning {src} {{input}} {{output}}"
    if lang == "lua":
        return f'"{tool}" {src} {{input}} {{output}}'
    raise ValueError(lang)


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
