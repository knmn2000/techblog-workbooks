// ======================================================================================
// Assignment 08: Draw an outline with straight lines
// Problem: problems/08-outline-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   These files draw a glyph's outline on the canvas, with straight lines between its
//   points and a marker on every point. In assignment 11 you add a second drawing, with
//   the real curves, to the same files.
//
// Your job:
//   Implement the outline drawing as "What to draw" describes: turn every point into a
//   pixel with the formulas in "From font units to pixels", join the points of each
//   contour with lines, including the closing line, then draw a marker on every point. Use
//   your canvas's line and rectangle for both. The Boilerplate gives you the declarations;
//   fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "render/Outline.h"

#include <stdexcept>

void renderGlyphOutline(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                        const OutlineStyle& style, const RGB color) {
  // TODO: see "What to draw" on the problem page.
  throw std::logic_error("not implemented: renderGlyphOutline");
}

void renderGlyphCurves(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                       const int lineThickness, const RGB color) {
  // TODO (assignment 11): see "Walking a contour", "Drawing a curve" and "Markers" on its
  // problem page. bezierLerp in utils/Geometry.h (assignment 10) gives the points of a curve.
  throw std::logic_error("not implemented: renderGlyphCurves");
}
