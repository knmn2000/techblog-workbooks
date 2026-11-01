// ======================================================================================
// Assignment 05: Render phase, then commit
// Problem: problems/05-commit.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Applies a finished fiber tree to the DOM in a single pass, which keeps half a render
//   from ever showing. Later, assignments 06, 08, 09 and 11 add to this file.
//
// Your job:
//   Define `commitRoot` and `commitWork`. Once the last unit is done, they append the
//   finished tree to the container in a single pass. The Boilerplate gives you the
//   declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import { state } from './state.js'; // state: wipRoot, the finished tree to apply

export function commitRoot() {
  // TODO: see "The period that ends the work", "After the commit" and Requirements R2 and R4 on the page.
  throw new Error('not implemented: commitRoot');
}

function commitWork(fiber) {
  // TODO: see "The modules" and Requirement R5 on the page.
  throw new Error('not implemented: commitWork');
}
