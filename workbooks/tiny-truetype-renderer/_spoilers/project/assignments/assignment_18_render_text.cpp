// Assignment 18 (render a line of text): draws the text lines of a test input.
// The drawing is src/TextRenderer, which puts every earlier step together; src/main.cpp is
// the same thing as a command-line program.

#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>

#include "TextRenderer.h"

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
    std::unique_ptr<TextRenderer> font;
    std::unique_ptr<FrameBufferCanvas> canvas;
    double penX = 0, baseline = 0, scale = 1;
    RGB color{255, 255, 255};
    for (std::string line; std::getline(input, line);) {
      if (!line.empty() && line.back() == '\r') line.pop_back();
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") {  // font <path>
        std::string path;
        words >> path;
        font = std::make_unique<TextRenderer>(path);
      } else if (keyword == "canvas") {  // canvas <w> <h>
        int w = 0, h = 0;
        words >> w >> h;
        canvas = std::make_unique<FrameBufferCanvas>(w, h);
      } else if (keyword == "pen") {  // pen <x> <baseline> <scale>
        words >> penX >> baseline >> scale;
      } else if (keyword == "color") {  // color <r> <g> <b>
        int r = 0, g = 0, b = 0;
        words >> r >> g >> b;
        color = RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
      } else if (keyword == "text") {  // text <the rest of the line, UTF-8>
        if (!font || !canvas) throw std::runtime_error("`text` needs a `font` and a `canvas` line first");
        penX = font->drawText(*canvas, line.size() > 5 ? line.substr(5) : "", penX, baseline, scale, color);
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
