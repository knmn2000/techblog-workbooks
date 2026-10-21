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
//   way your header declares. The Boilerplate has the declarations written: fill in what's
//   marked TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include "font/Cmap.h"

std::unordered_map<uint32_t, uint32_t> loadUnicodeToGlyphCodeMap(ByteReader& reader, const Tables& tables) {
  // TODO: find the subtable, check its format, and expand every group (problem page). Throw
  // UnsupportedCmap when the font has no format 12 subtable for platform 0, encoding 4.
  throw std::logic_error("not implemented: loadUnicodeToGlyphCodeMap");
}
