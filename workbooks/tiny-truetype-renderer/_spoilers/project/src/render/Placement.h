#pragma once
// Assignment 08: where a glyph goes on the canvas.

// Font point (x, y) lands on pixel (x0 + scale * x, baseline - scale * y): font y grows
// upwards, pixel y grows downwards.
struct Placement {
  double x0 = 0;
  double baseline = 0;
  double scale = 1;
};
