# Authoring an assignment

Use this guide to turn one row of the assignment map into a finished assignment. Build the first
one in full and use it as the model for the rest: copy its shape.

## Contents
1. Files
2. The problem page
3. The reference project
4. The starters
5. The generator and the case file
6. Picture assignments
7. Checking the checks (summary; details in test-trust.md)
8. Writing style
9. The primer

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

Register every assignment in `workbook.json`, with its place in the project, before work starts:

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

`files` lists the files this assignment creates, `extends` the earlier files it adds to, and
`buildsOn` the earlier files you expect it to use (the book shows them; nothing enforces them).
Add `"generatorNeedsReference": true` only when the generator runs the reference program, e.g. to
draw expected pictures. `assets/example-assignment/` shows a registered assignment.

Commands in `workbook.json` that name a compiled program end its name in `{exe}`, as
`new_workbook.py` writes them (`build/solutions/assignment_{id}{exe} {input} {output}`). The tools
turn it into `.exe` on Windows and leave it out on macOS and Linux, so never write `.exe` there
yourself. A generator finds the reference program without it: `wbcore.parse_args` defaults
`--ref` to `build/ref/assignment_NN`, with `.exe` on Windows.

Each project file gets a purpose in `project.purposes` (why it exists: its role, and which later
assignments use it), and each assignment gets `"jobs"`: for every file it touches, entry program
included, one to three imperative sentences on what the learner writes there, for someone starting
from an empty file (capabilities and data, not exact signatures or the algorithm). Purposes and
jobs become each starter's header and the book's "Start here" card, so they tell the learner where
to begin. The card shows a job's first sentence on its own and folds the rest away, so that
sentence must make sense alone: "Implement the even-odd fill with your `render/Scanline`", not
"Implement it" or "Implement those three functions".

## 2. The problem page

Write the page in Markdown, with these sections and headings word for word, in this order (the
book builder parses them):

1. `# NN · Title`
2. `**Difficulty:** Easy|Medium|Hard · **Assignment** N of M · **Check:** \`.\check NN\``
3. `**Tags**` followed by three bullets: `- *Language:* a · b · c`, `- *Library:* ...`,
   `- *Concepts:* ...`. The tags list what the learner may need to know or look up, and each
   one links to its primer entry: `[templates](#primer/templates) (optional)`.
4. `## Read in the blog first`: which section of the post, linked with a text fragment
   (`url#:~:text=Heading%20words`), and where to stop before the author's code. Say that the page
   is complete on its own.
5. `## Learning material`: one item per primer entry this assignment needs, as
   `- [Title](#primer/<id>): how this assignment uses it` (section 9). List what the assignment
   introduces, and any earlier entry it uses in a new way; the book adds the rest of the
   earlier ones it finds in the code.
6. `## Source material`: specification links, references the post cites, the post's section.
7. `## Where this fits`: two or three sentences on what came before, what this unlocks, and which
   files of the project it adds to.
8. `## The problem`: one or two short, plain sentences saying what the program does. The files,
   the jobs, the earlier files it can use and the two ways to start are on the book's "Start here"
   card (from `workbook.json`), so the page doesn't repeat them. Then come `### Input` (a table of
   line kinds), `### Output` (exact format, with a fenced block showing it), and `###` subsections
   with every rule, table, formula and edge case needed. Write binary
   layouts as tables of field / type / meaning, in your own words. A learner must be able to pass
   using only this page; the independent solver proves it.
