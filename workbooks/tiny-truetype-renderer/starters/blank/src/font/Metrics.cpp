// ======================================================================================
// Assignment 05: Read the horizontal metrics
// Problem: problems/05-metrics.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Reads `hhea`, `maxp` and `hmtx` into the ascent, the descent and a set of metrics for
//   each glyph id. Some glyphs store a side bearing and no advance; they get entries too.
//   Assignment 18 loads all of this once per font.
//
// Your job:
//   Read `ascent`, `descent` and `numberOfHMetrics` from `hhea` and `numGlyphs` from
//   `maxp`. Then read `hmtx` and give every glyph id from 0 to `numGlyphs` - 1 an advance
//   and an lsb, following the two rules under "A glyph's metrics".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
