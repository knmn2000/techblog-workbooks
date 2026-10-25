#pragma once
// ======================================================================================
// Assignment 06: Draw on a framebuffer
// Problem: problems/06-canvas.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   A picture in memory, one colour per pixel, with operations to paint a pixel, fill a
//   rectangle, draw a thick line and save a PNG. Outlines (08, 11), filled glyphs (14, 16,
//   17) and the line of text in 18 all end up drawn on it.
//
// Your job:
//   Declare a colour type (red, green and blue, one byte each) and a canvas type holding a
//   width, a height and one colour per pixel, all black to start. The canvas gets four
//   operations: paint one pixel, draw a filled rectangle from its centre and size, draw a
//   line of a given thickness between two points, and write the picture to a file.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
