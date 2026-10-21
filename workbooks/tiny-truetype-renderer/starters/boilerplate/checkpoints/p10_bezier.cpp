// Checkpoint 10 (Lerp and quadratic Bezier curves): the program the checker runs.
//
// Problem:  problems/10-bezier.md (also in the web problem book)
// Check:    .\check 10
//
// Boilerplate: the input and output are done here, and the project files declare what they
// need, named as the author names them. What's left to write is lerp and bezierLerp,
// marked TODO in src/utils/Geometry.h. Only the output is checked, so change anything you
// like.

#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

#include "utils/Geometry.h"

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
      Vec2 p;
      if (keyword == "lerp") {
        const Vec2 a = readPoint(words), b = readPoint(words);
        double t = 0;
        words >> t;
        p = lerp(a, b, t);
      } else if (keyword == "bezier") {
        const Vec2 a = readPoint(words), b = readPoint(words), c = readPoint(words);
        double t = 0;
        words >> t;
        p = bezierLerp(a, b, c, t);
      } else {
        throw std::runtime_error("unknown line: " + line);
      }
      if (!words) throw std::runtime_error("bad numbers in line: " + line);
      output << number(p.x) << ' ' << number(p.y) << '\n';
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
