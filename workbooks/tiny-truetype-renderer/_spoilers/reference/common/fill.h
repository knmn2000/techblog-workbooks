#pragma once
// Reference fill engine shared by the reference solutions of checkpoints 14, 16,
// 17 and 18. SPOILERS: try those checkpoints yourself first.
//
// A pixel is filled when its centre is inside the outline. Every row is scanned
// through the pixel centres; outline edges are split into pieces that are monotone
// in y, so each piece crosses a scanline at most once (half-open in y, which
// counts a shared vertex exactly once).

#include <algorithm>
#include <cmath>
#include <utility>
#include <vector>

#include "provided/Canvas.h"

namespace fill {

struct Point {
  double x = 0, y = 0;
  bool onCurve = true;
};

struct Outline {
  std::vector<int> ends;
  std::vector<Point> points;
};

// Glyph (x, y) -> pixel (x0 + scale*x, baseline - scale*y).
struct Placement {
  double x0 = 0, baseline = 0, scale = 1;
};

enum class Rule { EvenOdd, NonZero };

struct Vec {
  double x = 0, y = 0;
};

// A line (curve == false) or a quadratic curve from p0 via c to p1, monotone in y.
struct Piece {
  Vec p0, c, p1;
  bool curve = false;
};

inline Vec mid(const Vec a, const Vec b) { return {(a.x + b.x) / 2, (a.y + b.y) / 2}; }

// Splits a quadratic curve at its turning point in y, if it has one inside.
inline void addCurve(const Vec p0, const Vec c, const Vec p1, std::vector<Piece>& out) {
  const double denom = p0.y - 2 * c.y + p1.y;
  if (std::abs(denom) > 1e-12) {
    const double t = (p0.y - c.y) / denom;
    if (t > 1e-9 && t < 1 - 1e-9) {
      const Vec a = {p0.x + (c.x - p0.x) * t, p0.y + (c.y - p0.y) * t};
      const Vec b = {c.x + (p1.x - c.x) * t, c.y + (p1.y - c.y) * t};
      const Vec m = {a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t};
      out.push_back({p0, a, m, true});
      out.push_back({m, b, p1, true});
      return;
    }
  }
  out.push_back({p0, c, p1, true});
}

// The outline's edges in pixel space, with the implied on-curve points between
// consecutive off-curve points, and contours that start off-curve handled.
inline std::vector<Piece> pieces(const Outline& o, const Placement& at) {
  std::vector<Piece> out;
  int start = 0;
  for (const int end : o.ends) {
    std::vector<std::pair<Vec, bool>> pts;
    for (int i = start; i <= end; ++i) {
      const Point& p = o.points[i];
      pts.push_back({{at.x0 + at.scale * p.x, at.baseline - at.scale * p.y}, p.onCurve});
    }
    start = end + 1;
    if (pts.empty()) continue;

    // Make every implied on-curve point explicit.
    std::vector<std::pair<Vec, bool>> full;
    for (std::size_t i = 0; i < pts.size(); ++i) {
      const auto& p = pts[i];
      const auto& next = pts[(i + 1) % pts.size()];
      full.push_back(p);
      if (!p.second && !next.second) full.push_back({mid(p.first, next.first), true});
    }
    const auto first = std::find_if(full.begin(), full.end(), [](const auto& p) { return p.second; });
    if (first == full.end()) continue;  // a single off-curve point: nothing to fill
    std::rotate(full.begin(), first, full.end());

    Vec current = full[0].first;
    for (std::size_t i = 1; i <= full.size(); ++i) {
      const auto& p = full[i % full.size()];
      if (p.second) {
        out.push_back({current, current, p.first, false});
        current = p.first;
      } else {
        const Vec end = full[(i + 1) % full.size()].first;  // always on-curve now
        addCurve(current, p.first, end, out);
        current = end;
        ++i;
      }
    }
  }
  return out;
}

struct Crossing {
  double x = 0;
  int direction = 0;  // +1 going down the screen, -1 going up
};

// Where a monotone piece crosses the horizontal line y = scanY (half-open in y).
inline bool cross(const Piece& p, const double scanY, Crossing& out) {
  const double y0 = p.p0.y, y1 = p.p1.y;
  if (y0 == y1) return false;
  if (!(std::min(y0, y1) <= scanY && scanY < std::max(y0, y1))) return false;
  out.direction = y1 > y0 ? 1 : -1;
  if (!p.curve) {
    const double t = (scanY - y0) / (y1 - y0);
    out.x = p.p0.x + (p.p1.x - p.p0.x) * t;
    return true;
  }
  const double a = y0 - 2 * p.c.y + y1, b = 2 * (p.c.y - y0), c = y0 - scanY;
  double t;
  if (std::abs(a) < 1e-12) {
    t = -c / b;
  } else {
    const double disc = std::max(0.0, b * b - 4 * a * c);
    const double r1 = (-b + std::sqrt(disc)) / (2 * a), r2 = (-b - std::sqrt(disc)) / (2 * a);
    const auto dist = [](const double r) { return r < 0 ? -r : (r > 1 ? r - 1 : 0); };
    t = dist(r1) <= dist(r2) ? r1 : r2;  // the piece is monotone: one root is in [0, 1]
  }
  t = std::clamp(t, 0.0, 1.0);
  const double u = 1 - t;
  out.x = u * u * p.p0.x + 2 * u * t * p.c.x + t * t * p.p1.x;
  return true;
}

// Fills one outline: every pixel whose centre is inside it by `rule`.
inline void fillOutline(Canvas& canvas, const Outline& o, const Placement& at, const Rule rule,
                        const RGB color) {
  const std::vector<Piece> edges = pieces(o, at);
  if (edges.empty()) return;
  double top = 1e300, bottom = -1e300;
  for (const Piece& e : edges) {
    top = std::min({top, e.p0.y, e.c.y, e.p1.y});
    bottom = std::max({bottom, e.p0.y, e.c.y, e.p1.y});
  }
  const int firstRow = std::max(0, static_cast<int>(std::floor(top)) - 1);
  const int lastRow = std::min(canvas.height() - 1, static_cast<int>(std::ceil(bottom)) + 1);

  std::vector<Crossing> crossings;
  for (int row = firstRow; row <= lastRow; ++row) {
    const double scanY = row + 0.5;
    crossings.clear();
    for (const Piece& e : edges) {
      Crossing c;
      if (cross(e, scanY, c)) crossings.push_back(c);
    }
    std::sort(crossings.begin(), crossings.end(), [](const Crossing& a, const Crossing& b) { return a.x < b.x; });
    int winding = 0;
    for (std::size_t i = 0; i + 1 < crossings.size(); ++i) {
      winding += rule == Rule::EvenOdd ? 1 : crossings[i].direction;
      const bool inside = rule == Rule::EvenOdd ? (winding % 2 != 0) : (winding != 0);
      if (!inside) continue;
      // Pixels whose centre x + 0.5 lies in [crossings[i].x, crossings[i + 1].x).
      const int from = static_cast<int>(std::ceil(crossings[i].x - 0.5));
      const int to = static_cast<int>(std::ceil(crossings[i + 1].x - 0.5)) - 1;
      if (from <= to) canvas.drawSpan(row, from, to, color);
    }
  }
}

}  // namespace fill
