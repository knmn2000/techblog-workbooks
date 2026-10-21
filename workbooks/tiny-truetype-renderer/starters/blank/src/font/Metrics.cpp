// ======================================================================================
// Assignment 05: Read the horizontal metrics
// Problem: problems/05-metrics.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The code that reads `hhea`, `maxp` and `hmtx` into the ascent, the descent and one set
//   of metrics per glyph id, including the glyphs that store only a side bearing.
//   Assignment 18 loads it once per font.
//
// Your job:
//   Implement it: read `ascent`, `descent` and `numberOfHMetrics` from `hhea` and
//   `numGlyphs` from `maxp`, then read `hmtx` so that every glyph id from 0 to `numGlyphs`
//   - 1 gets an advance and an lsb, by the two rules under "A glyph's metrics".
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
