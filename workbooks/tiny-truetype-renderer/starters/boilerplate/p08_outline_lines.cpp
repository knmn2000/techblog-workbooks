// Checkpoint 08 - Draw an outline with straight lines
//
// Problem:  problems/08-outline-lines.md (also in the web problem book)
// Check:    .\check 08
//
// Only the picture your program writes is checked, so structure this however you
// like, or use another language or library (see README.md). The input/output code
// at the bottom is provided so you can focus on drawOutline().

#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "NotImplemented.h"
#define CANVAS_PNG_IMPLEMENTATION
#include "provided/Canvas.h"  // Canvas: drawLine, drawRect, writePng (checkpoint 06, ready-made)

struct Point {
  double x = 0;  // font units; x grows to the right
  double y = 0;  // font units; y grows upwards
  bool onCurve = false;
};

struct Outline {
  std::vector<int> endPtsOfContours;  // index of the last point of each contour
  std::vector<Point> points;
};

// Where the outline goes: font point (x, y) lands on pixel
// (x0 + scale * x, baseline - scale * y), rounded to the nearest whole pixel.
struct Placement {
  double x0 = 0;
  double baseline = 0;
  double scale = 1;
};

struct Style {
  int lineThickness = 1;  // passed to Canvas::drawLine
  int markerSize = 1;     // width and height of the square drawn at every point
};

// Draws every contour as straight lines between consecutive points, closing it back
// to its first point, then a markerSize square at every point. All in `color`.
void drawOutline(Canvas& canvas, const Outline& outline, const Placement& place, const Style& style,
                 const RGB color) {
  // TODO: see "What to draw" on the problem page.
  throw NotImplemented("drawOutline");
}

// ---- Input/output (provided) -------------------------------------------------

namespace {

std::vector<std::string> wordsAfterKeyword(const std::string& line) {
  std::istringstream in(line);
  std::vector<std::string> words;
  for (std::string w; in >> w;) words.push_back(w);
  if (!words.empty()) words.erase(words.begin());
  return words;
}

}  // namespace

// Usage: p08 <input-file> <output-file.png>
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
    std::unique_ptr<Canvas> canvas;
    Placement place;
    Style style;
    RGB color{255, 255, 255};
    Outline outline;
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      if (!(words >> keyword)) continue;  // blank line
      if (keyword == "canvas") {  // canvas <w> <h>
        int w = 0, h = 0;
        words >> w >> h;
        canvas = std::make_unique<Canvas>(w, h);
      } else if (keyword == "place") {  // place <x0> <baseline> <scale>
        words >> place.x0 >> place.baseline >> place.scale;
      } else if (keyword == "style") {  // style <lineThickness> <markerSize>
        words >> style.lineThickness >> style.markerSize;
      } else if (keyword == "color") {  // color <r> <g> <b>
        int r = 0, g = 0, b = 0;
        words >> r >> g >> b;
        color = RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
      } else if (keyword == "outline") {  // starts a new outline: an `ends` and a `points` line follow
        outline = Outline{};
      } else if (keyword == "ends") {  // ends <e0> <e1> ...
        for (const std::string& w : wordsAfterKeyword(line)) outline.endPtsOfContours.push_back(std::stoi(w));
      } else if (keyword == "points") {  // points <x> <y> <on|off> ... - completes the outline
        const std::vector<std::string> w = wordsAfterKeyword(line);
        for (std::size_t i = 0; i + 2 < w.size(); i += 3) {
          outline.points.push_back(Point{std::stod(w[i]), std::stod(w[i + 1]), w[i + 2] == "on"});
        }
        if (!canvas) throw std::runtime_error("the first line must be `canvas <w> <h>`");
        drawOutline(*canvas, outline, place, style, color);
      } else {
        throw std::runtime_error("unknown line: " + line);
      }
    }
    if (!canvas) throw std::runtime_error("no `canvas` line in the input");
    if (!canvas->writePng(argv[2])) throw std::runtime_error(std::string("cannot write ") + argv[2]);
  } catch (const NotImplemented& e) {
    std::cerr << "not implemented: " << e.what() << "\n";
    return 99;
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
