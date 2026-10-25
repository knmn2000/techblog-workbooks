#pragma once
// ======================================================================================
// Assignment 16: Fill a polygon: non-zero rule
// Problem: problems/16-nonzero-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   TrueType fills glyphs by the non-zero rule, and this is where yours is declared, on
//   top of your `render/Scanline`. Straight edges come first in assignment 16, curves in
//   17, and the text renderer in 18 fills every glyph with it.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "FrameBufferCanvas.h"  // FrameBufferCanvas and RGB (assignment 06): what the fill paints
#include "GlyphComponent.h"     // GlyphComponent (assignment 07): the outline to fill
#include "render/Placement.h"   // Placement (assignment 08): where the outline goes in pixels

// Fills every pixel whose centre is inside the outline: a point is inside when the edges a
// ray from it crosses don't cancel out, counting +1 for an edge going down, -1 going up.
void renderGlyphByNonZero(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          RGB color);
