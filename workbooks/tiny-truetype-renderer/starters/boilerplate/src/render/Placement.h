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
//   The Boilerplate gives you this file finished: the declarations, with the author's
//   names. You fill in the TODOs in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

// Font point (x, y) lands on pixel (x0 + scale * x, baseline - scale * y): font y grows
// upwards, pixel y grows downwards.
struct Placement {
  double x0 = 0;
  double baseline = 0;
  double scale = 1;
};
