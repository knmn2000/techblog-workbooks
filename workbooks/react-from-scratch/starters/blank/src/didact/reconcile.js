// ======================================================================================
// Assignment 04: Work in units: fibers
// Problem: problems/04-fibers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Decides which fibers a parent's children become. It starts by making a fresh fiber for
//   every child and grows into the comparison with the previous render. Later, assignments
//   06, 07 and 08 add to this file.
//
// Your job:
//   Write `reconcileChildren(wipFiber, elements)`: give every element a fiber of its own
//   and link the fibers with `child`, `sibling` and `parent`.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
