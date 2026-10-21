#pragma once
// ======================================================================================
// Assignment 10: Lerp and quadratic Bezier curves
// Problem: problems/10-bezier.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The project's 2D maths in one header: a point type, lerp, and the point at t on a
//   quadratic Bezier curve. Assignment 11 draws curves with it, assignments 12, 13 and 15
//   add where segments and curves meet and a curve's lowest point, and the fills from
//   assignment 14 on build on it. Later, assignments 12, 13 and 15 add to this file.
//
// Your job:
//   Declare a 2D point type with `double` x and y, and the arithmetic you want on it:
//   adding, subtracting and scaling by a number. Write two functions on it: lerp, the
//   point a fraction t of the way from a to b, and the point at t on a quadratic Bezier
//   curve given its start, control point and end. There is no `Geometry.cpp`, so define
//   the functions right here in the header and mark them `inline`. The Boilerplate has the
//   declarations written: fill in what's marked TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

// Points, curves and where they meet.
// Assignment 10: lerp and quadratic Bezier curves. 12: two segments. 13: a line and a curve.
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

// ---- Assignment 10 ------------------------------------------------------------------

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

// ---- Assignment 12 ------------------------------------------------------------------

// Where segment a1-a2 meets segment b1-b2; nothing if they don't, or are parallel.
inline std::optional<Vec2> segmentsIntersect(const Vec2 a1, const Vec2 a2, const Vec2 b1, const Vec2 b2) {
  // TODO: the side test, then the crossing point (see "The rules" on the problem page).
  throw std::logic_error("not implemented: segmentsIntersect");
}

// ---- Assignment 13 ------------------------------------------------------------------

// Where the infinite line through l1 and l2 meets the curve p1 (start), p2 (control),
// p3 (end), ordered along the curve.
inline std::vector<Vec2> segmentQuadBezierIntersect(const Vec2 p1, const Vec2 p2, const Vec2 p3, const Vec2 l1,
                                                    const Vec2 l2) {
  // TODO: see "From a line and a curve to a quadratic" and "Solving for t" on the problem page.
  throw std::logic_error("not implemented: segmentQuadBezierIntersect");
}

// ---- Assignment 15 ------------------------------------------------------------------

// The smallest y on the curve p1 (start), p2 (control), p3 (end) for 0 <= t <= 1.
inline double getBezierMinY(const Vec2 p1, const Vec2 p2, const Vec2 p3) {
  // TODO: see "Where the lowest point can be" on the problem page.
  throw std::logic_error("not implemented: getBezierMinY");
}
