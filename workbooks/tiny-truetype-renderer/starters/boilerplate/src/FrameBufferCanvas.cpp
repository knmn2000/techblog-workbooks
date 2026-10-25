// ======================================================================================
// Assignment 06: Draw on a framebuffer
// Problem: problems/06-canvas.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The canvas holds a picture in memory, one colour per pixel. It can paint one pixel,
//   fill a rectangle, draw a thick line and save the picture as a PNG. You draw every
//   later picture on it: outlines in 08 and 11, filled glyphs in 14, 16 and 17, and a line
//   of text in 18.
//
// Your job:
//   Implement the canvas operations as "Painting one pixel", "Drawing a rectangle" and
//   "Drawing a line" describe. Painting a pixel ignores coordinates outside the picture, a
//   rectangle clips its loops to the canvas, and a line stamps a square at every step.
//   Save the pixels as a PNG with `stbi_write_png` or as a binary PPM. The Boilerplate
//   gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "FrameBufferCanvas.h"  // FrameBufferCanvas (assignment 06), whose functions this file defines

#include <stdexcept>  // std::runtime_error if the PNG can't be written; std::logic_error

#define STB_IMAGE_WRITE_IMPLEMENTATION
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wall"
#pragma GCC diagnostic ignored "-Wextra"
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#include "stb_image_write.h"  // stbi_write_png, its code compiled here (the #define above)
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
