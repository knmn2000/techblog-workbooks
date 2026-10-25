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

// Fills every pixel whose centre is inside the outline: a point is inside when a ray from it
// crosses the outline an odd number of times.
void renderGlyphByEvenOdd(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          RGB color);
