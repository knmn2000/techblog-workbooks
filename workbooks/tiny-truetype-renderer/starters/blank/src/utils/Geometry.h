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
//   the functions right here in the header and mark them `inline`.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
