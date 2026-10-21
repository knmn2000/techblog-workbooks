// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Turning any glyph into the simple outlines it is drawn with: a compound glyph's
//   components are read, moved, scaled or rotated, and resolved however deeply they nest.
//   Assignment 18 draws every character of a line of text through it, so it never has to
//   tell simple glyphs from compound ones.
//
// Your job:
//   Implement it with "The compound glyph record" and "Placing a component": an empty
//   glyph gives no parts, and a simple glyph gives itself, decoded by your `GlyphParser`
//   from assignment 07. For a compound glyph, read all of its component records, then
//   resolve each component in record order, with its own transform applied first and the
//   outer ones after. The Boilerplate has the declarations written: fill in what's marked
//   TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include "font/CompoundGlyph.h"

#include <stdexcept>

#include "font/GlyphParser.h"

std::vector<GlyphComponent> resolveGlyph(ByteReader& reader, const std::map<uint32_t, GlyphLocation>& locations,
                                         const uint32_t glyphId) {
  // TODO: read the component records and apply their transforms, recursively (see the problem
  // page). readGlyph (assignment 07) decodes the simple glyphs they end in.
  throw std::logic_error("not implemented: resolveGlyph");
}
