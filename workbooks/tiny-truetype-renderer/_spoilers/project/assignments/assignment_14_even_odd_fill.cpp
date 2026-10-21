// Assignment 14 (fill a glyph, even-odd rule): fills each outline in a test input.
// The filling is src/render/EvenOdd, built on src/render/Scanline.

#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "render/EvenOdd.h"

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
    std::unique_ptr<FrameBufferCanvas> canvas;
    Placement place;
    RGB color{255, 255, 255};
    std::vector<GlyphComponent> outlines;  // each one filled on its own
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      if (!(words >> keyword)) continue;
      if (keyword == "canvas") {  // canvas <w> <h>
        int w = 0, h = 0;
        words >> w >> h;
        canvas = std::make_unique<FrameBufferCanvas>(w, h);
      } else if (keyword == "place") {  // place <x0> <baseline> <scale>
        words >> place.x0 >> place.baseline >> place.scale;
      } else if (keyword == "color") {  // color <r> <g> <b>
        int r = 0, g = 0, b = 0;
        words >> r >> g >> b;
        color = RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
      } else if (keyword == "outline") {  // then `ends ...` and `points x y on|off ...`
        outlines.emplace_back();
      } else if (keyword == "ends" && !outlines.empty()) {
        for (int e; words >> e;) outlines.back().endPtsOfContours.push_back(e);
      } else if (keyword == "points" && !outlines.empty()) {
        GlyphPoint p;
        for (std::string on; words >> p.x >> p.y >> on;) {
          p.onCurve = on == "on";
          outlines.back().points.push_back(p);
        }
      }
    }
    if (!canvas) throw std::runtime_error("no `canvas` line in the input");
    for (const GlyphComponent& outline : outlines) renderGlyphByEvenOdd(*canvas, outline, place, color);
    canvas->writePng(argv[2]);
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
