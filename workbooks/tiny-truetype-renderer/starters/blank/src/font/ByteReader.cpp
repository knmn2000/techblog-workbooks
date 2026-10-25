// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Opens the font, moves the position and assembles numbers from bytes. A bug here fails
//   the tests of every assignment that reads the font, so get it solid before moving on.
//
// Your job:
//   Open the file in binary mode, move the position on jumps and skips, and build each
//   number from its bytes, most significant first. The signed types use two's complement.
//   A read that needs a byte past the end of the file throws the error your header
//   declares (`UnexpectedEof` in the Boilerplate) instead of returning a value.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
