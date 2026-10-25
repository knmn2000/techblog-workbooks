// ======================================================================================
// Assignment 16: Fill a polygon: non-zero rule
// Problem: problems/16-nonzero-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   It fills a glyph by the non-zero rule, the rule TrueType uses, on top of your
//   `render/Scanline`. This assignment handles straight edges, assignment 17 adds curves,
//   and the text renderer in assignment 18 fills every glyph with it.
//
// Your job:
//   Implement the non-zero fill with your `render/Scanline`: on every row, walk the sorted
//   crossings left to right with a running winding count and fill each stretch where the
//   count isn't zero. Each crossing needs the direction of its edge; if your crossings
//   from assignment 14 don't record it yet, add it to `render/Scanline` first. The
//   Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "render/NonZero.h"  // the declaration this file implements

#include <stdexcept>  // std::logic_error: the "not implemented" stub

#include "render/Scanline.h"  // edgePieces, forEachRow, fillSpan (assignment 14)

void renderGlyphByNonZero(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          const RGB color) {
  // TODO: scanline fill by the winding count (see the problem page). Assignment 17 has curves:
  // each crossing needs the direction of the edge where it crosses.
  throw std::logic_error("not implemented: renderGlyphByNonZero");
}
