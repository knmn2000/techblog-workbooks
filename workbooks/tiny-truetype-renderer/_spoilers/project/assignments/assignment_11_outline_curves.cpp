// Assignment 11 (draw an outline with curves): draws a test input's outlines, curves included.
// The drawing is src/render/Outline, using the curve maths in src/utils/Geometry.h.

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
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
