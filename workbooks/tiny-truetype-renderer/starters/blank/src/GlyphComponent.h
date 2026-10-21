#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The form every outline takes in the project: its points (x and y in font units, on or
//   off the curve) and the index where each contour ends. Assignments 08 and 11 draw
//   outlines in this form, 09 produces one per part of a compound glyph, and 14, 16 and 17
//   fill them.
//
// Your job:
//   Declare a point type (x, y and whether it is on the curve) and an outline type that
//   holds the contour end indices and the list of points. Give x and y a type that can
//   hold fractions, such as `double`: assignment 08 reads coordinates like `120.75` and
//   assignment 09 scales points.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
