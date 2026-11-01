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
//   updater function, queues it and schedules a new render from the root.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
