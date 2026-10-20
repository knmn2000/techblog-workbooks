#pragma once
// Reference font reading for checkpoint 18: the work of checkpoints 02-05, 07 and 09
// in one place. SPOILERS: try those checkpoints yourself first.

#include <cstdint>
#include <fstream>
#include <map>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include "fill.h"
#include "provided/BigEndian.h"
#include "provided/SimpleGlyph.h"

namespace font {

struct Table {
  uint32_t offset = 0, length = 0;
};

class Font {
public:
  explicit Font(const std::string& path) : in_(path, std::ios::binary) {
    if (!in_) throw std::runtime_error("cannot open " + path);
    readDirectory();
    readCmap();
    readLoca();
    readMetrics();
  }

  // Glyph id for a code point; 0 (.notdef) when the font doesn't map it.
  [[nodiscard]] uint16_t glyphFor(const uint32_t cp) const {
    const auto it = cmap_.find(cp);
    return it == cmap_.end() ? 0 : it->second;
  }

  [[nodiscard]] uint16_t advance(const uint16_t gid) const { return advances_.at(gid); }

  // The simple glyphs `gid` is made of, in font units, compound glyphs resolved.
  std::vector<fill::Outline> outlines(const uint16_t gid) {
    std::vector<fill::Outline> out;
    resolve(gid, Affine{}, 0, out);
    return out;
  }

private:
  struct Affine {
    double a = 1, b = 0, c = 0, d = 1, e = 0, f = 0;
    [[nodiscard]] Affine after(const Affine& in) const {
      return {a * in.a + c * in.b, b * in.a + d * in.b, a * in.c + c * in.d, b * in.c + d * in.d,
              a * in.e + c * in.f + e, b * in.e + d * in.f + f};
    }
  };

  void seek(const uint32_t offset) {
    in_.clear();
    in_.seekg(offset);
  }

  const Table& table(const std::string& tag) const {
    const auto it = tables_.find(tag);
    if (it == tables_.end()) throw std::runtime_error("font has no '" + tag + "' table");
    return it->second;
  }

  void readDirectory() {
    seek(4);
    const uint16_t count = be::u16(in_);
    seek(12);
    for (uint16_t i = 0; i < count; ++i) {
      std::string tag(4, ' ');
      for (char& ch : tag) ch = static_cast<char>(be::u8(in_));
      be::u32(in_);  // checksum
      Table t;
      t.offset = be::u32(in_);
      t.length = be::u32(in_);
      tables_[tag] = t;
    }
  }

  void readCmap() {
    const uint32_t base = table("cmap").offset;
    seek(base + 2);
    const uint16_t count = be::u16(in_);
    uint32_t sub = 0;
    for (uint16_t i = 0; i < count; ++i) {
      const uint16_t platform = be::u16(in_), encoding = be::u16(in_);
      const uint32_t offset = be::u32(in_);
      if (platform == 0 && encoding == 4) sub = offset;
    }
    if (!sub) throw std::runtime_error("no format 12 cmap subtable");
    seek(base + sub);
    if (be::u16(in_) != 12) throw std::runtime_error("cmap subtable is not format 12");
    seek(base + sub + 12);
    const uint32_t groups = be::u32(in_);
    for (uint32_t g = 0; g < groups; ++g) {
      const uint32_t first = be::u32(in_), last = be::u32(in_), glyph = be::u32(in_);
      for (uint64_t cp = first; cp <= last; ++cp) cmap_[static_cast<uint32_t>(cp)] = static_cast<uint16_t>(glyph + (cp - first));
    }
  }

  void readLoca() {
    seek(table("maxp").offset + 4);
    numGlyphs_ = be::u16(in_);
    seek(table("head").offset + 50);
    const bool shortFormat = be::i16(in_) == 0;
    seek(table("loca").offset);
    std::vector<uint32_t> loca(numGlyphs_ + 1u);
    for (uint32_t& v : loca) v = shortFormat ? be::u16(in_) * 2u : be::u32(in_);
    const uint32_t glyf = table("glyf").offset;
    for (uint32_t i = 0; i < numGlyphs_; ++i) records_.push_back({glyf + loca[i], loca[i + 1] - loca[i]});
  }

