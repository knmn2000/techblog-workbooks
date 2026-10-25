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
//   Implement the canvas operations as "Painting one pixel", "Drawing a rectangle" and
//   "Drawing a line" describe. Painting a pixel ignores coordinates outside the picture, a
//   rectangle clips its loops to the canvas, and a line stamps a square at every step.
//   Save the pixels as a PNG with `stbi_write_png` or as a binary PPM.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
