// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The code that reads `maxp`, `head` and `loca` and works out one location per glyph id.
//   Assignments 09 and 18 look glyphs up in what it returns.
//
// Your job:
//   Implement it: read `numGlyphs` from `maxp` and `indexToLocFormat` from `head`, read
//   the `numGlyphs` + 1 `loca` entries, and turn them into an absolute offset and a length
//   for each glyph id. The fields and formulas are under "The tables you need".
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
