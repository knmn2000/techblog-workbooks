#pragma once
// Points, curves and where they meet.
// Checkpoint 10: lerp and quadratic Bezier curves. 12: two segments. 13: a line and a curve.
// 15: the lowest point of a curve.

#include <optional>
#include <stdexcept>
#include <vector>

struct Vec2 {
  double x = 0;
  double y = 0;
};

inline Vec2 operator+(const Vec2 a, const Vec2 b) { return {a.x + b.x, a.y + b.y}; }
inline Vec2 operator-(const Vec2 a, const Vec2 b) { return {a.x - b.x, a.y - b.y}; }
inline Vec2 operator*(const Vec2 v, const double s) { return {v.x * s, v.y * s}; }

// ---- Checkpoint 10 ------------------------------------------------------------------

// The point a fraction t of the way from a to b.
inline Vec2 lerp(const Vec2 a, const Vec2 b, const double t) {
  // TODO: see "Linear interpolation" on the problem page.
  throw std::logic_error("not implemented: lerp");
}

// The quadratic Bezier curve a (start), b (control), c (end) at t.
inline Vec2 bezierLerp(const Vec2 a, const Vec2 b, const Vec2 c, const double t) {
  // TODO: see "A point on a quadratic Bezier curve" on the problem page.
  throw std::logic_error("not implemented: bezierLerp");
}

// ---- Checkpoint 12 ------------------------------------------------------------------

// Where segment a1-a2 meets segment b1-b2; nothing if they don't, or are parallel.
inline std::optional<Vec2> segmentsIntersect(const Vec2 a1, const Vec2 a2, const Vec2 b1, const Vec2 b2) {
  // TODO: the side test, then the crossing point (see "The rules" on the problem page).
  throw std::logic_error("not implemented: segmentsIntersect");
}

// ---- Checkpoint 13 ------------------------------------------------------------------

// Where the infinite line through l1 and l2 meets the curve p1 (start), p2 (control),
// p3 (end), ordered along the curve.
inline std::vector<Vec2> segmentQuadBezierIntersect(const Vec2 p1, const Vec2 p2, const Vec2 p3, const Vec2 l1,
                                                    const Vec2 l2) {
  // TODO: see "From a line and a curve to a quadratic" and "Solving for t" on the problem page.
  throw std::logic_error("not implemented: segmentQuadBezierIntersect");
}

// ---- Checkpoint 15 ------------------------------------------------------------------

// The smallest y on the curve p1 (start), p2 (control), p3 (end) for 0 <= t <= 1.
inline double getBezierMinY(const Vec2 p1, const Vec2 p2, const Vec2 p3) {
  // TODO: see "Where the lowest point can be" on the problem page.
  throw std::logic_error("not implemented: getBezierMinY");
}
