#pragma once
// Assignment 07: the outline of one simple glyph.

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
