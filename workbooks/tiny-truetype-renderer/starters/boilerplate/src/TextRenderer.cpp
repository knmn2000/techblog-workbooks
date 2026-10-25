// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This class holds the whole pipeline. It loads a font's tables once, then maps each
//   character of a line of text to its glyph, fills the glyph by the non-zero rule and
//   moves the pen on by its advance. The checker's program and `main.cpp` both draw
//   through it.
//
// Your job:
//   Implement the class by calling your earlier work: load the cmap (assignment 03), the
//   glyph locations (04) and the advance widths (05) once, when you open the font. To
//   draw, decode the text, then for each code point find its glyph (glyph 0 if the font
//   has none), fill each of its outlines from your `font/CompoundGlyph` with your non-zero
//   fill, and move the pen by its advance times the scale. The Boilerplate gives you the
//   declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "TextRenderer.h"  // the class this file implements

#include <stdexcept>  // std::logic_error: the "not implemented" stubs

#include "font/Cmap.h"           // loadUnicodeToGlyphCodeMap (assignment 03): the cmap
#include "font/CompoundGlyph.h"  // resolveGlyph (assignment 09): any glyph as simple outlines
#include "render/NonZero.h"      // renderGlyphByNonZero (assignments 16, 17) for each outline
#include "utils/Unicode.h"       // utf8ToCodepoints (assignment 18): decoding the text

TextRenderer::TextRenderer(const std::string& fontPath) : parser_(fontPath) {
  // TODO: load the cmap (03), the glyph locations (04) and the metrics (05) once, here.
  throw std::logic_error("not implemented: TextRenderer::TextRenderer");
}

double TextRenderer::drawText(FrameBufferCanvas& canvas, const std::string& text, double penX,
                              const double baseline, const double scale, const RGB color) {
  // TODO: for each code point: its glyph, resolved into simple parts (09), each filled by the
  // non-zero rule (17), then the pen moved by the glyph's advance (see the problem page).
  throw std::logic_error("not implemented: TextRenderer::drawText");
}

double TextRenderer::measureText(const std::string& text, const double scale) const {
  // TODO: the sum of the advances, in pixels.
  throw std::logic_error("not implemented: TextRenderer::measureText");
}

uint32_t TextRenderer::glyphFor(const uint32_t codePoint) const {
  // TODO: the cmap's glyph, or 0 when the font has none.
  throw std::logic_error("not implemented: TextRenderer::glyphFor");
}

double TextRenderer::advance(const uint32_t glyphId) const {
  // TODO: the glyph's advance width, in font units.
  throw std::logic_error("not implemented: TextRenderer::advance");
}
