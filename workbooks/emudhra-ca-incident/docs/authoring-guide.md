# Authoring a checkpoint

How to turn one row of the checkpoint map into a finished checkpoint. Build the first one
completely and use it as the model for the rest: copy its shape exactly.

## Contents
1. Files
2. The problem page
3. The starter
4. The reference solution
5. The generator and the case file
6. Picture checkpoints
7. Checking the checks (summary; details in test-trust.md)
8. Writing style

## 1. Files

| File | Path |
|---|---|
| Problem page | `problems/NN-slug.md` |
| Starter | `solutions/pNN_slug.<ext>` |
| Reference solution | `_spoilers/reference/pNN_slug.<ext>` |
| Generator | `tools/gen_pNN.py` (uses `tools/wbcore.py`) |
| Generated tests | `tests/NN/cases.txt`, plus `tests/NN/data/` and, for pictures, `tests/NN/expected/` |

Every checkpoint is registered in `workbook.json` before work starts:

```json
"03": {
  "title": "Replay the log",
  "solution": "solutions/p03_replay_log.cpp",
  "problem": "problems/03-replay-log.md",
  "cases": "tests/03/cases.txt",
  "generator": "py -P tools/gen_p03.py --seed {seed} --out {out}"
}
```

(Add `"generatorNeedsReference": true` only when the generator runs the reference program,
e.g. to draw expected pictures.)
For C++, add `add_checkpoint(NN slug)` to `CMakeLists.txt`.

## 2. The problem page

Markdown, with exactly these sections and headings, in this order (the book builder parses them):

1. `# NN · Title`
2. `**Difficulty:** Easy|Medium|Hard · **Checkpoint** N of M · **Check:** \`.\check NN\``
3. `**Tags**` followed by three bullets: `- *Language:* a · b · c`, `- *Library:* ...`,
   `- *Concepts:* ...`. What the learner may need to know or look up.
4. `## Read in the blog first`: which section of the post, linked with a text fragment
   (`url#:~:text=Heading%20words`), and where to stop before the author's code. Say the page is
   complete on its own.
5. `## Where this fits`: two or three sentences: what came before, what this unlocks.
6. `## The problem`: one paragraph on what to build, then `### Input` (a table of line kinds),
   `### Output` (exact format, with a fenced block showing it), then `###` subsections with every
   rule, table, formula and edge case needed. Binary layouts as tables of field / type / meaning,
   in your own words. A learner must be able to pass using only this page; the independent solver
   proves it.
7. `## Requirements`: `- **R1** ...`, one testable behaviour each. Every case targets one.
8. `## Examples`: two or three `### Example k: title (test \`id\`)` blocks, each with `input:` and
   `output:` in fenced blocks copied from real cases, and a walkthrough of the one non-obvious
   step (a byte-by-byte table is ideal). Picture checkpoints embed the expected image:
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

## 3. The starter

Each checkpoint has two starters. The learner gets the **blank** one: a header comment (the
checkpoint, the problem page, how the program is run, `solutions/common/`, where the
boilerplate is) and an empty `main`, so the imports, the input parsing and the output are theirs
to write. The **boilerplate**, described below, does the input and output and leaves functions
marked TODO; it's the optional easier start.

Write the boilerplate as `solutions/pNN_slug.<ext>`, since the stub checks run on it. When every
checkpoint is done, run `py -P tools/blank_starters.py`: it keeps the boilerplate in
`starters/boilerplate/`, writes `starters/blank/`, and puts the blank starter in `solutions/`
(never over a file the learner changed). The checker then says "Not started yet" for an untouched
blank starter, and the book's editor offers both. If you change a boilerplate later, change the
copy in `starters/boilerplate/` too.

Because the blank starter does nothing for the learner, the problem page must state every
formatting rule the boilerplate handles (how numbers are rounded, how bytes are printed), and its
paragraph about the starter says the file starts empty, then what the boilerplate does and what it
leaves to fill in. Code the learner reuses across checkpoints goes in `solutions/common/`: for
C++ every `.cpp` there is compiled into every learner program (the `common` object library in
CMakeLists.txt); Python and JavaScript import from it. That lets the capstone call earlier work.

The boilerplate:

- One self-contained file. The header comment names the checkpoint, the problem page and
  `.\check NN`, and says only the output is checked.
- The input/output code is provided at the bottom, under a `---- Input/output (provided) ----`
  marker. It parses the input file and writes the output in the exact format, so the learner fills
  in one function (or a few), each marked `TODO:` and throwing/raising "not implemented".
- The program exits with **99** when a "not implemented" is raised (the checker then says "Not
  implemented yet: <function>"), and with 1 plus a message on stderr for other errors.
- Types the learner works with are declared in the starter with comments (they replace the blog's
  structs). Optional helpers for earlier checkpoints' work can be offered as provided headers or
  modules, clearly marked optional.
- Compiles/lints cleanly.

Language patterns:

| Language | Not implemented | Exit 99 |
|---|---|---|
| C++ | `throw NotImplemented("name");` (`include/NotImplemented.h`) | `catch (const NotImplemented& e) { std::cerr << "not implemented: " << e.what(); return 99; }` |
| Python | `raise NotImplementedError("name")` | `except NotImplementedError as e: print(f"not implemented: {e}", file=sys.stderr); sys.exit(99)` |
| JavaScript | `throw new Error("not implemented: name")` | catch, check the message prefix, `process.exit(99)` |

## 4. The reference solution

Same input/output code as the starter, function(s) filled in, written from the specification and
your own understanding, never copied from the blog. Header comment:
`Reference solution - checkpoint NN (...). SPOILERS: try it yourself first.` Shared reference code
(for a capstone, or several picture checkpoints) can live in `_spoilers/reference/common/`.

Learners read it: the Editorial shows the reference in full, with every file it includes from
`_spoilers/`, as "a solution that passes". Write it as a model answer: clear names, a short comment
wherever the reasoning isn't obvious, no dead code or debugging leftovers. An Accepted
`check NN -Ref` run on the committed tests records its fingerprint in `_spoilers/verified.json`, and
the book only says "Passes all N tests" while the files still match; after any change, run it
again. `build_book.py` warns (and exits non-zero) for any reference that isn't proven.

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
deterministic for a seed (fix timestamps, e.g. `SOURCE_DATE_EPOCH`).

## 6. Picture checkpoints

- The output path ends in `.png`; the program writes PNG or binary PPM of exactly the canvas size.
- End the page's Output section with a "**Writing the picture.**" paragraph for learners without
  the boilerplate: a binary PPM by hand (header, then 3 bytes per pixel; open the file in binary
  mode), or a PNG through a library such as stb_image_write. The checker reads either, whatever
  the file is called.
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
(details in `test-trust.md`): reference Accepted (committed cases and two fresh seeds); stub "Not
implemented yet"; three or more planted bugs fail with useful messages and causes, including the
blog's own bugs; correct variants pass where a tolerance exists; every requirement has cases; the
independent solver passes.

## 8. Writing style

Plain and direct: short sentences, active voice, no em-dash asides, no "not X but Y", no stock
phrases. Name things the way the learner knows them. Tables for layouts and rules, numbers for
everything that has one. In test titles and anything the checker prints, ASCII only.
