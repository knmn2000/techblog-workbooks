#include "render/Scanline.h"

#include <algorithm>
#include <cmath>
#include <utility>

namespace {

Vec2 mid(const Vec2 a, const Vec2 b) { return {(a.x + b.x) / 2, (a.y + b.y) / 2}; }

// Splits a quadratic curve at its turning point in y, if it has one inside.
void addCurve(const Vec2 p0, const Vec2 c, const Vec2 p1, std::vector<EdgePiece>& out) {
  const double denom = p0.y - 2 * c.y + p1.y;
  if (std::abs(denom) > 1e-12) {
    const double t = (p0.y - c.y) / denom;
    if (t > 1e-9 && t < 1 - 1e-9) {
      const Vec2 a = lerp(p0, c, t), b = lerp(c, p1, t), m = lerp(a, b, t);
      out.push_back({p0, a, m, true});
      out.push_back({m, b, p1, true});
      return;
    }
  }
  out.push_back({p0, c, p1, true});
}

// Where a piece crosses the horizontal line y = scanY (half-open in y).
bool cross(const EdgePiece& p, const double scanY, Crossing& out) {
  const double y0 = p.p0.y, y1 = p.p1.y;
  if (y0 == y1) return false;
  if (!(std::min(y0, y1) <= scanY && scanY < std::max(y0, y1))) return false;
  out.direction = y1 > y0 ? 1 : -1;
  if (!p.curve) {
    const double t = (scanY - y0) / (y1 - y0);
    out.x = p.p0.x + (p.p1.x - p.p0.x) * t;
    return true;
  }
  const double a = y0 - 2 * p.c.y + y1, b = 2 * (p.c.y - y0), c = y0 - scanY;
  double t;
  if (std::abs(a) < 1e-12) {
    t = -c / b;
  } else {
    const double disc = std::max(0.0, b * b - 4 * a * c);
    const double r1 = (-b + std::sqrt(disc)) / (2 * a), r2 = (-b - std::sqrt(disc)) / (2 * a);
    const auto dist = [](const double r) { return r < 0 ? -r : (r > 1 ? r - 1 : 0); };
    t = dist(r1) <= dist(r2) ? r1 : r2;  // the piece is monotone: one root is in [0, 1]
  }
  t = std::clamp(t, 0.0, 1.0);
  const double u = 1 - t;
  out.x = u * u * p.p0.x + 2 * u * t * p.c.x + t * t * p.p1.x;
  return true;
}

}  // namespace

std::vector<EdgePiece> edgePieces(const GlyphComponent& outline, const Placement& place) {
  std::vector<EdgePiece> out;
  int start = 0;
  for (const int end : outline.endPtsOfContours) {
    std::vector<std::pair<Vec2, bool>> pts;
    for (int i = start; i <= end; ++i) {
      const GlyphPoint& p = outline.points[i];
      pts.push_back({{place.x0 + place.scale * p.x, place.baseline - place.scale * p.y}, p.onCurve});
    }
    start = end + 1;
    if (pts.empty()) continue;

    // Make every implied on-curve point explicit.
    std::vector<std::pair<Vec2, bool>> full;
    for (std::size_t i = 0; i < pts.size(); ++i) {
      const auto& p = pts[i];
      const auto& next = pts[(i + 1) % pts.size()];
      full.push_back(p);
      if (!p.second && !next.second) full.push_back({mid(p.first, next.first), true});
    }
    const auto first = std::find_if(full.begin(), full.end(), [](const auto& p) { return p.second; });
    if (first == full.end()) continue;  // a single off-curve point: nothing to fill
    std::rotate(full.begin(), first, full.end());

    Vec2 current = full[0].first;
    for (std::size_t i = 1; i <= full.size(); ++i) {
      const auto& p = full[i % full.size()];
      if (p.second) {
        out.push_back({current, current, p.first, false});
        current = p.first;
      } else {
        const Vec2 next = full[(i + 1) % full.size()].first;  // always on-curve now
        addCurve(current, p.first, next, out);
        current = next;
        ++i;
      }
    }
  }
  return out;
}

void forEachRow(const std::vector<EdgePiece>& edges, const int height,
                const std::function<void(int, const std::vector<Crossing>&)>& visit) {
  if (edges.empty()) return;
  double top = 1e300, bottom = -1e300;
  for (const EdgePiece& e : edges) {
    top = std::min({top, e.p0.y, e.c.y, e.p1.y});
    bottom = std::max({bottom, e.p0.y, e.c.y, e.p1.y});
  }
  const int firstRow = std::max(0, static_cast<int>(std::floor(top)) - 1);
  const int lastRow = std::min(height - 1, static_cast<int>(std::ceil(bottom)) + 1);

  std::vector<Crossing> crossings;
  for (int row = firstRow; row <= lastRow; ++row) {
    const double scanY = row + 0.5;  // through the pixel centres
    crossings.clear();
    for (const EdgePiece& e : edges) {
      Crossing c;
      if (cross(e, scanY, c)) crossings.push_back(c);
    }
    std::sort(crossings.begin(), crossings.end(), [](const Crossing& a, const Crossing& b) { return a.x < b.x; });
    visit(row, crossings);
  }
}

void fillSpan(FrameBufferCanvas& canvas, const int row, const double fromX, const double toX, const RGB color) {
  if (row < 0 || row >= canvas.height()) return;
  // Pixel x has its centre at x + 0.5.
  const int from = std::max(0, static_cast<int>(std::ceil(fromX - 0.5)));
  const int to = std::min(canvas.width() - 1, static_cast<int>(std::ceil(toX - 0.5)) - 1);
  for (int x = from; x <= to; ++x) canvas.set(x, row, color);
}
