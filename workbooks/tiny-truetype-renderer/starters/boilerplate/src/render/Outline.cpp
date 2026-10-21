#include "render/Outline.h"

#include <stdexcept>

void renderGlyphOutline(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                        const OutlineStyle& style, const RGB color) {
  // TODO: see "What to draw" on the problem page.
  throw std::logic_error("not implemented: renderGlyphOutline");
}

void renderGlyphCurves(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                       const int lineThickness, const RGB color) {
  // TODO (checkpoint 11): see "Walking a contour", "Drawing a curve" and "Markers" on its
  // problem page. bezierLerp in utils/Geometry.h (checkpoint 10) gives the points of a curve.
  throw std::logic_error("not implemented: renderGlyphCurves");
}
