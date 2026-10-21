#pragma once
// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This header declares your reader for the `cmap` table, the font's map from each
//   character to the glyph that draws it. It reads the format 12 subtable, which covers
//   the full Unicode range, and assignment 18 looks up every character of a line of text
//   in the result.
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
#include <stdexcept>
#include <unordered_map>

#include "font/ByteReader.h"
#include "font/FontParser.h"

// The font has no format 12 subtable for the full Unicode range (platform 0, encoding 4).
struct UnsupportedCmap : std::runtime_error {
  using std::runtime_error::runtime_error;
};

// Code point -> glyph id, for every character the font maps.
std::unordered_map<uint32_t, uint32_t> loadUnicodeToGlyphCodeMap(ByteReader& reader, const Tables& tables);
