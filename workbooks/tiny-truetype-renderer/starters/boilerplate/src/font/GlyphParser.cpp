// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The parser decodes one glyph record from the glyf table into the types in `Glyph.h`:
//   the header of any glyph, and the contours and points of a simple one. In assignment 09
//   you call it for every simple glyph inside a compound glyph.
//
// Your job:
//   Implement the glyph decoder as "The glyph record you are decoding" lays out. Length 0
//   gives an empty glyph. A negative `numberOfContours` gives a compound glyph, and you
//   stop reading after the header. For a simple glyph, read the contour ends and every
//   point, with absolute coordinates and the point's own on/off flag. The Boilerplate
//   gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/GlyphParser.h"

#include <stdexcept>

Glyph readGlyph(ByteReader& reader, const uint32_t offset, const uint32_t length) {
  // TODO: decode the record (layout and rules are on the problem page). A simple glyph's
  // outline goes in g.components[0]; for a compound glyph, set its kind and stop.
  throw std::logic_error("not implemented: readGlyph");
}
