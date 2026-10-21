#pragma once
// ======================================================================================
// Assignment 03: Map characters to glyphs (cmap format 12)
// Problem: problems/03-cmap.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The `cmap` table: which glyph draws each character, read from the format 12 subtable
//   for the full Unicode range. Later, assignment 18 looks up every character of a line of
//   text here.
//
// Your job:
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
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
