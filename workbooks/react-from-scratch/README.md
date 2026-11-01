# Build React yourself

*Learn what React does by writing it.*

Twelve assignments that rebuild the core of React in JavaScript. You write elements and the DOM nodes behind them, a work loop
that can stop between fibers, a commit phase, reconciliation by position and then by key, function components, `useState`,
`useEffect`, and finally a todo app that runs on your own library. When you're done, `solutions/` holds a small React called
`didact` that you can put on GitHub as it is.

Two posts supply the design. Rodrigo Pombo's [Build your own React](https://pomb.us/build-your-own-react/) is the spine:
fibers, the render and commit phases, reconciliation, function components and hooks. Wim Jongeneel's
[Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d) supplies what Pombo
leaves out: matching children by key and the mount, update and unmount life cycle. Each page says which post to read first, and
where the workbook goes beyond them (reordering keyed children, `useEffect`, the todo app's removal and counts) it says that too.

Both posts describe React as it was in 2019 and 2021, so your code is checked against React as it is today. The tests
run your library on a small DOM of ours, and the expected output comes from React 19.3.1 running on jsdom. The posts also have
bugs, and the tests follow React, not the posts. [React today](docs/react-today.md) lists where React 19 and the posts part ways.

The problems are in `problems/` and, nicer to read, in the web problem book (`book/problem-book.html`). The book has a problem
list with your progress, and for each assignment the statement, what it adds to your project, hints that open in order, an
Editorial with a solution proven to pass every test, an editor with the assignment's files, the example test cases and a primer
for everything the assignments assume.

| # | Assignment | # | Assignment |
|---|---|---|---|
| 01 | Create elements | 07 | Match children by key |
| 02 | DOM nodes and props | 08 | Reorder keyed children |
| 03 | Render a tree | 09 | Function components |
| 04 | Work in units: fibers | 10 | `useState` |
| 05 | Render phase, then commit | 11 | `useEffect` |
| 06 | Reconcile children by position | 12 | The todo app |

Needs: Node.js 26 or newer for your code, and Python 3.11 or newer for the tools. Fresh test sets (`-Fresh`) also need React,
react-dom and jsdom, which `npm install` fetches inside `tools/oracle/`. It was last verified on 1 November 2026 against
React 19.3.1, jsdom 30.1.3 and Node 26.13; [Keeping the workbook current](docs/maintenance.md) says what to do when
those move.

## Start here

Ask your coding assistant to "set up my workbook": it checks the tools, creates the project and opens the book. Or open the book
yourself: double-click `study.cmd` on Windows or `study.command` on macOS, or run `.\study` (PowerShell) or `./study.sh`
from this folder. Run and Submit work in the book opened this way, and it offers to create the project if there isn't one yet. The
study script runs in a window: leave it open while you work, and use the book's Exit button when you're done.

## Your project

```
solutions/
  package.json         plain ES modules, nothing to install
  index.html           the page the todo app runs in
  harness/             given to you: the tiny DOM and the scenario runner the tests use
  assignments/         one small program per assignment, which the checker runs
  src/
    main.js            12  mounts the todo app
    app/TodoApp.js     12
    didact/
      index.js         04  the Didact object: createElement, render, useState, useEffect
      createElement.js 01
      dom.js           02
      renderSync.js    03  the first, recursive draft of render
      state.js         04  the library's shared bookkeeping
      render.js        04  render and the work loop
      reconcile.js     04  child fibers, growing through 06, 07 and 08
      commit.js        05  applying the finished tree to the DOM
      hooks.js         10  useState, then useEffect in 11
```

Do the assignments in order. Opening an assignment (in the book, or with `.\check NN` or `./check.sh NN`) creates its files,
each with a comment saying why the file exists and what your job in it is. It doesn't overwrite anything you've written. You
write the real work in `src/didact/`, where later assignments build on it, and several assignments rewrite a file you wrote
earlier: the reconciler is the clearest case, growing from one fiber per child to matching by position, then by key, then
across reorders. The program in `assignments/` is thin: it hands your library to the harness, which reads a test input, drives
your code and writes what the DOM looks like afterwards.

Each test input carries what earlier assignments would produce, so a test depends only on the files an assignment builds on. The
checker runs the whole project at once, though, and if a file from another assignment is missing it tells you which one. The
book's Re-check solved button runs every solved assignment again, so you see at once when a change breaks an earlier one (the
book marks it with a red `!`). The Files panel shows the project as it grows, and once every assignment passes, the problem
list shows your project next to the authors'.

## Doing an assignment

1. Read the problem (book or `problems/NN-*.md`). In the book, its Start here card lists the files to complete, your job in
   each and the earlier files you can use.
