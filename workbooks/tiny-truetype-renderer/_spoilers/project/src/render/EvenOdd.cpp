#include "render/EvenOdd.h"

#include "render/Scanline.h"

void renderGlyphByEvenOdd(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          const RGB color) {
  forEachRow(edgePieces(outline, place), canvas.height(), [&](const int row, const std::vector<Crossing>& crossings) {
    // Inside after an odd number of crossings: between the 1st and 2nd, the 3rd and 4th, ...
    for (std::size_t i = 0; i + 1 < crossings.size(); i += 2)
      fillSpan(canvas, row, crossings[i].x, crossings[i + 1].x, color);
  });
}
