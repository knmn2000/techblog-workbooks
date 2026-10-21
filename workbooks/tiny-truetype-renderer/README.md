# Tiny TrueType Workbook

LeetCode-style assignments for the blog post
[Writing a tiny TrueType parser and renderer from scratch](https://yayo1.com/en/blog/tiny-truetype-renderer/)
by Yohei Yamasaki. In each assignment you build what one part of the post builds, from reading
big-endian bytes (01) to rendering a line of text (18), and add its files, with names like
`Cmap.cpp` and `GlyphParser.cpp`, to a project of your own. After the last one, `solutions/` holds
a working TrueType renderer in C++, laid out much like the author's, that you can put on GitHub as
it is.

The problems are in `problems/` and, nicer to read, in the web problem book
(`book/problem-book.html`: open it in a browser). The book has a problem list with your
progress, and for each assignment the statement, what it adds to your project, hints that open in
order, an Editorial with a solution proven to pass every test, an editor with the assignment's
files, and the example test cases.

| # | Assignment | # | Assignment |
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
  assignments/      assignment_01_byte_readers.cpp ... assignment_18_render_text.cpp: one program
                    per assignment, which the checker runs; you write these too
  third_party/      stb_image_write.h, for writing PNG files
```

Do the assignments in order. Opening an assignment (in the book, or with `.\check NN`) creates
its files, each with a comment saying why the file exists and what your job in it is. It doesn't
overwrite anything you've written.
You write an assignment's real work in `src/`, and later assignments use it: the outline renderer
draws on your canvas, and the text renderer uses most of the project. The assignment's program in
`assignments/` reads a test input, calls your code and writes the answer.

Each test input carries what earlier assignments would produce (a table's offset, a glyph's
location), so an assignment's tests depend only on the earlier files it uses. The checker builds
the whole project at once, though, and if a file from another assignment doesn't compile, it tells
you which one. **Re-check solved** in the book runs every solved assignment again, so you see at
once when a change breaks an earlier one (the book marks it with a red `!`).

The **Files** panel in the book's editor shows the project as it grows, with each file's
assignment. The problem list shows your project next to the author's once all 18 assignments pass.
Build and run the finished program:

```
cmake --build build/solutions --target tiny_ttf
build/solutions/tiny_ttf.exe fonts/JetBrainsMonoNerdFont-Bold.ttf "Hello, TrueType!" hello.png
```

On its own (for example after you've pushed it to GitHub), `solutions/` builds with
`cmake -S . -B build` and `cmake --build build`.

## Doing an assignment

1. Read the problem (book or `problems/NN-*.md`). In the book, its **Start here** card lists the
   files to write, your job in each, the earlier files you can use, and the two ways to start.
2. Write the files. Each one starts as the Boilerplate, which gives you the input/output code and
   the declarations (with the author's names where the post has them), and you fill in the parts
   marked `TODO`. To write all of it yourself, including the includes, the parsing and the output,
   choose **From scratch** on the Start here card: each file then starts empty apart from its
   comment.
3. Check it from this folder in PowerShell, or with Run and Submit in the book:

```
.\check 07                         run every test
.\check 07 -Case <test-id>         one test in full: input, expected output, your output
.\check 07 -Fresh                  a newly generated set of tests (new random seed)
.\check 07 -Dispute <test-id> "why"    set aside a test you believe is wrong
```

The verdict is `Accepted`, `Wrong Answer`, `Compile Error`, `Runtime Error` or
`Time Limit Exceeded`. The checker compares text output word by word, so line endings (`\n` or
`\r\n`) and extra spaces don't matter, except inside quoted strings. For each failure it shows its
best guess at the requirement behind it, where the expected value came from, and the command that
reproduces it. For picture assignments it also writes a diff image (red: extra pixels, blue:
missing, yellow: forgiven).

**The checker compares pictures with a 1-pixel tolerance** along edges, so a different but correct
line or fill algorithm passes. Missing shapes, stray lines and holes in the wrong place still fail.

## If you think a test is wrong

Run `.\check 07 -Dispute <test-id> "your reason"`. That test stops counting and you can carry on;
the verdict reads `Accepted (1 disputed)`. Then ask Claude to "review my disputes". Claude
rechecks the expected value against its independent source and either fixes the test or shows
you why it's right. The checker keeps disputes in `disputes.json`.

## Another language

The checker reads only your program's output, so you can write the project in any language. This
workbook's project, its starters and its reference are C++.

To work in another language, ask Claude. It shows which languages you have installed
(`py -P tools/langs.py` lists them) and how to install the others, keeps your C++ project in a
folder of its own, and sets up a project in the new language, with its own build file and the same
layout in that language's style. It creates nothing for languages you don't choose.

To check a one-off program without changing anything, run
`.\check 07 -Run "path/to/program.exe {input} {output}"`.

## What's in here

| Path | What it is |
|---|---|
| `problems/` | Problem statements (`tools/build_book.py` makes the book from these) |
| `solutions/` | Your project, created when you set the workbook up (see above) |
| `starters/project/` | What your project starts with: the build file, README and `.gitignore` |
| `starters/blank/`, `starters/boilerplate/` | Each assignment's files, blank and with the input/output done |
| `tests/NN/` | Test inputs and expected outputs (`cases.txt`, plus data files and expected pictures) |
| `study.cmd`, `study.ps1` | Open the book with Run and Submit working (they start `tools/serve.py`) |
| `tools/serve.py` | The study server: only reachable from this computer; loads and saves your project's files and runs the checker |
| `tools/check.py` | The checker (`check.ps1` and `check.cmd` call it) |
| `tools/project.py` | Sets up your project and starts assignments (`setup`, `start NN`, `status`) |
| `tools/blank_starters.py` | Writes the blank starters from `workbook.json` |
| `tools/gen_pNN.py` | Each assignment's test generator (used by `-Fresh`) |
| `tools/build_book.py` | Builds `book/problem-book.html` (the page design is `tools/book_template.html`) |
| `fonts/` | JetBrains Mono Bold (Nerd Font build) and Noto Sans JP, both SIL Open Font License (see `fonts/README.md`) |
| `third_party/` | stb_image_write, under its own licence (see `third_party/README.md`) |
| `docs/authoring-guide.md` | How to write the assignments and their tests |
| `_spoilers/` | The reference project. Don't open it until you've passed. |

Needs: g++ (MinGW) with CMake and Ninja, and Python 3.11+ with `fontTools` for `-Fresh`. The
commands in `workbook.json` assume Windows (PowerShell, the `py` launcher, `.exe` programs). On
macOS or Linux, change the `.exe` paths there and run `python3 tools/check.py 07` instead of
`.\check 07`.

Apache-2.0 covers this workbook, except the fonts and `third_party/`. The workbook contains no
text or code from the blog post; the problem pages link to it.
