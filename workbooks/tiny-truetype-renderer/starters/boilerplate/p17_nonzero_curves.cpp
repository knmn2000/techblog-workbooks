// Checkpoint 17 - Fill a glyph: non-zero rule
//
// Problem:  problems/17-nonzero-curves.md (also in the web problem book)
// Check:    .\check 17
//
// Only the picture your program writes is checked, so structure this however you
// like, or use another language or library (see README.md). The input/output code at
// the bottom is provided so you can focus on fillOutline().

#include <cmath>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#define CANVAS_PNG_IMPLEMENTATION
#include "NotImplemented.h"
#include "provided/Canvas.h"  // Canvas: set(x, y, rgb), drawSpan(row, x0, x1, rgb) fills x0..x1 inclusive
                              // (nothing if x0 > x1), writePng(path)

struct Point {
  double x = 0;
  double y = 0;
  bool onCurve = true;
};

// One outline in glyph coordinates (y up), as checkpoints 07 and 09 produce it.
struct Outline {
  std::vector<int> endPtsOfContours;
  std::vector<Point> points;
};

// Glyph (x, y) is drawn at pixel (x0 + scale * x, baseline - scale * y).
struct Placement {
  double x0 = 0;
  double baseline = 0;
  double scale = 1;
};

// Fills every pixel whose centre is inside `outline` by the non-zero winding rule.
void fillOutline(Canvas& canvas, const Outline& outline, const Placement& place, const RGB color) {
  // TODO: scanline fill (see the problem page).
  throw NotImplemented("fillOutline");
}

// ---- Input/output (provided) -------------------------------------------------

// Usage: p17 <input-file> <output-png>
int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "usage: " << argv[0] << " <input-file> <output-png>\n";
    return 2;
  }
  std::ifstream input(argv[1]);
  if (!input) {
    std::cerr << "cannot open " << argv[1] << "\n";
    return 2;
  }
  try {
    int width = 0, height = 0;
    Placement place;
    RGB color{255, 255, 255};
    std::vector<Outline> outlines;
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "canvas") {  // canvas <width> <height>
        words >> width >> height;
      } else if (keyword == "place") {  // place <x0> <baseline> <scale>
        words >> place.x0 >> place.baseline >> place.scale;
      } else if (keyword == "color") {  // color <r> <g> <b>
        int r, g, b;
        words >> r >> g >> b;
        color = RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
      } else if (keyword == "outline") {
        outlines.emplace_back();
      } else if (keyword == "ends") {  // ends <e0> <e1> ...
        for (int e; words >> e;) outlines.back().endPtsOfContours.push_back(e);
      } else if (keyword == "points") {  // points <x> <y> <on|off> ...
        Point p;
        std::string on;
        while (words >> p.x >> p.y >> on) {
          p.onCurve = on == "on";
          outlines.back().points.push_back(p);
        }
      }
    }
    Canvas canvas(width, height);  // black to begin with
    for (const Outline& outline : outlines) fillOutline(canvas, outline, place, color);
    if (!canvas.writePng(argv[2])) throw std::runtime_error("cannot write the PNG");
  } catch (const NotImplemented& e) {
    std::cerr << "not implemented: " << e.what() << "\n";
    return 99;
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
