// Assignment 06 (draw on a framebuffer): draws a test input's points, rectangles and lines.
// The canvas is src/FrameBufferCanvas.

#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>

#include "FrameBufferCanvas.h"

namespace {

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
    std::optional<FrameBufferCanvas> canvas;
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      if (!(words >> keyword)) continue;
      if (keyword == "canvas") {
        int w = 0, h = 0;
        words >> w >> h;
        canvas.emplace(w, h);
        continue;
      }
      if (!canvas) throw std::runtime_error("the first line must be `canvas <w> <h>`");
      if (keyword == "point") {
        int x = 0, y = 0;
        words >> x >> y;
        canvas->set(x, y, readColor(words));
      } else if (keyword == "rect") {
        int cx = 0, cy = 0, w = 0, h = 0;
        words >> cx >> cy >> w >> h;
        canvas->drawRect(cx, cy, w, h, readColor(words));
      } else if (keyword == "line") {
        int ax = 0, ay = 0, bx = 0, by = 0, thickness = 0;
        words >> ax >> ay >> bx >> by >> thickness;
        canvas->drawLine(ax, ay, bx, by, thickness, readColor(words));
      } else {
        throw std::runtime_error("unknown line: " + line);
      }
    }
    if (!canvas) throw std::runtime_error("no `canvas` line in the input");
    canvas->writePng(argv[2]);
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
