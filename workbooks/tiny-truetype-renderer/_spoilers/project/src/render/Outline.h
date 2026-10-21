#pragma once
// Checkpoint 08: drawing a glyph's outline with straight lines; checkpoint 11: with curves.

#include "FrameBufferCanvas.h"
#include "GlyphComponent.h"
#include "render/Placement.h"

struct OutlineStyle {
  int lineThickness = 1;  // passed to FrameBufferCanvas::drawLine
  int markerSize = 1;     // width and height of the square drawn at every point
};

// A straight line between consecutive points of each contour (the last point joins the
// first), then a marker on every point, all in `color`.
void renderGlyphOutline(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                        const OutlineStyle& style, RGB color);

// ---- Checkpoint 11: curves --------------------------------------------------------

// The real outline, quadratic curves included, then markers twice the line thickness:
// red on-curve points, green off-curve points, blue implied on-curve points.
void renderGlyphCurves(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                       int lineThickness, RGB color);
