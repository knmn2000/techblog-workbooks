// ======================================================================================
// Assignment 08: Reorder keyed children
// Problem: problems/08-reorder.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 08 as `python -P tools/run_js.py
//   solutions 08 <input-file> <output-file>`. It reads a test input, calls your code and
//   writes the answer to the output file, and the checker compares that answer with the
//   expected one. Run `.\check 08` (`./check.sh 08` on macOS or Linux), or use Run and
//   Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   It adds to src/didact/reconcile.js, which you started earlier: Let a key match its old
//   child even when the order of the shared keys changed.
//   It adds to src/didact/commit.js, which you started earlier: Move the existing DOM node
//   of a reordered child instead of recreating it, so it keeps its state.
//   Earlier files you can use: src/didact/render.js.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import * as reconcile from '../src/didact/reconcile.js'
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import '../harness/env.js'; // first: installs document and a requestIdleCallback the tests control, before the library loads
import Didact from '../src/didact/index.js'; // Didact: the library under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], Didact);
