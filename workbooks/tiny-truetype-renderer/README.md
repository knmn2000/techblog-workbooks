# Tiny TrueType Workbook

LeetCode-style checkpoints for the blog post
[Writing a tiny TrueType parser and renderer from scratch](https://yayo1.com/en/blog/tiny-truetype-renderer/)
by Yohei Yamasaki. Each checkpoint asks you to build what one part of the post builds, from
reading big-endian bytes (01) to rendering a line of text (18), and each one adds properly named
files to a project of your own. When you finish, `solutions/` is a working TrueType renderer in
C++, laid out much like the author's, that you can put on GitHub as it is.

The problems are in `problems/` and, nicer to read, in the web problem book
(`book/problem-book.html`: open it in a browser). The book has a problem list with your
progress, and for each checkpoint the statement, what it adds to your project, hints that open in
order, an Editorial with a solution proven to pass every test, an editor with the checkpoint's
files, and the example test cases.

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

## Start here

Ask Claude to "set up my workbook": it checks the tools, asks which language you'd like (this
workbook's project is C++), creates the project and opens the book. Or double-click `study.cmd`
(or run `.\study` in PowerShell): the book opens with Run and Submit working, and offers to create
the C++ project if there isn't one yet. Leave its window open while you work, or use the book's
**Exit** button when you're done. If a tool is missing, it tells you which.

## Your project

```
solutions/
  CMakeLists.txt, README.md, .gitignore
  src/font/         reading the font: ByteReader (01), FontParser (02), Cmap (03), Loca (04),
                    Metrics (05), GlyphParser (07), CompoundGlyph (09)
  src/              FrameBufferCanvas (06), Glyph and GlyphComponent (07), TextRenderer and main (18)
  src/render/       Placement and Outline (08, 11), Scanline and EvenOdd (14), NonZero (16, 17)
  src/utils/        Geometry (10, 12, 13, 15), Unicode (18)
  checkpoints/      p01_byte_readers.cpp ... p18_render_text.cpp: the programs the checker runs
  third_party/      stb_image_write.h, for writing PNG files
```

Do the checkpoints in order. Opening a checkpoint (in the book, or `.\check NN`) creates its
files, each with a comment saying what belongs in it; nothing you've written is ever replaced.
A checkpoint's real work goes in `src/`, and later checkpoints include it: the outline renderer
draws on your canvas, the text renderer uses nearly everything. Its program in `checkpoints/`
reads a test input, calls your code and writes the answer.

Test inputs still carry what earlier checkpoints would produce (a table's offset, a glyph's
location), so a checkpoint's tests only depend on the earlier files it uses. The whole project is
built together, though: if a file of another checkpoint doesn't compile, the checker says which
one. **Re-check solved** in the book runs every solved checkpoint again, so a change that breaks
an earlier one shows up at once (marked with a red `!`).

The **Files** panel in the book's editor shows the project as it grows, with each file's
checkpoint. When everything passes, the problem list shows your project next to the author's.
Build and run the finished program:

```
cmake --build build/solutions --target tiny_ttf
build/solutions/tiny_ttf.exe fonts/JetBrainsMonoNerdFont-Bold.ttf "Hello, TrueType!" hello.png
```

On its own (for example after you've pushed it to GitHub), `solutions/` builds with
`cmake -S . -B build` and `cmake --build build`.

## Doing a checkpoint

1. Read the problem (book or `problems/NN-*.md`). Its "In your project" box lists the files the
   checkpoint creates or adds to, and the earlier files it can build on.
2. Write them. They start blank: the includes, reading the input and writing the output are
   yours. If you'd rather start from ready-made input/output code, pick Boilerplate in the book's
   editor (or copy the checkpoint's files from `starters/boilerplate/`) and fill in what's marked
   `TODO`. The boilerplate uses the author's names where the post has them.
3. Check it from this folder in PowerShell, or with Run and Submit in the book:

```
.\check 07                         run every test
.\check 07 -Case <test-id>         one test in full: input, expected output, your output
.\check 07 -Fresh                  a newly generated set of tests (new random seed)
.\check 07 -Dispute <test-id> "why"    set aside a test you believe is wrong
```

The verdict is `Accepted`, `Wrong Answer`, `Compile Error`, `Runtime Error` or
`Time Limit Exceeded`. Text output is compared word by word, so line endings (`\n` or `\r\n`)
and extra spaces don't matter, except inside quoted strings. Every failure shows the requirement
it most likely comes from, where the expected value came from, and the command to reproduce it.
Picture checkpoints also write a diff image (red: extra pixels, blue: missing, yellow: forgiven).

**Pictures are compared with a 1-pixel tolerance** along edges, so a different but correct
line or fill algorithm passes. Missing shapes, stray lines and holes in the wrong place don't.

## If you think a test is wrong

Run `.\check 07 -Dispute <test-id> "your reason"`. That test stops counting and you can carry on;
the verdict reads `Accepted (1 disputed)`. Then ask Claude to "review my disputes". Claude
rechecks the expected value against its independent source and either fixes the test or shows
you why it's right. Disputes are kept in `disputes.json`.

## Another language

Only the output is checked, so the project can be in any language. This workbook's project, its
starters and its reference are C++. To work in another language, ask Claude: it shows which
languages are installed (`py -P tools/langs.py` lists them) and how to install the others, keeps
your C++ project in a folder of its own, and sets up a project in the new language, with its own
build file and the same layout in that language's style. Nothing is created for languages you
don't choose.

To check a one-off program without changing anything:
`.\check 07 -Run "path/to/program.exe {input} {output}"`.

## What's in here

| Path | What it is |
|---|---|
| `problems/` | Problem statements (the book is built from these) |
| `solutions/` | Your project, created when you set the workbook up (see above) |
| `starters/project/` | What your project starts with: the build file, README and `.gitignore` |
| `starters/blank/`, `starters/boilerplate/` | Each checkpoint's files, blank and with the input/output done |
| `tests/NN/` | Test inputs and expected outputs (`cases.txt`, plus data files and expected pictures) |
| `study.cmd`, `study.ps1` | Open the book with Run and Submit working (they start `tools/serve.py`) |
| `tools/serve.py` | The study server: only reachable from this computer; loads and saves your project's files and runs the checker |
| `tools/check.py` | The checker (`check.ps1` and `check.cmd` call it) |
| `tools/project.py` | Sets up your project and starts checkpoints (`setup`, `start NN`, `status`) |
| `tools/blank_starters.py` | Writes the blank starters from `workbook.json` |
| `tools/gen_pNN.py` | Each checkpoint's test generator (used by `-Fresh`) |
| `tools/build_book.py` | Builds `book/problem-book.html` (the page design is `tools/book_template.html`) |
| `fonts/` | JetBrains Mono Bold (Nerd Font build) and Noto Sans JP, both SIL Open Font License (see `fonts/README.md`) |
| `third_party/` | stb_image_write, under its own licence (see `third_party/README.md`) |
| `docs/authoring-guide.md` | How the checkpoints and their tests are made |
| `_spoilers/` | The reference project. Don't open it until you've passed. |

Needs: g++ (MinGW) with CMake and Ninja, and Python 3.11+ with `fontTools` for `-Fresh`. The
commands in `workbook.json` are set up for Windows (PowerShell, the `py` launcher, `.exe`
programs); on macOS or Linux, change the `.exe` paths there and run `python3 tools/check.py 07`
instead of `.\check 07`.

This workbook is licensed under Apache-2.0, except the fonts and `third_party/`. It contains no
text or code from the blog post; the problem pages link to it.
