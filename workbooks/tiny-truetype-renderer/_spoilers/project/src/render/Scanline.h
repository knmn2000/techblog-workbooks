#pragma once
// Assignment 14: scanning an outline row by row, the part both fill rules share.
//
// A pixel is filled when its centre is inside the outline. Each row is scanned along the
// line through its pixel centres, and the outline's edges are split into pieces that never
// turn back in y, so each piece crosses a row at most once.

#include <functional>
#include <vector>

#include "FrameBufferCanvas.h"
#include "GlyphComponent.h"
#include "render/Placement.h"
#include "utils/Geometry.h"

// A straight edge (curve == false) or a quadratic curve p0 -> c -> p1, in pixels.
struct EdgePiece {
  Vec2 p0, c, p1;
  bool curve = false;
};

// Where a row crosses an edge, and which way the edge runs there.
struct Crossing {
  double x = 0;
  int direction = 0;  // +1 going down the screen, -1 going up
};

// The outline's edges in pixels: implied on-curve points made explicit, contours that start
// off-curve handled, and curves split where they turn in y.
std::vector<EdgePiece> edgePieces(const GlyphComponent& outline, const Placement& place);

// Calls visit(row, crossings) for every pixel row the edges reach, with that row's crossings
// sorted by x. A piece counts from its upper end up to, not including, its lower end, so a
// shared vertex is crossed exactly once.
void forEachRow(const std::vector<EdgePiece>& edges, int height,
                const std::function<void(int row, const std::vector<Crossing>& crossings)>& visit);

// Fills the pixels of `row` whose centres lie in [fromX, toX).
void fillSpan(FrameBufferCanvas& canvas, int row, double fromX, double toX, RGB color);
