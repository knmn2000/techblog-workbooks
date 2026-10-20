// Checkpoint 06 - Draw on a framebuffer
//
// Problem:  problems/06-canvas.md (also in the web problem book)
// Check:    .\check 06
//
// Only the picture your program writes is checked, so structure this however you
// like, or use another language or library (see README.md). The input/output code
// at the bottom is provided so you can focus on set(), drawRect() and drawLine().
//
// Later checkpoints use include/provided/Canvas.h, a ready-made version of what you
// build here. Don't include it in this one: writing it is the exercise.

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

#include "NotImplemented.h"

struct RGB {
  uint8_t r = 0, g = 0, b = 0;
};

// A width x height picture. Pixel (x, y) is pixels[y * width + x]: (0, 0) is the
// top-left corner, x grows to the right and y grows downwards. Every pixel starts black.
struct FrameBuffer {
  int width = 0;
  int height = 0;
  std::vector<RGB> pixels;

  FrameBuffer(const int w, const int h)
      : width(w), height(h), pixels(static_cast<std::size_t>(w) * h) {}

  // Paints pixel (x, y). A pixel outside the picture is ignored.
  void set(int x, int y, RGB color) {
    // TODO: bounds check, then write pixels[y * width + x].
    throw NotImplemented("FrameBuffer::set");
  }

  // A w x h rectangle centred on (cx, cy): columns cx - w/2 ... cx - w/2 + w - 1
  // (w/2 rounds down), rows cy - h/2 ... cy - h/2 + h - 1. Parts outside are ignored.
  void drawRect(int cx, int cy, int w, int h, RGB color) {
    // TODO
    throw NotImplemented("FrameBuffer::drawRect");
  }

  // A line from (ax, ay) to (bx, by), both ends included: one thickness x thickness
  // square, centred like drawRect, for every step along the longer axis.
  void drawLine(int ax, int ay, int bx, int by, int thickness, RGB color) {
    // TODO: see "Drawing a line" on the problem page.
    throw NotImplemented("FrameBuffer::drawLine");
  }
};

// ---- Input/output (provided) -------------------------------------------------

// stb_image_write (third_party/stb) encodes the PNG. This file compiles its code.
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
  // 3 bytes per pixel (RGB), rows from the top down, width * 3 bytes per row.
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

// Usage: p06 <input-file> <output-file.png>
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
      if (!(words >> keyword)) continue;  // blank line
      if (keyword == "canvas") {  // canvas <w> <h>
        int w = 0, h = 0;
        words >> w >> h;
        fb.emplace(w, h);
        continue;
      }
      if (!fb) throw std::runtime_error("the first line must be `canvas <w> <h>`");
      if (keyword == "point") {  // point <x> <y> <r> <g> <b>
        int x = 0, y = 0;
        words >> x >> y;
        fb->set(x, y, readColor(words));
      } else if (keyword == "rect") {  // rect <cx> <cy> <w> <h> <r> <g> <b>
        int cx = 0, cy = 0, w = 0, h = 0;
        words >> cx >> cy >> w >> h;
        fb->drawRect(cx, cy, w, h, readColor(words));
      } else if (keyword == "line") {  // line <ax> <ay> <bx> <by> <thickness> <r> <g> <b>
        int ax = 0, ay = 0, bx = 0, by = 0, thickness = 0;
        words >> ax >> ay >> bx >> by >> thickness;
        fb->drawLine(ax, ay, bx, by, thickness, readColor(words));
      } else {
        throw std::runtime_error("unknown line: " + line);
      }
    }
    if (!fb) throw std::runtime_error("no `canvas` line in the input");
    writePng(*fb, argv[2]);
  } catch (const NotImplemented& e) {
    std::cerr << "not implemented: " << e.what() << "\n";
    return 99;
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
