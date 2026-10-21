// Checkpoint 13 (Intersect a line and a quadratic curve): the program the checker runs.
//
// Problem:  problems/13-line-curve-intersection.md (also in the web problem book)
// Check:    .\check 13
//
// Boilerplate: the input and output are done here, and the project files declare what they
// need, named as the author names them. What's left to write is
// segmentQuadBezierIntersect, marked TODO in src/utils/Geometry.h. Only the output is
// checked, so change anything you like.

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
