#include "font/GlyphParser.h"

#include <stdexcept>

Glyph readGlyph(ByteReader& reader, const uint32_t offset, const uint32_t length) {
  // TODO: decode the record (layout and rules are on the problem page). A simple glyph's
  // outline goes in g.components[0]; for a compound glyph, set its kind and stop.
  throw std::logic_error("not implemented: readGlyph");
}
