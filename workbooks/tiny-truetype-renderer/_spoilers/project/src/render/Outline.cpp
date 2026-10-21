#include "render/Outline.h"

#include <cmath>
#include <utility>

namespace {

int nearest(const double v) { return static_cast<int>(std::lround(v)); }

// Font units -> the nearest pixel (y flipped: font y grows upwards, pixel y downwards).
std::pair<int, int> pixelOf(const GlyphPoint& p, const Placement& place) {
  return {nearest(place.x0 + place.scale * p.x), nearest(place.baseline - place.scale * p.y)};
}

}  // namespace

void renderGlyphOutline(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                        const OutlineStyle& style, const RGB color) {
  int first = 0;
  for (const int last : outline.endPtsOfContours) {
    for (int i = first; i <= last; ++i) {
      const int next = i == last ? first : i + 1;  // the last point closes the contour
      const auto [ax, ay] = pixelOf(outline.points[i], place);
      const auto [bx, by] = pixelOf(outline.points[next], place);
      canvas.drawLine(ax, ay, bx, by, style.lineThickness, color);
    }
    first = last + 1;
  }
  for (const GlyphPoint& p : outline.points) {  // markers on top of the lines
    const auto [x, y] = pixelOf(p, place);
    canvas.drawRect(x, y, style.markerSize, style.markerSize, color);
  }
}

// ---- Checkpoint 11: curves --------------------------------------------------------
// These includes arrived with the curves.

#include <algorithm>
#include <vector>

#include "utils/Geometry.h"

namespace {

const RGB ON_CURVE_COLOR{255, 0, 0};   // red: on-curve points from the outline
const RGB OFF_CURVE_COLOR{0, 255, 0};  // green: off-curve (control) points
const RGB IMPLIED_COLOR{0, 0, 255};    // blue: on-curve points implied between two off-curve points

// Font units -> pixels, not rounded yet.
Vec2 toPixel(const GlyphPoint& p, const Placement& place) {
  return {place.x0 + place.scale * p.x, place.baseline - place.scale * p.y};
}

Vec2 midpoint(const Vec2 a, const Vec2 b) { return {(a.x + b.x) / 2, (a.y + b.y) / 2}; }

void line(FrameBufferCanvas& canvas, const Vec2 a, const Vec2 b, const int thickness, const RGB color) {
  // Rounded through float, as the pictures in the tests were drawn.
  const auto round = [](const double v) { return nearest(static_cast<float>(v)); };
  canvas.drawLine(round(a.x), round(a.y), round(b.x), round(b.y), thickness, color);
}

// A quadratic curve as short straight pieces. The control polygon is never shorter than the
// curve, so this gives at most about one pixel per piece.
void drawQuadratic(FrameBufferCanvas& canvas, const Vec2 p0, const Vec2 p1, const Vec2 p2, const int thickness,
                   const RGB color) {
  const double length = std::hypot(p1.x - p0.x, p1.y - p0.y) + std::hypot(p2.x - p1.x, p2.y - p1.y);
  const int pieces = std::max(1, static_cast<int>(std::ceil(length)));
  Vec2 previous = p0;
  for (int i = 1; i <= pieces; ++i) {
    const Vec2 next = bezierLerp(p0, p1, p2, static_cast<double>(i) / pieces);
    line(canvas, previous, next, thickness, color);
    previous = next;
  }
}

}  // namespace

void renderGlyphCurves(FrameBufferCanvas& canvas, const GlyphComponent& outline, const Placement& place,
                       const int lineThickness, const RGB color) {
  struct Marker {
    Vec2 at;
    RGB color;
  };
  std::vector<Marker> markers;
  int first = 0;
  for (const int last : outline.endPtsOfContours) {
    const int n = last - first + 1;
    const auto at = [&](const int k) { return toPixel(outline.points[first + k % n], place); };
    const auto on = [&](const int k) { return outline.points[first + k % n].onCurve; };

    // Start from an on-curve point. With none, start from the implied on-curve point
    // between the last and the first point; every point is then visited once.
    int k = 0;
    while (k < n && !on(k)) ++k;
    Vec2 current;
    int stop;
    if (k < n) {
      current = at(k);
      stop = k + n + 1;  // ends with the start point again, which closes the contour
      ++k;
    } else {
      current = midpoint(at(n - 1), at(0));
      k = 0;
      stop = n;
    }
    while (k < stop) {
      if (on(k)) {
        line(canvas, current, at(k), lineThickness, color);
        current = at(k);
        ++k;
      } else if (on(k + 1)) {  // off, on: one curve, and the on-curve point is used up
        drawQuadratic(canvas, current, at(k), at(k + 1), lineThickness, color);
        current = at(k + 1);
        k += 2;
      } else {  // off, off: the curve ends at the implied point halfway between them
        const Vec2 implied = midpoint(at(k), at(k + 1));
        drawQuadratic(canvas, current, at(k), implied, lineThickness, color);
        current = implied;
        ++k;
      }
    }

    for (int i = 0; i < n; ++i) {
      markers.push_back({at(i), on(i) ? ON_CURVE_COLOR : OFF_CURVE_COLOR});
      if (!on(i) && !on(i + 1)) markers.push_back({midpoint(at(i), at(i + 1)), IMPLIED_COLOR});
    }
    first = last + 1;
  }
  for (const Marker& m : markers)  // on top of every line
    canvas.drawRect(nearest(m.at.x), nearest(m.at.y), 2 * lineThickness, 2 * lineThickness, m.color);
}
