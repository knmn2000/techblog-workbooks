#pragma once
// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This header declares the code that opens a font and reads its table directory: the
//   tag, checksum, offset and length of each table (`cmap`, `glyf`, `loca`, ...).
//   Assignments 03 to 05 find their tables by tag in these records, and assignment 18
//   opens the font through it.
//
// Your job:
//   Declare a record for one table (its 4-character tag, `checkSum`, `offset` and
//   `length`), a function that reads the whole directory through your `ByteReader`, and a
//   collection of records that assignments 03 to 05 can search by tag. Assignment 18 also
//   uses one object that opens a font and holds its reader and tables. You can declare it
//   now or when you reach assignment 18.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
