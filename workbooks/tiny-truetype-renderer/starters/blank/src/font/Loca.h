#pragma once
// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This header declares your reader for the `loca` table, which gives the position and
//   size in bytes of each glyph's record, by glyph id. Assignment 09 uses it to find the
//   parts of a compound glyph, and assignment 18 to find the glyph of every character.
//
// Your job:
//   Declare a glyph location (an offset from the start of the file and a length in bytes)
//   and a function that reads the location of every glyph, given your `ByteReader` and the
//   table records from your `FontParser`. Have its result also carry `numGlyphs` and
//   whether `loca` uses the short or long format, because the first output line prints
//   both.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
