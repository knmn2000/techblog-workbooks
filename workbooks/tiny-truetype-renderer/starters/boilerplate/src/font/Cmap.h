#pragma once
// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Characters map to glyphs through the `cmap` table, and this is your reader for it.
//   Only the format 12 subtable stored for platform 0, encoding 4 is needed, which covers
//   the full Unicode range. Assignment 18 looks up every character of a line of text in
//   the result.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>        // uint32_t: code points and glyph ids
#include <stdexcept>      // std::runtime_error, the base of UnsupportedCmap
#include <unordered_map>  // std::unordered_map: the map from code point to glyph id

#include "font/ByteReader.h"  // ByteReader (assignment 01): the reader cmap is read through
#include "font/FontParser.h"  // Tables (assignment 02): the record that gives cmap's offset

// The font has no format 12 subtable for the full Unicode range (platform 0, encoding 4).
struct UnsupportedCmap : std::runtime_error {
  using std::runtime_error::runtime_error;
};

// Code point -> glyph id, for every character the font maps.
std::unordered_map<uint32_t, uint32_t> loadUnicodeToGlyphCodeMap(ByteReader& reader, const Tables& tables);
