# Authoring an assignment

How to turn one row of the assignment map into a finished assignment. Build the first one
completely and use it as the model for the rest: copy its shape exactly.

## Contents
1. Files
2. The problem page
3. The reference project
4. The starters
5. The generator and the case file
6. Picture assignments
7. Checking the checks (summary; details in test-trust.md)
8. Writing style

## 1. Files

An assignment is part of a project the learner builds (`references/mapping.md`, section 6). It has
an entry program the checker runs and the project files it creates or adds to. Paths of project
files are relative to the project folder (`solutions/` for the learner, `_spoilers/project/` for the
reference).

| File | Path |
|---|---|
| Problem page | `problems/NN-slug.md` |
| Entry program | `assignments/assignment_NN_slug.<ext>` in the project |
| Project files | where the layout puts them, e.g. `src/font/Cmap.h` |
| Reference | the same paths under `_spoilers/project/` |
| Starters | the same paths under `starters/blank/` and `starters/boilerplate/` |
| Generator | `tools/gen_pNN.py` (uses `tools/wbcore.py`) |
| Generated tests | `tests/NN/cases.txt`, plus `tests/NN/data/` and, for pictures, `tests/NN/expected/` |

Every assignment is registered in `workbook.json` before work starts, with its place in the project:

```json
"03": {
  "title": "Replay the log",
  "solution": "solutions/assignments/assignment_03_replay_log.cpp",
  "files": ["src/log/Replay.h", "src/log/Replay.cpp"],
  "extends": [],
  "buildsOn": ["src/log/Record.h"],
  "problem": "problems/03-replay-log.md",
  "cases": "tests/03/cases.txt",
  "generator": "py -P tools/gen_p03.py --seed {seed} --out {out}"
}
```

`files` are created by this assignment, `extends` are earlier files it adds to, and `buildsOn` are
earlier files it's likely to use (the book shows them; nothing enforces them). Each project file
gets a purpose in `project.purposes` (why it exists: its role, and which later assignments use
it), and each assignment gets `"jobs"`: for every file it touches, entry program included, one to
three imperative sentences on what the learner writes there, for someone starting from an empty
file (capabilities and data, not exact signatures or the algorithm). Purposes and jobs become each
starter's header and the book's "Start here" card, so they're how the learner knows where to
begin. Add `"generatorNeedsReference": true` only when the generator
runs the reference program, e.g. to draw expected pictures. `assets/example-assignment/` shows a
registered assignment.

## 2. The problem page

Markdown, with exactly these sections and headings, in this order (the book builder parses them):

1. `# NN · Title`
2. `**Difficulty:** Easy|Medium|Hard · **Assignment** N of M · **Check:** \`.\check NN\``
3. `**Tags**` followed by three bullets: `- *Language:* a · b · c`, `- *Library:* ...`,
   `- *Concepts:* ...`. What the learner may need to know or look up.
4. `## Read in the blog first`: which section of the post, linked with a text fragment
   (`url#:~:text=Heading%20words`), and where to stop before the author's code. Say the page is
   complete on its own.
5. `## Where this fits`: two or three sentences: what came before, what this unlocks, and which
   files of the project it adds to.
6. `## The problem`: one or two short sentences saying plainly what the program does. The files,
   the jobs, the earlier files it can use and the two ways to start are on the book's "Start here"
   card (from `workbook.json`), so the page doesn't repeat them. Then
   `### Input` (a table of line kinds), `### Output` (exact format, with a fenced block showing it),
   then `###` subsections with every rule, table, formula and edge case needed. Binary layouts as
   tables of field / type / meaning, in your own words. A learner must be able to pass using only
   this page; the independent solver proves it.
