// ======================================================================================
// Assignment 11: Draw an outline with curves
// Problem: problems/11-outline-curves.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This is the program the checker runs for assignment 11, as
//   `build/solutions/assignment_11.exe <input-file> <output-file>`: it reads a test input,
//   calls your code and writes the answer to the output file. Only that output is checked.
//   Check it with `.\check 11`, or Run and Submit in the book.
//
// Your job:
//   Read the input as in assignment 08: make the canvas from the `canvas` line, keep the
//   latest `place`, `style` (now only the line thickness) and `color`, and build each
//   outline from its `ends` and `points` lines. Draw every outline with your new curve
//   function from `render/Outline.h`, then write the canvas to the output path with your
//   `FrameBufferCanvas` from assignment 06.
//
// The other files of this assignment:
//   It adds to src/render/Outline.h, which you started earlier: Add a second drawing
//   function next to your straight-line one from assignment 08. It takes the canvas, an
//   outline, its placement, a line thickness and a colour, and draws the outline with real
//   curves. The Boilerplate's `Outline.h` already declares it as `renderGlyphCurves`; if
//   you wrote the header your own way, add the declaration now.
//   It adds to src/render/Outline.cpp, which you started earlier: Implement the curve
//   drawing. Walk each contour from an on-curve point, turning the points into straight
//   lines and quadratic curves (with an implied on-curve point between two off-curve
//   points), and draw each curve as short lines using your curve function from
//   `utils/Geometry.h`. Draw the red, green and blue markers only after all the lines of
//   the outline.
//   Earlier files you can use: src/utils/Geometry.h.
//   Include them by their path under src/, e.g. #include "render/Outline.h".
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
