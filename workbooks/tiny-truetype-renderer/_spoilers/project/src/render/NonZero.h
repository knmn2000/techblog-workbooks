#pragma once
// Assignment 16: filling by the non-zero rule, for straight edges; assignment 17: with curves.

#include "FrameBufferCanvas.h"
#include "GlyphComponent.h"
#include "render/Placement.h"

// Fills every pixel whose centre is inside the outline: a point is inside when the edges a
// ray from it crosses don't cancel out, counting +1 for an edge going down, -1 going up.
void renderGlyphByNonZero(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                          RGB color);
