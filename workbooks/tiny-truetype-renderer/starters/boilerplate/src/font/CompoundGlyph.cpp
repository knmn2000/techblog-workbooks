// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This code turns any glyph into the simple outlines you draw it with. It reads a
//   compound glyph's components, moves, scales or rotates each one, and resolves
//   components nested at any depth. In assignment 18 you draw every character of a line of
//   text through it, so your text renderer doesn't need to tell simple glyphs from
//   compound ones.
//
// Your job:
//   Implement the glyph resolver as "The compound glyph record" and "Placing a component"
//   describe. An empty glyph gives no parts, and a simple glyph gives itself, decoded by
//   your `GlyphParser` from assignment 07. For a compound glyph, read all of its component
//   records first, then resolve each component in record order: apply its own transform
//   first and the outer ones after. The Boilerplate gives you the declarations; fill in
//   each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
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
