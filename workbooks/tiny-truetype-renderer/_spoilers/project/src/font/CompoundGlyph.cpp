#include "font/CompoundGlyph.h"

#include <stdexcept>
#include <string>

#include "font/GlyphParser.h"

namespace {

constexpr uint16_t ARG_1_AND_2_ARE_WORDS = 0x0001;
constexpr uint16_t ARGS_ARE_XY_VALUES = 0x0002;
constexpr uint16_t WE_HAVE_A_SCALE = 0x0008;
constexpr uint16_t MORE_COMPONENTS = 0x0020;
constexpr uint16_t WE_HAVE_AN_X_AND_Y_SCALE = 0x0040;
constexpr uint16_t WE_HAVE_A_TWO_BY_TWO = 0x0080;
constexpr uint16_t SCALED_COMPONENT_OFFSET = 0x0800;

// x' = a*x + c*y + e, y' = b*x + d*y + f
struct Affine {
  double a = 1, b = 0, c = 0, d = 1, e = 0, f = 0;

  // This transform applied after `inner`.
  [[nodiscard]] Affine after(const Affine& inner) const {
    return {a * inner.a + c * inner.b, b * inner.a + d * inner.b,
            a * inner.c + c * inner.d, b * inner.c + d * inner.d,
            a * inner.e + c * inner.f + e, b * inner.e + d * inner.f + f};
  }
};

struct Component {
  uint32_t glyphId = 0;
  Affine transform;
};

class Resolver {
 public:
  Resolver(ByteReader& reader, const std::map<uint32_t, GlyphLocation>& locations)
      : reader_(reader), locations_(locations) {}

  void resolve(const uint32_t glyphId, const Affine& toGlyph, const int depth, std::vector<GlyphComponent>& out) {
    if (depth > 16) throw std::runtime_error("compound glyphs nested too deeply");
    const auto it = locations_.find(glyphId);
    if (it == locations_.end()) throw std::runtime_error("no location for glyph " + std::to_string(glyphId));
    const Glyph glyph = readGlyph(reader_, it->second.offset, it->second.length);
    if (glyph.kind == Glyph::Kind::Empty) return;  // nothing to draw

    if (glyph.kind == Glyph::Kind::Simple) {
      GlyphComponent outline = glyph.components.front();
      if (outline.points.empty()) return;
      for (GlyphPoint& p : outline.points) {
        const double x = p.x, y = p.y;
        p.x = toGlyph.a * x + toGlyph.c * y + toGlyph.e;
        p.y = toGlyph.b * x + toGlyph.d * y + toGlyph.f;
      }
      out.push_back(std::move(outline));
      return;
    }

    // Read every component record first: resolving one moves the reader elsewhere.
    reader_.jumpTo(it->second.offset + 10);  // after numberOfContours and the bounding box
    std::vector<Component> components;
    uint16_t flags = 0;
    do {
      flags = reader_.readUint16();
      Component comp;
      comp.glyphId = reader_.readUint16();
      int arg1 = 0, arg2 = 0;
      if (flags & ARG_1_AND_2_ARE_WORDS) {
        arg1 = reader_.readInt16();
        arg2 = reader_.readInt16();
      } else {
        arg1 = reader_.readInt8();
        arg2 = reader_.readInt8();
      }
      if (!(flags & ARGS_ARE_XY_VALUES)) throw std::runtime_error("point-matched components aren't supported");

      Affine& t = comp.transform;
      if (flags & WE_HAVE_A_SCALE) {
        t.a = t.d = reader_.readF2Dot14();
      } else if (flags & WE_HAVE_AN_X_AND_Y_SCALE) {
        t.a = reader_.readF2Dot14();
        t.d = reader_.readF2Dot14();
      } else if (flags & WE_HAVE_A_TWO_BY_TWO) {
        t.a = reader_.readF2Dot14();
        t.b = reader_.readF2Dot14();
        t.c = reader_.readF2Dot14();
        t.d = reader_.readF2Dot14();
      }
      t.e = arg1;
      t.f = arg2;
      if (flags & SCALED_COMPONENT_OFFSET) {  // the offset goes through the 2x2 part too
        t.e = t.a * arg1 + t.c * arg2;
        t.f = t.b * arg1 + t.d * arg2;
      }
      components.push_back(comp);
    } while (flags & MORE_COMPONENTS);

    for (const Component& comp : components) resolve(comp.glyphId, toGlyph.after(comp.transform), depth + 1, out);
  }

 private:
  ByteReader& reader_;
  const std::map<uint32_t, GlyphLocation>& locations_;
};

}  // namespace

std::vector<GlyphComponent> resolveGlyph(ByteReader& reader, const std::map<uint32_t, GlyphLocation>& locations,
                                         const uint32_t glyphId) {
  std::vector<GlyphComponent> out;
  Resolver(reader, locations).resolve(glyphId, Affine{}, 0, out);
  return out;
}
