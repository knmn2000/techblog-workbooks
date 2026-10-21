// ======================================================================================
// Assignment 06: Draw on a framebuffer
// Problem: problems/06-canvas.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This is the program the checker runs for assignment 06, as
//   `build/solutions/assignment_06.exe <input-file> <output-file>`: it reads a test input,
//   calls your code and writes the answer to the output file. Only that output is checked.
//   Check it with `.\check 06`, or Run and Submit in the book.
//
// Your job:
//   In the Boilerplate this program is already written: it reads the input, calls your
//   code and writes the answer. Your work is in this assignment's other files, where it
//   says TODO.
//
// The other files of this assignment:
//   This assignment also has you write src/FrameBufferCanvas.h and
//   src/FrameBufferCanvas.cpp; each says its job at the top.
//   Include them by their path under src/, e.g. #include "FrameBufferCanvas.h".
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

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
