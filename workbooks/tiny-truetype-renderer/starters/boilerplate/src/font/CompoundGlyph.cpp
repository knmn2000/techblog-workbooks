// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Resolving a compound glyph means reading its components, transforming each one, and
//   following any component that is itself compound, to any depth. A simple glyph comes
//   back as itself and an empty one gives no parts.
//
// Your job:
//   Implement the resolver as "The compound glyph record" and "Placing a component"
//   describe. An empty glyph gives no parts, and a simple glyph gives itself, decoded by
//   your `GlyphParser`. For a compound glyph, read all the component records first, then
//   resolve each component in record order, applying its own transform before the outer
//   ones. The Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/CompoundGlyph.h"  // resolveGlyph's declaration (assignment 09)

#include <stdexcept>  // std::logic_error for the "not implemented" TODO

#include "font/GlyphParser.h"  // readGlyph (assignment 07): decodes the simple parts

std::vector<GlyphComponent> resolveGlyph(ByteReader& reader, const std::map<uint32_t, GlyphLocation>& locations,
                                         const uint32_t glyphId) {
  // TODO: read the component records and apply their transforms, recursively (see the problem
  // page). readGlyph (assignment 07) decodes the simple glyphs they end in.
  throw std::logic_error("not implemented: resolveGlyph");
}
