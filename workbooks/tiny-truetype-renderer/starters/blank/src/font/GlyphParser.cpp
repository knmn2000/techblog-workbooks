// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Decoding one glyph record from the glyf table into the types in `Glyph.h`: the header
//   of every glyph, and the contours and points of a simple one. Assignment 09 calls it
//   for every simple glyph a compound glyph is made of.
//
// Your job:
//   Implement it as "The glyph record you are decoding" lays out: length 0 gives an empty
//   glyph, a negative `numberOfContours` gives a compound glyph with nothing read past the
//   header, and a simple glyph gets its contour ends and every point, with absolute
//   coordinates and its own on/off flag.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
