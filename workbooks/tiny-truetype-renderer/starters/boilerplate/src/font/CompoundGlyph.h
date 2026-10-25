#pragma once
// ======================================================================================
// Assignment 09: Resolve compound glyphs
// Problem: problems/09-compound-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Turns any glyph into the simple outlines you draw it with. It reads a compound glyph's
//   components, moves, scales or rotates each one, and resolves components nested at any
//   depth. The text renderer in 18 draws every character through it, so it doesn't have to
//   ask whether a glyph is simple.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>  // uint32_t for glyph ids
#include <map>      // std::map: where each glyph's record is, by glyph id
#include <vector>   // std::vector<GlyphComponent>: one outline per simple part

#include "GlyphComponent.h"   // GlyphComponent (assignment 07): the outline of each part
#include "font/ByteReader.h"  // ByteReader (assignment 01): big-endian reads from the font
#include "font/Loca.h"        // GlyphLocation (assignment 04): a record's offset and length

// The simple glyphs `glyphId` is drawn with, every point in the glyph's own coordinates
// (font units). A simple glyph gives itself; an empty one gives nothing.
std::vector<GlyphComponent> resolveGlyph(ByteReader& reader, const std::map<uint32_t, GlyphLocation>& locations,
                                         uint32_t glyphId);
