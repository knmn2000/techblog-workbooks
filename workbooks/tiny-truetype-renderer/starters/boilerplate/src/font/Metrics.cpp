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
//   - 1 gets an advance and an lsb, by the two rules under "A glyph's metrics". The
//   Boilerplate has the declarations written: fill in what's marked TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include "font/Metrics.h"

#include <stdexcept>

HorizontalMetrics loadHorizontalMetrics(ByteReader& reader, const Tables& tables) {
  // TODO: ascent, descent and numberOfHMetrics from hhea, then hmtx (see the problem page).
  throw std::logic_error("not implemented: loadHorizontalMetrics");
}
