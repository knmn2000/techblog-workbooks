#pragma once
// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Your reader for big-endian numbers at any position in a font file: signed and unsigned
//   integers of 8, 16 and 32 bits, and F2Dot14 fixed point. The table directory, `cmap`,
//   `loca`, the metrics and the glyph outlines all get read through it.
//
// Your job:
//   Declare a reader that opens a binary file and tracks a current position. It needs
//   functions to jump to an absolute offset, skip forward, read each of the six integer
//   types (`u8` to `i32`) big-endian, and read an F2Dot14 as a floating-point number. Also
//   declare how a read reports running out of bytes, with an exception type for instance.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
