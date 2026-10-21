// ======================================================================================
// Assignment 14: Fill a glyph: even-odd rule
// Problem: problems/14-even-odd-fill.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Filling a glyph by the even-odd rule, on top of `render/Scanline`. Assignment 16 adds
//   the non-zero rule beside it, and that is the one the text renderer of assignment 18
//   uses.
//
// Your job:
//   Implement it with your `render/Scanline`: build the edge pieces, then on every row
//   fill from the 1st crossing to the 2nd, the 3rd to the 4th, and so on.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
