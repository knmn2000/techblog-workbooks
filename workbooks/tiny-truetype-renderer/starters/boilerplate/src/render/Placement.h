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
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

// Font point (x, y) lands on pixel (x0 + scale * x, baseline - scale * y): font y grows
// upwards, pixel y grows downwards.
struct Placement {
  double x0 = 0;
  double baseline = 0;
  double scale = 1;
};
