#pragma once
// Checkpoint 09: compound glyphs, made of other glyphs that are moved, scaled or rotated.

#include <cstdint>
#include <map>
#include <vector>

#include "GlyphComponent.h"
#include "font/ByteReader.h"
#include "font/Loca.h"

// The simple glyphs `glyphId` is drawn with, every point in the glyph's own coordinates
// (font units). A simple glyph gives itself; an empty one gives nothing.
std::vector<GlyphComponent> resolveGlyph(ByteReader& reader, const std::map<uint32_t, GlyphLocation>& locations,
                                         uint32_t glyphId);
