// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This file reads `maxp`, `head` and `loca` and works out one location per glyph id.
//   Assignments 09 and 18 look glyphs up in its result.
//
// Your job:
//   Read `numGlyphs` from `maxp` and `indexToLocFormat` from `head`, read the `numGlyphs`
//   + 1 `loca` entries, and turn them into an absolute offset and a length for each glyph
//   id. The page lists the fields and formulas under "The tables you need". The
//   Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/Loca.h"  // loadGlyphLocations (assignment 04), defined here

#include <stdexcept>  // std::logic_error, which the TODO throws

GlyphLocations loadGlyphLocations(ByteReader& reader, const Tables& tables) {
  // TODO: numGlyphs from maxp, the offset format from head, then loca (see the problem page).
  throw std::logic_error("not implemented: loadGlyphLocations");
}
