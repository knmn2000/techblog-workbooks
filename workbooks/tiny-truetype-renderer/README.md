# Tiny TrueType Workbook

LeetCode-style checkpoints for the blog post
[Writing a tiny TrueType parser and renderer from scratch](https://yayo1.com/en/blog/tiny-truetype-renderer/)
by Yohei Yamasaki. Each checkpoint asks you to build what one part of the post builds, from
reading big-endian bytes (01) to rendering a line of text (18). Your program is checked by its
output only, so you can structure it your own way, in any language, with any library.

The problems are in `problems/` and, nicer to read, in the web problem book
(`book/problem-book.html`: open it in a browser). The book has a problem list
with your progress, and for each checkpoint the statement, hints that open in order, an Editorial with a solution proven to pass every test, an editor
preloaded with the starter, and the example test cases. Its Submit button copies your code and
shows the command to run; paste the checker's output back into Test Result to record the verdict.

| # | Checkpoint | # | Checkpoint |
|---|---|---|---|
| 01 | Read big-endian numbers | 10 | Lerp and quadratic Bezier curves |
| 02 | Read the table directory | 11 | Draw an outline with curves |
| 03 | Map characters to glyphs (cmap) | 12 | Intersect two segments |
| 04 | Locate glyph records (loca) | 13 | Intersect a line and a quadratic curve |
| 05 | Read the horizontal metrics | 14 | Fill a glyph: even-odd rule |
| 06 | Draw on a framebuffer | 15 | Lowest point of a quadratic curve |
| 07 | Decode simple glyphs | 16 | Fill a polygon: non-zero rule |
| 08 | Draw an outline with straight lines | 17 | Fill a glyph: non-zero rule |
| 09 | Resolve compound glyphs | 18 | Render a line of text |

Checkpoints don't depend on each other: each input carries what earlier checkpoints would
produce. Checkpoint 18 is where your own pieces come together; keep the parts you'll reuse in
`solutions/common/` and it can call them directly.

## Start here

Double-click `study.cmd` (or run `.\study` in PowerShell). It opens the problem book in your
browser with Run and Submit working: what you type is saved to `solutions/`, and the verdict
appears right in the page, with the failing tests and pictures. Leave its window open while you
work; close it to stop. The first start sets up the build, which takes a few seconds. If a tool is
missing, it tells you which; or ask Claude to set the workbook up.

You can also work in your own editor and check from a terminal, as below. The book picks up
changes you save to the solution files.

## Doing a checkpoint

1. Read the problem (book or `problems/NN-*.md`).
2. Write your solution in `solutions/pNN_*.cpp`. It starts as a comment and an empty `main`:
   the includes, reading the input and writing the output are yours. If you'd rather start
   from ready-made input/output code, copy `starters/boilerplate/pNN_*.cpp` over it (or pick
   Boilerplate in the book's editor) and fill in the functions marked `TODO`.
   Code you want to reuse in later checkpoints can go in `solutions/common/`: every `.cpp`
   there is compiled into every checkpoint, so checkpoint 18 can call what you wrote earlier.
3. Check it from this folder in PowerShell:

```
.\check 07                         run every test
.\check 07 -Case <test-id>         one test in full: input, expected output, your output
.\check 07 -Fresh                  a newly generated set of tests (new random seed)
.\check 07 -Dispute <test-id> "why"    set aside a test you believe is wrong
```

The verdict is `Accepted`, `Wrong Answer`, `Compile Error`, `Runtime Error` or
`Time Limit Exceeded`. Text output is compared word by word, so line endings (`\n` or `\r\n`)
and extra spaces don't matter, except inside quoted strings. Every failure shows the requirement it most likely comes from, where the
expected value came from, and the command to reproduce it. Picture checkpoints also write a
diff image (red: extra pixels, blue: missing, yellow: forgiven).

**Pictures are compared with a 1-pixel tolerance** along edges, so a different but correct
line or fill algorithm passes. Missing shapes, stray lines and holes in the wrong place don't.

## If you think a test is wrong

Run `.\check 07 -Dispute <test-id> "your reason"`. That test stops counting and you can carry on;
the verdict reads `Accepted (1 disputed)`. Then ask Claude to "review my disputes". Claude
rechecks the expected value against its independent source and either fixes the test or shows
you why it's right. Disputes are kept in `disputes.json`.

## Using another language or library

The checker runs `<run> <input-file> <output-file>` from this folder and compares the output file
(for pictures: a PNG, or a binary PPM, at the output path). Change `build` and `run` in
`workbook.json`, for example:

```json
"build": "",
"run": "py solutions/p{id}.py {input} {output}"
```

or `"build": "cargo build --release --bin p{id}"` with `"run": "target/release/p{id}.exe {input} {output}"`.
`{id}` becomes the checkpoint number. To check a one-off program without changing the config:
`.\check 07 -Run "path/to/program.exe {input} {output}"`.

## What's in here

| Path | What it is |
|---|---|
| `problems/` | Problem statements (the book is built from these) |
| `solutions/` | Your code: one file per checkpoint, blank to begin with |
| `solutions/common/` | Code shared by your checkpoints (compiled into all of them) |
| `starters/blank/` | The blank starters. Copy one over `solutions/` to start again. |
| `starters/boilerplate/` | Starters with the input/output code done, if you want them |
| `tools/blank_starters.py` | Writes the blank starters and puts them in `solutions/` (never over your own code) |
| `tests/NN/` | Test inputs and expected outputs (`cases.txt`, plus data files and expected pictures) |
| `study.cmd`, `study.ps1` | Open the book with Run and Submit working (they start `tools/serve.py`) |
| `tools/serve.py` | The study server: only reachable from this computer; loads and saves solution files and runs the checker |
| `tools/check.py` | The checker (`check.ps1` and `check.cmd` call it) |
| `tools/gen_pNN.py` | Each checkpoint's test generator (used by `-Fresh`) |
| `tools/build_book.py` | Builds `book/problem-book.html` from `problems/` and `starters/` (the page design is `tools/book_template.html`) |
| `include/provided/` | Optional helpers: big-endian reads (01), a framebuffer with PNG output (06), a simple-glyph decoder (07) |
| `fonts/` | JetBrains Mono Bold (Nerd Font build) and Noto Sans JP, both SIL Open Font License (see `fonts/README.md`) |
| `third_party/` | GLM and stb_image_write, under their own licences (see `third_party/README.md`) |
| `docs/authoring-guide.md` | How the checkpoints and their tests are made |
| `_spoilers/` | Reference solutions. Don't open these until you've passed. |

Needs: g++ (MinGW) with CMake and Ninja for the C++ starters, and Python 3 with `fontTools`
for `-Fresh`. The commands in `workbook.json` are set up for Windows (PowerShell, the `py`
launcher, `.exe` programs); on macOS or Linux, change `build`, `run` and the generator commands
there and run `python3 tools/check.py 07` instead of `.\check 07`.

This workbook is licensed under Apache-2.0, except the fonts and `third_party/`. It contains no
text or code from the blog post; the problem pages link to it.
