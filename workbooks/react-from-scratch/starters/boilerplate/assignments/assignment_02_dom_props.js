// ======================================================================================
// Assignment 02: DOM nodes and props
// Problem: problems/02-dom-props.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 02 as `python -P tools/run_js.py
//   solutions 02 <input-file> <output-file>`. It reads a test input, calls your code and
//   writes the answer to the output file, and the checker compares that answer with the
//   expected one. Run `.\check 02` (`./check.sh 02` on macOS or Linux), or use Run and
//   Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   You also write src/didact/dom.js in this assignment; each one gives its job at the
//   top.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import { createDom, updateDom } from '../src/didact/dom.js'
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

// Test wiring, nothing to change: it hands your createDom and updateDom to the harness, which reads
// the test file, calls them for each line and writes down what the node looks like.

import { createDom, updateDom } from '../src/didact/dom.js'; // createDom and updateDom (assignment 02): the functions under test
import { runScenarioFile } from '../harness/scenario.js'; // runScenarioFile: reads the scenario file, runs it against your code, writes the output file

await runScenarioFile(process.argv[2], process.argv[3], { createDom, updateDom });
