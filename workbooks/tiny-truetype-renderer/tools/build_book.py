"""Builds the web problem book (book/problem-book.html) from problems/*.md.

    py -P tools/build_book.py

The page is tools/book_template.html filled with one JSON object: the book's metadata from
workbook.json and, for each checkpoint, its problem page split into parts (statement,
examples, hints, editorial, ...), its starter code and the starter's language. The template
renders that as a problem list and a split-pane problem view with a code editor.

The Markdown is the small subset the problem pages use: headings, paragraphs, lists, tables,
fenced code, images (embedded as data URIs), links, **bold**, *italic*, `code`, <details>
blocks, and raw <figure>/<svg>/<div> blocks. Sections are recognised by their names (see
ROLES); any other section is shown in the statement under its own heading.

Starters: the editor offers the blank starter (starters/blank/<file>) and, when there is one,
the boilerplate (starters/boilerplate/<file>). tools/blank_starters.py makes both.
"""

import base64
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODEMIRROR = "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/"

# Starter file extension -> (label, CodeMirror MIME type, mode).
LANGS = {
    ".cpp": ("C++", "text/x-c++src", "clike"), ".cc": ("C++", "text/x-c++src", "clike"),
    ".cxx": ("C++", "text/x-c++src", "clike"), ".c": ("C", "text/x-csrc", "clike"),
    ".java": ("Java", "text/x-java", "clike"), ".cs": ("C#", "text/x-csharp", "clike"),
    ".kt": ("Kotlin", "text/x-kotlin", "clike"), ".py": ("Python", "text/x-python", "python"),
    ".js": ("JavaScript", "text/javascript", "javascript"), ".mjs": ("JavaScript", "text/javascript", "javascript"),
    ".ts": ("TypeScript", "text/typescript", "javascript"), ".rs": ("Rust", "text/x-rustsrc", "rust"),
    ".go": ("Go", "text/x-go", "go"),
}
# Mode -> the CodeMirror files it needs, after codemirror.min.js.
MODE_FILES = {
    "clike": ["mode/clike/clike.min.js"], "python": ["mode/python/python.min.js"],
    "javascript": ["mode/javascript/javascript.min.js"], "go": ["mode/go/go.min.js"],
    "rust": ["addon/mode/simple.min.js", "mode/rust/rust.min.js"],
}
# Section name (lower case) -> where the page shows it.
ROLES = {
    "read in the blog first": "read", "where this fits": "context", "the problem": "problem",
    "requirements": "requirements", "examples": "examples", "source material": "sources",
    "hints": "hints", "checking your solution": "checking",
}


# ---- Markdown subset ----------------------------------------------------------------

def inline(text: str) -> str:
    codes = []

    def keep_code(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep_code, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)",
                  lambda m: f'<a href="{html.escape(m.group(2))}" target="_blank" rel="noopener">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def plain(text: str) -> str:
    """Markdown inline text without its markup, for search and filters."""
    return re.sub(r"[`*]", "", text).strip()


def data_uri(src: str):
    path = (ROOT / "problems" / src).resolve() if src.startswith("../") else ROOT / src
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
            ".svg": "image/svg+xml", ".webp": "image/webp"}.get(path.suffix.lower(), "application/octet-stream")
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}", path.relative_to(ROOT).as_posix()


def image(alt: str, src: str) -> str:
    uri, rel = data_uri(src)
    return (f'<figure class="pic"><img src="{uri}" alt="{html.escape(alt)}">'
            f'<figcaption>{html.escape(rel)}</figcaption></figure>')


def table(rows) -> str:
    def cells(row):
        row = row.strip().strip("|").replace("\\|", "\x01")
        return [c.strip().replace("\x01", "|") for c in row.split("|")]

    head, body = cells(rows[0]), [cells(r) for r in rows[2:]]
    out = ["<div class=\"table-wrap\"><table><thead><tr>"]
    out += [f"<th>{inline(c)}</th>" for c in head]
    out.append("</tr></thead><tbody>")
    for r in body:
        out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def fenced(lines, i):
    """(code lines, index after the closing fence) for the fence opening at lines[i]."""
    j = i + 1
    while j < len(lines) and not lines[j].strip().startswith("```"):
        j += 1
    return lines[i + 1:j], j + 1


