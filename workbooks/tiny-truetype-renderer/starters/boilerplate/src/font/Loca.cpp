#include "font/Loca.h"

#include <stdexcept>

GlyphLocations loadGlyphLocations(ByteReader& reader, const Tables& tables) {
  // TODO: numGlyphs from maxp, the offset format from head, then loca (see the problem page).
  throw std::logic_error("not implemented: loadGlyphLocations");
}
