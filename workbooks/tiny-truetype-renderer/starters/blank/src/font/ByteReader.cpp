// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This file implements the reader: it opens the font, moves the position and turns bytes
//   into numbers. Every later assignment that reads the font runs this code, so a bug here
//   makes their tests fail too.
//
// Your job:
//   Open the file in binary mode, move the position for jumps and skips, and build each
//   number from its bytes, most significant first, with two's complement for the signed
//   types. If a read needs a byte past the end of the file, throw the error your header
//   declares (`UnexpectedEof` in the Boilerplate) instead of returning a value.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
