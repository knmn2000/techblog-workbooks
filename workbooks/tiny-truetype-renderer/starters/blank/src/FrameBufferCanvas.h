#pragma once
// ======================================================================================
// Assignment 06: Draw on a framebuffer
// Problem: problems/06-canvas.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The canvas holds a picture in memory, one colour per pixel. It can paint one pixel,
//   fill a rectangle, draw a thick line and save the picture as a PNG. You draw every
//   later picture on it: outlines in 08 and 11, filled glyphs in 14, 16 and 17, and a line
//   of text in 18.
//
// Your job:
//   Declare a colour type (red, green and blue, one byte each) and a canvas type that
//   holds a width, a height and one colour per pixel, all black to start. Give the canvas
//   four operations: paint one pixel, draw a filled rectangle from its centre and size,
//   draw a line of a given thickness between two points, and write the picture to a file.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
