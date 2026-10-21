#pragma once
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
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "FrameBufferCanvas.h"
#include "GlyphComponent.h"
#include "render/Placement.h"

struct OutlineStyle {
  int lineThickness = 1;  // passed to FrameBufferCanvas::drawLine
  int markerSize = 1;     // width and height of the square drawn at every point
};

// Assignment 08: a straight line between consecutive points of each contour (the last point
// joins the first), then a marker on every point, all in `color`.
void renderGlyphOutline(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                        const OutlineStyle& style, RGB color);

// Assignment 11: the real outline, quadratic curves included, then markers twice the line
// thickness: red on-curve points, green off-curve points, blue implied on-curve points.
void renderGlyphCurves(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                       int lineThickness, RGB color);
