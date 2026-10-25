// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   From the first bytes of the font, through your `ByteReader`, this file reads the table
//   directory. Later assignments look up their table's offset in these records.
//
// Your job:
//   Read `numTables` from the 12-byte header and skip the other header fields, then read
//   one 16-byte record per table, keeping each tag's 4 bytes as the font stores them. The
//   Boilerplate's `FontParser` constructor already opens the file and loads the directory.
//   Writing from scratch, how you wrap that in a font object is up to you.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
