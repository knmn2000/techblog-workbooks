#pragma once
// ======================================================================================
// Assignment 04: Locate glyph records (loca)
// Problem: problems/04-loca.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This header declares your reader for the `loca` table, which gives the position and
//   size in bytes of each glyph's record, by glyph id. Assignment 09 uses it to find the
//   parts of a compound glyph, and assignment 18 to find the glyph of every character.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>  // uint32_t offset and length; uint16_t numGlyphs
#include <vector>   // std::vector<GlyphLocation>: one location per glyph id

#include "font/ByteReader.h"  // ByteReader (assignment 01): the reader the tables are read through
#include "font/FontParser.h"  // Tables (assignment 02): the records of maxp, head, loca and glyf

struct GlyphLocation {
  uint32_t offset = 0;  // from the start of the file
  uint32_t length = 0;  // 0: the glyph has no outline, e.g. space
};

struct GlyphLocations {
  uint16_t numGlyphs = 0;
  bool longFormat = false;            // head.indexToLocFormat: 32-bit offsets
  std::vector<GlyphLocation> glyphs;  // one per glyph id
};

GlyphLocations loadGlyphLocations(ByteReader& reader, const Tables& tables);
