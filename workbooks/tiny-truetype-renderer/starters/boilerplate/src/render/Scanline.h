#pragma once
// ======================================================================================
// Assignment 14: Fill a glyph: even-odd rule
// Problem: problems/14-even-odd-fill.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   It holds the steps both fill rules share: it turns an outline into edges in pixels and
//   finds, row by row, where the line through the pixel centres crosses them. Your
//   even-odd fill in this assignment and your non-zero fill in assignments 16 and 17 both
//   run on it.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

// The fill paints a pixel when its centre is inside the outline. It scans each row along the
// line through its pixel centres, and splits the outline's edges into pieces that don't turn
// back in y, so each piece crosses a row at most once.

#include <functional>  // std::function: the work forEachRow does for each row
#include <vector>      // std::vector of edge pieces and of crossings

#include "FrameBufferCanvas.h"  // FrameBufferCanvas and RGB (assignment 06), for fillSpan
#include "GlyphComponent.h"     // GlyphComponent (assignment 07): the outline edgePieces reads
#include "render/Placement.h"   // Placement (assignment 08): font units to pixels
#include "utils/Geometry.h"     // Vec2 (assignment 10): the points of an EdgePiece

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
// row through a vertex that two pieces share counts one crossing there.
void forEachRow(const std::vector<EdgePiece>& edges, int height,
                const std::function<void(int row, const std::vector<Crossing>& crossings)>& visit);

// Fills the pixels of `row` whose centres lie in [fromX, toX).
void fillSpan(FrameBufferCanvas& canvas, int row, double fromX, double toX, RGB color);
