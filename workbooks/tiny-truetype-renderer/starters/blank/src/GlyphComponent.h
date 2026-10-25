#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   An outline is a list of points (x and y in font units, on or off the curve) plus the
//   index where each contour ends, and this header defines that shape. Assignments 08 and
//   11 draw it, 09 produces one per part of a compound glyph, and 14, 16 and 17 fill it.
//
// Your job:
//   Declare a point type (x, y, and whether it is on the curve) and an outline type
//   holding the contour end indices and the list of points. Give x and y a type that can
//   hold fractions, such as `double`: assignment 08 reads coordinates like `120.75` and
//   assignment 09 scales points.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
