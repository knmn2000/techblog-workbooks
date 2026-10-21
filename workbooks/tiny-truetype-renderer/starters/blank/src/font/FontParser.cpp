// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This file reads the table directory from the first bytes of the font through your
//   `ByteReader`. Each later assignment that needs a table looks up its offset in these
//   records.
//
// Your job:
//   Read `numTables` from the 12-byte header and skip the other header fields, then read
//   one 16-byte record per table and keep each tag's 4 bytes as the font stores them. If
//   you declared a font object, have it open the file and load the directory once.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
