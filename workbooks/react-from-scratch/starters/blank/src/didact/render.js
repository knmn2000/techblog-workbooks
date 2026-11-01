// ======================================================================================
// Assignment 04: Work in units: fibers
// Problem: problems/04-fibers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   `render` and the work loop behind it: one fiber per unit of work, and the browser can
//   interrupt between units. Later, assignments 05, 06, 09 and 10 add to this file.
//
// Your job:
//   Build `render`, `workLoop` and `performUnitOfWork`. `render` only schedules the work;
//   each idle period then runs fibers, one per unit of work, until `timeRemaining()` falls
//   below 1.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
