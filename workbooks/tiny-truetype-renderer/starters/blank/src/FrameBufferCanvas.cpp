// ======================================================================================
// Assignment 06: Draw on a framebuffer
// Problem: problems/06-canvas.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   A picture in memory, one colour per pixel, with three ways to draw on it (one pixel, a
//   filled rectangle, a thick line) and a way to save it as a PNG. Every picture from
//   assignment 08 on is drawn on it: outlines in 08 and 11, filled glyphs in 14, 16 and
//   17, and a line of text in 18.
//
// Your job:
//   Implement those operations as "Painting one pixel", "Drawing a rectangle" and "Drawing
//   a line" describe: painting a pixel ignores anything outside the picture, a rectangle
//   clips its loops to the canvas, and a line stamps a square at every step. Write the
//   pixels out as a PNG with `stbi_write_png`, or as a binary PPM.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
