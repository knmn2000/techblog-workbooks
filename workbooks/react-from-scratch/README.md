# Build React yourself

*Learn what React does by writing it.*

Twelve assignments, and at the end you have rebuilt the core of React in JavaScript: elements and the DOM nodes behind them, a work loop that can stop between fibers, a commit phase, reconciliation by position and then by key, function components, `useState` and `useEffect`. The last assignment is a todo app that runs on your own library. What's left in `solutions/` is a small React called `didact`, and you can put it on GitHub as it is.

The design comes from two posts. Rodrigo Pombo's [Build your own React](https://pomb.us/build-your-own-react/) is the spine: fibers, the render and commit phases, reconciliation, function components and hooks. Wim Jongeneel's [Creating Our Own React From Scratch](https://itnext.io/creating-our-own-react-from-scratch-82dd6356676d) fills in what Pombo leaves out: matching children by key and the mount, update and unmount life cycle. Every page tells you which post to read first. Where the workbook goes past both (reordering keyed children, `useEffect`, the removal and counts in the todo app) the page says so.

The posts describe React as it was in 2019 and 2021, and React has moved on, so your code is checked against React as it is today. The tests run your library on a small DOM of ours, and the expected output comes from React 19.3.1 running on jsdom. The posts have bugs too. When a post and React disagree, the tests side with React. [React today](docs/react-today.md) lists the places where React 19 and the posts part ways.

The problems live in `problems/`, but they read better in the web problem book, `book/problem-book.html`. It keeps a problem list with your progress. Each assignment gets its statement, the files it puts into your project, hints that open one at a time, an Editorial whose solution is proven to pass every test, an editor holding the assignment's files, the example test cases, and a primer on everything the assignments assume you know.

| # | Assignment | # | Assignment |
|---|---|---|---|
| 01 | Create elements | 07 | Match children by key |
| 02 | DOM nodes and props | 08 | Reorder keyed children |
| 03 | Render a tree | 09 | Function components |
| 04 | Work in units: fibers | 10 | `useState` |
| 05 | Render phase, then commit | 11 | `useEffect` |
| 06 | Reconcile children by position | 12 | The todo app |

You need Node.js 26 or newer for your code and Python 3.11 or newer for the tools. Fresh test sets (`-Fresh`) also want React, react-dom and jsdom, which `npm install` fetches inside `tools/oracle/`. Last verified on 1 November 2026 against React 19.3.1, jsdom 30.1.3 and Node 26.13. When those move, [Keeping the workbook current](docs/maintenance.md) says what to redo.

## Start here

The quick way: tell your coding assistant "set up my workbook". It checks the tools, creates the project and opens the book. To open the book yourself, double-click `study.cmd` on Windows or `study.command` on macOS, or run `.\study` (PowerShell) or `./study.sh` from this folder. Opened like that, Run and Submit work in the book, and it offers to create the project if there isn't one yet. The study script keeps a window open. Leave it there while you work, and press the book's Exit button when you're done.

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

Do the assignments in order. Opening one, in the book or with `.\check NN` or `./check.sh NN`, creates its files. Each carries a comment on why it exists and what your job in it is. Nothing you've written gets overwritten. The real work goes in `src/didact/`, and assignments keep coming back to files you wrote before. The reconciler is the clearest case: it starts as one fiber per child, then learns to match by position, then by key, then across reorders. The program in `assignments/` is thin. It hands your library to the harness, which reads a test input, drives your code and writes out what the DOM looks like afterwards.

Every test input already contains what the preceding assignments would produce, which means a test depends only on the files its own assignment builds on. Each check runs the whole project at once, though, and if a file from another assignment is missing the checker names the one you need. When a change breaks something you solved before, the book's Re-check solved button finds it: it runs every solved assignment again and marks a failure with a red `!`. The Files panel shows the project as it grows. Once every assignment passes, the problem list puts your project next to the authors'.

## Doing an assignment

1. Read the problem, in the book or as `problems/NN-*.md`. The book's Start here card lists the files to complete, what you do in each, and what you already have to build on.
2. Fill in the files. Each starts as the Boilerplate: the program that `check` runs and the declarations are done, and the parts marked `TODO` are yours. If you'd rather write all of it, pick From scratch above the editor and each file starts empty except for its comment.
3. Check your work from this folder (`./check.sh` in place of `.\check` on macOS or Linux), or press Run and Submit in the book:

```
.\check 01                         run every test
.\check 01 -Case <test-id>         one test in full: input, expected output, your output
.\check 01 -Fresh                  a newly generated set of tests (new random seed)
.\check 01 -Dispute <test-id> "why"    set aside a test you believe is wrong
```

You get one of `Accepted`, `Wrong Answer`, `Compile Error`, `Runtime Error` or `Time Limit Exceeded`. Text output is compared word by word, so line endings and extra spaces don't matter, except inside quoted strings. For each failure the checker guesses at the requirement behind it, says where the expected value came from and gives the command that reproduces it. Whatever your program prints is never compared, because the answer goes to the output file. The book shows that printout under the test result, so `console.log` debugging works.

## How the tests work

No browser is involved. Your library draws into `harness/minidom.js`, a small DOM that counts what you do to it. The harness runs scenario files, which are a few lines that define trees of elements, render them, click things, wait for the work loop and print what the page looks like. Each element in that print gets a label (`a`, `b`, `c`...) the first time it's seen. The question "did you keep this node or build a new one?" comes down to one word in the diff.

The expected print comes from real React 19.3.1 on jsdom, running the same scenario through `createRoot` inside `act`. React can't answer two questions: how many units of work a render takes, and what your code did to the DOM. Small independent models in each test generator answer those. The reference solution never supplies an expected value.

## If you think a test is wrong

Run `.\check 01 -Dispute <test-id> "your reason"`. That test stops counting and you can carry on. The verdict reads `Accepted (1 disputed)`. Later, tell your coding assistant to "review my disputes". It rechecks the expected value against its independent source, then fixes the test or shows you why it was right. Disputes are stored in `disputes.json`.

## Another language

JavaScript only. What the workbook teaches leans on closures and function identity, and the harness is written in JavaScript too, so a project in another language would have to port the harness first. A one-off program can still be checked without changing anything: `.\check 01 -Run "path/to/program {input} {output}"`.

## What's in here

| Path | What it is |
|---|---|
| `problems/` | The problem statements. `tools/build_book.py` builds the book from them |
| `primer/` | The primer: every term, library and tool the assignments use, explained, with links to learn more |
| `solutions/` | Your project, created when you set the workbook up |
| `starters/project/` | The skeleton your project starts from: `package.json`, `index.html`, its README and `.gitignore` |
| `starters/blank/`, `starters/boilerplate/` | Each assignment's files twice over, blank, and with the program and declarations filled in |
| `harness/` | The mini DOM, the scenario runner and the components the tests use. A copy goes into your project |
| `tests/NN/` | Test inputs and expected outputs |
| `docs/react-today.md` | Where React 19 and the posts differ |
| `docs/maintenance.md` | Keeping the versions and the expected outputs current |
| `study.cmd`, `study.command`, `study.ps1`, `study.sh` | Open the book with Run and Submit working; they start `tools/serve.py` |
| `tools/serve.py` | The study server. It answers only on this computer, loads and saves your project's files, opens them in your editor and runs the checker |
| `tools/check.py` | The checker, called by `check.ps1`, `check.cmd` and `check.sh` |
| `tools/run_js.py` | Runs an assignment's program under Node |
| `tools/project.py` | Sets up your project and starts assignments: `setup`, `start NN`, `status` |
| `tools/langs.py` | Which languages a project can be in, and how to install them |
| `tools/gen_pNN.py`, `tools/reactgen.py` | One test generator per assignment (`-Fresh` uses them) and the helpers they share |
| `tools/oracle/` | Runs a scenario on real React and jsdom |
| `tools/build_book.py` | Builds `book/problem-book.html`; the page design lives in `tools/book_template.html` |
| `tools/primer_check.py` | Checks that the primer covers what each assignment uses, and with `--links` that its links work |
| `docs/authoring-guide.md` | How the assignments and their tests are written |
| `_spoilers/` | The reference project. Keep it closed until you've passed. |

The tools run on Windows, macOS and Linux. Program names in `workbook.json` end in `{exe}`: the tools turn that into `.exe` on Windows and drop it on macOS and Linux, which keeps one file valid on all three.

## Credit and licence

Both posts belong to their authors. The workbook links to them and holds none of their text or code. Assignments, tests, tools and reference solution are original, under the repository's Apache License 2.0. Neither author's repository carries a licence, so nothing from them was reused.
