// Checkpoint 13 - Intersect a line and a quadratic curve
//
// Problem:  problems/13-line-curve-intersection.md (also in the web problem book)
// Check:    .\check 13
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on solveQuadratic() and intersect().

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "NotImplemented.h"

struct Vec2 {
  double x = 0;
  double y = 0;
};

// Optional helpers: add, subtract, scale, dot product. (glm::dvec2 from third_party/ works too.)
Vec2 operator+(const Vec2 a, const Vec2 b) { return {a.x + b.x, a.y + b.y}; }
Vec2 operator-(const Vec2 a, const Vec2 b) { return {a.x - b.x, a.y - b.y}; }
Vec2 operator*(const Vec2 v, const double s) { return {v.x * s, v.y * s}; }
double dot(const Vec2 u, const Vec2 v) { return u.x * v.x + u.y * v.y; }

// The real roots of a t^2 + b t + c = 0, each one once. Remember that a can be 0.
std::vector<double> solveQuadratic(const double a, const double b, const double c) {
  // TODO: see "Solving for t" on the problem page.
  throw NotImplemented("solveQuadratic");
}

// The points where the infinite line through l1 and l2 meets the curve that starts
// at p1, is pulled toward the control point p2 and ends at p3. Only points with
// 0 <= t <= 1, in order of t.
std::vector<Vec2> intersect(const Vec2 p1, const Vec2 p2, const Vec2 p3, const Vec2 l1, const Vec2 l2) {
  // TODO: see "From a line and a curve to a quadratic" on the problem page.
  throw NotImplemented("intersect");
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

// Usage: p13 <input-file> <output-file>
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
      if (!(words >> keyword)) continue;  // blank line
      if (keyword != "curve") throw std::runtime_error("unknown line: " + line);
      // curve p1x p1y p2x p2y p3x p3y line l1x l1y l2x l2y
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
  } catch (const NotImplemented& e) {
    std::cerr << "not implemented: " << e.what() << "\n";
    return 99;
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
