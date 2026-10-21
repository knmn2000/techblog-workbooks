#include "font/Loca.h"

GlyphLocations loadGlyphLocations(ByteReader& reader, const Tables& tables) {
  GlyphLocations result;
  reader.jumpTo(tables.at("maxp").offset + 4);  // after the 4-byte version
  result.numGlyphs = reader.readUint16();
  reader.jumpTo(tables.at("head").offset + 50);
  result.longFormat = reader.readInt16() == 1;  // indexToLocFormat: 0 short, 1 long

  // loca has numGlyphs + 1 entries: the last one marks where the last glyph ends.
  reader.jumpTo(tables.at("loca").offset);
  std::vector<uint32_t> entries(result.numGlyphs + 1u);
  for (uint32_t& entry : entries) entry = result.longFormat ? reader.readUint32() : 2u * reader.readUint16();

  const uint32_t glyf = tables.at("glyf").offset;
  for (std::size_t i = 0; i < result.numGlyphs; ++i)
    result.glyphs.push_back({glyf + entries[i], entries[i + 1] - entries[i]});
  return result;
}
