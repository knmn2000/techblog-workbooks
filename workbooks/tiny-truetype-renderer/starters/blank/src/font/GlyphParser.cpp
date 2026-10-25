// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Bytes of a glyph record become the types in `Glyph.h` here: the header of any glyph,
//   then the contours and points of a simple one. The compound glyph code in assignment 09
//   calls it once per simple part.
//
// Your job:
//   Implement the decoder as "The glyph record you are decoding" lays it out. Length 0
//   gives an empty glyph. A negative `numberOfContours` means compound, and you stop after
//   the header. A simple glyph needs the contour ends and every point, with absolute
//   coordinates and the point's own on/off flag.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
