// Reference solution - checkpoint 06 (draw on a framebuffer).
// SPOILERS: try the checkpoint yourself first.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

struct RGB {
  uint8_t r = 0, g = 0, b = 0;
};

struct FrameBuffer {
  int width = 0;
  int height = 0;
  std::vector<RGB> pixels;

  FrameBuffer(const int w, const int h)
      : width(w), height(h), pixels(static_cast<std::size_t>(w) * h) {}

  void set(const int x, const int y, const RGB color) {
    if (x < 0 || y < 0 || x >= width || y >= height) return;
    pixels[static_cast<std::size_t>(y) * width + x] = color;
  }

  void drawRect(const int cx, const int cy, const int w, const int h, const RGB color) {
    const int left = cx - w / 2, top = cy - h / 2;
    // Clip the ranges first, so a huge or far-away rectangle costs nothing.
    for (int y = std::max(top, 0); y < std::min(top + h, height); ++y) {
      for (int x = std::max(left, 0); x < std::min(left + w, width); ++x) set(x, y, color);
    }
  }

  void drawLine(int ax, int ay, int bx, int by, const int thickness, const RGB color) {
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
};

// ---- Input/output (same as the starter) --------------------------------------

#define STB_IMAGE_WRITE_IMPLEMENTATION
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wall"
#pragma GCC diagnostic ignored "-Wextra"
#pragma GCC diagnostic ignored "-Wmissing-field-initializers"
#include "stb_image_write.h"
#pragma GCC diagnostic pop

namespace {

static_assert(sizeof(RGB) == 3, "RGB must be 3 tightly packed bytes for the PNG writer");

void writePng(const FrameBuffer& fb, const std::string& path) {
  if (!stbi_write_png(path.c_str(), fb.width, fb.height, 3, fb.pixels.data(), fb.width * 3)) {
    throw std::runtime_error("cannot write " + path);
  }
}

RGB readColor(std::istream& words) {
  int r = 0, g = 0, b = 0;
  words >> r >> g >> b;
  return RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
}

}  // namespace

int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "usage: " << argv[0] << " <input-file> <output-file.png>\n";
    return 2;
  }
  std::ifstream input(argv[1]);
  if (!input) {
    std::cerr << "cannot open " << argv[1] << "\n";
    return 2;
  }
  try {
    std::optional<FrameBuffer> fb;
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      if (!(words >> keyword)) continue;
      if (keyword == "canvas") {
        int w = 0, h = 0;
        words >> w >> h;
        fb.emplace(w, h);
        continue;
      }
      if (!fb) throw std::runtime_error("the first line must be `canvas <w> <h>`");
      if (keyword == "point") {
        int x = 0, y = 0;
        words >> x >> y;
        fb->set(x, y, readColor(words));
      } else if (keyword == "rect") {
        int cx = 0, cy = 0, w = 0, h = 0;
        words >> cx >> cy >> w >> h;
        fb->drawRect(cx, cy, w, h, readColor(words));
      } else if (keyword == "line") {
        int ax = 0, ay = 0, bx = 0, by = 0, thickness = 0;
        words >> ax >> ay >> bx >> by >> thickness;
        fb->drawLine(ax, ay, bx, by, thickness, readColor(words));
      } else {
        throw std::runtime_error("unknown line: " + line);
      }
    }
    if (!fb) throw std::runtime_error("no `canvas` line in the input");
    writePng(*fb, argv[2]);
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
