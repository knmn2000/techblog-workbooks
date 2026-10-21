#include "font/Cmap.h"

#include <optional>

std::unordered_map<uint32_t, uint32_t> loadUnicodeToGlyphCodeMap(ByteReader& reader, const Tables& tables) {
  const uint32_t cmap = tables.at("cmap").offset;
  reader.jumpTo(cmap);
  reader.readUint16();  // version
  const uint16_t numberSubtables = reader.readUint16();

  std::optional<uint32_t> subtable;  // offset from the start of cmap
  for (uint16_t i = 0; i < numberSubtables; ++i) {
    const uint16_t platformID = reader.readUint16();
    const uint16_t encodingID = reader.readUint16();
    const uint32_t offset = reader.readUint32();
    if (platformID == 0 && encodingID == 4 && !subtable) subtable = offset;
  }
  if (!subtable) throw UnsupportedCmap("no platform 0 / encoding 4 subtable");

  reader.jumpTo(cmap + *subtable);
  if (reader.readUint16() != 12) throw UnsupportedCmap("the (0, 4) subtable is not format 12");
  reader.skipBytes(10);  // reserved (uint16), length (uint32), language (uint32)
  const uint32_t nGroups = reader.readUint32();

  std::unordered_map<uint32_t, uint32_t> glyphFor;
  for (uint32_t g = 0; g < nGroups; ++g) {
    const uint32_t startCharCode = reader.readUint32();
    const uint32_t endCharCode = reader.readUint32();
    const uint32_t startGlyphID = reader.readUint32();
    for (uint64_t c = startCharCode; c <= endCharCode; ++c)  // both ends included
      glyphFor[static_cast<uint32_t>(c)] = startGlyphID + static_cast<uint32_t>(c - startCharCode);
  }
  return glyphFor;
}
