#pragma once
// ======================================================================================
// Assignment 08: Draw an outline with straight lines
// Problem: problems/08-outline-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Where a glyph goes on the canvas: the pixel column of font x = 0, the pixel row of the
//   baseline and the pixels per font unit, which together turn font units (y up) into
//   pixels (y down). Assignments 11, 14, 16 and 17 place their glyphs with it, and
//   assignment 18 moves it along a line of text, one glyph at a time.
//
// Your job:
//   Declare a small type for the three values of a `place` line: `x0`, `baseline` and
//   `scale`, as numbers that can be fractional or negative. It is a header with no `.cpp`.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
