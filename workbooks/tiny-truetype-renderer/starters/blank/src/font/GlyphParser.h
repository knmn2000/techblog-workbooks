#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Decoding one glyph record from the glyf table into the types in `Glyph.h`: the header
//   of every glyph, and the contours and points of a simple one. Assignment 09 calls it
//   for every simple glyph a compound glyph is made of.
//
// Your job:
//   Declare one function that decodes the glyph record at a given offset and length,
//   reading through your `ByteReader` from assignment 01, and returns a glyph from
//   `Glyph.h`.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
