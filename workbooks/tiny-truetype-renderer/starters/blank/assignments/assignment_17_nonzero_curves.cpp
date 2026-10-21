// ======================================================================================
// Assignment 17: Fill a glyph: non-zero rule
// Problem: problems/17-nonzero-curves.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This is the program the checker runs for assignment 17, as
//   `build/solutions/assignment_17.exe <input-file> <output-file>`: it reads a test input,
//   calls your code and writes the answer to the output file. Only that output is checked.
//   Check it with `.\check 17`, or Run and Submit in the book.
//
// Your job:
//   Read the `canvas`, `place` and `color` lines and each `outline` with its `ends` and
//   `points` lines, where points can now be `off` (see Input). Make the canvas, fill every
//   outline in turn with your non-zero fill, and write the picture to the output path (see
//   Output).
//
// The other files of this assignment:
//   It adds to src/render/NonZero.h, which you started earlier: Keep the same fill
//   function: from now on it also gets outlines with off-curve points, so curves. There is
//   nothing new to declare unless you add a helper for curves.
//   It adds to src/render/NonZero.cpp, which you started earlier: Make the non-zero fill
//   right for curved outlines: every crossing on a curve needs the direction the curve
//   runs at that row, which is easy once each curve is split where its y turns around. If
//   your `render/Scanline` from assignment 14 already splits curves and gives every
//   crossing its direction, your assignment 16 fill may pass as it is; otherwise add
//   what's missing (in `render/Scanline` or here).
//   Earlier files you can use: src/render/Scanline.h and src/utils/Geometry.h.
//   Include them by their path under src/, e.g. #include "render/NonZero.h".
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
