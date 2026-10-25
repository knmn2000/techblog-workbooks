#pragma once
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
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>
#include <map>
#include <string>
#include <unordered_map>

#include "FrameBufferCanvas.h"
#include "font/FontParser.h"
#include "font/Loca.h"
#include "font/Metrics.h"

class TextRenderer {
 public:
  explicit TextRenderer(const std::string& fontPath);

  // Draws UTF-8 text from x = penX with its baseline at y = baseline, `scale` pixels per
  // font unit, each glyph filled by the non-zero rule. Returns the pen position after it.
  double drawText(FrameBufferCanvas& canvas, const std::string& text, double penX, double baseline,
                  double scale, RGB color);

  // How far drawText would move the pen, in pixels.
  [[nodiscard]] double measureText(const std::string& text, double scale) const;

  [[nodiscard]] const HorizontalMetrics& metrics() const { return metrics_; }

 private:
  [[nodiscard]] uint32_t glyphFor(uint32_t codePoint) const;  // 0, the "missing" glyph, if none
  [[nodiscard]] double advance(uint32_t glyphId) const;

  FontParser parser_;
  std::unordered_map<uint32_t, uint32_t> glyphCodes_;
  std::map<uint32_t, GlyphLocation> locations_;
  HorizontalMetrics metrics_;
};
