// Checkpoint 10 - Lerp and quadratic Bezier curves
//
// Problem:  problems/10-bezier.md (also in the web problem book)
// Check:    .\check 10
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on lerp() and bezier().

#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

#include "NotImplemented.h"

struct Vec2 {
  double x = 0;
  double y = 0;
};

// Optional helpers: add, subtract, scale. (glm::dvec2 from third_party/ works too.)
Vec2 operator+(const Vec2 a, const Vec2 b) { return {a.x + b.x, a.y + b.y}; }
Vec2 operator-(const Vec2 a, const Vec2 b) { return {a.x - b.x, a.y - b.y}; }
Vec2 operator*(const Vec2 v, const double s) { return {v.x * s, v.y * s}; }

// The point a fraction t of the way from a to b (0 <= t <= 1).
Vec2 lerp(const Vec2 a, const Vec2 b, const double t) {
  // TODO: see "Linear interpolation" on the problem page.
  throw NotImplemented("lerp");
}

// The point at parameter t on the quadratic Bezier curve that starts at a,
// is pulled toward the control point b, and ends at c (0 <= t <= 1).
Vec2 bezier(const Vec2 a, const Vec2 b, const Vec2 c, const double t) {
  // TODO: see "A point on a quadratic Bezier curve" on the problem page.
  throw NotImplemented("bezier");
}

// ---- Input/output (provided) -------------------------------------------------

namespace {

// Whole numbers print plainly; others with 4 decimals, trailing zeros dropped.
std::string number(double v) {
  if (std::isnan(v)) return "nan";
  if (std::isinf(v)) return v > 0 ? "inf" : "-inf";
  char text[64];
  std::snprintf(text, sizeof text, "%.4f", v);
  std::string s = text;
  s.erase(s.find_last_not_of('0') + 1);
  if (s.back() == '.') s.pop_back();
  return s == "-0" ? "0" : s;
}

Vec2 readPoint(std::istream& words) {
  Vec2 p;
  words >> p.x >> p.y;
  return p;
}

}  // namespace

// Usage: p10 <input-file> <output-file>
int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "usage: " << argv[0] << " <input-file> <output-file>\n";
    return 2;
  }
  std::ifstream input(argv[1]);
  std::ofstream output(argv[2]);
  if (!input || !output) {
    std::cerr << "cannot open " << argv[1] << " or " << argv[2] << "\n";
    return 2;
  }

  try {
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      if (!(words >> keyword)) continue;  // blank line
      Vec2 p;
      if (keyword == "lerp") {  // lerp ax ay bx by t
        const Vec2 a = readPoint(words), b = readPoint(words);
        double t = 0;
        words >> t;
        p = lerp(a, b, t);
      } else if (keyword == "bezier") {  // bezier ax ay bx by cx cy t
        const Vec2 a = readPoint(words), b = readPoint(words), c = readPoint(words);
        double t = 0;
        words >> t;
        p = bezier(a, b, c, t);
      } else {
        throw std::runtime_error("unknown line: " + line);
      }
      if (!words) throw std::runtime_error("bad numbers in line: " + line);
      output << number(p.x) << ' ' << number(p.y) << '\n';
    }
  } catch (const NotImplemented& e) {
    std::cerr << "not implemented: " << e.what() << "\n";
    return 99;
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
