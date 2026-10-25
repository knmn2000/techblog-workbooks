#pragma once
// ======================================================================================
// Assignment 14: Fill a glyph: even-odd rule
// Problem: problems/14-even-odd-fill.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Both fill rules start the same way, and this is that part: turn an outline into edges
//   in pixels, then find, row by row, where the line through the pixel centres crosses
//   them. Your even-odd fill in 14 and your non-zero fill in 16 and 17 sit on top.
//
// Your job:
//   Declare what both fill rules share: a type for an edge piece (a straight line or a
//   quadratic curve, in pixels) and one for a crossing (its x, and whether the edge runs
//   up or down the screen there, which assignment 16 needs). Then declare functions that
//   turn an outline and its placement into edge pieces, give each pixel row its crossings
//   sorted by x, and fill a stretch of one row.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
