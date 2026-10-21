#include "font/Metrics.h"

#include <cstdint>

HorizontalMetrics loadHorizontalMetrics(ByteReader& reader, const Tables& tables) {
  HorizontalMetrics m;
  const uint32_t hhea = tables.at("hhea").offset;
  reader.jumpTo(hhea + 4);
  m.ascent = reader.readInt16();
  m.descent = reader.readInt16();
  reader.jumpTo(hhea + 34);
  const uint16_t numberOfHMetrics = reader.readUint16();
  reader.jumpTo(tables.at("maxp").offset + 4);
  const uint16_t numGlyphs = reader.readUint16();

  reader.jumpTo(tables.at("hmtx").offset);
  for (uint16_t i = 0; i < numberOfHMetrics; ++i) {  // longHorMetric records
    const int advance = reader.readUint16();
    const int lsb = reader.readInt16();
    m.glyphs.push_back({advance, lsb});
  }
  // The remaining glyphs repeat the last advance; only their lsb is stored.
  const int lastAdvance = m.glyphs.empty() ? 0 : m.glyphs.back().advanceWidth;
  for (uint32_t i = numberOfHMetrics; i < numGlyphs; ++i) m.glyphs.push_back({lastAdvance, reader.readInt16()});
  return m;
}
