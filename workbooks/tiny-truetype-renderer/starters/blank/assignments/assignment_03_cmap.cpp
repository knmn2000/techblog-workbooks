// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 03 as `build/solutions/assignment_03
//   <input-file> <output-file>` (its name ends in .exe on Windows). It reads a test input,
//   calls your code and writes the answer to the output file, and the checker compares
//   that answer with the expected one. Run `.\check 03` (`./check.sh 03` on macOS or
//   Linux), or use Run and Submit in the book.
//
// Your job:
//   Read the `font` line, turn the `table "cmap"` line into a table record (you need its
//   offset), and load the character map once with your `Cmap` code. If loading reports no
//   usable subtable, write the single line `unsupported`. Otherwise answer each `count`
//   and `lookup` line in input order, in the formats the Output section gives.
//
// The other files of this assignment:
//   You also write src/font/Cmap.h and src/font/Cmap.cpp in this assignment; each one
//   gives its job at the top.
//   Earlier files you can use: src/font/ByteReader.h and src/font/FontParser.h.
//   Include them by their path under src/, e.g. #include "font/Cmap.h".
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
