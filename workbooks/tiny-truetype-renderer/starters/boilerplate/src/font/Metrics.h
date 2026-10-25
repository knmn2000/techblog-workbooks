#pragma once
// ======================================================================================
// Assignment 05: Read the horizontal metrics
// Problem: problems/05-metrics.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This header declares your reader for the `hhea` and `hmtx` tables: the font's ascent
//   and descent, and each glyph's advance width and left side bearing. Assignment 18 moves
//   the pen by each glyph's advance width and sizes the text from the ascent and descent.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <vector>

#include "font/ByteReader.h"
#include "font/FontParser.h"

struct GlyphMetric {
  int advanceWidth = 0;
  int leftSideBearing = 0;
};

struct HorizontalMetrics {
  int ascent = 0;   // above the baseline, font units
  int descent = 0;  // below it (negative)
  std::vector<GlyphMetric> glyphs;  // one per glyph id
};

HorizontalMetrics loadHorizontalMetrics(ByteReader& reader, const Tables& tables);
