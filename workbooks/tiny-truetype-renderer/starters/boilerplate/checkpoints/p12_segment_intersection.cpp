// Checkpoint 12 (Intersect two segments): the program the checker runs.
//
// Problem:  problems/12-segment-intersection.md (also in the web problem book)
// Check:    .\check 12
//
// Boilerplate: the input and output are done here, and the project files declare what they
// need, named as the author names them. What's left to write is segmentsIntersect, marked
// TODO in src/utils/Geometry.h. Only the output is checked, so change anything you like.

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
