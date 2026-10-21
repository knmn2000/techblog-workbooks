#pragma once
// Assignment 07: decoding a glyph record from the glyf table.

#include <cstdint>

#include "Glyph.h"
#include "font/ByteReader.h"

// The glyph whose record starts at `offset` (a length of 0 means no outline). A compound
// glyph comes back with its kind and bounds only; see resolveGlyph for its parts.
Glyph readGlyph(ByteReader& reader, uint32_t offset, uint32_t length);
