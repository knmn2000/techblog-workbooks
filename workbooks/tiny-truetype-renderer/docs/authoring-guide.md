# Authoring a checkpoint

How to turn one part of a blog post into a LeetCode-style checkpoint for this workbook.
Checkpoint 07 is the worked example: copy its shape exactly.

| File | Example |
|---|---|
| Problem page | `problems/07-simple-glyph.md` |
| Starter | `solutions/p07_simple_glyph.cpp` |
| Reference solution | `_spoilers/reference/p07_simple_glyph.cpp` |
| Test generator | `tools/gen_p07.py` (newer generators use `tools/wb.py`) |
| Generated tests | `tests/07/cases.txt` (+ `tests/07/data/`, `tests/07/expected/` for pictures) |

`workbook.json` and `CMakeLists.txt` already list every checkpoint with its slug, paths and
generator command. Don't edit them, or any shared tool (`tools/check.py`, `tools/imageio.py`,
`tools/wb.py`, `include/provided/*`). If one needs a change, say what and why in your report.

## Principles

1. **One kind of exercise: write a program whose output must match.** The program is run as
   `<program> <input-file> <output-file>` from the workbook folder. Tests only see the output, so
   the learner may structure the code any way, in any language or library.
2. **Same task as the snippet.** The checkpoint asks for what the blog's snippet accomplishes,
   with the same scope and simplifications. It does not prescribe the author's structure; the
   author's structure appears only as a hint and in "After you pass".
3. **Where the snippet is wrong, follow the spec** and say so in "After you pass" (neutrally:
   "something to look for").
4. **Each input carries what earlier checkpoints would produce** (offsets, outlines, ...), so a
   checkpoint can be done without the earlier ones.
5. **Expected outputs come from an independent source**: fontTools, Python's `struct`, exact
   `fractions.Fraction` arithmetic, fontTools' `PointInsidePen`, ... never from the reference
   solution alone. For pictures, the reference program draws the expected image and the
   generator validates it against an independent source before writing it (e.g. sample pixels
   and check them with `wb.inside()`, or check that every outline point is inked).
6. **No copying the blog.** Never paste its prose or code. Summaries are in your own words and
   much shorter. Link to sections with text fragments:
   `https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Some%20heading`.

## The problem page (Markdown)

Use exactly these sections, in this order, with the same heading text as checkpoint 07:

1. `# NN · Title`, then the line `**Difficulty:** Easy|Medium|Hard · **Checkpoint** N of 18 · **Check:** \`.\check NN\``
2. `**Tags**`: three bullets, `*Language:*`, `*Library:*`, `*Concepts:*` (what the learner may need).
3. `## Read in the blog first`: which blog section, where to stop before the author's code. Say
   the page is complete on its own.
4. `## Where this fits`: two or three sentences on the pipeline.
5. `## The problem`: what to build; `### Input` (a table of line kinds); `### Output` (exact
   format); then `###` subsections with every rule, table and formula needed. Exhaustive: a
   learner must be able to pass using only this page. Describe binary layouts as tables of
   field / type / meaning in your own words.
6. `## Requirements`: `- **R1** ...` one testable behaviour each. Every test targets one.
7. `## Examples`: two or three `### Example k: title (test \`id\`)` blocks with `input:` and
   `output:` in fenced text blocks, taken from real test cases, with a short walkthrough of the
   one non-obvious step.
8. `## Constraints`: input limits, what is guaranteed well-formed, number of tests, time limit.
9. `## Source material`: spec links (Apple TrueType manual, Microsoft OpenType spec, ...) and the
   blog section.
10. `## Hints`: four `<details><summary>Hint k: ...</summary>` blocks: 1 nudge, 2 approach,
    3 traps, 4 pseudocode. Each gives away more than the last.
11. `## Checking your solution`: the four commands (see 07) and one sample failure message.
12. `## After you pass: compare with the author's code`: how the author structured it (by name),
    and anything the snippet does differently from the spec.

Write plainly: short sentences, active voice, no em-dash asides. Use ASCII in test titles.

The web book (`tools/build_book.py`) recognises these sections by their heading text, so keep
it exact: "The problem", Requirements, Examples and Constraints form the statement; "Read in the
blog first" becomes a note at the top; Hints become hints that open in order; "Where this fits"
and "Source material" fold away under the statement; "Checking your solution" goes with the test
results; "After you pass" becomes the Editorial tab, locked until the learner passes. Any other
`##` section appears in the statement under its own heading. Each example's `input:` block,
and its `output:` block or expected picture, also become a test case in the bottom panel.

## The starter (`solutions/pNN_slug.cpp`)

