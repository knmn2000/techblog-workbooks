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
//   Pass your `Didact` object to `runScenarioFile`; the scenario renders a second tree
//   into the container that already holds the first.
//
// The other files of this assignment:
//   It adds to src/didact/state.js, which you started earlier: Add `currentRoot`, the last
//   tree you committed, and `deletions`, the fibers to remove.
//   It adds to src/didact/render.js, which you started earlier: Point the new root's
//   `alternate` at `currentRoot`, the tree you committed last time, and reset `deletions`
//   on every `render`.
//   It adds to src/didact/reconcile.js, which you started earlier: Rewrite
//   `reconcileChildren` to compare each element with the old fiber at the same position.
//   Same type reuses the old DOM node and updates it, a different type gets a new node,
//   and an old fiber with no element left is queued for deletion.
//   It adds to src/didact/commit.js, which you started earlier: Act on what reconciliation
//   decided: put a new node before the next sibling that already has a DOM node, so it
//   keeps its position, call `updateDom` for an update, and remove each deleted node
//   exactly once.
//   Earlier files you can use: src/didact/dom.js.
//   Import them as ES modules, by a relative path with the .js ending, for example:
//       import { state } from '../src/didact/state.js'
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================

function main() {
}

main();
