#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Decoding one glyph record from the glyf table into the types in `Glyph.h`: the header
//   of every glyph, and the contours and points of a simple one. Assignment 09 calls it
//   for every simple glyph a compound glyph is made of.
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

#include "Glyph.h"
#include "font/ByteReader.h"

// The glyph whose record starts at `offset` (a length of 0 means no outline). A compound
// glyph comes back with its kind and bounds only; see resolveGlyph for its parts.
Glyph readGlyph(ByteReader& reader, uint32_t offset, uint32_t length);