2. Write the files. Each one starts as the Boilerplate, which gives you the program the checker runs and the declarations, and you
   fill in the parts marked `TODO`. To write all of it yourself, choose From scratch above the editor: each file then starts empty
   apart from its comment.
3. Check it from this folder (`./check.sh` instead of `.\check` on macOS or Linux), or with Run and Submit in the book:

```
.\check 01                         run every test
.\check 01 -Case <test-id>         one test in full: input, expected output, your output
.\check 01 -Fresh                  a newly generated set of tests (new random seed)
.\check 01 -Dispute <test-id> "why"    set aside a test you believe is wrong
```

The verdict is `Accepted`, `Wrong Answer`, `Compile Error`, `Runtime Error` or `Time Limit Exceeded`. The checker compares text
output word by word, so line endings and extra spaces don't matter, except inside quoted strings. For each failure it shows its
best guess at the requirement behind it, where the expected value came from, and the command that reproduces it. What your
program prints is never compared, since the answer goes to the output file; the book shows it under the test result, so
`console.log` debugging works.

## How the tests work

There is no browser in the checker. Your library draws into `harness/minidom.js`, a small DOM that counts what you do to it, and
the harness runs scenario files: a few lines that define trees of elements, render them, click things, wait for the work loop
and print what the page looks like. Every element in that print carries a label (`a`, `b`, `c`...) assigned the first time it
is seen, so "did you keep this node or build a new one?" shows up as one word in the diff.

The expected print comes from real React 19.3.1, driven through `createRoot` inside `act` on jsdom, running the same scenario. The
two things React can't answer, how many units of work a render takes and what your code did to the DOM, come from small
independent models in each test generator. The reference solution is never the source of an expected value.

## If you think a test is wrong

Run `.\check 01 -Dispute <test-id> "your reason"`. That test stops counting and you can carry on; the verdict reads `Accepted (1
disputed)`. Then ask your coding assistant to "review my disputes". It rechecks the expected value against its independent source
and either fixes the test or shows you why it's right. The checker keeps disputes in `disputes.json`.

## Another language

This workbook is JavaScript only. What it teaches leans on JavaScript's closures and function identity, and the harness is
JavaScript, so a project in another language would have to port the harness first. To check a one-off program without changing
anything, run `.\check 01 -Run "path/to/program {input} {output}"`.

## What's in here

| Path | What it is |
|---|---|
| `problems/` | Problem statements (`tools/build_book.py` makes the book from these) |
| `primer/` | The primer: every term, library and tool the assignments use, explained, with links to learn more |
| `solutions/` | Your project, created when you set the workbook up |
| `starters/project/` | What your project starts with: `package.json`, `index.html`, its README and `.gitignore` |
| `starters/blank/`, `starters/boilerplate/` | Each assignment's files, blank and with the program and declarations done |
| `harness/` | The mini DOM, the scenario runner and the components the tests use; copied into your project |
| `tests/NN/` | Test inputs and expected outputs |
| `docs/react-today.md` | Where React 19 and the posts differ |
| `docs/maintenance.md` | How to keep the versions and the expected outputs current |
| `study.cmd`, `study.command`, `study.ps1`, `study.sh` | Open the book with Run and Submit working (they start `tools/serve.py`) |
| `tools/serve.py` | The study server: only reachable from this computer; loads and saves your project's files, opens them in your editor and runs the checker |
| `tools/check.py` | The checker (`check.ps1`, `check.cmd` and `check.sh` call it) |
| `tools/run_js.py` | Runs an assignment's program with Node |
| `tools/project.py` | Sets up your project and starts assignments (`setup`, `start NN`, `status`) |
| `tools/langs.py` | The languages a project can be in, and how to install them |
| `tools/gen_pNN.py`, `tools/reactgen.py` | Each assignment's test generator (used by `-Fresh`) and the helpers they share |
| `tools/oracle/` | Runs a scenario on real React and jsdom |
| `tools/build_book.py` | Builds `book/problem-book.html` (the page design is `tools/book_template.html`) |
| `tools/primer_check.py` | Checks that the primer covers what each assignment uses (`--links` also tests its links) |
| `docs/authoring-guide.md` | How to write the assignments and their tests |
| `_spoilers/` | The reference project. Don't open it until you've passed. |

The tools work on Windows, macOS and Linux. Program names in `workbook.json` end in `{exe}`, which the tools turn into `.exe` on
Windows and leave out on macOS and Linux, so the same file works on all three.

## Credit and licence

The posts belong to their authors. This workbook links to them and contains none of their text or code; the assignments, tests,
tools and reference solution are original, under the repository's Apache License 2.0. Neither author's repository carries a
licence, so nothing from them was reused.