Each checkpoint has two starters. The learner gets the **blank** one: a header comment and an
empty `main`, so the includes, the input parsing and the output are theirs to write. The
**boilerplate** (what this section describes) does the input and output and leaves functions
marked `TODO`; it's the optional easier start. Write the boilerplate as
`solutions/pNN_slug.cpp`, since the stub checks run on it. When every checkpoint is done, run
`py -P tools/blank_starters.py`: it keeps the boilerplate in `starters/boilerplate/`, writes
`starters/blank/`, and puts the blank starter in `solutions/` (never over a file the learner
changed). The checker says "Not started yet" while a solution is still the blank starter, and
the book's editor offers both.

The problem page's paragraph about the starter says the file starts as a comment and an empty
`main`, then what the boilerplate does and what it leaves to fill in (see 07). Formatting the
boilerplate does for the learner (rounding, printing bytes as numbers) must also be stated as a
rule on the page, since the blank starter doesn't do it. Picture pages end their Output section
with a "**Writing the picture.**" paragraph (binary PPM by hand, or PNG via stb), as in 14.

Code the learner shares between checkpoints goes in `solutions/common/`: every `.cpp` there is
compiled into every learner program (CMake `common` object library), so the capstone can call
earlier work.

- One self-contained C++20 file. The header comment names the checkpoint, the problem page and
  `.\check NN`, and says only the output is checked.
- Provided input/output code at the bottom, marked `// ---- Input/output (provided) ----`. It
  parses the input file and writes the output, so the learner fills in one function (or a
  few), each with a `// TODO:` comment and `throw NotImplemented("name");`.
- `main` catches `NotImplemented` and exits 99 (the checker then says "Not implemented yet"),
  catches other exceptions and exits 1 with the message on stderr.
- Optional helpers: `#include "provided/BigEndian.h"` (big-endian reads, checkpoint 01) and
  `#define CANVAS_PNG_IMPLEMENTATION` + `#include "provided/Canvas.h"` (framebuffer + PNG,
  checkpoint 06). Picture checkpoints write the PNG to the output path.
- Compiles cleanly with `-Wall -Wextra -Wno-unused-parameter`.

## The reference (`_spoilers/reference/pNN_slug.cpp`)

Same input/output code as the starter, function(s) filled in. Written from the spec, not the
blog. Header comment: `// Reference solution - checkpoint NN (...). SPOILERS: try it yourself first.`

## The generator (`tools/gen_pNN.py`)

Use `tools/wb.py`: `wb.parse_args("NN")`, `wb.Cases(...)`, `cases.add(...)`, `cases.save()`.

- Header lines: `compare` (`records ...` line by line with named tuples, `unordered`, or
  `image band=1 allow=...`), `explain` (where a difference is → likely requirement; see 07),
  and the requirements.
- Case ids: `NN-R<k>-<slug>` for cases aimed at a requirement, `NN-E2E-<slug>` for end to end.
  Titles in ASCII.
- Deterministic for a given `--seed`. The default (seed 1) output is committed in `tests/NN/`.
  Cases built from randomness include the seed in their id, so `-Fresh` gives new ones.
- Hand-made inputs are checked against the independent source before they're written (assert).
- Cover: every requirement (at least 2 cases each where possible), the blog's traps, real data
  from the fonts (`wb.JETBRAINS`, `wb.NOTO_JP`), edge cases, and a random section.
- Pictures: canvases at most about 600 x 600 (the checker's PNG decoding is pure Python). Draw
  the expected image with `wb.run_reference(args.ref, input_lines, cases.image_path(id))`, then
  validate it independently before adding the case.

## Checking the checks (all must hold before you're done)

Don't run `cmake` or `.\check NN` without `-Run`: other people build in `build/` at the same
time. Compile with g++ into your own folder, `build/agent-<name>/`, for example
`g++ -std=c++20 -O1 -Wall -Wextra -Wno-unused-parameter -Iinclude -Ithird_party/stb -Ithird_party/glm-1.0.1 -static -o build/agent-x/ref_p10.exe _spoilers/reference/p10_bezier.cpp`.

1. Generate: `py -P tools/gen_pNN.py` (pictures: add `--ref build/agent-x/ref_pNN.exe`).
2. Reference passes: `.\check NN -Run "build/agent-x/ref_pNN.exe {input} {output}"` gives Accepted.
3. Stub fails cleanly: the compiled starter gives "Not implemented yet".
4. Planted bugs fail: write at least three copies of the reference, each with one realistic
   mistake (the blog's own bug if it has one), and confirm each gets Wrong Answer with a useful
   message and a sensible "likely cause".
5. Fresh sets: run the generator with `--seed 2` and `--seed 77 --out build/fresh/NN`, and check
   the reference passes with `-Cases build/fresh/NN/cases.txt`.
6. Every requirement has cases (look at the summary table).
