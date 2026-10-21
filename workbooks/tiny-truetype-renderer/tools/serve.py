"""Opens the workbook in your browser, where Run and Submit really run your code.

    .\\study                          (or double-click study.cmd; ./study.sh on macOS or Linux)
    py -P tools/serve.py [--port 8787] [--no-browser]

Starts a small web server that only this computer can reach (127.0.0.1), does the first-time
build setup if it's needed, and opens the problem book. The page can load and save the files of
your project (solutions/ by default), start an assignment, and run the checker, and nothing else.
Leave the window open while you work; close it or press Ctrl+C to stop.
"""

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_book  # noqa: E402
import project  # noqa: E402
from check import to_args  # noqa: E402
from imageio import ImageError, png_bytes, read_image  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "tools" / "check.py"
IMAGE_ROOTS = ("build/cases/", "build/fresh/", "tests/")  # the only folders /files/ will read from
MAX_BODY = 4 * 1024 * 1024
CASE_ID = re.compile(r"^[\w.+-]+$")
# Files of the project the page may create and edit.
SOURCE_EXTS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".py", ".js", ".mjs", ".ts", ".rs", ".go", ".lua",
               ".java", ".kt", ".cs", ".md", ".txt", ".json", ".toml", ".cmake"}
SKIP_DIRS = {"build", ".git", "node_modules", "target", "__pycache__", ".cache"}  # never listed or served


class Workbook:
    def __init__(self):
        self.config = json.loads((ROOT / "workbook.json").read_text(encoding="utf-8"))
        self.title = self.config.get("book", {}).get("title", ROOT.name)
        self.token = secrets.token_urlsafe(24)
        self.lock = threading.Lock()  # one checker run at a time: they share the build folder
        self.setup_error = None
        self.home = project.home(self.config).resolve()

    def learner_file(self, rel: str):
        """A path the page may read or write: a source or text file inside the project, outside its
        build folders. Everything else is refused."""
        target = (ROOT / rel.replace("\\", "/").lstrip("/")).resolve()
        if self.home not in target.parents:
            return None
        inside = target.relative_to(self.home).parts
        if any(part in SKIP_DIRS or part.startswith(".") for part in inside[:-1]):
            return None
        if target.suffix.lower() in SOURCE_EXTS or target.name in ("CMakeLists.txt", ".gitignore"):
            return target
        return None

    def files(self) -> list:
        """Every file of the project, with the assignment it belongs to and whether it's still blank."""
        out = []
        if not self.home.is_dir():
            return out
        for p in sorted(self.home.rglob("*")):
            parts = p.relative_to(self.home).parts
            if not p.is_file() or any(part in SKIP_DIRS for part in parts[:-1]):
                continue
            path = "/".join(parts)
            text = p.read_text(encoding="utf-8", errors="replace") if p.stat().st_size < 1_000_000 else ""
            out.append({"path": p.relative_to(ROOT.resolve()).as_posix(), "checkpoint": project.owner(self.config, path),
                        "state": "blank" if project.still_blank(self.config, path) else "written",
                        "lines": text.count("\n") + 1 if text else 0})
        return out


def missing_tools(config: dict) -> list:
    """Programs the build commands need that aren't on PATH."""
    commands = [config.get("setup", {}).get("command", ""), config.get("build", "")]
    needed = []
    for command in filter(None, commands):
        words = to_args(command)
        needed.append(words[0])
        needed += [m.group(1) for m in re.finditer(r"-DCMAKE_(?:CXX|C)_COMPILER=(\S+)", command)]
        if re.search(r"-G\s*\"?Ninja", command):
            needed.append("ninja")
    return [tool for tool in dict.fromkeys(needed) if not ("/" in tool or "\\" in tool) and not shutil.which(tool)]


def first_time_setup(wb: Workbook):
    """Runs the workbook's setup step once (e.g. CMake configure). Returns a problem, or None.
    Before the project exists there's nothing to set up yet: the book offers to make it."""
    missing = missing_tools(wb.config)
    if missing:
        return (f"Your code can't be built yet: {', '.join(missing)} isn't installed (or isn't on PATH). "
                "Ask Claude to set this workbook up, or see the README's Needs line.")
    setup = wb.config.get("setup")
    if not setup or not project.exists(wb.config) or (ROOT / setup["creates"]).exists():
        return None
    print("First run: preparing the build. This takes a few seconds...")
    proc = subprocess.run(to_args(setup["command"]), cwd=ROOT, capture_output=True, text=True)
    if proc.returncode != 0:
        print((proc.stdout + proc.stderr).strip())
        return "The first-time build setup failed; the window that started the book shows why."
    return None


