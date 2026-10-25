#pragma once
// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   One glyph record from the `glyf` table goes in and a glyph from `Glyph.h` comes out:
//   the header of any glyph, plus contours and points when it is simple. Assignment 09
//   calls it for each simple glyph inside a compound glyph.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>  // uint32_t for the record's offset and length

#include "Glyph.h"            // Glyph (assignment 07): what readGlyph returns
#include "font/ByteReader.h"  // ByteReader (assignment 01): big-endian reads from the font

// The glyph whose record starts at `offset` (a length of 0 means no outline). A compound
// glyph comes back with its kind and bounds only; see resolveGlyph for its parts.
Glyph readGlyph(ByteReader& reader, uint32_t offset, uint32_t length);
