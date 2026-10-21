#include "TextRenderer.h"

#include "font/Cmap.h"
#include "font/CompoundGlyph.h"
#include "render/NonZero.h"
#include "utils/Unicode.h"

TextRenderer::TextRenderer(const std::string& fontPath)
    : parser_(fontPath),
      glyphCodes_(loadUnicodeToGlyphCodeMap(parser_.reader(), parser_.tables())),
      metrics_(loadHorizontalMetrics(parser_.reader(), parser_.tables())) {
  const GlyphLocations loca = loadGlyphLocations(parser_.reader(), parser_.tables());
  for (uint32_t id = 0; id < loca.glyphs.size(); ++id) locations_[id] = loca.glyphs[id];
}

double TextRenderer::drawText(FrameBufferCanvas& canvas, const std::string& text, double penX,
                              const double baseline, const double scale, const RGB color) {
  for (const uint32_t cp : utf8ToCodepoints(text)) {
    const uint32_t id = glyphFor(cp);
    // A compound glyph's parts are filled one by one.
    for (const GlyphComponent& part : resolveGlyph(parser_.reader(), locations_, id))
      renderGlyphByNonZero(canvas, part, Placement{penX, baseline, scale}, color);
    penX += advance(id) * scale;
  }
  return penX;
}

double TextRenderer::measureText(const std::string& text, const double scale) const {
  double width = 0;
  for (const uint32_t cp : utf8ToCodepoints(text)) width += advance(glyphFor(cp)) * scale;
  return width;
}

uint32_t TextRenderer::glyphFor(const uint32_t codePoint) const {
  const auto it = glyphCodes_.find(codePoint);
  return it == glyphCodes_.end() ? 0 : it->second;
}

double TextRenderer::advance(const uint32_t glyphId) const {
  return glyphId < metrics_.glyphs.size() ? metrics_.glyphs[glyphId].advanceWidth : 0;
}
