// Reference solution - checkpoint 13 (intersect a line and a quadratic curve).
// SPOILERS: try the checkpoint yourself first.

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Vec2 {
  double x = 0;
  double y = 0;
};

Vec2 operator+(const Vec2 a, const Vec2 b) { return {a.x + b.x, a.y + b.y}; }
Vec2 operator-(const Vec2 a, const Vec2 b) { return {a.x - b.x, a.y - b.y}; }
Vec2 operator*(const Vec2 v, const double s) { return {v.x * s, v.y * s}; }

namespace {

double dot(const Vec2 u, const Vec2 v) { return u.x * v.x + u.y * v.y; }

// Real roots of a t^2 + b t + c = 0, in increasing order; a double root once.
// The test data make a, and the discriminant of a tangent, exactly 0 when they are 0.
std::vector<double> solveQuadratic(const double a, const double b, const double c) {
  if (a == 0) {
    if (b == 0) return {};  // no root (or every t, which the tests exclude)
    return {-c / b};
  }
  const double discriminant = b * b - 4 * a * c;
  if (discriminant < 0) return {};
  if (discriminant == 0) return {-b / (2 * a)};
  // The stable form: no cancellation between b and the square root.
  const double q = -0.5 * (b + std::copysign(std::sqrt(discriminant), b));
  std::vector<double> roots = {q / a, c / q};
  std::sort(roots.begin(), roots.end());
  return roots;
}

}  // namespace

// Where the infinite line through l1 and l2 meets the curve p1 (start), p2 (control),
// p3 (end), ordered by the curve parameter t.
std::vector<Vec2> intersect(const Vec2 p1, const Vec2 p2, const Vec2 p3, const Vec2 l1, const Vec2 l2) {
  const Vec2 d = l2 - l1;
  const Vec2 k = {d.y, -d.x};  // perpendicular to the line: dot(k, X - l1) = 0 on it
  // The curve as a polynomial: P(t) = A t^2 + B t + C.
  const Vec2 A = p1 - p2 * 2 + p3, B = (p2 - p1) * 2, C = p1;
  std::vector<Vec2> points;
  for (const double t : solveQuadratic(dot(k, A), dot(k, B), dot(k, C - l1))) {
    if (t >= 0 && t <= 1) points.push_back(A * (t * t) + B * t + C);
  }
  return points;
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
      std::string keyword, lineWord;
      if (!(words >> keyword)) continue;
      if (keyword != "curve") throw std::runtime_error("unknown line: " + line);
      const Vec2 p1 = readPoint(words), p2 = readPoint(words), p3 = readPoint(words);
      words >> lineWord;
      const Vec2 l1 = readPoint(words), l2 = readPoint(words);
      if (!words || lineWord != "line") throw std::runtime_error("bad line: " + line);
      const std::vector<Vec2> points = intersect(p1, p2, p3, l1, l2);
      if (points.empty()) {
        output << "none\n";
        continue;
      }
      for (std::size_t i = 0; i < points.size(); ++i) {
        output << (i ? " " : "") << number(points[i].x) << ' ' << number(points[i].y);
      }
      output << '\n';
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
