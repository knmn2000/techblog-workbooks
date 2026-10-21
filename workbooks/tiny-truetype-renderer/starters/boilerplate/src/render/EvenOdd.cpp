#include "render/EvenOdd.h"

#include <stdexcept>

#include "render/Scanline.h"

void renderGlyphByEvenOdd(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          const RGB color) {
  // TODO: a scanline fill with edgePieces, forEachRow and fillSpan (see "From points to edges"
  // and "The even-odd rule" on the problem page).
  throw std::logic_error("not implemented: renderGlyphByEvenOdd");
}
