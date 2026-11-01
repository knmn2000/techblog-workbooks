// ======================================================================================
// Assignment 09: Function components
// Problem: problems/09-function-components.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 09 as `python -P tools/run_js.py
//   solutions 09 <input-file> <output-file>`. It reads a test input, calls your code and
//   writes the answer to the output file, and the checker compares that answer with the
//   expected one. Run `.\check 09` (`./check.sh 09` on macOS or Linux), or use Run and
//   Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   It adds to src/didact/render.js, which you started earlier: Branch in
//   `performUnitOfWork`: a fiber whose type is a function has no DOM node, and its
//   children are whatever calling the function returns.
//   It adds to src/didact/commit.js, which you started earlier: Find the parent DOM node
//   by walking up through fibers that have none, and the node to remove by walking down
//   through them.
//   Earlier files you can use: src/didact/reconcile.js and src/didact/createElement.js.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import { render } from '../src/didact/render.js'
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import '../harness/env.js'; // first: installs document and a requestIdleCallback the tests control, before the library loads
import Didact from '../src/didact/index.js'; // Didact: the library under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], Didact);
