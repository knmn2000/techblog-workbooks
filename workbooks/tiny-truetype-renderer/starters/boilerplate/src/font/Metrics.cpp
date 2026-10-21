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
//   and an lsb, by the two rules under "A glyph's metrics". The Boilerplate gives you the
//   declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/Metrics.h"

#include <stdexcept>

HorizontalMetrics loadHorizontalMetrics(ByteReader& reader, const Tables& tables) {
  // TODO: ascent, descent and numberOfHMetrics from hhea, then hmtx (see the problem page).
  throw std::logic_error("not implemented: loadHorizontalMetrics");
}
