// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 18 as `build/solutions/assignment_18
//   <input-file> <output-file>` (its name ends in .exe on Windows). It reads a test input,
//   calls your code and writes the answer to the output file, and the checker compares
//   that answer with the expected one. Run `.\check 18` (`./check.sh 18` on macOS or
//   Linux), or use Run and Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   You also write src/utils/Unicode.h, src/TextRenderer.h, src/TextRenderer.cpp and
//   src/main.cpp in this assignment; each one gives its job at the top.
//   Earlier files you can use: src/font/FontParser.h, src/font/Cmap.h, src/font/Loca.h,
//   src/font/Metrics.h, src/font/CompoundGlyph.h and src/render/NonZero.h.
//   Include them by their path under src/, e.g. #include "utils/Unicode.h".
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

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
    const std::string what = e.what();
    if (what.rfind("not implemented", 0) == 0) {  // a TODO in your project: the checker names it
      std::cerr << what << "\n";
      return 99;
    }
    std::cerr << "error: " << what << "\n";
    return 1;
  }
  return 0;
}
