// ======================================================================================
// Assignment 05: Render phase, then commit
// Problem: problems/05-commit.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 05 as `python -P tools/run_js.py
//   solutions 05 <input-file> <output-file>`. It reads a test input, calls your code and
//   writes the answer to the output file, and the checker compares that answer with the
//   expected one. Run `.\check 05` (`./check.sh 05` on macOS or Linux), or use Run and
//   Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   You also write src/didact/commit.js in this assignment; each one gives its job at the
//   top.
//   It adds to src/didact/render.js, which you started earlier: Stop attaching DOM nodes
//   while units run. Hold the tree under construction in `wipRoot`, and call `commitRoot`
//   after the last unit.
//   Earlier files you can use: src/didact/state.js, src/didact/dom.js,
//   src/didact/reconcile.js and src/didact/index.js.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import { commitRoot } from '../src/didact/commit.js'
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import '../harness/env.js'; // first: installs document and a requestIdleCallback the tests control, before the library loads
import Didact from '../src/didact/index.js'; // Didact: the library under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], Didact);
