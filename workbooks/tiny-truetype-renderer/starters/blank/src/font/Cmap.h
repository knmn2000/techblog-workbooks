#pragma once
// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Characters map to glyphs through the `cmap` table, and this is your reader for it.
//   Only the format 12 subtable stored for platform 0, encoding 4 is needed, which covers
//   the full Unicode range. Assignment 18 looks up every character of a line of text in
//   the result.
//
// Your job:
//   Declare a function that reads a font's character map, taking your `ByteReader` and the
//   table records from your `FontParser`. The result has to give the number of mapped code
//   points and a code point's glyph id, or no glyph where the map has none. Also declare
//   how a font without a usable subtable is reported, with an exception type for instance.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
