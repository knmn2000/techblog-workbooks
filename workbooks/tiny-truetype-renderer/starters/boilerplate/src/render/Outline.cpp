// ======================================================================================
// Assignment 08: Draw an outline with straight lines
// Problem: problems/08-outline-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Drawing a glyph's outline on the canvas: straight lines between its points and a
//   marker on every point. Assignment 11 adds a second drawing with the real curves to the
//   same files. Later, assignment 11 adds to this file.
//
// Your job:
//   Implement it: turn every point into a pixel with the formulas in "From font units to
//   pixels", join the points of each contour with lines, closing line included, then draw
//   a marker on every point. Use your canvas's line and rectangle for both. The
//   Boilerplate has the declarations written: fill in what's marked TODO.
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
