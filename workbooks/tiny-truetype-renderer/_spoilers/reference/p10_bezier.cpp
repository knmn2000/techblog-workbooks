// Reference solution - checkpoint 10 (lerp and quadratic Bezier curves).
// SPOILERS: try the checkpoint yourself first.

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

Vec2 operator+(const Vec2 a, const Vec2 b) { return {a.x + b.x, a.y + b.y}; }
Vec2 operator-(const Vec2 a, const Vec2 b) { return {a.x - b.x, a.y - b.y}; }
Vec2 operator*(const Vec2 v, const double s) { return {v.x * s, v.y * s}; }

Vec2 lerp(const Vec2 a, const Vec2 b, const double t) {
  return a + (b - a) * t;
}

// De Casteljau: lerp along both legs of the control polygon, then between the two results.
Vec2 bezier(const Vec2 a, const Vec2 b, const Vec2 c, const double t) {
  return lerp(lerp(a, b, t), lerp(b, c, t), t);
}

// ---- Input/output (same as the starter) --------------------------------------

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
        p = bezier(a, b, c, t);
      } else {
        throw std::runtime_error("unknown line: " + line);
      }
      if (!words) throw std::runtime_error("bad numbers in line: " + line);
      output << number(p.x) << ' ' << number(p.y) << '\n';
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
