#pragma once
// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The `cmap` table: which glyph draws each character, read from the format 12 subtable
//   for the full Unicode range. Later, assignment 18 looks up every character of a line of
//   text here.
//
// Your job:
//   Declare a function that reads a font's character map, given your `ByteReader` and the
//   table records from your `FontParser`, and returns something that can say how many code
//   points are mapped and which glyph id a code point maps to, if any. Also declare how it
//   reports a font without a usable subtable (an exception type, for example).
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
