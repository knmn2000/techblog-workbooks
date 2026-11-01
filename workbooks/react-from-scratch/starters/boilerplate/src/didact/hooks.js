// ======================================================================================
// Assignment 10: useState
// Problem: problems/10-use-state.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   `useState` and `useEffect`: state and effects that belong to a component and survive
//   its re-renders, kept on the fiber. Later, assignment 11 adds to this file.
//
// Your job:
//   Write `useState(initial)`: state kept on the fiber, found again on the next render by
//   hook index. The setter takes an updater function, queues it, and schedules a new
//   render from the root. The Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

import { state } from './state.js'; // state: wipFiber and hookIndex say whose hook this is; currentRoot is what to render again

export function useState(initial) {
  // TODO: see "What `useState` does" and Requirements R1 to R9 on the page.
  throw new Error('not implemented: useState');
}
