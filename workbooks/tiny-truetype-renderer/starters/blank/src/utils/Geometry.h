#pragma once
// ======================================================================================
// Assignment 10: Lerp and quadratic Bezier curves
// Problem: problems/10-bezier.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This header holds the project's 2D maths: a point type, lerp, and the point at t on a
//   quadratic Bezier curve. In assignment 11 you draw curves with it. Assignments 12, 13
//   and 15 add the blog's helpers for where segments and curves meet and for a curve's
//   lowest point. The blog's fill uses them; your fills from assignment 14 on work out
//   each crossing from its edge instead.
//
// Your job:
//   Declare a 2D point type with `double` x and y, and the arithmetic you want on it:
//   adding, subtracting and scaling by a number. Then write two functions: lerp, which
//   returns the point a fraction t of the way from a to b, and one that returns the point
//   at t on a quadratic Bezier curve from its start, control point and end. The project
//   has no `Geometry.cpp`, so define the functions in this header and mark them `inline`.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
