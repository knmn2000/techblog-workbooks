# Tiny TrueType Workbook

LeetCode-style assignments for the blog post
[Writing a tiny TrueType parser and renderer from scratch](https://yayo1.com/en/blog/tiny-truetype-renderer/)
by Yohei Yamasaki. Each assignment builds what one part of the post builds, from reading
big-endian bytes (01) to rendering a line of text (18), and the files go into a C++ project of your
own, with names like `Cmap.cpp` and `GlyphParser.cpp`. At the end `solutions/` holds a working
TrueType renderer, laid out much like the author's, that you can put on GitHub as it is.

The statements are in `problems/`, but the web problem book (`book/problem-book.html`, open it in a
browser) is the better way to read them: it adds a progress list, hints that open in order, an
Editorial with a solution proven to pass every test, and an editor with the example cases.

If C++ or fonts are new to you, begin with the book's Primer (`primer/` in this folder). It covers
the language features, standard headers, font and drawing terms and tools the assignments lean on,
with links for further reading, and each assignment's Learning material list points to the entries
it needs.

| # | Assignment | # | Assignment |
|---|---|---|---|
| 01 | Read big-endian numbers | 10 | Lerp and quadratic Bezier curves |
| 02 | Read the table directory | 11 | Draw an outline with curves |
| 03 | Map characters to glyphs (cmap format 12) | 12 | Intersect two segments |
| 04 | Locate glyph records (loca) | 13 | Intersect a line and a quadratic curve |
| 05 | Read the horizontal metrics | 14 | Fill a glyph: even-odd rule |
| 06 | Draw on a framebuffer | 15 | Lowest point of a quadratic curve |
| 07 | Decode simple glyphs | 16 | Fill a polygon: non-zero rule |
| 08 | Draw an outline with straight lines | 17 | Fill a glyph: non-zero rule |
| 09 | Resolve compound glyphs | 18 | Render a line of text |

## Start here

Ask your coding assistant to "set up my workbook". It checks your tools, asks for a language (this
workbook's project is C++), creates the project and opens the book. Or double-click `study.cmd` on
Windows or `study.command` on macOS (or run `.\study` in PowerShell, `./study.sh` on macOS or
Linux). The book opens with Run and Submit working, and offers to create the C++ project if there
isn't one yet. Keep the window open while you work and use the book's Exit button when you're done.
If a tool is missing, it tells you which.

From a terminal, run `py -P tools/project.py setup` in this folder once to create the C++ project in
`solutions/`. Then `.\check 01` creates assignment 01's files, starting as the Boilerplate, and the
next `.\check 01` builds and tests them. For installing g++, CMake, Ninja and Python on Windows, see
the primer's Building and checking entries.

## Your project

Each file below carries the number of the assignment that creates it.

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

Do them in order. Opening an assignment (in the book, or with `.\check NN` or `./check.sh NN`)
creates its files. Each starts with a comment saying why it exists and what's yours to write, and
anything you've already written stays as it is. The real work goes in `src/`, and later assignments
build on it: the outline renderer draws on your canvas, the text renderer pulls in most of the
project. The program in `assignments/` is glue. It reads a test input, calls your code and writes
the answer.

Test inputs carry the results of earlier assignments (a table's offset, a glyph's location), so a
test needs only the earlier files its assignment uses. The checker still builds the whole project
in one go, though. If a file from some other assignment doesn't compile, it names that assignment.
The book's Re-check solved button reruns every solved assignment and flags any that a change broke
with a red `!`. In the book's editor the Files panel shows the project as it grows, each file with
its assignment, and once all 18 pass, the problem list sets your project beside the author's. Build
and run the finished program (on macOS or Linux, leave out the `.exe`):

```
cmake --build build/solutions --target tiny_ttf
build/solutions/tiny_ttf.exe fonts/JetBrainsMonoNerdFont-Bold.ttf "Hello, TrueType!" hello.png
```

Pushed to GitHub, `solutions/` builds on its own with `cmake -S . -B build` and
`cmake --build build`.

## Doing an assignment

1. Read the problem (book or `problems/NN-*.md`). In the book, its Start here card lists the
   files to complete, what each is for and the earlier files you can reuse.
2. Write the files. They start as the Boilerplate, which gives you the input/output code and the
   declarations; `TODO` marks your part. To write all of it yourself, includes, parsing and output
   too, choose From scratch above the editor and each file starts empty apart from its comment.
3. Check from this folder in PowerShell (`./check.sh` on macOS or Linux), or use Run and Submit in
   the book:

```
.\check 07                         run every test
.\check 07 -Case <test-id>         one test in full: input, expected output, your output
.\check 07 -Fresh                  a newly generated set of tests (new random seed)
.\check 07 -Dispute <test-id> "why"    set aside a test you believe is wrong
```

The verdict is one of `Accepted`, `Wrong Answer`, `Compile Error`, `Runtime Error` or
`Time Limit Exceeded`. Output is compared word by word, so line endings (`\n` or `\r\n`) and extra
spaces don't matter, except inside quoted strings. A failure comes with the checker's best guess at
the requirement behind it, where the expected value came from, and the command that reproduces it.
Picture assignments also get a diff image (red: extra pixels, blue: missing, yellow: forgiven).

Pictures are compared with a 1-pixel tolerance along edges, so a different but correct line or fill
algorithm passes. Missing shapes, stray lines and holes in the wrong place still fail.

## If you think a test is wrong

`.\check 07 -Dispute <test-id> "your reason"` sets a test aside, and the verdict becomes
`Accepted (1 disputed)`. Afterwards tell your coding assistant to "review my disputes". It checks
the expected value again against its independent source, then either corrects the test or explains
why it stands. Disputes are kept in `disputes.json`.

## Another language

The checker only sees output, so the language is up to you. This workbook's project, starters and
reference are C++. To switch, ask your coding assistant. It reports which languages you have
installed (`py -P tools/langs.py` lists them; use `python3` in place of `py` on macOS or Linux) and
how to install others, keeps the C++ project in a folder of its own, and sets up the new one with
its own build file and the same layout in that language's style. Languages you don't pick get
nothing created.

To check a one-off program without changing anything, run
`.\check 07 -Run "path/to/program {input} {output}"`.

## What's in here

| Path | What it is |
|---|---|
| `problems/` | Problem statements, which `tools/build_book.py` turns into the book |
| `primer/` | The primer, shown in the book as its Primer view: the C++, font, drawing and tool terms the assignments use |
| `solutions/` | Your project. It appears when you set the workbook up |
| `starters/project/` | What your project starts with: the build file, README and `.gitignore` |
| `starters/blank/`, `starters/boilerplate/` | Each assignment's files, once blank and once with the input/output filled in |
| `tests/NN/` | Test inputs and expected outputs (`cases.txt`, plus data files and expected pictures) |
| `study.cmd`, `study.command`, `study.ps1`, `study.sh` | Open the book with Run and Submit working (they start `tools/serve.py`) |
| `tools/serve.py` | The study server. Reachable only from this computer; it loads and saves your project's files and runs the checker |
| `tools/check.py` | The checker (`check.ps1`, `check.cmd` and `check.sh` call it) |
| `tools/project.py` | Sets up your project and starts assignments (`setup`, `start NN`, `status`) |
| `tools/blank_starters.py` | Writes the blank starters from `workbook.json` |
| `tools/gen_pNN.py` | Each assignment's test generator (used by `-Fresh`) |
| `tools/build_book.py` | Builds `book/problem-book.html` (the page design is `tools/book_template.html`) |
| `tools/primer_check.py` | Checks that the primer covers what each assignment uses (`--links` also tests its links) |
| `fonts/` | JetBrains Mono Bold (Nerd Font build) and Noto Sans JP (variable font), both under the SIL Open Font License (see `fonts/README.md`). The post uses `JetBrainsMono-Bold.ttf` and `NotoSansJP-Regular.ttf`, so a glyph id or offset it quotes can differ here. The problem pages flag the places where that matters |
| `third_party/` | stb_image_write, under its own licence (see `third_party/README.md`) |
| `docs/authoring-guide.md` | How to write the assignments and their tests |
| `_spoilers/` | The reference project. Leave it shut until you've passed. |

Needs g++ (MinGW on Windows, GCC on Linux, the one from Xcode's command line tools on macOS) with
CMake and Ninja, and Python 3.11+ with `fontTools` for `-Fresh`. The program names in
`workbook.json` end in `{exe}`, which the tools turn into `.exe` on Windows and drop on macOS and
Linux, so one file serves all three. The checks pass on Windows and Linux. On macOS they use the
Linux commands and haven't been run yet.

Apache-2.0 covers this workbook, except the fonts and `third_party/`. Nothing from the blog post's
text or code is in the workbook, and the problem pages link to it.
