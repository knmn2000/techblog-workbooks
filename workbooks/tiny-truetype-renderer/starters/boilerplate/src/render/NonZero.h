#pragma once
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
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include "FrameBufferCanvas.h"
#include "GlyphComponent.h"
#include "render/Placement.h"

// Fills every pixel whose centre is inside the outline: a point is inside when the edges a
// ray from it crosses don't cancel out, counting +1 for an edge going down, -1 going up.
void renderGlyphByNonZero(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          RGB color);
