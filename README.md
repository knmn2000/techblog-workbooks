# techblog-workbooks

The collection of tech blog posts turned into hands-on workbooks. Each workbook asks you to
rebuild what a post builds, one checkpoint at a time, until you understand what the post was
teaching, because you wrote it yourself.

There's one workbook so far, and more are on their way. If you've turned a post into a workbook,
or there's a post you'd love to see here, [contributions are welcome](#contributing).

The workbooks are made with [tech-blog-to-workbook](https://github.com/knmn2000/tech-blog-to-workbook),
a Claude Code plugin that reads a post and builds the checkpoints, tests and problem book.

![A checkpoint in the problem book: the statement on the left, the editor and test cases on the right](docs/screenshots/problem-view.png)

## Workbooks

| Workbook | Built on | Language | Checkpoints | What you build |
|---|---|---|---|---|
| [Tiny TrueType renderer](workbooks/tiny-truetype-renderer) | [Writing a tiny TrueType parser and renderer from scratch](https://yayo1.com/en/blog/tiny-truetype-renderer/) by Yohei Yamasaki | C++ starters (any language works) | 18, with 572 tests | A font renderer from raw bytes: the table directory, character maps, glyph outlines, Bézier curves, scanline filling, and finally a line of text |

*More workbooks on the way.*

### What you build in the TrueType workbook

Every picture below is an expected output from the workbook's tests. Your program draws the same
thing from the font file's bytes.

| 08 · Straight lines | 11 · Curves | 14 · Even-odd fill | 16 · Non-zero fill | 17 · Glyph fill |
|:---:|:---:|:---:|:---:|:---:|
| <img src="workbooks/tiny-truetype-renderer/tests/08/expected/08-R3-B.png" width="120" alt="The outline of B drawn with straight lines"> | <img src="workbooks/tiny-truetype-renderer/tests/11/expected/11-R3-S.png" width="120" alt="The outline of S drawn with quadratic curves"> | <img src="workbooks/tiny-truetype-renderer/tests/14/expected/14-R5-ten.png" width="120" alt="十 filled with the even-odd rule, leaving a hole where the strokes cross"> | <img src="workbooks/tiny-truetype-renderer/tests/16/expected/16-R2-ten.png" width="120" alt="十 filled with the non-zero rule, with no hole"> | <img src="workbooks/tiny-truetype-renderer/tests/17/expected/17-E2E-s1-U+6C34.png" width="120" alt="水 filled from Noto Sans JP"> |

And at the end, checkpoint 18 puts your pieces together:

<img src="workbooks/tiny-truetype-renderer/tests/18/expected/18-E2E-hello.png" width="420" alt="Hello, World! rendered in JetBrains Mono Bold">

## Start a workbook

```bash
git clone https://github.com/knmn2000/techblog-workbooks
cd techblog-workbooks/workbooks/tiny-truetype-renderer
```

Then double-click `study.cmd` in that folder (or run `.\study`). That's the whole setup: it
prepares the build the first time and opens the problem book in your browser, with **Run** and
**Submit** running your code right there. Or, with the plugin installed, ask Claude Code to "open
my workbook": it checks the tools, offers to install anything missing, and opens the book for you.

In the book you get a problem list with your progress and, for each checkpoint, the statement,
hints that open in order, an Editorial with a solution proven to pass, an editor and the example
test cases. Your program lives in `solutions/pNN_*.cpp`. Each one starts as a comment and an
empty `main`: the includes, reading the input and writing the output are yours. If you'd rather
start with the input/output done, pick **Boilerplate** in the editor. You can also write in your
own editor and check from a terminal with `.\check 01`; the book picks up your saved changes.

Each workbook's own README lists what it needs (for the TrueType workbook: g++ with CMake and
Ninja, and Python 3.11 or newer).

## How checking works

- **Only your output is checked.** Your program runs as `<program> <input-file> <output-file>`,
  so you choose the structure, the language and the libraries.
- **Expected answers come from somewhere independent**, never from the reference solution. In the
  TrueType workbook that's mostly [fontTools](https://github.com/fonttools/fonttools).
- **The checks are checked.** Before a checkpoint ships, the reference solution passes, planted
  bugs fail (including any bug in the post's own code), different-but-correct solutions pass, and
  a separate solver passes using only the problem page.
- **A wrong test never blocks you.** `.\check 07 -Dispute <test-id> "why"` sets a test aside, and
  `.\check 07 -Fresh` gives you a new set of tests you haven't seen.
- **Checkpoints stand alone, and build on each other.** Every input carries what the earlier
  checkpoints would produce, so you can start anywhere. Code you put in `solutions/common/` is
  shared by all your checkpoints, so the last one can call what you wrote earlier.

| Problem list | Test result |
|---|---|
| ![The problem list with progress by difficulty](docs/screenshots/problem-list.png) | ![An Accepted verdict with a pass bar for each requirement](docs/screenshots/test-result.png) |

The book follows your system's light or dark theme:

![A fill checkpoint in the light theme](docs/screenshots/problem-view-light.png)

## Contributing

This repository is the home for every tech blog post converted into a workbook, and it grows with
your help.

- **Add a workbook.** Install [tech-blog-to-workbook](https://github.com/knmn2000/tech-blog-to-workbook)
  in Claude Code and ask it to turn a post into a workbook. Put the result in
  `workbooks/<short-name>/`, add a row to the table above, and open a pull request. Before you do:
  - every checkpoint passes the plugin's checks (reference Accepted, planted bugs fail, an
    independent solver passes from the page alone);
  - `py -P tools/blank_starters.py` has run, so `solutions/` holds blank starters, and
    `tools/build_book.py` has rebuilt the book;
  - nothing from the post is copied: problem pages explain in their own words and link to it;
  - anything bundled from elsewhere (fonts, libraries, data) is allowed to be shared, with its
    licence next to it.
- **Suggest a post.** Open an issue with the link and what you'd like to learn from it.
- **Report a wrong test.** If `-Dispute` turned up a test you believe is wrong, open an issue with
  the checkpoint, the test id and why.

## Licence

The workbooks' own content (problem pages, tools, tests and solutions) is under the
[Apache License 2.0](LICENSE) unless a workbook says otherwise. Fonts and third-party code keep
their own licences, noted inside each workbook (for example `fonts/README.md`). The blog posts
belong to their authors; the workbooks link to them and contain none of their text or code.
