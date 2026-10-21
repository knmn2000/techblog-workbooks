#include "render/NonZero.h"

#include <stdexcept>

#include "render/Scanline.h"

void renderGlyphByNonZero(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          const RGB color) {
  // TODO: scanline fill by the winding count (see the problem page). Checkpoint 17 has curves:
  // each crossing needs the direction of the edge where it crosses.
  throw std::logic_error("not implemented: renderGlyphByNonZero");
}
