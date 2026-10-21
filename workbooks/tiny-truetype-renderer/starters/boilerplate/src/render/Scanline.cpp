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
//   Implement the three functions you declared in `Scanline.h`. When you build the edges,
//   make implied on-curve points explicit, start each contour at an on-curve point and
//   split every curve where its y turns around. For each row, find where the line through
//   its pixel centres crosses each piece (by the half-open rule) and sort the crossings.
//   To fill a stretch, paint the pixels whose centres lie in it, clipped to the canvas.
//   The Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "render/Scanline.h"

#include <stdexcept>

std::vector<EdgePiece> edgePieces(const GlyphComponent& outline, const Placement& place) {
  // TODO: walk each contour as in assignment 11, making implied on-curve points explicit, and
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
