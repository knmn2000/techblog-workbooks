// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This is the program the checker runs for assignment 03, as
//   `build/solutions/assignment_03.exe <input-file> <output-file>`: it reads a test input,
//   calls your code and writes the answer to the output file. Only that output is checked.
//   Check it with `.\check 03`, or Run and Submit in the book.
//
// Your job:
//   Read the `font` line, turn the `table "cmap"` line into a table record (you need its
//   offset), and load the character map once with your `Cmap` code. If loading reports no
//   usable subtable, write only `unsupported`; otherwise answer each `count` and `lookup`
//   line in input order, in the formats the Output section gives.
//
// The other files of this assignment:
//   This assignment also has you write src/font/Cmap.h and src/font/Cmap.cpp; each says
//   its job at the top.
//   Earlier files you can use: src/font/ByteReader.h and src/font/FontParser.h.
//   Include them by their path under src/, e.g. #include "font/Cmap.h".
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
