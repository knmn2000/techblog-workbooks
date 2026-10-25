// ======================================================================================
// Assignment 06: Draw on a framebuffer
// Problem: problems/06-canvas.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Painting, rectangles, thick lines and the PNG save all live here. All later drawing
//   assignments go through this code, so a stray pixel in it shows up in all of them.
//
// Your job:
//   Implement the operations as "Painting one pixel", "Drawing a rectangle" and "Drawing a
//   line" describe them. A pixel outside the picture is ignored, a rectangle clips its
//   loops to the canvas, and a line stamps a square at every step. Save the pixels as a
//   PNG with `stbi_write_png`, or as a binary PPM.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
