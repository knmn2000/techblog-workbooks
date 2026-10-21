// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The reader's implementation: opening the file, moving around in it, and turning its
//   bytes into numbers. Every later assignment that reads the font runs through this code,
//   so a mistake here shows up everywhere.
//
// Your job:
//   Implement the reader: open the file in binary mode, move the position for jumps and
//   skips, and build each number from its bytes, most significant first, with two's
//   complement for the signed types. A read that needs a byte past the end of the file
//   must report it instead of returning a value.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
