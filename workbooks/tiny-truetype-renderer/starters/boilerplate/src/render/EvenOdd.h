#pragma once
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
//   The Boilerplate gives you this file finished: the declarations, with the author's
//   names. You fill in the TODOs in this assignment's other files.
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
