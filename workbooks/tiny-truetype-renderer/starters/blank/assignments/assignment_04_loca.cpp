// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This is the program the checker runs for assignment 04, as
//   `build/solutions/assignment_04.exe <input-file> <output-file>`: it reads a test input,
//   calls your code and writes the answer to the output file. Only that output is checked.
//   Check it with `.\check 04`, or Run and Submit in the book.
//
// Your job:
//   Read the `font` line, turn the four `table` lines (`glyf`, `head`, `loca`, `maxp`)
//   into table records, collect the `glyph` ids, and load the locations once with your
//   `Loca` code. Write the `glyphs <numGlyphs> loca <short|long>` line, then one `glyph
//   <id> <offset> <length>` line per requested id, in input order.
//
// The other files of this assignment:
//   This assignment also has you write src/font/Loca.h and src/font/Loca.cpp; each says
//   its job at the top.
//   Earlier files you can use: src/font/ByteReader.h and src/font/FontParser.h.
//   Include them by their path under src/, e.g. #include "font/Loca.h".
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================

int main(int argc, char** argv) {
}
