#include "FrameBufferCanvas.h"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <stdexcept>
#include <utility>

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
  if (x < 0 || y < 0 || x >= width_ || y >= height_) return;
  pixels_[static_cast<std::size_t>(y) * width_ + x] = color;
}

RGB FrameBufferCanvas::get(const int x, const int y) const {
  return pixels_[static_cast<std::size_t>(y) * width_ + x];
}

void FrameBufferCanvas::drawRect(const int cx, const int cy, const int w, const int h, const RGB color) {
  const int left = cx - w / 2, top = cy - h / 2;
  // Clip the ranges first, so a huge or far-away rectangle costs nothing.
  for (int y = std::max(top, 0); y < std::min(top + h, height_); ++y) {
    for (int x = std::max(left, 0); x < std::min(left + w, width_); ++x) set(x, y, color);
  }
}

void FrameBufferCanvas::drawLine(int ax, int ay, int bx, int by, const int thickness, const RGB color) {
  // Step along the longer axis, so consecutive squares never leave a gap.
  const bool steep = std::abs(by - ay) > std::abs(bx - ax);
  if (steep) {
    std::swap(ax, ay);
    std::swap(bx, by);
  }
  if (ax > bx) {
    std::swap(ax, bx);
    std::swap(ay, by);
  }
  const double slope = bx == ax ? 0.0 : static_cast<double>(by - ay) / (bx - ax);
  for (int x = ax; x <= bx; ++x) {
    const int y = static_cast<int>(std::lround(ay + slope * (x - ax)));
    if (steep) drawRect(y, x, thickness, thickness, color);
    else drawRect(x, y, thickness, thickness, color);
  }
}

void FrameBufferCanvas::writePng(const std::string& path) const {
  if (!stbi_write_png(path.c_str(), width_, height_, 3, pixels_.data(), width_ * 3))
    throw std::runtime_error("cannot write " + path);
}
