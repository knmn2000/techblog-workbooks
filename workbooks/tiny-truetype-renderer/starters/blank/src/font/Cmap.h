#pragma once
// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This header declares your reader for the `cmap` table, the font's map from each
//   character to the glyph that draws it. It reads the format 12 subtable stored for
//   platform 0, encoding 4, which covers the full Unicode range, and assignment 18 looks
//   up every character of a line of text in the result.
//
// Your job:
//   Declare a function that reads a font's character map, given your `ByteReader` and the
//   table records from your `FontParser`. Its result should give the number of mapped code
//   points and the glyph id for a code point, or no glyph if the map doesn't cover it.
//   Also declare how the function reports a font without a usable subtable, such as an
//   exception type.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations (the same files are in starters/boilerplate/).
// ======================================================================================
