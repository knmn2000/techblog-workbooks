// Reference solution - checkpoint 07 (decode simple glyphs).
// SPOILERS: try the checkpoint yourself first.

#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "provided/BigEndian.h"

struct Point {
  int x = 0;
  int y = 0;
  bool onCurve = false;
};

struct DecodedGlyph {
  enum class Kind { Empty, Compound, Simple };
  Kind kind = Kind::Empty;
  int numberOfContours = 0;
  int xMin = 0, yMin = 0, xMax = 0, yMax = 0;
  std::vector<int> endPtsOfContours;
  std::vector<Point> points;
};

namespace {

constexpr uint8_t ON_CURVE_POINT = 0x01;
constexpr uint8_t X_SHORT_VECTOR = 0x02;
constexpr uint8_t Y_SHORT_VECTOR = 0x04;
constexpr uint8_t REPEAT_FLAG = 0x08;
constexpr uint8_t X_IS_SAME_OR_POSITIVE = 0x10;
constexpr uint8_t Y_IS_SAME_OR_POSITIVE = 0x20;

// Reads one axis of delta-encoded coordinates into points[i].*axis.
void readAxis(std::istream& in, const std::vector<uint8_t>& flags, const uint8_t shortBit,
              const uint8_t sameOrPositiveBit, int Point::*axis, std::vector<Point>& points) {
  int value = 0;  // deltas run on across contours, starting from 0
  for (std::size_t i = 0; i < flags.size(); ++i) {
    const uint8_t flag = flags[i];
    if (flag & shortBit) {
      const int magnitude = be::u8(in);
      value += (flag & sameOrPositiveBit) ? magnitude : -magnitude;
    } else if (!(flag & sameOrPositiveBit)) {
      value += be::i16(in);
    }  // else: same as the previous point, no bytes
    points[i].*axis = value;
  }
}

}  // namespace

DecodedGlyph decodeGlyph(std::ifstream& file, const uint32_t offset, const uint32_t length) {
  DecodedGlyph g;
  if (length == 0) return g;  // no outline, e.g. space

  file.seekg(offset);
  g.numberOfContours = be::i16(file);
  if (g.numberOfContours < 0) {
    g.kind = DecodedGlyph::Kind::Compound;
    return g;
  }
  g.kind = DecodedGlyph::Kind::Simple;
  g.xMin = be::i16(file);
  g.yMin = be::i16(file);
  g.xMax = be::i16(file);
  g.yMax = be::i16(file);
  if (g.numberOfContours == 0) return g;

  std::size_t numPoints = 0;
  for (int i = 0; i < g.numberOfContours; ++i) {
    const int end = be::u16(file);
    g.endPtsOfContours.push_back(end);
    numPoints = std::max(numPoints, static_cast<std::size_t>(end) + 1);
  }

  file.seekg(be::u16(file), std::ios::cur);  // hinting instructions

  std::vector<uint8_t> flags;
  flags.reserve(numPoints);
  while (flags.size() < numPoints) {
    const uint8_t flag = be::u8(file);
    const std::size_t copies = (flag & REPEAT_FLAG) ? 1u + be::u8(file) : 1u;
    flags.insert(flags.end(), copies, flag);
  }
  flags.resize(numPoints);  // a malformed repeat count can't add points

  g.points.resize(numPoints);
  readAxis(file, flags, X_SHORT_VECTOR, X_IS_SAME_OR_POSITIVE, &Point::x, g.points);
  readAxis(file, flags, Y_SHORT_VECTOR, Y_IS_SAME_OR_POSITIVE, &Point::y, g.points);
  for (std::size_t i = 0; i < numPoints; ++i) g.points[i].onCurve = flags[i] & ON_CURVE_POINT;
  return g;
}

// ---- Input/output (same as the starter) --------------------------------------

namespace {

void write(std::ostream& out, const uint32_t id, const DecodedGlyph& g) {
  out << "glyph " << id;
  if (g.kind == DecodedGlyph::Kind::Empty) {
    out << " empty\n";
    return;
  }
  if (g.kind == DecodedGlyph::Kind::Compound) {
    out << " compound\n";
    return;
  }
  out << " contours " << g.numberOfContours << " bbox " << g.xMin << ' ' << g.yMin << ' '
      << g.xMax << ' ' << g.yMax << "\nends";
  for (const int end : g.endPtsOfContours) out << ' ' << end;
  out << "\npoints";
  for (const Point& p : g.points) out << ' ' << p.x << ' ' << p.y << (p.onCurve ? " on" : " off");
  out << '\n';
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
    std::ifstream font;
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") {
        std::string path;
        words >> path;
        font = std::ifstream(path, std::ios::binary);
        if (!font) throw std::runtime_error("cannot open font file " + path);
      } else if (keyword == "glyph") {
        uint32_t id = 0, offset = 0, length = 0;
        words >> id >> offset >> length;
        font.clear();
        write(output, id, decodeGlyph(font, offset, length));
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
