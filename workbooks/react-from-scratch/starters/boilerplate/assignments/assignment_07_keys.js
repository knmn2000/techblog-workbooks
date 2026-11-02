// ======================================================================================
// Assignment 07: Match children by key
// Problem: problems/07-keys.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 07 as `python -P tools/run_js.py
//   solutions 07 <input-file> <output-file>`. It reads a test input, calls your code and
//   writes the answer to the output file, and the checker compares that answer with the
//   expected one. Run `.\check 07` (`./check.sh 07` on macOS or Linux), or use Run and
//   Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   It adds to src/didact/reconcile.js, which you started earlier: Pair each child with
//   the old child that has the same `key`, wherever that one stood, as long as the keys
//   both lists share stay in the same order. Children without a key still match by
//   position.
//   Earlier files you can use: src/didact/dom.js and src/didact/render.js.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import { reconcileChildren } from '../src/didact/reconcile.js'
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import '../harness/env.js'; // first: installs document and a requestIdleCallback the tests control, before the library loads
import Didact from '../src/didact/index.js'; // Didact: the library under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], Didact);
