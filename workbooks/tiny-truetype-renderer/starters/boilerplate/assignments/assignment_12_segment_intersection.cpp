// ======================================================================================
// Assignment 12: Intersect two segments
// Problem: problems/12-segment-intersection.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 12 as `build/solutions/assignment_12.exe
//   <input-file> <output-file>`. It reads a test input, calls your code and writes the
//   answer to the output file, and the checker compares that answer with the expected one.
//   Run `.\check 12`, or use Run and Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished: it reads the input, calls your code
//   and writes the answer. You fill in the TODOs in this assignment's other files.
//
// The other files of this assignment:
//   It adds to src/utils/Geometry.h, which you started earlier: Add a function that takes
//   two segments, each given by its two end points, and returns the one point where they
//   meet. If they don't meet, or are parallel or collinear, it returns nothing;
//   `std::optional` suits this. Put small helpers for the 2D cross product and the side
//   value here too, `inline` like the rest of the header. The Boilerplate's `Geometry.h`
//   from assignment 10 already declares the function as `segmentsIntersect`.
//   Include them by their path under src/, e.g. #include "utils/Geometry.h".
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>

#include "utils/Geometry.h"

namespace {

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
      if (!(words >> keyword)) continue;
      if (keyword != "segments") throw std::runtime_error("unknown line: " + line);
      const Vec2 a1 = readPoint(words), a2 = readPoint(words);
      const Vec2 b1 = readPoint(words), b2 = readPoint(words);
      if (!words) throw std::runtime_error("bad numbers in line: " + line);
      if (const std::optional<Vec2> p = segmentsIntersect(a1, a2, b1, b2)) {
        output << number(p->x) << ' ' << number(p->y) << '\n';
      } else {
        output << "none\n";
      }
    }
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
