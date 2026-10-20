// Checkpoint 09 - Resolve compound glyphs
//
// Problem:  problems/09-compound-glyph.md (also in the web problem book)
// Check:    .\check 09
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on resolveGlyph().

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

#include "NotImplemented.h"
#include "provided/BigEndian.h"   // optional: be::u16(file), be::i8(file), be::f2dot14(file), ...
#include "provided/SimpleGlyph.h" // optional: provided::readSimpleGlyph (checkpoint 07's job)

// One simple glyph's outline. Coordinates are doubles because transforms can make
// them fractional.
using provided::Outline;  // { std::vector<int> endPtsOfContours; std::vector<OutlinePoint> points; }
                          // OutlinePoint: { double x, y; bool onCurve; }

struct GlyphRecord {
  uint32_t offset = 0;  // where the glyph's record starts in the file
  uint32_t length = 0;  // 0 = the glyph has no outline
};

// Returns the outlines of every simple glyph that `glyphId` is made of, in final
// position, in depth-first order. `records` holds every glyph the input listed.
std::vector<Outline> resolveGlyph(std::ifstream& file, const std::map<uint32_t, GlyphRecord>& records,
                                  uint32_t glyphId) {
  // TODO: read the component records and apply their transforms (see the problem page).
  throw NotImplemented("resolveGlyph");
}

// ---- Input/output (provided) -------------------------------------------------

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

// Usage: p09 <input-file> <output-file>
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
      if (keyword == "font") {  // font <path>
        std::string path;
        words >> path;
        font = std::ifstream(path, std::ios::binary);
        if (!font) throw std::runtime_error("cannot open font file " + path);
        records.clear();
      } else if (keyword == "glyph") {  // glyph <id> <offset> <length>
        uint32_t id = 0;
        GlyphRecord r;
        words >> id >> r.offset >> r.length;
        records[id] = r;
      } else if (keyword == "decode") {  // decode <id>
        uint32_t id = 0;
        words >> id;
        font.clear();
        write(output, id, resolveGlyph(font, records, id));
      }
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
