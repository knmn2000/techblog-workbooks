#pragma once
// Points, curves and where they meet.
// Assignment 10: lerp and quadratic Bezier curves. 12: two segments. 13: a line and a curve.
// 15: the lowest point of a curve.

#include <algorithm>
#include <cmath>
#include <optional>
#include <vector>

struct Vec2 {
  double x = 0;
  double y = 0;
};

inline Vec2 operator+(const Vec2 a, const Vec2 b) { return {a.x + b.x, a.y + b.y}; }
inline Vec2 operator-(const Vec2 a, const Vec2 b) { return {a.x - b.x, a.y - b.y}; }
inline Vec2 operator*(const Vec2 v, const double s) { return {v.x * s, v.y * s}; }

// ---- Assignment 10 ------------------------------------------------------------------

// The point a fraction t of the way from a to b.
inline Vec2 lerp(const Vec2 a, const Vec2 b, const double t) { return a + (b - a) * t; }

// The quadratic Bezier curve a (start), b (control), c (end) at t. De Casteljau: lerp along
// both legs of the control polygon, then between the two results.
inline Vec2 bezierLerp(const Vec2 a, const Vec2 b, const Vec2 c, const double t) {
  return lerp(lerp(a, b, t), lerp(b, c, t), t);
}

// ---- Assignment 12 ------------------------------------------------------------------

namespace geometry_detail {

inline double cross(const Vec2 u, const Vec2 v) { return u.x * v.y - u.y * v.x; }
inline double dot(const Vec2 u, const Vec2 v) { return u.x * v.x + u.y * v.y; }

// Positive on one side of the line through start and end, negative on the other, 0 on it.
inline double side(const Vec2 pt, const Vec2 start, const Vec2 end) { return cross(end - start, pt - start); }

}  // namespace geometry_detail

// Where segment a1-a2 meets segment b1-b2; nothing if they don't, or are parallel.
inline std::optional<Vec2> segmentsIntersect(const Vec2 a1, const Vec2 a2, const Vec2 b1, const Vec2 b2) {
  using namespace geometry_detail;
  // Each segment's endpoints must not lie strictly on the same side of the other's line.
  if (side(b1, a1, a2) * side(b2, a1, a2) > 0) return std::nullopt;
  if (side(a1, b1, b2) * side(a2, b1, b2) > 0) return std::nullopt;
  const Vec2 v1 = a2 - a1, v2 = b2 - b1;
  const double denominator = cross(v1, v2);
  if (std::abs(denominator) < 1e-9) return std::nullopt;  // parallel or collinear
  const double t = cross(b1 - a1, v2) / denominator;
  return a1 + v1 * t;
}

// ---- Assignment 13 ------------------------------------------------------------------

namespace geometry_detail {

// Real roots of a t^2 + b t + c = 0, in increasing order; a double root once.
// The test data make a, and the discriminant of a tangent, exactly 0 when they are 0.
inline std::vector<double> solveQuadratic(const double a, const double b, const double c) {
  if (a == 0) {
    if (b == 0) return {};  // no root (or every t, which the tests exclude)
    return {-c / b};
  }
  const double discriminant = b * b - 4 * a * c;
  if (discriminant < 0) return {};
  if (discriminant == 0) return {-b / (2 * a)};
  // The stable form: no cancellation between b and the square root.
  const double q = -0.5 * (b + std::copysign(std::sqrt(discriminant), b));
  std::vector<double> roots = {q / a, c / q};
  std::sort(roots.begin(), roots.end());
  return roots;
}

}  // namespace geometry_detail

// Where the infinite line through l1 and l2 meets the curve p1 (start), p2 (control),
// p3 (end), ordered along the curve.
inline std::vector<Vec2> segmentQuadBezierIntersect(const Vec2 p1, const Vec2 p2, const Vec2 p3, const Vec2 l1,
                                                    const Vec2 l2) {
  using namespace geometry_detail;
  const Vec2 d = l2 - l1;
  const Vec2 k = {d.y, -d.x};  // perpendicular to the line: dot(k, X - l1) = 0 on it
  // The curve as a polynomial: P(t) = A t^2 + B t + C.
  const Vec2 A = p1 - p2 * 2 + p3, B = (p2 - p1) * 2, C = p1;
  std::vector<Vec2> points;
  for (const double t : solveQuadratic(dot(k, A), dot(k, B), dot(k, C - l1))) {
    if (t >= 0 && t <= 1) points.push_back(A * (t * t) + B * t + C);
  }
  return points;
}

// ---- Assignment 15 ------------------------------------------------------------------

// The smallest y on the curve p1 (start), p2 (control), p3 (end) for 0 <= t <= 1.
inline double getBezierMinY(const Vec2 p1, const Vec2 p2, const Vec2 p3) {
  // y(t) = a t^2 + b t + p1.y
  const double a = p1.y - 2 * p2.y + p3.y;
  const double b = 2 * (p2.y - p1.y);
  double lowest = std::min(p1.y, p3.y);  // the ends are always candidates
  if (a > 0) {                           // a valley: its turning point is the lowest point
    const double t = -b / (2 * a);
    if (t > 0 && t < 1) lowest = std::min(lowest, (a * t + b) * t + p1.y);
  }
  return lowest;
}