7. `## Requirements`: `- **R1** ...`, one testable behaviour each. Every case targets one.
8. `## Examples`: two or three `### Example k: title (test \`id\`)` blocks, each with `input:` and
   `output:` in fenced blocks copied from real cases (say once in the README that line endings and
   runs of spaces don't matter; the checker compares words), and a walkthrough of the one
   non-obvious step (a byte-by-byte table is ideal). Picture assignments embed the expected image:
   `![expected picture for <id>](tests/NN/expected/<id>.png)`.
9. `## Constraints`: input limits, what is guaranteed well-formed, number of tests and what they
   cover, the time limit.
10. `## Source material`: specification links, references the post cites, the post's section.
11. `## Hints`: four blocks, each
    `<details><summary>Hint k: title</summary>` ... `</details>`:
    1. a nudge (where to start, what to think about),
    2. the approach in words,
    3. the traps (a bullet list),
    4. pseudocode.
    Each gives away more than the last; none gives the full solution in the learner's language.
12. `## Checking your solution`: the four commands (`.\check NN`, `-Case <id>`, `-Fresh`,
    `-Dispute <id> "why"`) and one real failure message copied from a planted bug's run.
13. `## After you pass: compare with the author's code`: how the author structured it (by
    function name), linked to the snippet's caption with a text fragment, and "Something to look
    for:" any place the snippet differs from the spec, worded neutrally.

The web book (`tools/build_book.py`) finds these sections by their heading text, so keep it
exact. "The problem", Requirements, Examples and Constraints form the statement; "Read in the blog
first" becomes a note at the top; Hints open in order; "Where this fits" and "Source material" fold
away under the statement; "Checking your solution" sits with the test results; "After you pass"
becomes the Editorial tab, locked until the learner passes. Any other `##` section appears in the
statement under its own heading. Each example's `input:` block, and its `output:` block or expected
picture, also becomes a test case in the book's bottom panel.

## 3. The reference project

Write the reference first, in `_spoilers/project/`: the assignment's project files and its entry
program, from the specification and your own understanding, never copied from the blog. Later
references include earlier ones exactly as the learner's will, so the reference reads as the
finished project and doubles as the proof that the layout works.

- **The entry program** reads the input, calls the project, and writes the output in the exact
  format. It holds no logic later assignments need.
- **Project files** use the author's names where the post has them (types, functions, files),
  and carry a short header comment saying which assignment they belong to.
- **A file later assignments add to** is split into sections: everything a later assignment adds
  goes under a marker line, `// ---- Assignment 12: two segments ----` (`#` or `--` in languages
  with those comments). Everything before the first marker belongs to the assignment that creates
  the file. Includes a later section needs go in that section, even mid-file, so the file builds
  at every point in the series.
- **Learners read it.** The Editorial shows the assignment's files as they stand after it (later
  sections left out), with the names of earlier files it uses. Write a model answer: clear names,
  a short comment wherever the reasoning isn't obvious, no dead code or debugging leftovers.

`check NN -Ref` builds and checks the reference *as it stands after assignment NN*: the files of
assignments 01 to NN, later sections left out (`tools/project.py`, `reference_as_of`). An Accepted
run on the committed tests records the fingerprint of every file the program includes in
`_spoilers/verified.json`, and the book only says "Passes all N tests" while they still match.
After any change to a reference file, run `-Ref` again for every assignment that includes it.
`build_book.py` warns (and exits non-zero) for any reference that isn't proven.

## 4. The starters

Each of an assignment's own files (its entry program and the files it creates) has two starters at
the same path: `starters/blank/` and `starters/boilerplate/`. Opening an assignment copies its
starters into the learner's project (`tools/project.py start`), never over an existing file: the
boilerplate by default (`project.starter` in `workbook.json`), or the blank ones when the learner
chose From scratch; the book's switch replaces them after asking.

