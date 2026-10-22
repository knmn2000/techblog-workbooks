// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 04 as `build/solutions/assignment_04
//   <input-file> <output-file>` (its name ends in .exe on Windows). It reads a test input,
//   calls your code and writes the answer to the output file, and the checker compares
//   that answer with the expected one. Run `.\check 04` (`./check.sh 04` on macOS or
//   Linux), or use Run and Submit in the book.
//
// Your job:
//   Read the `font` line, turn the four `table` lines (`glyf`, `head`, `loca`, `maxp`)
//   into table records, collect the `glyph` ids, and load the locations once with your
//   `Loca` code. Write the `glyphs <numGlyphs> loca <short|long>` line, then one `glyph
//   <id> <offset> <length>` line per requested id, in input order.
//
// The other files of this assignment:
//   You also write src/font/Loca.h and src/font/Loca.cpp in this assignment; each one
//   gives its job at the top.
//   Earlier files you can use: src/font/ByteReader.h and src/font/FontParser.h.
//   Include them by their path under src/, e.g. #include "font/Loca.h".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
