// Reference solution - checkpoint 15 (lowest point of a quadratic curve).
// SPOILERS: try the checkpoint yourself first.

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

struct Vec2 {
  double x = 0;
  double y = 0;
};

// The smallest y on the curve p1 (start), p2 (control), p3 (end) for 0 <= t <= 1.
double minY(const Vec2 p1, const Vec2 p2, const Vec2 p3) {
  // y(t) = a t^2 + b t + p1.y
  const double a = p1.y - 2 * p2.y + p3.y;
  const double b = 2 * (p2.y - p1.y);
  double lowest = std::min(p1.y, p3.y);  // the ends are always candidates
  if (a > 0) {                           // a valley: its turning point is the lowest point
    const double t = -b / (2 * a);
    if (t > 0 && t < 1) lowest = std::min(lowest, (a * t + b) * t + p1.y);
  }
  return lowest;
}

// ---- Input/output (same as the starter) --------------------------------------

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
      if (keyword != "curve") throw std::runtime_error("unknown line: " + line);
      const Vec2 p1 = readPoint(words), p2 = readPoint(words), p3 = readPoint(words);
      if (!words) throw std::runtime_error("bad numbers in line: " + line);
      output << number(minY(p1, p2, p3)) << '\n';
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
