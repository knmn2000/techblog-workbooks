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
//   Implement those three steps. Building the edges makes implied on-curve points
//   explicit, starts each contour at an on-curve point and splits every curve where its y
//   turns around. Scanning a row finds where the line through its pixel centres crosses
//   each piece (by the half-open rule) and sorts the crossings, and filling a stretch
//   paints the pixels whose centres lie in it, clipped to the canvas. The Boilerplate has
//   the declarations written: fill in what's marked TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
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
