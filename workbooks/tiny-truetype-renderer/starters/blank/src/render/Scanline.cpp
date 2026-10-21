// ======================================================================================
// Assignment 14: Fill a glyph: even-odd rule
// Problem: problems/14-even-odd-fill.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The part of filling that doesn't depend on the rule: an outline turned into edges in
//   pixels and, row by row, where the line through the pixel centres crosses them. Your
//   even-odd fill here and the non-zero fill of assignments 16 and 17 both run on it.
//
// Your job:
//   Implement those three steps. Building the edges makes implied on-curve points
//   explicit, starts each contour at an on-curve point and splits every curve where its y
//   turns around. Scanning a row finds where the line through its pixel centres crosses
//   each piece (by the half-open rule) and sorts the crossings, and filling a stretch
//   paints the pixels whose centres lie in it, clipped to the canvas.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
