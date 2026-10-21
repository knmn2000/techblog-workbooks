#pragma once
// Assignment 07: a glyph as stored in the glyf table.

#include <vector>

#include "GlyphComponent.h"

struct BoundingRect {
  int xMin = 0, yMin = 0, xMax = 0, yMax = 0;
};

struct Glyph {
  enum class Kind { Empty, Simple, Compound };
  Kind kind = Kind::Empty;
  int numberOfContours = 0;  // negative for a compound glyph
  BoundingRect bounds;
  // A simple glyph has one component. A compound glyph is made of other glyphs;
  // resolveGlyph (assignment 09) turns it into one component per part.
  std::vector<GlyphComponent> components;
};
