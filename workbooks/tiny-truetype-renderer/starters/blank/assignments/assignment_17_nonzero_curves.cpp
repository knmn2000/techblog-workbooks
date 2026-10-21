// ======================================================================================
// Assignment 17: Fill a glyph: non-zero rule
// Problem: problems/17-nonzero-curves.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 17 as `build/solutions/assignment_17.exe
//   <input-file> <output-file>`. It reads a test input, calls your code and writes the
//   answer to the output file, and the checker compares that answer with the expected one.
//   Run `.\check 17`, or use Run and Submit in the book.
//
// Your job:
//   Read the `canvas`, `place` and `color` lines and each `outline` with its `ends` and
//   `points` lines, where points can now be `off` (see Input). Make the canvas, fill every
//   outline in turn with your non-zero fill, and write the picture to the output path (see
//   Output).
//
// The other files of this assignment:
//   It adds to src/render/NonZero.h, which you started earlier: Keep the non-zero fill
//   function you declared in assignment 16. Your program now also passes it outlines with
//   off-curve points, so it has to handle curves. You have nothing new to declare unless
//   you add a helper for curves.
//   It adds to src/render/NonZero.cpp, which you started earlier: Make the non-zero fill
//   work for curved outlines. Every crossing on a curve needs the direction the curve runs
//   at that row. Once you split each curve where its y turns around, each piece runs one
//   way, and comparing its end's y with its start's y gives that direction. If your
//   `render/Scanline` from assignment 14 already splits curves and gives every crossing
//   its direction, your assignment 16 fill may pass as it is; otherwise add what's
//   missing, in `render/Scanline` or here.
//   Earlier files you can use: src/render/Scanline.h and src/utils/Geometry.h.
//   Include them by their path under src/, e.g. #include "render/NonZero.h".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
