// ======================================================================================
// Assignment 14: Fill a glyph: even-odd rule
// Problem: problems/14-even-odd-fill.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Edge building and row crossings: outlines become edges in pixels, and each pixel row
//   gets the crossings of the line through its pixel centres. Even-odd and non-zero both
//   fill from that list.
//
// Your job:
//   Implement the three functions declared in `Scanline.h`. To build the edges, make
//   implied on-curve points explicit, start each contour at an on-curve point and split
//   every curve where its y turns around. For each row, find where the line through its
//   pixel centres crosses each piece (by the half-open rule) and sort the crossings.
//   Filling a stretch paints the pixels whose centres lie in it, clipped to the canvas.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
