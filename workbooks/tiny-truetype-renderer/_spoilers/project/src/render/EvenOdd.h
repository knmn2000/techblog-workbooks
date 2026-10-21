#pragma once
// Assignment 14: filling a glyph by the even-odd rule.

#include "FrameBufferCanvas.h"
#include "GlyphComponent.h"
#include "render/Placement.h"

// Fills every pixel whose centre is inside the outline: a point is inside when a ray from it
// crosses the outline an odd number of times.
void renderGlyphByEvenOdd(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          RGB color);
