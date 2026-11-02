// ======================================================================================
// Assignment 10: useState
// Problem: problems/10-use-state.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 10 as `python -P tools/run_js.py
//   solutions 10 <input-file> <output-file>`. It reads a test input, calls your code and
//   writes the answer to the output file, and the checker compares that answer with the
//   expected one. Run `.\check 10` (`./check.sh 10` on macOS or Linux), or use Run and
//   Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   You also write src/didact/hooks.js in this assignment; each one gives its job at the
//   top.
//   It adds to src/didact/state.js, which you started earlier: Add `wipFiber` and
//   `hookIndex`. The first is the fiber of the component being rendered, the second the
//   position of the next hook call.
//   It adds to src/didact/render.js, which you started earlier: Before a function
//   component is called, point `wipFiber` at its fiber, give that fiber an empty `hooks`
//   array and reset `hookIndex`.
//   It adds to src/didact/index.js, which you started earlier: Expose `useState` on the
//   `Didact` object.
//   Earlier files you can use: src/didact/commit.js and src/didact/reconcile.js.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import { useState } from '../src/didact/hooks.js'
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import '../harness/env.js'; // first: installs document and a requestIdleCallback the tests control, before the library loads
import Didact from '../src/didact/index.js'; // Didact: the library under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], Didact);
