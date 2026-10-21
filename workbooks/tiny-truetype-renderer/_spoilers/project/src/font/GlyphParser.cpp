#include "font/GlyphParser.h"

#include <algorithm>
#include <vector>

namespace {

constexpr uint8_t ON_CURVE_POINT = 0x01;
constexpr uint8_t X_SHORT_VECTOR = 0x02;
constexpr uint8_t Y_SHORT_VECTOR = 0x04;
constexpr uint8_t REPEAT_FLAG = 0x08;
constexpr uint8_t X_IS_SAME_OR_POSITIVE = 0x10;
constexpr uint8_t Y_IS_SAME_OR_POSITIVE = 0x20;

// Reads one axis of delta-encoded coordinates into points[i].*axis.
void readAxis(ByteReader& reader, const std::vector<uint8_t>& flags, const uint8_t shortBit,
              const uint8_t sameOrPositiveBit, double GlyphPoint::*axis, std::vector<GlyphPoint>& points) {
  int value = 0;  // deltas run on across contours, starting from 0
  for (std::size_t i = 0; i < flags.size(); ++i) {
    const uint8_t flag = flags[i];
    if (flag & shortBit) {
      const int magnitude = reader.readUint8();
      value += (flag & sameOrPositiveBit) ? magnitude : -magnitude;
    } else if (!(flag & sameOrPositiveBit)) {
      value += reader.readInt16();
    }  // else: same as the previous point, no bytes
    points[i].*axis = value;
  }
}

}  // namespace

Glyph readGlyph(ByteReader& reader, const uint32_t offset, const uint32_t length) {
  Glyph g;
  if (length == 0) return g;  // no outline, e.g. space

  reader.jumpTo(offset);
  g.numberOfContours = reader.readInt16();
  g.kind = g.numberOfContours < 0 ? Glyph::Kind::Compound : Glyph::Kind::Simple;
  g.bounds.xMin = reader.readInt16();
  g.bounds.yMin = reader.readInt16();
  g.bounds.xMax = reader.readInt16();
  g.bounds.yMax = reader.readInt16();
  if (g.kind == Glyph::Kind::Compound) return g;

  GlyphComponent& outline = g.components.emplace_back();
  if (g.numberOfContours == 0) return g;

  std::size_t numPoints = 0;
  for (int i = 0; i < g.numberOfContours; ++i) {
    const int end = reader.readUint16();
    outline.endPtsOfContours.push_back(end);
    numPoints = std::max(numPoints, static_cast<std::size_t>(end) + 1);
  }

  reader.skipBytes(reader.readUint16());  // hinting instructions

  std::vector<uint8_t> flags;
  flags.reserve(numPoints);
  while (flags.size() < numPoints) {
    const uint8_t flag = reader.readUint8();
    const std::size_t copies = (flag & REPEAT_FLAG) ? 1u + reader.readUint8() : 1u;
    flags.insert(flags.end(), copies, flag);
  }
  flags.resize(numPoints);  // a malformed repeat count can't add points

  outline.points.resize(numPoints);
  readAxis(reader, flags, X_SHORT_VECTOR, X_IS_SAME_OR_POSITIVE, &GlyphPoint::x, outline.points);
  readAxis(reader, flags, Y_SHORT_VECTOR, Y_IS_SAME_OR_POSITIVE, &GlyphPoint::y, outline.points);
  for (std::size_t i = 0; i < numPoints; ++i) outline.points[i].onCurve = flags[i] & ON_CURVE_POINT;
  return g;
}
