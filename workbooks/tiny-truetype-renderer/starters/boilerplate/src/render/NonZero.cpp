// ======================================================================================
// Assignment 16: Fill a polygon: non-zero rule
// Problem: problems/16-nonzero-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Filling a glyph by the non-zero rule, the rule fonts are designed for, on top of
//   `render/Scanline`. This assignment handles straight edges, assignment 17 adds curves,
//   and the text renderer of assignment 18 fills every glyph with it. Later, assignment 17
//   adds to this file.
//
// Your job:
//   Implement it with your `render/Scanline`: on every row, walk the sorted crossings left
//   to right with a running winding count and fill each stretch where the count isn't
//   zero. Each crossing needs the direction of its edge; if your crossings from assignment
//   14 don't record it yet, add it to `render/Scanline` first. The Boilerplate has the
//   declarations written: fill in what's marked TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include "render/NonZero.h"

#include <stdexcept>

#include "render/Scanline.h"

void renderGlyphByNonZero(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          const RGB color) {
  // TODO: scanline fill by the winding count (see the problem page). Assignment 17 has curves:
  // each crossing needs the direction of the edge where it crosses.
  throw std::logic_error("not implemented: renderGlyphByNonZero");
}
