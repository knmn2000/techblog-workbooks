#pragma once
// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Reading big-endian numbers from any position in a font file: unsigned and signed
//   integers of 8, 16 and 32 bits, and F2Dot14 fixed point. Every later assignment that
//   reads the font reads it through this: assignment 02 the table directory, 03 to 05 the
//   `cmap`, `loca` and metrics tables, and 07 and 09 the glyph outlines.
//
// Your job:
//   Declare a reader that opens a binary file and keeps a current position. It needs a way
//   to jump to an absolute offset, skip forward, read each of the six integer types (`u8`
//   to `i32`) big-endian, and read an F2Dot14 as a floating-point number, plus a way to
//   report that a read ran out of bytes (an exception type, for example).
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
