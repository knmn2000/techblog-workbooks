// ======================================================================================
// Assignment 13: Intersect a line and a quadratic curve
// Problem: problems/13-line-curve-intersection.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This is the program the checker runs for assignment 13, as
//   `build/solutions/assignment_13.exe <input-file> <output-file>`: it reads a test input,
//   calls your code and writes the answer to the output file. Only that output is checked.
//   Check it with `.\check 13`, or Run and Submit in the book.
//
// Your job:
//   In the Boilerplate this program is already written: it reads the input, calls your
//   code and writes the answer. Your work is in this assignment's other files, where it
//   says TODO.
//
// The other files of this assignment:
//   It adds to src/utils/Geometry.h, which you started earlier: Add a function that takes
//   a quadratic curve (start, control point, end) and two points on an infinite line, and
//   returns the points where they meet: none, one or two, in increasing t. A dot product
//   helper and a helper that solves a t^2 + b t + c = 0, the linear case a = 0 included,
//   belong here too. The Boilerplate's `Geometry.h` from assignment 10 already declares
//   the function as `segmentQuadBezierIntersect`.
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
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

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
      std::string keyword, lineWord;
      if (!(words >> keyword)) continue;
      if (keyword != "curve") throw std::runtime_error("unknown line: " + line);
      const Vec2 p1 = readPoint(words), p2 = readPoint(words), p3 = readPoint(words);
      words >> lineWord;
      const Vec2 l1 = readPoint(words), l2 = readPoint(words);
      if (!words || lineWord != "line") throw std::runtime_error("bad line: " + line);
      const std::vector<Vec2> points = segmentQuadBezierIntersect(p1, p2, p3, l1, l2);
      if (points.empty()) {
        output << "none\n";
        continue;
      }
      for (std::size_t i = 0; i < points.size(); ++i)
        output << (i ? " " : "") << number(points[i].x) << ' ' << number(points[i].y);
      output << '\n';
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
