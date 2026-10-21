#include "render/NonZero.h"

#include "render/Scanline.h"

void renderGlyphByNonZero(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          const RGB color) {
  // Curves need nothing extra here: edgePieces splits each one where it turns in y, so every
  // piece runs one way, like a straight edge.
  forEachRow(edgePieces(outline, place), canvas.height(), [&](const int row, const std::vector<Crossing>& crossings) {
    int winding = 0;
    for (std::size_t i = 0; i + 1 < crossings.size(); ++i) {
      winding += crossings[i].direction;
      if (winding != 0) fillSpan(canvas, row, crossings[i].x, crossings[i + 1].x, color);
    }
  });
}
