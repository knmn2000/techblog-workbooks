// ======================================================================================
// Assignment 10: useState
// Problem: problems/10-use-state.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   State and effects that belong to a component and outlive its re-renders, stored on the
//   fiber: `useState` and `useEffect`. Later, assignment 11 adds to this file.
//
// Your job:
//   Give function components memory with `useState(initial)`, keeping the state on the
//   fiber and finding it again on the next render by hook index. The setter takes an
//   updater function, queues it and schedules a new render from the root. The Boilerplate
//   gives you the declarations; fill in each TODO.
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