def blocks(lines) -> str:
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
        elif stripped.startswith("```"):
            code, i = fenced(lines, i)
            out.append(f"<pre><code>{html.escape(chr(10).join(code))}</code></pre>")
        elif m := re.match(r"^(#{2,4})\s+(.*)", line):
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
        elif stripped.startswith("<details>"):
            j = i
            while j < n and "</details>" not in lines[j]:
                j += 1
            summary = re.search(r"<summary>(.*?)</summary>", line).group(1)
            out.append(f'<details class="md-details"><summary>{inline(summary)}</summary>'
                       f'<div class="flow">{blocks(lines[i + 1:j])}</div></details>')
            i = j + 1
        elif stripped.startswith(("<figure", "<svg", "<div")):
            j = i
            while j < n and lines[j].strip():
                j += 1
            out.append("\n".join(lines[i:j]))
            i = j
        elif stripped.startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            j = i
            while j < n and lines[j].strip().startswith("|"):
                j += 1
            out.append(table(lines[i:j]))
            i = j
        elif m := re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped):
            out.append(image(m.group(1), m.group(2)))
            i += 1
        elif re.match(r"^(\s*)([-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.", line))
            items, j = [], i
            while j < n and lines[j].strip():
                if re.match(r"^\s*([-*]|\d+\.)\s+", lines[j]) and not lines[j].startswith("    "):
                    items.append(re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[j]))
                else:
                    items[-1] += " " + lines[j].strip()
                j += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>" + "".join(f"<li>{inline(it)}</li>" for it in items) + f"</{tag}>")
            i = j
        else:
            j = i
            para = []
            while j < n and lines[j].strip() and not re.match(r"^(#{1,4}\s|```|\||!\[|<details>|\s*[-*]\s|\s*\d+\.\s)", lines[j]):
                para.append(lines[j].strip())
                j += 1
            if not para:
                para, j = [lines[j].strip()], j + 1
            out.append(f"<p>{inline(' '.join(para))}</p>")
            i = j
    return "\n".join(out)


# ---- Parts of a problem page --------------------------------------------------------

def requirements(body) -> str:
    joined = []
    for line in body:
        if line.startswith("- **R"):
            joined.append(line)
        elif line.strip() and joined and not line.startswith("- "):
            joined[-1] += " " + line.strip()
    items = []
    for item in joined:
        m = re.match(r"- \*\*(R\d+)\*\*\s*(.*)", item)
        items.append(f'<li><span class="rid">{m.group(1)}</span><span>{inline(m.group(2))}</span></li>')
    intro = [l for l in body if l.strip() and not l.startswith("- ") and not l.startswith("  ")]
    return (blocks(intro) if intro else "") + '<ul class="reqs">' + "".join(items) + "</ul>"


def labelled(code) -> dict:
    """Splits a code block written as 'input:   ...' / 'output:  ...' into its parts."""
    parts, current, indent = {}, None, 0
    for line in code:
        m = re.match(r"^(input|output):(\s*)(.*)$", line)
        if m:
            current, indent = m.group(1), len(m.group(1)) + 1 + len(m.group(2))
            parts[current] = [m.group(3)] if m.group(3) else []
        elif current:
            parts[current].append(line[indent:] if not line[:indent].strip() else line.strip())
    return {k: "\n".join(v).strip("\n") for k, v in parts.items()}


