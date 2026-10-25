#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The parser decodes one glyph record from the glyf table into the types in `Glyph.h`:
//   the header of any glyph, and the contours and points of a simple one. In assignment 09
//   you call it for every simple glyph inside a compound glyph.
//
// Your job:
//   Declare one function that decodes the glyph record at a given offset and length,
//   reading through your `ByteReader` from assignment 01, and returns a glyph from
//   `Glyph.h`.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
