// ======================================================================================
// Assignment 11: Draw an outline with curves
// Problem: problems/11-outline-curves.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 11 as `build/solutions/assignment_11
//   <input-file> <output-file>` (its name ends in .exe on Windows). It reads a test input,
//   calls your code and writes the answer to the output file, and the checker compares
//   that answer with the expected one. Run `.\check 11` (`./check.sh 11` on macOS or
//   Linux), or use Run and Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   It adds to src/render/Outline.h, which you started earlier: Declare a second drawing
//   function next to your straight-line one from assignment 08. It takes the canvas, an
//   outline, its placement, a line thickness and a colour, and draws the outline with its
//   curves. The Boilerplate's `Outline.h` already declares it as `renderGlyphCurves`; if
//   you wrote the header your own way, add the declaration now.
//   It adds to src/render/Outline.cpp, which you started earlier: Implement the curve
//   drawing. Walk each contour from an on-curve point and turn its points into straight
//   lines and quadratic curves, adding an implied on-curve point between two off-curve
//   points. Draw each curve as short lines with your curve function from
//   `utils/Geometry.h`. Draw the red, green and blue markers after all the lines of the
//   outline.
//   Earlier files you can use: src/utils/Geometry.h.
//   Include them by their path under src/, e.g. #include "render/Outline.h".
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
#include <vector>

#include "render/Outline.h"

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
    int lineThickness = 1;
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
      } else if (keyword == "style") {  // style <lineThickness>
        words >> lineThickness;
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
        renderGlyphCurves(*canvas, outline, place, lineThickness, color);
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
