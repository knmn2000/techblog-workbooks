#include "font/Cmap.h"

std::unordered_map<uint32_t, uint32_t> loadUnicodeToGlyphCodeMap(ByteReader& reader, const Tables& tables) {
  // TODO: find the subtable, check its format, and expand every group (problem page). Throw
  // UnsupportedCmap when the font has no format 12 subtable for platform 0, encoding 4.
  throw std::logic_error("not implemented: loadUnicodeToGlyphCodeMap");
}
