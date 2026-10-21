// ======================================================================================
// Assignment 14: Fill a glyph: even-odd rule
// Problem: problems/14-even-odd-fill.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Filling a glyph by the even-odd rule, on top of `render/Scanline`. Assignment 16 adds
//   the non-zero rule beside it, and that is the one the text renderer of assignment 18
//   uses.
//
// Your job:
//   Implement it with your `render/Scanline`: build the edge pieces, then on every row
//   fill from the 1st crossing to the 2nd, the 3rd to the 4th, and so on. The Boilerplate
//   has the declarations written: fill in what's marked TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include "render/EvenOdd.h"

#include <stdexcept>

#include "render/Scanline.h"

void renderGlyphByEvenOdd(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          const RGB color) {
  // TODO: a scanline fill with edgePieces, forEachRow and fillSpan (see "From points to edges"
  // and "The even-odd rule" on the problem page).
  throw std::logic_error("not implemented: renderGlyphByEvenOdd");
}
