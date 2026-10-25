// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 09 as `build/solutions/assignment_09
//   <input-file> <output-file>` (its name ends in .exe on Windows). It reads a test input,
//   calls your code and writes the answer to the output file, and the checker compares
//   that answer with the expected one. Run `.\check 09` (`./check.sh 09` on macOS or
//   Linux), or use Run and Submit in the book.
//
// Your job:
//   On each `font` line, open the font and forget the earlier glyph locations; record each
//   `glyph` line's offset and length by id. For each `decode` line, resolve the glyph and
//   write the header line and one `ends` / `points` pair per part, as Output shows
//   (fractional coordinates to at least 2 decimals).
//
// The other files of this assignment:
//   You also write src/font/CompoundGlyph.h and src/font/CompoundGlyph.cpp in this
//   assignment; each one gives its job at the top.
//   Earlier files you can use: src/font/GlyphParser.h and src/font/Loca.h.
//   Include them by their path under src/, e.g. #include "font/CompoundGlyph.h".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
