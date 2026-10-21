#pragma once
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
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include <cstdint>
#include <map>
#include <vector>

#include "GlyphComponent.h"
#include "font/ByteReader.h"
#include "font/Loca.h"

// The simple glyphs `glyphId` is drawn with, every point in the glyph's own coordinates
// (font units). A simple glyph gives itself; an empty one gives nothing.
std::vector<GlyphComponent> resolveGlyph(ByteReader& reader, const std::map<uint32_t, GlyphLocation>& locations,
                                         uint32_t glyphId);
