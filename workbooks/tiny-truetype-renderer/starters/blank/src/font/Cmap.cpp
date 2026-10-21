// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This file reads the platform 0 / encoding 4 subtable of `cmap` into a map from
//   character to glyph. Assignment 18 builds this map once per font.
//
// Your job:
//   Find the encoding record with platform 0 and encoding 4, check that its subtable is
//   format 12, and read its groups so your code can look up every code point they cover.
//   Report the two `unsupported` cases (no such record, or another format) the way your
//   header declares.
//
// How to start:
//   Write it yourself from here, or press Boilerplate in the book's editor to get the
//   input/output code and the declarations, with the author's names (the same files are in
//   starters/boilerplate/).
// ======================================================================================
