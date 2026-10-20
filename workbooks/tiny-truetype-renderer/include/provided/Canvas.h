#pragma once
// Provided, optional: an RGB framebuffer with checkpoint 06's drawing operations
// and PNG output. If you've done checkpoint 06, you can use your own instead.
//
// One source file per program must `#define CANVAS_PNG_IMPLEMENTATION` before
// including this header (the starters do), so the PNG writer is compiled once.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <string>
#include <utility>
#include <vector>

#ifdef CANVAS_PNG_IMPLEMENTATION
#define STB_IMAGE_WRITE_IMPLEMENTATION
#endif
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wall"
#pragma GCC diagnostic ignored "-Wextra"
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#include "stb_image_write.h"
#pragma GCC diagnostic pop

struct RGB {
  uint8_t r = 0, g = 0, b = 0;
  bool operator==(const RGB&) const = default;
};
static_assert(sizeof(RGB) == 3, "RGB must be 3 tightly packed bytes for the PNG writer");

class Canvas {
public:
  Canvas(const int width, const int height)
      : width_(width), height_(height), pixels_(static_cast<std::size_t>(width) * height) {}

  [[nodiscard]] int width() const { return width_; }
  [[nodiscard]] int height() const { return height_; }

  // Pixels outside the canvas are ignored.
  void set(const int x, const int y, const RGB color) {
    if (x < 0 || y < 0 || x >= width_ || y >= height_) return;
    pixels_[static_cast<std::size_t>(y) * width_ + x] = color;
  }

  [[nodiscard]] RGB get(const int x, const int y) const {
    return pixels_[static_cast<std::size_t>(y) * width_ + x];
  }

  // A w x h rectangle centred on (cx, cy): columns cx - w/2 ... cx - w/2 + w - 1,
  // rows likewise (w/2 rounds down).
  void drawRect(const int cx, const int cy, const int w, const int h, const RGB color) {
    const int left = cx - w / 2, top = cy - h / 2;
    for (int y = std::max(top, 0); y < std::min(top + h, height_); ++y) {
      for (int x = std::max(left, 0); x < std::min(left + w, width_); ++x) set(x, y, color);
    }
  }

  // A line from (ax, ay) to (bx, by), both ends included. Every step stamps a
  // thickness x thickness square centred on the line.
  void drawLine(int ax, int ay, int bx, int by, const int thickness, const RGB color) {
    const bool steep = std::abs(by - ay) > std::abs(bx - ax);
    if (steep) {
      std::swap(ax, ay);
      std::swap(bx, by);
    }
    if (ax > bx) {
      std::swap(ax, bx);
      std::swap(ay, by);
    }
    const float slope = bx == ax ? 0.0f : static_cast<float>(by - ay) / static_cast<float>(bx - ax);
    for (int x = ax; x <= bx; ++x) {
      const int y = static_cast<int>(std::lround(ay + slope * static_cast<float>(x - ax)));
      if (steep) drawRect(y, x, thickness, thickness, color);
      else drawRect(x, y, thickness, thickness, color);
    }
  }

  // The same, from floating-point coordinates (float or double) rounded to the nearest pixel.
  void drawLine(const double ax, const double ay, const double bx, const double by,
                const int thickness, const RGB color) {
    drawLine(static_cast<int>(std::lround(ax)), static_cast<int>(std::lround(ay)),
             static_cast<int>(std::lround(bx)), static_cast<int>(std::lround(by)), thickness, color);
  }

  // Fills columns x0 ... x1 (inclusive) of row y. Nothing when x0 > x1, so an empty span
  // stays empty. Columns outside the canvas are skipped.
  void drawSpan(const int y, const int x0, const int x1, const RGB color) {
    if (y < 0 || y >= height_) return;
    for (int x = std::max(x0, 0); x <= std::min(x1, width_ - 1); ++x) set(x, y, color);
  }

  bool writePng(const std::string& path) const {
    return stbi_write_png(path.c_str(), width_, height_, 3, pixels_.data(), width_ * 3) != 0;
  }

private:
  int width_;
  int height_;
  std::vector<RGB> pixels_;
};
