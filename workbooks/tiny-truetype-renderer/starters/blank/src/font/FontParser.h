#pragma once
// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Opening a font and reading its table directory: the tag, checksum, offset and length
//   of every table (`cmap`, `glyf`, `loca`, ...). Assignments 03 to 05 find their tables
//   by tag in these records, and assignment 18 opens the font through it.
//
// Your job:
//   Declare a record for one table (its 4-character tag, `checkSum`, `offset` and
//   `length`), a function that reads the whole directory through your `ByteReader`, and a
//   collection of records you can look up by tag, which assignments 03 to 05 use.
//   Assignment 18 also wants one object that opens a font and holds its reader and tables;
//   you can declare it now or then.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
