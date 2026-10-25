// ======================================================================================
// Assignment 08: Draw an outline with straight lines
// Problem: problems/08-outline-lines.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 08 as `build/solutions/assignment_08
//   <input-file> <output-file>` (its name ends in .exe on Windows). It reads a test input,
//   calls your code and writes the answer to the output file, and the checker compares
//   that answer with the expected one. Run `.\check 08` (`./check.sh 08` on macOS or
//   Linux), or use Run and Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   You also write src/render/Placement.h, src/render/Outline.h and src/render/Outline.cpp
//   in this assignment; each one gives its job at the top.
//   Earlier files you can use: src/FrameBufferCanvas.h and src/GlyphComponent.h.
//   Include them by their path under src/, e.g. #include "render/Placement.h".
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <fstream>    // std::ifstream: the input file
#include <iostream>   // std::cerr for usage and error messages
#include <memory>     // std::unique_ptr: the canvas, made at the `canvas` line
#include <sstream>    // std::istringstream: splitting each input line into words
#include <stdexcept>  // std::runtime_error for a missing canvas or an unknown line
#include <string>     // std::string, std::getline, std::stoi and std::stod
#include <vector>     // std::vector<std::string>: the words after a line's keyword

#include "render/Outline.h"  // renderGlyphOutline (assignment 08) and the types it takes

namespace {

std::vector<std::string> wordsAfterKeyword(const std::string& line) {
  std::istringstream in(line);
  std::vector<std::string> words;
  for (std::string w; in >> w;) words.push_back(w);
  if (!words.empty()) words.erase(words.begin());
  return words;
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
    std::unique_ptr<FrameBufferCanvas> canvas;
    Placement place;
    OutlineStyle style;
    RGB color{255, 255, 255};
    GlyphComponent outline;
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      if (!(words >> keyword)) continue;  // blank line
      if (keyword == "canvas") {  // canvas <w> <h>
        int w = 0, h = 0;
        words >> w >> h;
        canvas = std::make_unique<FrameBufferCanvas>(w, h);
      } else if (keyword == "place") {  // place <x0> <baseline> <scale>
        words >> place.x0 >> place.baseline >> place.scale;
      } else if (keyword == "style") {  // style <lineThickness> <markerSize>
        words >> style.lineThickness >> style.markerSize;
      } else if (keyword == "color") {  // color <r> <g> <b>
        int r = 0, g = 0, b = 0;
        words >> r >> g >> b;
        color = RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
      } else if (keyword == "outline") {  // starts a new outline: an `ends` and a `points` line follow
        outline = GlyphComponent{};
      } else if (keyword == "ends") {  // ends <e0> <e1> ...
        for (const std::string& w : wordsAfterKeyword(line)) outline.endPtsOfContours.push_back(std::stoi(w));
      } else if (keyword == "points") {  // points <x> <y> <on|off> ... - completes the outline
        const std::vector<std::string> w = wordsAfterKeyword(line);
        for (std::size_t i = 0; i + 2 < w.size(); i += 3)
          outline.points.push_back(GlyphPoint{std::stod(w[i]), std::stod(w[i + 1]), w[i + 2] == "on"});
        if (!canvas) throw std::runtime_error("the first line must be `canvas <w> <h>`");
        renderGlyphOutline(*canvas, outline, place, style, color);
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
