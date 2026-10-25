// ======================================================================================
// Assignment 14: Fill a glyph: even-odd rule
// Problem: problems/14-even-odd-fill.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   It holds the steps both fill rules share: it turns an outline into edges in pixels and
//   finds, row by row, where the line through the pixel centres crosses them. Your
//   even-odd fill in this assignment and your non-zero fill in assignments 16 and 17 both
//   run on it.
//
// Your job:
//   Implement the three functions you declared in `Scanline.h`. When you build the edges,
//   make implied on-curve points explicit, start each contour at an on-curve point and
//   split every curve where its y turns around. For each row, find where the line through
//   its pixel centres crosses each piece (by the half-open rule) and sort the crossings.
//   To fill a stretch, paint the pixels whose centres lie in it, clipped to the canvas.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