def example(chunk) -> dict:
    """One '### Example n: ...' chunk -> its input, expected output and explanation."""
    heading = chunk[0][4:].strip()
    test = re.search(r"\(test `([^`]+)`\)", heading)
    heading = re.sub(r"\s*\(test `[^`]+`\)", "", heading)
    m = re.match(r"(Example\s+\d+)\s*[:.]\s*(.*)", heading)
    label, name = (m.group(1), m.group(2)) if m else (heading, "")
    ex = {"label": label, "name": inline(name), "test": test.group(1) if test else None}

    lines, parts, rest, picture, i = chunk[1:], {}, [], None, 0
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            code, j = fenced(lines, i)
            first = next((l for l in code if l.strip()), "")
            if re.match(r"^(input|output):", first):
                for key, value in labelled(code).items():
                    parts.setdefault(key, value)
            else:
                rest.extend(lines[i:j])
            i = j
            continue
        if picture is None and (pm := re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped)):
            picture = (len(rest), pm.group(1), pm.group(2))
        rest.append(lines[i])
        i += 1

    if "input" not in parts:
        ex["raw"] = blocks(lines)
        return ex
    ex["input"] = parts["input"]
    ex["output"] = parts.get("output")
    ex["image"] = None
    if ex["output"] is None and picture is not None:
        at, alt, src = picture
        del rest[at]
        uri, rel = data_uri(src)
        ex["image"] = {"src": uri, "alt": alt, "path": rel}
    ex["explain"] = blocks(rest)
    return ex


def examples(body):
    intro, chunks = [], []
    for line in body:
        if line.startswith("### "):
            chunks.append([line])
        elif chunks:
            chunks[-1].append(line)
        else:
            intro.append(line)
    return blocks(intro), [example(c) for c in chunks]


def hints(body) -> list:
    out, i = [], 0
    while i < len(body):
        if not body[i].strip().startswith("<details>"):
            i += 1
            continue
        j = i
        while j < len(body) and "</details>" not in body[j]:
            j += 1
        summary = re.search(r"<summary>(.*?)</summary>", body[i]).group(1)
        m = re.match(r"(Hint\s+\d+)\s*[:.]\s*(.*)", summary)
        title, sub = (m.group(1), m.group(2)) if m else (f"Hint {len(out) + 1}", summary)
        out.append({"title": title, "sub": inline(sub), "html": blocks(body[i + 1:j])})
        i = j + 1
    return out


def indent_unit(code: str, default: int) -> int:
    """The starter's indent width: the smallest one used on at least three code lines."""
    widths = {}
    for line in code.splitlines():
        body = line.lstrip(" ")
        width = len(line) - len(body)
        if width and body and not body.startswith(("*", "//", "#")):
            widths[width] = widths.get(width, 0) + 1
    common = sorted(w for w, count in widths.items() if count >= 3 and w >= 2)
    return min(common[0], 8) if common else default


# ---- One checkpoint ---------------------------------------------------------------

def starters(meta: dict):
    """(blank starter, boilerplate or None) from starters/ (see tools/blank_starters.py)."""
    name = Path(meta["solution"]).name

    def read(path: Path):
        return path.read_text(encoding="utf-8").replace("\r\n", "\n") if path.exists() else None

    blank = read(ROOT / "starters" / "blank" / name) or read(ROOT / meta["solution"]) or ""
    return blank, read(ROOT / "starters" / "boilerplate" / name)


