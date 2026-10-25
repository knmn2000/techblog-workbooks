#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   What the `glyf` table stores for a glyph: whether it is empty, simple or compound, its
//   contour count, its bounding box and, for a simple glyph, its outline. Your
//   `GlyphParser` returns it, and in assignment 09 the kind tells compound glyphs from
//   simple ones.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <vector>  // std::vector<GlyphComponent>: a glyph's outlines

#include "GlyphComponent.h"  // GlyphPoint and GlyphComponent (assignment 07): the outline types

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
