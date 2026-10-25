// ======================================================================================
// Assignment 14: Fill a glyph: even-odd rule
// Problem: problems/14-even-odd-fill.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   It fills a glyph by the even-odd rule, on top of your `render/Scanline`. Assignment 16
//   adds the non-zero rule beside it, and the text renderer in assignment 18 uses that
//   rule.
//
// Your job:
//   Implement the even-odd fill with your `render/Scanline`: build the edge pieces, then
//   on every row fill from the 1st crossing to the 2nd, the 3rd to the 4th, and so on. The
//   Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "render/EvenOdd.h"  // the declaration this file implements

#include <stdexcept>  // std::logic_error: the "not implemented" stub

#include "render/Scanline.h"  // edgePieces, forEachRow, fillSpan (assignment 14)

void renderGlyphByEvenOdd(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          const RGB color) {
  // TODO: a scanline fill with edgePieces, forEachRow and fillSpan (see "From points to edges"
  // and "The even-odd rule" on the problem page).
  throw std::logic_error("not implemented: renderGlyphByEvenOdd");
}
