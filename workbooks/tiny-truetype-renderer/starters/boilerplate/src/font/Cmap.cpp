// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Finds the platform 0 / encoding 4 subtable of `cmap` and reads it into a map from
//   character to glyph. Assignment 18 builds the map once per font.
//
// Your job:
//   Find the encoding record with platform 0 and encoding 4, check that its subtable is
//   format 12, and read its groups so you can look up any code point they cover. Report
//   the two `unsupported` cases (no such record, or another format) the way your header
//   declares. The Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/Cmap.h"  // loadUnicodeToGlyphCodeMap (assignment 03), defined here

#include <stdexcept>  // std::logic_error for the "not implemented" TODO

std::unordered_map<uint32_t, uint32_t> loadUnicodeToGlyphCodeMap(ByteReader& reader, const Tables& tables) {
  // TODO: find the subtable, check its format, and expand every group (problem page). Throw
  // UnsupportedCmap when the font has no format 12 subtable for platform 0, encoding 4.
  throw std::logic_error("not implemented: loadUnicodeToGlyphCodeMap");
}