9. `## Requirements`: `- **R1** ...`, one testable behaviour each. Every case targets one.
10. `## Examples`: two or three `### Example k: title (test \`id\`)` blocks, each with `input:` and
   `output:` in fenced blocks copied from real cases (say once in the README that line endings and
   runs of spaces don't matter; the checker compares words), and a walkthrough of the one
   non-obvious step (a byte-by-byte table is ideal). Picture assignments embed the expected image:
   `![expected picture for <id>](tests/NN/expected/<id>.png)`.
11. `## Constraints`: input limits, the guarantees about well-formed input, the number of tests and
    what they cover, the time limit.
12. `## Hints`: four blocks, each
    `<details><summary>Hint k: title</summary>` ... `</details>`:
    1. a nudge (where to start, what to think about),
    2. the approach in words,
    3. the traps (a bullet list),
    4. pseudocode.
    Each gives away more than the last; none gives the full solution in the learner's language.
13. `## Checking your solution`: the four commands (`.\check NN`, `-Case <id>`, `-Fresh`,
    `-Dispute <id> "why"`) and one real failure message copied from a planted bug's run.
14. `## After you pass: compare with the author's code`: how the author structured it (by
    function name), linked to the snippet's caption with a text fragment. Then point out, in a
    neutral tone, any place the snippet differs from the spec, in a sentence that leads with the
    difference (no label such as "Something to look for:").

The web book (`tools/build_book.py`) finds these sections by their heading text, so keep it
exact. It places them like this:
- "The problem", Requirements, Examples and Constraints form the statement.
- "Learning material" folds away at the top, with a collapsible block for each primer group
  that this assignment introduces and one for what earlier ones did; its links open the entry
  over the problem. (Pages that still say `## What you need` are read the same way.)
- "Read in the blog first" becomes a note at the top, with "Source material" folded away right
  under it.
- "Where this fits" folds away under the statement.
- Hints open in order.
- "Checking your solution" sits with the test results.
- "After you pass" becomes the Editorial tab, locked until the learner passes.
- Any other `##` section appears in the statement under its own heading.

Each example's `input:` block, and its `output:` block or expected picture, also becomes a test
case in the book's bottom panel.

## 3. The reference project

Write the reference first, in `_spoilers/project/`: the assignment's project files and its entry
program, from the specification and your own understanding; never copy from the blog. Later
references include earlier ones the same way the learner's will, so the reference reads as the
finished project and doubles as the proof that the layout works.

- The entry program reads the input, calls the project, and writes the output in the exact format.
  It holds no logic later assignments need.
- Project files use the author's names where the post has them (types, functions, files), and
  carry a short header comment saying which assignment they belong to. Where the project layout
  needs a different name (a `FontParser` method split into its own module, say), the problem page
  maps the workbook's name to the post's, so a learner reading both can follow.
- A file later assignments add to has sections: each later assignment's additions go under a
  marker line, `// ---- Assignment 12: two segments ----` (`#` or `--` in languages with those
  comments). The code before the first marker belongs to the assignment that creates the file.
  Includes a later section needs go in that section, even mid-file, so the file builds at every
  point in the series.
- Learners read the reference: the Editorial shows the assignment's files as they stand after it
  (later sections left out), with the names of earlier files it uses. Write a model answer: clear
  names, a short comment wherever the reasoning isn't obvious, no dead code or debugging leftovers.

`check NN -Ref` builds and checks the reference *as it stands after assignment NN*: the files of
assignments 01 to NN, later sections left out (`tools/project.py`, `reference_as_of`). An Accepted
run on the committed tests records the fingerprint of every file the program includes in
`_spoilers/verified.json`, and the book says "Passes all N tests" only while they still match.
After any change to a reference file, run `-Ref` again for every assignment that includes it.
`build_book.py` warns (and exits non-zero) for any unproven reference.

## 4. The starters

Each of an assignment's own files (its entry program and the files it creates) has two starters at
the same path: `starters/blank/` and `starters/boilerplate/`. Opening an assignment copies its
starters into the learner's project (`tools/project.py start`), never over an existing file: the
boilerplate by default (`project.starter` in `workbook.json`), or the blank ones when the learner
chose From scratch; the book's switch replaces them after asking.

`py -P tools/blank_starters.py` writes the same header, from `workbook.json`, at the top of every
starter, blank or boilerplate: the assignment and its problem page, then "Why this file exists:"
(the purpose), "Your job:" (the assignment's job for this file) and "How to start:" (write it all
yourself, or press Boilerplate). The entry program's header also says how the checker runs it and
lists the assignment's other files, with the job in any earlier file it adds to. Blank starters
are that header and nothing else (an empty `main` in the entry program; `#pragma once` for C++
headers): the learner writes the imports, the API, the input parsing and the output. Rerun the
script with `--force` after changing titles, files, purposes or jobs; it replaces only the header
of boilerplate files.

You write the Boilerplate starters from the reference:
- The entry program is the reference's, with a header comment saying what's left to write. It
  exits with 99 when it catches a "not implemented" error (the checker then says "Not implemented
  yet: <function>"), and with 1 plus a message on stderr for other errors.
- Headers that only declare things are the reference's. Function bodies become a `TODO:` comment
  pointing at the page's section, then a "not implemented" error naming the function.
- A file later assignments add to has stubs for their functions too (marked with the assignment),
  so the boilerplate path keeps compiling.
- Every include or import line ends with a comment saying what the file uses it for:
  `#include <sstream>  // std::istringstream: splitting an input line into words`,
  `#include "font/ByteReader.h"  // ByteReader (assignment 01): reading big-endian numbers`.
  The learner meets the line before any page explains it.
- Every starter compiles without errors or warnings: build every blank and every boilerplate
  starter into a scratch project and check that each boilerplate program reports its TODO.

| Language | Not implemented | Exit 99 |
|---|---|---|
| C++ | `throw std::logic_error("not implemented: name");` | `catch (const std::exception& e)`: if `what()` starts with `not implemented`, print it to stderr and `return 99` |
| Python | `raise NotImplementedError("name")` | `except NotImplementedError as e: print(f"not implemented: {e}", file=sys.stderr); sys.exit(99)` |
| JavaScript | `throw new Error("not implemented: name")` | catch, check the message prefix, `process.exit(99)` |

Because the blank starter does nothing for the learner, the problem page must state every
formatting rule the boilerplate handles (how to round numbers, how to print bytes).

## 5. The generator and the case file

Use `tools/wbcore.py`: `wbcore.parse_args("NN")`, `wbcore.Cases(out, seed, compare, requirements,
explain, source=...)`, `cases.add(id, req, title, input_lines, expected=... | expected_file=...)`,
`cases.save()`. Domain helpers (file formats, sample data) go in a workbook-specific module next
to it.

The case file's header has:
- `source` (default source of expected values; cases may override),
- `compare` (`records name=field1,field2 tolerance=x`, `unordered name=...`, or
  `image band=1 allow=0.0002`),
- `explain` (location of a difference -> the requirement it points to: `key=R4`, `key:field=R7`,
  `key~word=R3`, `_lines=R1`; for `unordered`, `key:missing`),
- `requirement R1 text` lines.

Name a case aimed at a requirement `NN-R<k>-<slug>`, and an end-to-end case `NN-E2E-<slug>`.
Write titles in ASCII, saying what the input is. Cases built from randomness include the seed in
their id. Cover every requirement (two or more cases each), every trap the blog's text or code
reveals, real data, edge cases, and a random section that changes with `--seed`.

The generator checks hand-made inputs with the oracle (`assert`) before writing them. Make
generators deterministic for a seed (fix timestamps, e.g. `SOURCE_DATE_EPOCH`). Inputs carry what
earlier assignments would produce (an offset, a parsed record), so an assignment's tests depend
only on the earlier files it chooses to use.

## 6. Picture assignments

- The output path ends in `.png`; the program writes a PNG or binary PPM the size of the canvas.
- End the page's Output section with a plain paragraph, with no bold label, for learners without
  the boilerplate. Say that the program writes the picture to the output path the checker gives
  it, as a PNG (through the project's canvas or a library such as stb_image_write) or as a binary
  PPM written by hand (header, then 3 bytes per pixel; open the file in binary mode). The checker
  reads either, whatever the file's name. A header the project needs goes in through `project.copy` (e.g.
  `third_party/stb_image_write.h`), so the learner's project builds on its own.
- State the exact pixel rule (e.g. "filled when the pixel's centre is inside", "a w x h
  rectangle covers columns cx - floor(w/2) ..."), and say that edges may move one pixel.
- The reference draws expected images; the generator validates each against an independent
  source before writing it (sampled pixels against an inside test, every point marker present,
  points along every segment inked).
- Keep canvases under about 600 x 600 and thin features at least ~2 pixels wide.
- Build at least one different-but-correct variant (other sampling, other rounding) and confirm it
  passes.

## 7. Checking the checks

Compile into your own build folder and use `-Run` while others work in parallel. All of these must
hold (details in `test-trust.md`):
- The reference as it stands after the assignment passes with Accepted (committed cases and two
  fresh seeds), which also proves the project builds at that point in the series.
- The boilerplate says "Not implemented yet".
- The blank starter says "Not started yet".
- Three or more planted bugs fail with useful messages and causes, including the blog's own bugs.
- Correct variants pass where a tolerance exists.
- Every requirement has cases.
- The independent solver passes.

## 8. Writing style

All text the learner reads should sound like a person wrote it for them: the book's labels and
messages, the problem pages, the starter headers, the `jobs` and `purposes` in `workbook.json`,
the checker's output, the READMEs and a collection site's pages. The rules below adapt
[stop-slop](https://github.com/hardikpandya/stop-slop) (MIT) to this kind of text.

Every page and README also gets a pass with the
[avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) skill (MIT) in edit mode,
technical context, keeping the page's plain technical voice. Install it once as a skill for your agent
(it brings its `bin/avoid-ai-writing.js` detector; `scripts/aiw_scan.py` says where it looks), and
read its `SKILL.md` and `references/patterns.md` in full before the pass, as it asks. Its editing contract
fits workbooks: code blocks, test ids, links, tables of formats and anything the tests check are
protected, and a rewrite never adds facts.

Before you call a page or a pass done, run both scanners (in this skill):
`py -P scripts/slop_scan.py <workbook>` for the rules below, and
`py -P scripts/aiw_scan.py <workbook>` for avoid-ai-writing's detector. Each hit is a prompt to
look; you decide it.

### Formatting

- Bold only what the book or the tests parse: the header line (`**Difficulty:**`,
  `**Assignment** N of M`, `**Check:**`), `**Tags**`, and requirement ids (`- **R1**`, and
  `- **E2E**` where a page has one). Don't bold defined terms or phrases for emphasis; allow at
  most one bold phrase in a `##` section, and usually none. Lead with the important word instead.
- Don't open list items or paragraphs with bold labels ("**Writing the picture.** The name
  ends..."). Write the point as a sentence, or use a `###` heading when it starts a real
  subsection.
- Use sentence case for headings and every UI label ("Problem list", "Test result"), except names
  such as verdicts ("Wrong Answer") that the checker prints.
- Use a list where the content is a list (steps, rules, cases, fields) and prose for
  explanations. Don't follow a heading with a one-line warm-up that repeats it.

### Sentences

- Use active voice and name the actor: "the checker compares what your program writes", not "the
  output is checked".
- Talk to the learner as "you". Don't lecture from a distance ("Learners often...", "This is
  why...").
- Lead with the subject or the verb. Don't open with a What/When/Why/How clause that delays the
  point, or with "So" or "Look".
- Write whole sentences. No staccato fragments ("Small. Fast. Yours."), and no short line at the
  end of a paragraph that sounds like a slogan ("Tests stay fair.", "so the design is yours").
- Don't use em dashes or spaced en dashes. Use a comma, a colon, brackets or a new sentence.

### Structures to drop

- Binary contrasts: "not X but Y", "it isn't A, it's B", "not just X". Say the true thing once.
- Saying what something isn't before saying what it is.
- Rhetorical questions and set-ups ("Think a test is wrong?", "Here's the thing:"). Write a
  statement, or start with "If".
- Things doing human verbs ("the page wants", "the test insists"). Name who acts: you, the
  checker, the font, the parser.
- A list of three out of habit. Give the real items, however many there are.

### Words

- Cut adverbs and fillers: just, really, simply, actually, basically, exactly, very, quite, truly,
  easily, carefully, clearly, completely.
- Use sweeping words (always, never, everything, everyone, nobody) only when they state a rule the
  tests check. "Every point gets a marker" is a spec; "always be careful" is filler.
- Leave out meta-commentary ("This section explains...", "Let's walk through...", "Note
  that..."), and don't tell the reader something is important, hard or easy. Start with the
  content; show the number or the case that makes it hard.

### Specifics

- Give the number wherever there is one, and use the names the learner knows (their project's
  file and function names).
- Use tables for layouts and rules.
- Use ASCII only in test titles and in anything the checker prints.

### Final read

Read for the patterns avoid-ai-writing names that neither scanner catches: a colon leading into
three items, runs of sentences with the same opener, paragraphs of the same length, and a
punchline that restates the paragraph.

Last, score the page as stop-slop does: directness, rhythm, trust in the reader, sounding human
and density, 1 to 10 each. Under 35 of 50, revise it.

## 9. The primer

`primer/*.md` explains everything the assignments expect the learner to know, so the workbook is
the one place they need. The format is in `tools/primer.py`; the book shows it as the Primer view.

Groups, one file each, in this order: the language, its standard library (one entry per header or
module the code imports), the field (one or two files: for a font renderer, the font format, then
drawing and geometry), and the tools the learner runs (compiler, build tool, the checker).

Each entry:
- The title is the term, with at most a short gloss: `` `<sstream>`: parsing text ``.
- `id` is what pages link to. `also` lists other names, for search. `code` is a regular expression
  that finds the entry in an assignment's Boilerplate; give one to every language and library
  entry, and make it precise, because a match counts as the assignment using the entry. The
  reference doesn't count: what the learner needs beyond the Boilerplate is what the page asks
  for, and its tags link those entries.
- Never give away an answer. The learner hasn't opened `_spoilers/`, so an entry or a What you
  need note describes the Boilerplate's finished code, or says in general terms what an
  assignment needs the feature for. It never quotes or paraphrases how the reference writes a
  TODO body. Teaching examples of your own are fine.
- Keep "where the workbook uses it" short: the first use and one or two later ones. A learner
  on the first assignment hasn't met the later files.
- The tools entries say how to install each tool on the learner's systems (official page and a
  package-manager command you have confirmed) and how to check it from a terminal.
- The text says what it is from zero, why it matters here, with a small example of your own, and
  where the workbook uses it (assignment numbers and files, checked). 120 to 300 words is typical.
- `Learn more:` lists two or three references you have opened: the language's reference site, a
  good tutorial, the specification, an encyclopedia article.

On each page, the Learning material list (section 2) names the entries the assignment introduces and
says how this assignment uses each. Tags link to entries too.

An entry belongs on the page where the learner first needs it. A long first list (the first
assignment meets most of the language) is fine, but move tool entries to the assignment where
the tool first matters, and leave a technique only the reference uses to the entries that link
to it.

`py -P tools/primer_check.py` reports an entry the Boilerplate or tags use before any page lists
it, a link to an unknown entry, an entry that no page lists and no entry links to, an entry
without text or links, and an include without its comment. Add `--links` to fetch every outside link. Then have a separate agent read
the first three assignments as a learner who knows another language but not this one or the
field, using only the book, and fold in every term it had to look up elsewhere.
