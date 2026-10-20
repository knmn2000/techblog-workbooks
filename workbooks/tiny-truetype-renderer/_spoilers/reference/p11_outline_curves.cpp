// Reference solution - checkpoint 11 (draw an outline with curves).
// SPOILERS: try the checkpoint yourself first.

#include <algorithm>
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
// (x0 + scale * x, baseline - scale * y).
struct Placement {
  double x0 = 0;
  double baseline = 0;
  double scale = 1;
};

struct Vec2 {
  double x = 0;
  double y = 0;
};

const RGB ON_CURVE_COLOR{255, 0, 0};   // red: on-curve points from the input
const RGB OFF_CURVE_COLOR{0, 255, 0};  // green: off-curve (control) points from the input
const RGB IMPLIED_COLOR{0, 0, 255};    // blue: on-curve points implied between two off-curve points

namespace {

Vec2 midpoint(const Vec2 a, const Vec2 b) { return {(a.x + b.x) / 2, (a.y + b.y) / 2}; }

// Font units -> pixels, not rounded yet (y flipped: font y grows up, pixel y grows down).
Vec2 toPixel(const Point& p, const Placement& place) {
  return {place.x0 + place.scale * p.x, place.baseline - place.scale * p.y};
}

void line(Canvas& canvas, const Vec2 a, const Vec2 b, const int thickness, const RGB color) {
  canvas.drawLine(static_cast<float>(a.x), static_cast<float>(a.y), static_cast<float>(b.x),
                  static_cast<float>(b.y), thickness, color);
}

void marker(Canvas& canvas, const Vec2 at, const int size, const RGB color) {
  canvas.drawRect(static_cast<int>(std::lround(at.x)), static_cast<int>(std::lround(at.y)), size, size, color);
}

}  // namespace

void drawQuadratic(Canvas& canvas, const Vec2 p0, const Vec2 p1, const Vec2 p2, const int thickness,
                   const RGB color) {
  // The control polygon is never shorter than the curve, so this gives at most
  // about one pixel per piece.
  const double length = std::hypot(p1.x - p0.x, p1.y - p0.y) + std::hypot(p2.x - p1.x, p2.y - p1.y);
  const int pieces = std::max(1, static_cast<int>(std::ceil(length)));
  Vec2 previous = p0;
  for (int i = 1; i <= pieces; ++i) {
    const double t = static_cast<double>(i) / pieces, u = 1 - t;
    const Vec2 next{u * u * p0.x + 2 * u * t * p1.x + t * t * p2.x, u * u * p0.y + 2 * u * t * p1.y + t * t * p2.y};
    line(canvas, previous, next, thickness, color);
    previous = next;
  }
}

void drawOutline(Canvas& canvas, const Outline& outline, const Placement& place, const int lineThickness,
                 const RGB color) {
  struct Marker {
    Vec2 at;
    RGB color;
  };
  std::vector<Marker> markers;
  int first = 0;
  for (const int last : outline.endPtsOfContours) {
    const int n = last - first + 1;
    const auto at = [&](const int k) { return toPixel(outline.points[first + k % n], place); };
    const auto on = [&](const int k) { return outline.points[first + k % n].onCurve; };

    // Start from an on-curve point. With none, start from the implied on-curve point
    // between the last and the first point; every point is then visited once.
    int k = 0;
    while (k < n && !on(k)) ++k;
    Vec2 current;
    int stop;
    if (k < n) {
      current = at(k);
      stop = k + n + 1;  // ends with the start point again, which closes the contour
      ++k;
    } else {
      current = midpoint(at(n - 1), at(0));
      k = 0;
      stop = n;
    }
    while (k < stop) {
      if (on(k)) {
        line(canvas, current, at(k), lineThickness, color);
        current = at(k);
        ++k;
      } else if (on(k + 1)) {  // off, on: one curve, and the on-curve point is used up
        drawQuadratic(canvas, current, at(k), at(k + 1), lineThickness, color);
        current = at(k + 1);
        k += 2;
      } else {  // off, off: the curve ends at the implied point halfway between them
        const Vec2 implied = midpoint(at(k), at(k + 1));
        drawQuadratic(canvas, current, at(k), implied, lineThickness, color);
        current = implied;
        ++k;
      }
    }

    for (int i = 0; i < n; ++i) {
      markers.push_back({at(i), on(i) ? ON_CURVE_COLOR : OFF_CURVE_COLOR});
      if (!on(i) && !on(i + 1)) markers.push_back({midpoint(at(i), at(i + 1)), IMPLIED_COLOR});
    }
    first = last + 1;
  }
  for (const Marker& m : markers) marker(canvas, m.at, 2 * lineThickness, m.color);  // on top of every line
}

// ---- Input/output (same as the starter) --------------------------------------

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
    std::unique_ptr<Canvas> canvas;
    Placement place;
    int lineThickness = 1;
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
      } else if (keyword == "style") {  // style <lineThickness>
        words >> lineThickness;
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
        drawOutline(*canvas, outline, place, lineThickness, color);
      } else {
        throw std::runtime_error("unknown line: " + line);
      }
    }
    if (!canvas) throw std::runtime_error("no `canvas` line in the input");
    if (!canvas->writePng(argv[2])) throw std::runtime_error(std::string("cannot write ") + argv[2]);
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
