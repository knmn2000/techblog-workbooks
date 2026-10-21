#pragma once
// ======================================================================================
// Assignment 14: Fill a glyph: even-odd rule
// Problem: problems/14-even-odd-fill.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The part of filling that doesn't depend on the rule: an outline turned into edges in
//   pixels and, row by row, where the line through the pixel centres crosses them. Your
//   even-odd fill here and the non-zero fill of assignments 16 and 17 both run on it.
//
// Your job:
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

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
