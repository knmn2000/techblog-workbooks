// ======================================================================================
// Assignment 11: useEffect
// Problem: problems/11-use-effect.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 11 as `python -P tools/run_js.py
//   solutions 11 <input-file> <output-file>`. It reads a test input, calls your code and
//   writes the answer to the output file, and the checker compares that answer with the
//   expected one. Run `.\check 11` (`./check.sh 11` on macOS or Linux), or use Run and
//   Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   It adds to src/didact/hooks.js, which you started earlier: Write `useEffect(effect,
//   deps)`: store the effect on its fiber, along with its dependencies and whatever
//   cleanup function the effect returned.
//   It adds to src/didact/commit.js, which you started earlier: Once the DOM is up to
//   date, run the cleanups of effects that run again, then the effects that are new or
//   whose dependencies changed. A removed component's cleanups run too.
//   It adds to src/didact/index.js, which you started earlier: Export `useEffect` on the
//   `Didact` object next to `useState`.
//   Earlier files you can use: src/didact/render.js and src/didact/state.js.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import * as hooks from '../src/didact/hooks.js'
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import '../harness/env.js'; // first: installs document and a requestIdleCallback the tests control, before the library loads
import Didact from '../src/didact/index.js'; // Didact: the library under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], Didact);
