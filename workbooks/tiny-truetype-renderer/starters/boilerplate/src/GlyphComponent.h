#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Every outline in the project takes this form: its points (x and y in font units, on or
//   off the curve) and the index where each contour ends. Assignments 08 and 11 draw
//   outlines in this form, 09 produces one per part of a compound glyph, and 14, 16 and 17
//   fill them.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <vector>

struct GlyphPoint {
  double x = 0;  // font units; x grows to the right
  double y = 0;  // font units; y grows upwards
  bool onCurve = false;
};

// Contours are runs of points: contour k ends at point endPtsOfContours[k].
struct GlyphComponent {
  std::vector<int> endPtsOfContours;
  std::vector<GlyphPoint> points;
};
