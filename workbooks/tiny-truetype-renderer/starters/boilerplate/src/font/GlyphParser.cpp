// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Bytes of a glyph record become the types in `Glyph.h` here: the header of any glyph,
//   then the contours and points of a simple one. The compound glyph code in assignment 09
//   calls it once per simple part.
//
// Your job:
//   Implement the decoder as "The glyph record you are decoding" lays it out. Length 0
//   gives an empty glyph. A negative `numberOfContours` means compound, and you stop after
//   the header. A simple glyph needs the contour ends and every point, with absolute
//   coordinates and the point's own on/off flag. The Boilerplate gives you the
//   declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/GlyphParser.h"  // readGlyph's declaration (assignment 07)

#include <stdexcept>  // std::logic_error for the "not implemented" TODO

Glyph readGlyph(ByteReader& reader, const uint32_t offset, const uint32_t length) {
  // TODO: decode the record (layout and rules are on the problem page). A simple glyph's
  // outline goes in g.components[0]; for a compound glyph, set its kind and stop.
  throw std::logic_error("not implemented: readGlyph");
}
