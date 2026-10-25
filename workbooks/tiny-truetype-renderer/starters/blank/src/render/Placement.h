#pragma once
// ======================================================================================
// Assignment 08: Draw an outline with straight lines
// Problem: problems/08-outline-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   A placement is where a glyph goes on the canvas, given as three numbers: the pixel
//   column of font x = 0, the pixel row of the baseline and the pixels per font unit.
//   Together they turn font units (y up) into pixels (y down). You place glyphs with it in
//   assignments 11, 14, 16 and 17, and in assignment 18 you move it along a line of text,
//   one glyph at a time.
//
// Your job:
//   Declare a small type in this header, with no `.cpp`, for the three values of a `place`
//   line: `x0`, `baseline` and `scale`, as numbers that can be fractional or negative.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
