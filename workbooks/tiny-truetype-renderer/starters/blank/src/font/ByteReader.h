#pragma once
// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This header declares your reader for big-endian numbers at any position in a font
//   file: unsigned and signed integers of 8, 16 and 32 bits, and F2Dot14 fixed point.
//   Every later assignment that reads the font goes through it: assignment 02 reads the
//   table directory, 03 to 05 the `cmap`, `loca` and metrics tables, and 07 and 09 the
//   glyph outlines.
//
// Your job:
//   Declare a reader that opens a binary file and keeps a current position. Give it
//   functions to jump to an absolute offset, skip forward, read each of the six integer
//   types (`u8` to `i32`) big-endian, and read an F2Dot14 as a floating-point number. Also
//   declare how a read reports that it ran out of bytes, such as an exception type.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