def file_state(target: Path) -> dict:
    """A solution file's text and version. The version (mtime in ns) goes out as a string, since
    JavaScript numbers can't hold it exactly."""
    path = target.relative_to(ROOT).as_posix()
    if not target.exists():
        return {"path": path, "text": None, "mtime": "0"}
    return {"path": path, "mtime": str(target.stat().st_mtime_ns),
            "text": target.read_text(encoding="utf-8", errors="replace")}


class Server(ThreadingHTTPServer):
    allow_reuse_address = os.name != "nt"  # on Windows this would let two servers share a port
    daemon_threads = True


class Handler(BaseHTTPRequestHandler):
    server_version = "workbook-study"

    def log_message(self, *args):
        pass

    # ---- plumbing
    def send(self, code: int, body: bytes, kind: str):
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def reply(self, code: int, obj):
        self.send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def allowed(self, query=None) -> bool:
        """Only pages this server handed out can use the API: right Host (no DNS rebinding),
        same Origin if one is sent, and the per-run token."""
        if self.headers.get("Host", "") not in self.server.hosts:
            return False
        origin = self.headers.get("Origin")
        if origin and urlsplit(origin).netloc not in self.server.hosts:
            return False
        token = self.headers.get("X-Workbook-Token") or (query or {}).get("t", [""])[0]
        return secrets.compare_digest(token, self.server.wb.token)

    def body(self) -> dict:
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            raise ValueError("request too large")
        return json.loads(self.rfile.read(length) or b"{}")

    # ---- routes
    def do_GET(self):
        url = urlsplit(self.path)
        path, query = unquote(url.path), parse_qs(url.query)
        if self.headers.get("Host", "") not in self.server.hosts:
            return self.reply(403, {"error": "unknown host"})
        if path in ("/", "/index.html"):
            return self.page()
        if path == "/api/hello":  # lets a second launch find this one
            return self.reply(200, {"workbook": self.server.wb.title, "folder": str(ROOT)})
        if path.startswith("/files/"):
            return self.file(path[len("/files/"):]) if self.allowed(query) else self.reply(403, {"error": "forbidden"})
        if not self.allowed():
            return self.reply(403, {"error": "forbidden"})
        if path == "/api/status":
            return self.reply(200, {"ready": self.server.wb.setup_error is None, "problem": self.server.wb.setup_error})
        if path == "/api/files":
            wb = self.server.wb
            return self.reply(200, {"exists": project.exists(wb.config), "files": wb.files()})
        if path == "/api/file":
            target = self.server.wb.learner_file(query.get("path", [""])[0])
            if target is None:
                return self.reply(404, {"error": "not a file you can open here"})
            return self.reply(200, file_state(target))
        return self.reply(404, {"error": "not found"})

    def do_PUT(self):
        path = unquote(urlsplit(self.path).path)
        if not self.allowed():
            return self.reply(403, {"error": "forbidden"})
        try:
            body = self.body()
        except ValueError as e:
            return self.reply(400, {"error": str(e)})
        target = self.server.wb.learner_file(str(body.get("path", ""))) if path == "/api/file" else None
        if target is None:
            return self.reply(404, {"error": "not a file you can save here"})
        text, base = body.get("text"), body.get("base")
        if not isinstance(text, str):
            return self.reply(400, {"error": "text missing"})
        # The page says which version it edited; if another editor saved the file since, ask instead
        # of overwriting.
        if base is not None and file_state(target)["mtime"] != base:
            return self.reply(409, {"error": "the file changed on disk", **file_state(target)})
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        return self.reply(200, file_state(target))

    def do_POST(self):
        path = unquote(urlsplit(self.path).path)
        if not self.allowed():
            return self.reply(403, {"error": "forbidden"})
        if path == "/api/exit":  # the book's Exit button: answer, then stop serving
            self.reply(200, {"bye": True})
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return None
        wb = self.server.wb
        try:
            options = self.body()
        except ValueError as e:
            return self.reply(400, {"error": str(e)})
        if path == "/api/setup":  # the book's "Set up the project" button
            created = project.setup(wb.config)
            wb.setup_error = first_time_setup(wb)
            return self.reply(200, {"created": created, "problem": wb.setup_error})
        if path in ("/api/start", "/api/starter"):
            cid = str(options.get("checkpoint", ""))
            if cid not in wb.config["checkpoints"]:
                return self.reply(404, {"error": "no such assignment"})
            if not project.exists(wb.config):
                return self.reply(409, {"error": "no-project"})
            if path == "/api/start":  # opening an assignment creates its files (never over existing ones)
                return self.reply(200, {"created": project.start(wb.config, cid)})
            kind = str(options.get("kind", ""))
            if kind not in ("blank", "boilerplate"):
                return self.reply(400, {"error": "kind must be blank or boilerplate"})
            written = project.use_starter(wb.config, cid, kind)
            return self.reply(200, {"files": [file_state(project.home(wb.config) / p) for p in written]})
        m = re.match(r"^/api/check/(\w+)$", path)
        if not m or m.group(1) not in wb.config["checkpoints"]:
            return self.reply(404, {"error": "no such assignment"})
        args = [sys.executable, "-P", str(CHECK), m.group(1), "-Json"]
        if options.get("case"):
            if not CASE_ID.match(str(options["case"])):
                return self.reply(400, {"error": "bad test id"})
            args += ["-Case", str(options["case"])]
        if options.get("fresh"):
            args.append("-Fresh")
        with self.server.wb.lock:
            started = time.time()
            proc = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
                                  errors="replace", timeout=900)
        lines = proc.stdout.strip().splitlines()
        try:
            report = json.loads(lines[-1])
        except (IndexError, json.JSONDecodeError):
            report = {"verdict": "error", "message": "the checker didn't return a result",
                      "text": (proc.stdout + proc.stderr).strip()}
        report["seconds"] = round(time.time() - started, 1)
        return self.reply(200, report)

    # ---- responses
    def page(self):
        wb = self.server.wb
        local = json.dumps({"token": wb.token, "folder": str(ROOT), "problem": wb.setup_error}).replace("</", "<\\/")
        page = build_book.build_page().replace(
            '<script type="application/json" id="book-data">',
            f'<script>window.WORKBOOK_LOCAL = {local};</script>\n<script type="application/json" id="book-data">', 1)
        document = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width,initial-scale=1"></head><body>'
                    + page + "</body></html>")
        self.send(200, document.encode("utf-8"), "text/html; charset=utf-8")

    def file(self, rel: str):
        """A picture from the test folders, as PNG (a PPM the learner wrote is converted)."""
        rel = rel.lstrip("/")
        target = (ROOT / rel).resolve()
        if not rel.startswith(IMAGE_ROOTS) or ROOT.resolve() not in target.parents or not target.is_file():
            return self.reply(404, {"error": "not found"})
        data = target.read_bytes()
        if not data.startswith(b"\x89PNG"):
            try:
                width, height, rgb = read_image(target)
            except (ImageError, ValueError, IndexError):
                return self.reply(415, {"error": "not a PNG or PPM picture"})
            data = png_bytes(width, height, rgb, level=1)
        self.send(200, data, "image/png")


