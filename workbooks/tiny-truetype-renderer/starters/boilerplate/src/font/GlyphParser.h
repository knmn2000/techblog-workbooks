#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The parser decodes one glyph record from the glyf table into the types in `Glyph.h`:
//   the header of any glyph, and the contours and points of a simple one. In assignment 09
//   you call it for every simple glyph inside a compound glyph.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>

#include "Glyph.h"
#include "font/ByteReader.h"

// The glyph whose record starts at `offset` (a length of 0 means no outline). A compound
// glyph comes back with its kind and bounds only; see resolveGlyph for its parts.
Glyph readGlyph(ByteReader& reader, uint32_t offset, uint32_t length);
