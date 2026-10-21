#include "render/Scanline.h"

#include <stdexcept>

std::vector<EdgePiece> edgePieces(const GlyphComponent& outline, const Placement& place) {
  // TODO: walk each contour as in checkpoint 11, making implied on-curve points explicit, and
  // split each curve where it turns in y (see the problem page).
  throw std::logic_error("not implemented: edgePieces");
}

void forEachRow(const std::vector<EdgePiece>& edges, const int height,
                const std::function<void(int, const std::vector<Crossing>&)>& visit) {
  // TODO: for each pixel row the edges reach, find where the line through its pixel centres
  // crosses each edge, sort the crossings by x, and call visit (see the problem page).
  throw std::logic_error("not implemented: forEachRow");
}

void fillSpan(FrameBufferCanvas& canvas, const int row, const double fromX, const double toX, const RGB color) {
  // TODO: fill the pixels of `row` whose centres (x + 0.5) lie in [fromX, toX).
  throw std::logic_error("not implemented: fillSpan");
}
