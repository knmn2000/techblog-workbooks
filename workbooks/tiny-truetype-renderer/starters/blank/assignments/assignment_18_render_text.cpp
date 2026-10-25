// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 18 as `build/solutions/assignment_18
//   <input-file> <output-file>` (its name ends in .exe on Windows). It reads a test input,
//   calls your code and writes the answer to the output file, and the checker compares
//   that answer with the expected one. Run `.\check 18` (`./check.sh 18` on macOS or
//   Linux), or use Run and Submit in the book.
//
// Your job:
//   Read the input line by line (see Input): load the font on `font`, make the canvas on
//   `canvas`, keep the pen and colour from `pen` and `color`, and draw each `text` line
//   (the rest of the line after `text` and its space) with your `TextRenderer`, carrying
//   the returned pen x on to the next `text` line. Then write the picture to the output
//   path (see Output).
//
// The other files of this assignment:
//   You also write src/utils/Unicode.h, src/TextRenderer.h, src/TextRenderer.cpp and
//   src/main.cpp in this assignment; each one gives its job at the top.
//   Earlier files you can use: src/font/FontParser.h, src/font/Cmap.h, src/font/Loca.h,
//   src/font/Metrics.h, src/font/CompoundGlyph.h and src/render/NonZero.h.
//   Include them by their path under src/, e.g. #include "utils/Unicode.h".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
