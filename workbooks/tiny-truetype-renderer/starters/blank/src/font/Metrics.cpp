// ======================================================================================
// Assignment 05: Read the horizontal metrics
// Problem: problems/05-metrics.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This file reads `hhea`, `maxp` and `hmtx` into the ascent, the descent and one set of
//   metrics per glyph id, including the glyphs that store a side bearing and no advance.
//   Assignment 18 loads these metrics once per font.
//
// Your job:
//   Read `ascent`, `descent` and `numberOfHMetrics` from `hhea` and `numGlyphs` from
//   `maxp`. Then read `hmtx` and give every glyph id from 0 to `numGlyphs` - 1 an advance
//   and an lsb, by the two rules under "A glyph's metrics".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
