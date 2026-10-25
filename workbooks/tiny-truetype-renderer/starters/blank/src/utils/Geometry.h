#pragma once
// ======================================================================================
// Assignment 10: Lerp and quadratic Bezier curves
// Problem: problems/10-bezier.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   2D maths in one header: a point type, lerp, and the point at t on a quadratic Bezier
//   curve, which the curve drawing in 11 uses. Assignments 12, 13 and 15 add the blog's
//   helpers for where segments and curves meet and for a curve's lowest point. The blog's
//   fill relies on those; yours, from 14 on, works out each crossing from its edge and
//   skips them.
//
// Your job:
//   Declare a 2D point type with `double` x and y, and whatever arithmetic you want on it:
//   adding, subtracting, scaling by a number. Then write two functions: lerp, which
//   returns the point a fraction t of the way from a to b, and one that returns the point
//   at t on a quadratic Bezier curve from its start, control point and end. The project
//   has no `Geometry.cpp`, so define them in this header and mark them `inline`.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
