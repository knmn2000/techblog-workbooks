#pragma once
// Checkpoint 05: how far each glyph moves the pen (the hhea and hmtx tables).

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
