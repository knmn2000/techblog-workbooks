// ======================================================================================
// Assignment 06: Reconcile children by position
// Problem: problems/06-reconcile.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 06 as `python -P tools/run_js.py
//   solutions 06 <input-file> <output-file>`. It reads a test input, calls your code and
//   writes the answer to the output file, and the checker compares that answer with the
//   expected one. Run `.\check 06` (`./check.sh 06` on macOS or Linux), or use Run and
//   Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   It adds to src/didact/state.js, which you started earlier: Track the last tree you
//   committed in `currentRoot`, and the fibers waiting for removal in `deletions`.
//   It adds to src/didact/render.js, which you started earlier: On every `render`, point
//   the new root's `alternate` at `currentRoot` (the tree you committed last time) and
//   reset `deletions`.
//   It adds to src/didact/reconcile.js, which you started earlier: Rewrite
//   `reconcileChildren` to compare each element with the old fiber at the same position.
//   The same type keeps its DOM node and gets updated, a different type gets a fresh node,
//   and an old fiber left without an element is queued for deletion.
//   It adds to src/didact/commit.js, which you started earlier: Carry out what
//   reconciliation decided. A new node goes before the next sibling that already has a DOM
//   node, which keeps its position; an updated one goes through `updateDom`; each deleted
//   node is removed once.
//   Earlier files you can use: src/didact/dom.js.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import { state } from '../src/didact/state.js'
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import '../harness/env.js'; // first: installs document and a requestIdleCallback the tests control, before the library loads
import Didact from '../src/didact/index.js'; // Didact: the library under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], Didact);