def already_running(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/hello", timeout=1) as r:
            return json.load(r).get("folder") == str(ROOT)
    except (OSError, ValueError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Open the workbook with Run and Submit working.")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--no-browser", action="store_true", help="don't open a browser window")
    ap.add_argument("--check", action="store_true",
                    help="only check the tools and do the first-time setup; exit 0 when ready")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    wb = Workbook()
    if args.check:
        problem = first_time_setup(wb)
        print(problem or f"{wb.title} is ready: the build tools are installed and set up.")
        return 1 if problem else 0
    server = None
    for port in range(args.port, args.port + 12):
        try:
            server = Server(("127.0.0.1", port), Handler)
            break
        except OSError:
            if already_running(port):
                url = f"http://127.0.0.1:{port}/"
                print(f"{wb.title} is already open at {url}")
                if not args.no_browser:
                    webbrowser.open(url)
                return 0
    if server is None:
        print(f"No free port between {args.port} and {args.port + 11}. Try:  .\\study --port 9000")
        return 1
    port = server.server_address[1]
    server.wb = wb
    server.hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}

    wb.setup_error = first_time_setup(wb)
    if wb.setup_error:
        print(wb.setup_error)
    url = f"http://127.0.0.1:{port}/"
    print(f"{wb.title} is open at {url}\n"
          "Leave this window open while you work. Close it or press Ctrl+C to stop.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    print(f"{wb.title} has stopped. See you again!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
