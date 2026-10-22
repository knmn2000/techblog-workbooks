// ======================================================================================
// Assignment 11: Draw an outline with curves
// Problem: problems/11-outline-curves.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 11 as `build/solutions/assignment_11
//   <input-file> <output-file>` (its name ends in .exe on Windows). It reads a test input,
//   calls your code and writes the answer to the output file, and the checker compares
//   that answer with the expected one. Run `.\check 11` (`./check.sh 11` on macOS or
//   Linux), or use Run and Submit in the book.
//
// Your job:
//   Read the input as in assignment 08: make the canvas from the `canvas` line, keep the
//   latest `place`, `style` (which now holds only the line thickness) and `color`, and
//   build each outline from its `ends` and `points` lines. Draw every outline with your
//   new curve function from `render/Outline.h`, then write the canvas to the output path
//   with your `FrameBufferCanvas` from assignment 06.
//
// The other files of this assignment:
//   It adds to src/render/Outline.h, which you started earlier: Declare a second drawing
//   function next to your straight-line one from assignment 08. It takes the canvas, an
//   outline, its placement, a line thickness and a colour, and draws the outline with its
//   curves. The Boilerplate's `Outline.h` already declares it as `renderGlyphCurves`; if
//   you wrote the header your own way, add the declaration now.
//   It adds to src/render/Outline.cpp, which you started earlier: Implement the curve
//   drawing. Walk each contour from an on-curve point and turn its points into straight
//   lines and quadratic curves, adding an implied on-curve point between two off-curve
//   points. Draw each curve as short lines with your curve function from
//   `utils/Geometry.h`. Draw the red, green and blue markers after all the lines of the
//   outline.
//   Earlier files you can use: src/utils/Geometry.h.
//   Include them by their path under src/, e.g. #include "render/Outline.h".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
