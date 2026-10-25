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
//   and an lsb, following the two rules under "A glyph's metrics". The Boilerplate gives
//   you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/Metrics.h"  // loadHorizontalMetrics (assignment 05), defined here

#include <stdexcept>  // std::logic_error, which the TODO throws

HorizontalMetrics loadHorizontalMetrics(ByteReader& reader, const Tables& tables) {
  // TODO: ascent, descent and numberOfHMetrics from hhea, then hmtx (see the problem page).
  throw std::logic_error("not implemented: loadHorizontalMetrics");
}
