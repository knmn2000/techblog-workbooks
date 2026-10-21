#include "FrameBufferCanvas.h"

#include <stdexcept>

#define STB_IMAGE_WRITE_IMPLEMENTATION
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wall"
#pragma GCC diagnostic ignored "-Wextra"
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#include "stb_image_write.h"
#pragma GCC diagnostic pop

static_assert(sizeof(RGB) == 3, "RGB must be 3 tightly packed bytes for the PNG writer");

FrameBufferCanvas::FrameBufferCanvas(const int width, const int height)
    : width_(width), height_(height), pixels_(static_cast<std::size_t>(width) * height) {}

void FrameBufferCanvas::set(const int x, const int y, const RGB color) {
  // TODO: ignore pixels outside the canvas, then write pixels_[y * width_ + x].
  throw std::logic_error("not implemented: FrameBufferCanvas::set");
}

RGB FrameBufferCanvas::get(const int x, const int y) const {
  return pixels_[static_cast<std::size_t>(y) * width_ + x];
}

void FrameBufferCanvas::drawRect(const int cx, const int cy, const int w, const int h, const RGB color) {
  // TODO: see "Drawing a rectangle" on the problem page.
  throw std::logic_error("not implemented: FrameBufferCanvas::drawRect");
}

void FrameBufferCanvas::drawLine(int ax, int ay, int bx, int by, const int thickness, const RGB color) {
  // TODO: see "Drawing a line" on the problem page.
  throw std::logic_error("not implemented: FrameBufferCanvas::drawLine");
}

void FrameBufferCanvas::writePng(const std::string& path) const {
  if (!stbi_write_png(path.c_str(), width_, height_, 3, pixels_.data(), width_ * 3))
    throw std::runtime_error("cannot write " + path);
}
