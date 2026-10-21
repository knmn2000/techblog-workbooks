// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The code that reads `maxp`, `head` and `loca` and works out one location per glyph id.
//   Assignments 09 and 18 look glyphs up in what it returns.
//
// Your job:
//   Implement it: read `numGlyphs` from `maxp` and `indexToLocFormat` from `head`, read
//   the `numGlyphs` + 1 `loca` entries, and turn them into an absolute offset and a length
//   for each glyph id. The fields and formulas are under "The tables you need". The
//   Boilerplate has the declarations written: fill in what's marked TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/Loca.h"

#include <stdexcept>

GlyphLocations loadGlyphLocations(ByteReader& reader, const Tables& tables) {
  // TODO: numGlyphs from maxp, the offset format from head, then loca (see the problem page).
  throw std::logic_error("not implemented: loadGlyphLocations");
}
