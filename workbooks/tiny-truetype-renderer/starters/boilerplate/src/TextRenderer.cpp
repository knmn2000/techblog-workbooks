#include "TextRenderer.h"

#include <stdexcept>

#include "font/Cmap.h"
#include "font/CompoundGlyph.h"
#include "render/NonZero.h"
#include "utils/Unicode.h"

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
