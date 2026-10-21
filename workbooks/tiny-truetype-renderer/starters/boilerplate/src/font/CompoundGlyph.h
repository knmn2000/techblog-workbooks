#pragma once
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
//   The Boilerplate gives you this file finished: the declarations, with the author's
//   names. You fill in the TODOs in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
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
