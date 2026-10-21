#pragma once
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
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "FrameBufferCanvas.h"
#include "GlyphComponent.h"
#include "render/Placement.h"

// Fills every pixel whose centre is inside the outline: a point is inside when a ray from it
// crosses the outline an odd number of times.
void renderGlyphByEvenOdd(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          RGB color);