def checkpoint(cid: str, meta: dict) -> dict:
    md = (ROOT / meta["problem"]).read_text(encoding="utf-8").splitlines()
    title = re.sub(r"^#\s+\d+\s*·\s*", "", md[0]).strip()
    found = re.search(r"\*\*Difficulty:\*\*\s*(\w+)", "\n".join(md[:8]))
    difficulty = found.group(1) if found else "Medium"
    tags = []
    k = next((i for i, line in enumerate(md) if line.strip() == "**Tags**"), 0) + 1
    while k < len(md) and md[k].startswith("- "):
        if m := re.match(r"- \*(\w+):\*\s*(.*)", md[k]):
            items = [t.strip() for t in m.group(2).split("·") if t.strip()]
            tags.append({"label": m.group(1), "items": [inline(t) for t in items], "text": [plain(t) for t in items]})
        k += 1

    sections = []
    for line in md[k:]:
        if line.startswith("## "):
            sections.append([line[3:].strip(), []])
        elif sections:
            sections[-1][1].append(line)

    data = {"read": "", "context": "", "sources": "", "checking": "", "hints": [], "examples": [],
            "editorial": None}
    body = []
    for name, lines in sections:
        low = name.lower()
        role = "editorial" if low.startswith("after you pass") else ROLES.get(low, "other")
        if role in ("read", "context", "sources", "checking"):
            data[role] = blocks(lines)
        elif role == "hints":
            data["hints"] = hints(lines)
        elif role == "editorial":
            heading = re.sub(r"^after you pass\s*[:-]?\s*", "", name, flags=re.I) or name
            data["editorial"] = {"title": heading[:1].upper() + heading[1:], "html": blocks(lines)}
        elif role == "problem":
            body.append(f'<div class="d-problem flow">{blocks(lines)}</div>')
        elif role == "requirements":
            body.append(f'<section class="d-sec flow"><h2>Requirements</h2>{requirements(lines)}</section>')
        elif role == "examples":
            intro, data["examples"] = examples(lines)
            body.append(intro + '<div class="examples" data-examples></div>')
        else:
            body.append(f'<section class="d-sec flow"><h2>{inline(name)}</h2>{blocks(lines)}</section>')

    blank, boilerplate = starters(meta)
    label, mime, mode = LANGS.get(Path(meta["solution"]).suffix.lower(), ("Text", "text/plain", None))
    cases = (ROOT / meta["cases"]).read_text(encoding="utf-8").count("\ncase ")
    return {"id": cid, "num": str(int(cid)) if cid.isdigit() else cid, "title": title,
            "difficulty": difficulty, "tests": cases, "solution": meta["solution"], "problem": meta["problem"],
            "lang": {"label": label, "mime": mime, "mode": mode}, "starter": blank, "boilerplate": boilerplate,
            "indent": indent_unit(boilerplate or blank, 4 if mode == "python" else 2),
            "tags": tags, "body": "".join(body), **data}


# ---- Page -------------------------------------------------------------------------

def build_page() -> str:
    """The whole book as one HTML string (tools/serve.py serves this directly)."""
    config = json.loads((ROOT / "workbook.json").read_text(encoding="utf-8"))
    cps = [checkpoint(cid, meta) for cid, meta in sorted(config["checkpoints"].items())
           if (ROOT / meta["problem"]).exists() and (ROOT / meta["cases"]).exists()]
    book = config["book"]
    data = {
        "key": re.sub(r"[^a-z0-9]+", "-", book["title"].lower()).strip("-"),
        "title": book["title"], "headline": book["headline"], "lede": book["lede"], "credits": book["credits"],
        "sourceUrl": book["sourceUrl"], "sourceTitle": book["sourceTitle"], "author": book["author"],
        # Shown as "run the checker in <folder>"; the folder's name unless workbook.json says otherwise,
        # so a shared book doesn't carry the author's local path.
        "folder": book.get("folder") or ROOT.name, "check": book.get("checkCommand", ".\\check {id}"), "shell": book.get("shell", "PowerShell"),
        "checkpoints": cps,
    }
    modes = dict.fromkeys(f for c in cps if c["lang"]["mode"] for f in MODE_FILES[c["lang"]["mode"]])
    scripts = "\n".join(f'<script src="{CODEMIRROR}{f}"></script>' for f in modes)
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/").replace("<!--", "\\u003c!--")

    page = (ROOT / "tools" / "book_template.html").read_text(encoding="utf-8")
    page = page.replace("{{TITLE}}", html.escape(book["title"])).replace("{{MODES}}", scripts)
    return page.replace("{{DATA}}", blob)


def main():
    page = build_page()
    out = ROOT / "book" / "problem-book.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(page, encoding="utf-8")
    count = page.count('"difficulty":')
    print(f"wrote {out.relative_to(ROOT).as_posix()}: {count} checkpoints, {len(page) // 1024} KB")


if __name__ == "__main__":
    main()
