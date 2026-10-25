// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The parser decodes one glyph record from the glyf table into the types in `Glyph.h`:
//   the header of any glyph, and the contours and points of a simple one. In assignment 09
//   you call it for every simple glyph inside a compound glyph.
//
// Your job:
//   Implement the glyph decoder as "The glyph record you are decoding" lays out. Length 0
//   gives an empty glyph. A negative `numberOfContours` gives a compound glyph, and you
//   stop reading after the header. For a simple glyph, read the contour ends and every
//   point, with absolute coordinates and the point's own on/off flag.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