Every starter, blank or boilerplate, begins with the same header, written by
`py -P tools/blank_starters.py` from `workbook.json`: the assignment and its problem page, **Why
this file exists** (the purpose), **Your job** (the assignment's job for this file) and **How to
start** (write it all yourself, or press Boilerplate). The entry program's header also says how
the checker runs it and lists the assignment's other files, with the job in any earlier file it
adds to. **Blank** starters are that header and nothing else (an empty `main` in the entry
program; `#pragma once` for C++ headers): the learner writes the imports, the API, the input
parsing and the output. Rerun the script with `--force` after changing titles, files, purposes or
jobs; it only replaces the header of boilerplate files.

**Boilerplate** starters are written by you, from the reference:
- The entry program is the reference's, with a header comment saying what's left to write, and
  exit **99** when it catches a "not implemented" error (the checker then says "Not implemented
  yet: <function>"); 1 plus a message on stderr for other errors.
- Headers that only declare things are the reference's. Function bodies become a `TODO:` comment
  pointing at the page's section, then a "not implemented" error naming the function.
- A file later assignments add to has stubs for their functions too (marked with the assignment),
  so the boilerplate path keeps compiling.
- Everything compiles cleanly: build every blank and every boilerplate starter into a scratch
  project and check that each boilerplate program reports its TODO.

| Language | Not implemented | Exit 99 |
|---|---|---|
| C++ | `throw std::logic_error("not implemented: name");` | `catch (const std::exception& e)`: if `what()` starts with `not implemented`, print it to stderr and `return 99` |
| Python | `raise NotImplementedError("name")` | `except NotImplementedError as e: print(f"not implemented: {e}", file=sys.stderr); sys.exit(99)` |
| JavaScript | `throw new Error("not implemented: name")` | catch, check the message prefix, `process.exit(99)` |

Because the blank starter does nothing for the learner, the problem page must state every
formatting rule the boilerplate handles (how numbers are rounded, how bytes are printed).

## 5. The generator and the case file

Use `tools/wbcore.py`: `wbcore.parse_args("NN")`, `wbcore.Cases(out, seed, compare, requirements,
explain, source=...)`, `cases.add(id, req, title, input_lines, expected=... | expected_file=...)`,
`cases.save()`. Domain helpers (file formats, sample data) go in a workbook-specific module next to it.

The case file header:
- `source` (default source of expected values; cases may override),
- `compare` (`records name=field1,field2 tolerance=x`, `unordered name=...`, or
  `image band=1 allow=0.0002`),
- `explain` (where a difference is -> likely requirement: `key=R4`, `key:field=R7`,
  `key~word=R3`, `_lines=R1`; for `unordered`, `key:missing`),
- `requirement R1 text` lines.

Case ids: `NN-R<k>-<slug>` for a case aimed at a requirement, `NN-E2E-<slug>` for end-to-end
cases. Titles in ASCII, saying what the input is. Cases built from randomness include the seed in
their id. Cover every requirement (two or more cases each), every trap the blog's text or code
reveals, real data, edge cases, and a random section that changes with `--seed`.

Hand-made inputs are checked by the oracle before they're written (`assert`). Make generators
deterministic for a seed (fix timestamps, e.g. `SOURCE_DATE_EPOCH`). Inputs carry what earlier
assignments would produce (an offset, a parsed record), so an assignment's tests depend only on the
earlier files it chooses to use.

## 6. Picture assignments

- The output path ends in `.png`; the program writes PNG or binary PPM of exactly the canvas size.
- End the page's Output section with a "**Writing the picture.**" paragraph for learners without
  the boilerplate: a binary PPM by hand (header, then 3 bytes per pixel; open the file in binary
  mode), or a PNG through a library such as stb_image_write. The checker reads either, whatever
  the file is called. A header the project needs goes in through `project.copy` (e.g.
  `third_party/stb_image_write.h`), so the learner's project builds on its own.
- Define the pixel rule precisely (e.g. "filled when the pixel's centre is inside", "a w x h
  rectangle covers columns cx - floor(w/2) ..."), and say that edges may move one pixel.
- The reference draws expected images; the generator validates each against an independent
  source before writing it (sampled pixels against an inside test, every point marker present,
  points along every segment inked).
- Keep canvases under about 600 x 600 and thin features at least ~2 pixels wide.
- Build at least one different-but-correct variant (other sampling, other rounding) and confirm it
  passes.

## 7. Checking the checks

Compile into your own build folder and use `-Run` while others work in parallel. All must hold
(details in `test-trust.md`): the reference as it stands after the assignment is Accepted
(committed cases and two fresh seeds), which also proves the project builds at that point in the
series; the boilerplate says "Not implemented yet"; the blank starter says "Not started yet";
three or more planted bugs fail with useful messages and causes, including the blog's own bugs;
correct variants pass where a tolerance exists; every requirement has cases; the independent
solver passes.

## 8. Writing style

Plain and direct: short sentences, active voice, no em-dash asides, no "not X but Y", no stock
phrases. Name things the way the learner knows them. Tables for layouts and rules, numbers for
everything that has one. In test titles and anything the checker prints, ASCII only.