  void readMetrics() {
    seek(table("hhea").offset + 34);
    const uint16_t longMetrics = be::u16(in_);
    seek(table("hmtx").offset);
    uint16_t last = 0;
    for (uint16_t i = 0; i < longMetrics; ++i) {
      last = be::u16(in_);
      be::i16(in_);
      advances_.push_back(last);
    }
    while (advances_.size() < numGlyphs_) advances_.push_back(last);
  }

  void resolve(const uint16_t gid, const Affine& m, const int depth, std::vector<fill::Outline>& out) {
    if (depth > 16 || gid >= records_.size()) throw std::runtime_error("bad compound glyph");
    const Table& r = records_[gid];
    if (r.length == 0) return;
    seek(r.offset);
    if (be::i16(in_) >= 0) {
      const provided::Outline simple = provided::readSimpleGlyph(in_, r.offset);
      if (simple.points.empty()) return;
      fill::Outline o;
      o.ends = simple.endPtsOfContours;
      for (const auto& p : simple.points) {
        o.points.push_back({m.a * p.x + m.c * p.y + m.e, m.b * p.x + m.d * p.y + m.f, p.onCurve});
      }
      out.push_back(std::move(o));
      return;
    }
    seek(r.offset + 10);
    std::vector<std::pair<uint16_t, Affine>> parts;
    uint16_t flags = 0;
    do {
      flags = be::u16(in_);
      const uint16_t child = be::u16(in_);
      const int x = (flags & 0x1) ? be::i16(in_) : be::i8(in_);
      const int y = (flags & 0x1) ? be::i16(in_) : be::i8(in_);
      Affine t;
      if (flags & 0x8) {
        t.a = t.d = be::f2dot14(in_);
      } else if (flags & 0x40) {
        t.a = be::f2dot14(in_);
        t.d = be::f2dot14(in_);
      } else if (flags & 0x80) {
        t.a = be::f2dot14(in_);
        t.b = be::f2dot14(in_);
        t.c = be::f2dot14(in_);
        t.d = be::f2dot14(in_);
      }
      t.e = x;
      t.f = y;
      if (flags & 0x800) {
        t.e = t.a * x + t.c * y;
        t.f = t.b * x + t.d * y;
      }
      parts.emplace_back(child, t);
    } while (flags & 0x20);
    for (const auto& [child, t] : parts) resolve(child, m.after(t), depth + 1, out);
  }

  std::ifstream in_;
  std::map<std::string, Table> tables_;
  std::unordered_map<uint32_t, uint16_t> cmap_;
  std::vector<Table> records_;
  std::vector<uint16_t> advances_;
  uint16_t numGlyphs_ = 0;
};

// UTF-8 bytes to code points. Malformed bytes become U+FFFD.
inline std::vector<uint32_t> decodeUtf8(const std::string& s) {
  std::vector<uint32_t> out;
  std::size_t i = 0;
  while (i < s.size()) {
    const auto b = static_cast<unsigned char>(s[i]);
    int extra = -1;
    uint32_t cp = 0;
    if (b < 0x80) extra = 0, cp = b;
    else if ((b >> 5) == 0x6) extra = 1, cp = b & 0x1F;
    else if ((b >> 4) == 0xE) extra = 2, cp = b & 0x0F;
    else if ((b >> 3) == 0x1E) extra = 3, cp = b & 0x07;
    bool ok = extra >= 0 && i + extra < s.size();
    for (int k = 1; ok && k <= extra; ++k) {
      const auto next = static_cast<unsigned char>(s[i + k]);
      ok = (next >> 6) == 0x2;
      cp = (cp << 6) | (next & 0x3F);
    }
    if (!ok) {
      out.push_back(0xFFFD);
      ++i;
      continue;
    }
    out.push_back(cp);
    i += 1 + extra;
  }
  return out;
}

}  // namespace font
