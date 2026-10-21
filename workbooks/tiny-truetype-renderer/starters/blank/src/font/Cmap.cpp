// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The code that reads the platform 0 / encoding 4 subtable of `cmap` into a
//   character-to-glyph map. Assignment 18 builds this map once per font.
//
// Your job:
//   Implement it: find the encoding record with platform 0 and encoding 4, check that its
//   subtable is format 12, and read its groups so that every code point they cover can be
//   looked up. Report the two `unsupported` cases (no such record, or another format) the
//   way your header declares.
//
// How to start:
//   Two ways: write it all yourself from here, or press Boilerplate in the book's editor
//   for ready-made input/output code and declarations named as the author names them (the
//   same files are in starters/boilerplate/).
// ======================================================================================
