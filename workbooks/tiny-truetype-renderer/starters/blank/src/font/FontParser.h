#pragma once
// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Every table in the font gets a record: tag, checksum, offset and length (`cmap`,
//   `glyf`, `loca` and the rest). Assignments 03 to 05 find their tables by tag in these
//   records, and 18 opens the font through them.
//
// Your job:
//   Declare a record for one table (its 4-character tag, `checkSum`, `offset` and
//   `length`), a function that reads the whole directory through your `ByteReader`, and a
//   collection of records that assignments 03 to 05 can search by tag. Assignment 18 also
//   wants one object that opens a font and holds its reader and tables; declare it now or
//   wait until you get there.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
