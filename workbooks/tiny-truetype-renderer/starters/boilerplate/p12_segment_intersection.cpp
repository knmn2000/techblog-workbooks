// Checkpoint 12 - Intersect two segments
//
// Problem:  problems/12-segment-intersection.md (also in the web problem book)
// Check:    .\check 12
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on intersect().

#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <optional>
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

// The point where segment a1-a2 meets segment b1-b2, or std::nullopt if they
// don't meet or are parallel (rules on the problem page).
std::optional<Vec2> intersect(const Vec2 a1, const Vec2 a2, const Vec2 b1, const Vec2 b2) {
  // TODO: the side test, then the crossing point (see "The rules" on the problem page).
  throw NotImplemented("intersect");
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

// Usage: p12 <input-file> <output-file>
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
      if (keyword != "segments") throw std::runtime_error("unknown line: " + line);
      // segments a1x a1y a2x a2y b1x b1y b2x b2y
      const Vec2 a1 = readPoint(words), a2 = readPoint(words);
      const Vec2 b1 = readPoint(words), b2 = readPoint(words);
      if (!words) throw std::runtime_error("bad numbers in line: " + line);
      const std::optional<Vec2> p = intersect(a1, a2, b1, b2);
      if (p) {
        output << number(p->x) << ' ' << number(p->y) << '\n';
      } else {
        output << "none\n";
      }
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
