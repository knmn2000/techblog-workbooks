#pragma once
// Assignment 03: which glyph draws each character (the cmap table, format 12).

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
