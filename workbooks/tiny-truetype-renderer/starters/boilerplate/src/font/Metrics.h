#pragma once
// ======================================================================================
// Assignment 05: Read the horizontal metrics
// Problem: problems/05-metrics.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Ascent and descent from `hhea`, and each glyph's advance width and left side bearing
//   from `hmtx`; this header is the reader for both. In assignment 18 the pen moves by
//   advance widths and the text is sized from the ascent and descent.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <vector>  // std::vector<GlyphMetric>: one set of metrics per glyph id

#include "font/ByteReader.h"  // ByteReader (assignment 01): the reader the tables are read through
#include "font/FontParser.h"  // Tables (assignment 02): the records of hhea, hmtx and maxp

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
