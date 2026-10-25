#pragma once
// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Glyph records sit at positions the `loca` table lists by glyph id, each with an offset
//   and a size in bytes. This header is your reader for that table. Assignment 09 uses it
//   to find the parts of a compound glyph, and 18 to find the glyph for every character.
//
// Your job:
//   Two declarations: a glyph location (an offset from the start of the file and a length
//   in bytes) and a function that reads the location of every glyph, taking your
//   `ByteReader` and the table records from your `FontParser`. The result also carries
//   `numGlyphs` and whether `loca` is in the short or long format, because the first
//   output line prints both.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
