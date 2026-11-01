// ======================================================================================
// Assignment 01: Create elements
// Problem: problems/01-create-element.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 01 as `python -P tools/run_js.py
//   solutions 01 <input-file> <output-file>`. It reads a test input, calls your code and
//   writes the answer to the output file, and the checker compares that answer with the
//   expected one. Run `.\check 01` (`./check.sh 01` on macOS or Linux), or use Run and
//   Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   You also write src/didact/createElement.js in this assignment; each one gives its job
//   at the top.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import { createElement } from '../src/didact/createElement.js'
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import { createElement } from '../src/didact/createElement.js'; // createElement (assignment 01): the function under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], { createElement });
