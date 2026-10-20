// Reference solution - checkpoint 09 (resolve compound glyphs).
// SPOILERS: try the checkpoint yourself first.

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "provided/BigEndian.h"
#include "provided/SimpleGlyph.h"

using provided::Outline;

struct GlyphRecord {
  uint32_t offset = 0;
  uint32_t length = 0;
};

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
  uint16_t glyphId = 0;
  Affine transform;
};

class Resolver {
public:
  Resolver(std::ifstream& file, const std::map<uint32_t, GlyphRecord>& records)
      : file_(file), records_(records) {}

  void resolve(const uint32_t glyphId, const Affine& toGlyph, const int depth,
               std::vector<Outline>& out) {
    if (depth > 16) throw std::runtime_error("compound glyphs nested too deeply");
    const auto it = records_.find(glyphId);
    if (it == records_.end()) throw std::runtime_error("no glyph line for glyph " + std::to_string(glyphId));
    if (it->second.length == 0) return;  // empty glyph: nothing to draw

    file_.clear();
    file_.seekg(it->second.offset);
    const int numberOfContours = be::i16(file_);
    if (numberOfContours >= 0) {
      Outline outline = provided::readSimpleGlyph(file_, it->second.offset);
      if (outline.points.empty()) return;
      for (auto& p : outline.points) {
        const double x = p.x, y = p.y;
        p.x = toGlyph.a * x + toGlyph.c * y + toGlyph.e;
        p.y = toGlyph.b * x + toGlyph.d * y + toGlyph.f;
      }
      out.push_back(std::move(outline));
      return;
    }

    // Read every component record first: resolving one moves the stream elsewhere.
    file_.seekg(8, std::ios::cur);  // bounding box
    std::vector<Component> components;
    uint16_t flags = 0;
    do {
      flags = be::u16(file_);
      Component comp;
      comp.glyphId = be::u16(file_);
      int arg1 = 0, arg2 = 0;
      if (flags & ARG_1_AND_2_ARE_WORDS) {
        arg1 = be::i16(file_);
        arg2 = be::i16(file_);
      } else {
        arg1 = be::i8(file_);
        arg2 = be::i8(file_);
      }
      if (!(flags & ARGS_ARE_XY_VALUES)) throw std::runtime_error("point-matched components aren't supported");

      Affine& t = comp.transform;
      if (flags & WE_HAVE_A_SCALE) {
        t.a = t.d = be::f2dot14(file_);
      } else if (flags & WE_HAVE_AN_X_AND_Y_SCALE) {
        t.a = be::f2dot14(file_);
        t.d = be::f2dot14(file_);
      } else if (flags & WE_HAVE_A_TWO_BY_TWO) {
        t.a = be::f2dot14(file_);
        t.b = be::f2dot14(file_);
        t.c = be::f2dot14(file_);
        t.d = be::f2dot14(file_);
      }
      t.e = arg1;
      t.f = arg2;
      if (flags & SCALED_COMPONENT_OFFSET) {  // the offset goes through the 2x2 part too
        t.e = t.a * arg1 + t.c * arg2;
        t.f = t.b * arg1 + t.d * arg2;
      }
      components.push_back(comp);
    } while (flags & MORE_COMPONENTS);

    for (const Component& comp : components) {
      resolve(comp.glyphId, toGlyph.after(comp.transform), depth + 1, out);
    }
  }

private:
  std::ifstream& file_;
  const std::map<uint32_t, GlyphRecord>& records_;
};

}  // namespace

std::vector<Outline> resolveGlyph(std::ifstream& file, const std::map<uint32_t, GlyphRecord>& records,
                                  const uint32_t glyphId) {
  std::vector<Outline> out;
  Resolver(file, records).resolve(glyphId, Affine{}, 0, out);
  return out;
}

// ---- Input/output (same as the starter) --------------------------------------

namespace {

std::string number(const double v) {
  if (std::abs(v - std::round(v)) < 1e-9) return std::to_string(static_cast<long long>(std::llround(v)));
  char buf[32];
  std::snprintf(buf, sizeof buf, "%.4f", v);
  std::string s = buf;
  while (s.back() == '0') s.pop_back();
  if (s.back() == '.') s.pop_back();  // 4.99999 rounds to "5.0000": print "5"
  return s == "-0" ? "0" : s;
}

void write(std::ostream& out, const uint32_t id, const std::vector<Outline>& outlines) {
  out << "glyph " << id << " components " << outlines.size() << '\n';
  for (const Outline& o : outlines) {
    out << "ends";
    for (const int e : o.endPtsOfContours) out << ' ' << e;
    out << "\npoints";
    for (const auto& p : o.points) out << ' ' << number(p.x) << ' ' << number(p.y) << (p.onCurve ? " on" : " off");
    out << '\n';
  }
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
    std::map<uint32_t, GlyphRecord> records;
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") {
        std::string path;
        words >> path;
        font = std::ifstream(path, std::ios::binary);
        if (!font) throw std::runtime_error("cannot open font file " + path);
        records.clear();
      } else if (keyword == "glyph") {
        uint32_t id = 0;
        GlyphRecord r;
        words >> id >> r.offset >> r.length;
        records[id] = r;
      } else if (keyword == "decode") {
        uint32_t id = 0;
        words >> id;
        write(output, id, resolveGlyph(font, records, id));
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
