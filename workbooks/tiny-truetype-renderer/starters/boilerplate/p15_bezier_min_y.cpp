// Checkpoint 15 - Lowest point of a quadratic curve
//
// Problem:  problems/15-bezier-min-y.md (also in the web problem book)
// Check:    .\check 15
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on minY().

#include <algorithm>
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

// The smallest y on the curve that starts at p1, is pulled toward the control
// point p2 and ends at p3, over 0 <= t <= 1. Only the y coordinates matter.
double minY(const Vec2 p1, const Vec2 p2, const Vec2 p3) {
  // TODO: see "Where the lowest point can be" on the problem page.
  throw NotImplemented("minY");
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

// Usage: p15 <input-file> <output-file>
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
      if (keyword != "curve") throw std::runtime_error("unknown line: " + line);
      // curve p1x p1y p2x p2y p3x p3y
      const Vec2 p1 = readPoint(words), p2 = readPoint(words), p3 = readPoint(words);
      if (!words) throw std::runtime_error("bad numbers in line: " + line);
      output << number(minY(p1, p2, p3)) << '\n';
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
