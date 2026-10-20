#pragma once
// Provided, optional: decodes a simple glyph record - what checkpoint 07 builds.
// If you've done checkpoint 07, you can use your own code instead.

#include <cstdint>
#include <istream>
#include <stdexcept>
#include <vector>

#include "provided/BigEndian.h"

namespace provided {

struct OutlinePoint {
  double x = 0;
  double y = 0;
  bool onCurve = false;
};

struct Outline {
  std::vector<int> endPtsOfContours;
  std::vector<OutlinePoint> points;
};

// Reads the simple glyph whose record starts at `offset`. Throws std::invalid_argument
// if the record is a compound glyph (numberOfContours < 0).
inline Outline readSimpleGlyph(std::istream& in, const uint32_t offset) {
  in.clear();
  in.seekg(offset);
  const int numberOfContours = be::i16(in);
  if (numberOfContours < 0) throw std::invalid_argument("compound glyph");
  in.seekg(8, std::ios::cur);  // bounding box
  Outline out;
  for (int i = 0; i < numberOfContours; ++i) out.endPtsOfContours.push_back(be::u16(in));
  if (numberOfContours == 0) return out;
  const std::size_t n = static_cast<std::size_t>(out.endPtsOfContours.back()) + 1;
  in.seekg(be::u16(in), std::ios::cur);  // instructions

  std::vector<uint8_t> flags;
  while (flags.size() < n) {
    const uint8_t flag = be::u8(in);
    const std::size_t copies = (flag & 0x08) ? 1u + be::u8(in) : 1u;
    flags.insert(flags.end(), copies, flag);
  }
  flags.resize(n);
  out.points.resize(n);
  for (const bool isX : {true, false}) {
    const uint8_t shortBit = isX ? 0x02 : 0x04, sameBit = isX ? 0x10 : 0x20;
    int value = 0;
    for (std::size_t i = 0; i < n; ++i) {
      if (flags[i] & shortBit) {
        const int d = be::u8(in);
        value += (flags[i] & sameBit) ? d : -d;
      } else if (!(flags[i] & sameBit)) {
        value += be::i16(in);
      }
      (isX ? out.points[i].x : out.points[i].y) = value;
    }
  }
  for (std::size_t i = 0; i < n; ++i) out.points[i].onCurve = flags[i] & 0x01;
  return out;
}

}  // namespace provided
