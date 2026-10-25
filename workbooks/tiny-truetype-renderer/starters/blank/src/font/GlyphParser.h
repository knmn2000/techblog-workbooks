#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   One glyph record from the `glyf` table goes in and a glyph from `Glyph.h` comes out:
//   the header of any glyph, plus contours and points when it is simple. Assignment 09
//   calls it for each simple glyph inside a compound glyph.
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
