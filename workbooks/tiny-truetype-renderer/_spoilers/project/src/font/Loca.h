#pragma once
// Checkpoint 04: where each glyph's record is (the loca table).

#include <cstdint>
#include <vector>

#include "font/ByteReader.h"
#include "font/FontParser.h"

struct GlyphLocation {
  uint32_t offset = 0;  // from the start of the file
  uint32_t length = 0;  // 0: the glyph has no outline, e.g. space
};

struct GlyphLocations {
  uint16_t numGlyphs = 0;
  bool longFormat = false;            // head.indexToLocFormat: 32-bit offsets
  std::vector<GlyphLocation> glyphs;  // one per glyph id
};

GlyphLocations loadGlyphLocations(ByteReader& reader, const Tables& tables);
