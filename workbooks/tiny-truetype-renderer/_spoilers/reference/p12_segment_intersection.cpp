// Reference solution - checkpoint 12 (intersect two segments).
// SPOILERS: try the checkpoint yourself first.

#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <optional>
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

namespace {

double cross(const Vec2 u, const Vec2 v) { return u.x * v.y - u.y * v.x; }

// Positive on one side of the line through start and end, negative on the other, 0 on it.
double side(const Vec2 pt, const Vec2 start, const Vec2 end) { return cross(end - start, pt - start); }

}  // namespace

std::optional<Vec2> intersect(const Vec2 a1, const Vec2 a2, const Vec2 b1, const Vec2 b2) {
  // Each segment's endpoints must not lie strictly on the same side of the other's line.
  if (side(b1, a1, a2) * side(b2, a1, a2) > 0) return std::nullopt;
  if (side(a1, b1, b2) * side(a2, b1, b2) > 0) return std::nullopt;
  const Vec2 v1 = a2 - a1, v2 = b2 - b1;
  const double denominator = cross(v1, v2);
  if (std::abs(denominator) < 1e-9) return std::nullopt;  // parallel or collinear
  const double t = cross(b1 - a1, v2) / denominator;
  return a1 + v1 * t;
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
      if (keyword != "segments") throw std::runtime_error("unknown line: " + line);
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
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
