#pragma once
// Assignment 18: a font ready to draw lines of text, built from the earlier steps.

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
