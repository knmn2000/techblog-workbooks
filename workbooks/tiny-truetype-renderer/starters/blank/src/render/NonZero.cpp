// ======================================================================================
// Assignment 16: Fill a polygon: non-zero rule
// Problem: problems/16-nonzero-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Walk the sorted crossings of a row with a running winding count and paint wherever it
//   isn't zero. The file builds on your `render/Scanline`, and assignment 17 extends it to
//   curves.
//
// Your job:
//   Build on your `render/Scanline`. On every row, walk the sorted crossings left to right
//   with a running winding count and fill each stretch where the count isn't zero. That
//   needs each crossing's edge direction; if your crossings from assignment 14 don't
//   record it yet, add it to `render/Scanline` first.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
