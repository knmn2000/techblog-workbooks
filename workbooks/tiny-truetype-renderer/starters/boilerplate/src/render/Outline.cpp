// ======================================================================================
// Assignment 08: Draw an outline with straight lines
// Problem: problems/08-outline-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Lines between a glyph's points, then a marker on every point: that is what this file
//   draws. The curved version arrives here in assignment 11.
//
// Your job:
//   Implement the drawing as "What to draw" describes. Turn every point into a pixel with
//   the formulas in "From font units to pixels", join the points of each contour with
//   lines (the closing line included), then put a marker on every point. Your canvas's
//   line and rectangle do both jobs. The Boilerplate gives you the declarations; fill in
//   each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "render/Outline.h"  // the two drawing functions (assignments 08 and 11)

#include <stdexcept>  // std::logic_error for the "not implemented" TODOs

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
