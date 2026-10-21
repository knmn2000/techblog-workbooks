#include "font/CompoundGlyph.h"

#include <stdexcept>

#include "font/GlyphParser.h"

std::vector<GlyphComponent> resolveGlyph(ByteReader& reader, const std::map<uint32_t, GlyphLocation>& locations,
                                         const uint32_t glyphId) {
  // TODO: read the component records and apply their transforms, recursively (see the problem
  // page). readGlyph (checkpoint 07) decodes the simple glyphs they end in.
  throw std::logic_error("not implemented: resolveGlyph");
}
