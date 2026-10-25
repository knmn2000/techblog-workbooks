// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This file reads `maxp`, `head` and `loca` and works out one location per glyph id.
//   Assignments 09 and 18 look glyphs up in its result.
//
// Your job:
//   Read `numGlyphs` from `maxp` and `indexToLocFormat` from `head`, read the `numGlyphs`
//   + 1 `loca` entries, and turn them into an absolute offset and a length for each glyph
//   id. The page lists the fields and formulas under "The tables you need".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
