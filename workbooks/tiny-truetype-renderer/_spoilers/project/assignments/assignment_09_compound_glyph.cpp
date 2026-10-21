// Assignment 09 (resolve compound glyphs): prints the simple parts of each glyph a test
// input asks about. The resolving is src/font/CompoundGlyph.

#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "font/CompoundGlyph.h"

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

void write(std::ostream& out, const uint32_t id, const std::vector<GlyphComponent>& parts) {
  out << "glyph " << id << " components " << parts.size() << '\n';
  for (const GlyphComponent& part : parts) {
    out << "ends";
    for (const int e : part.endPtsOfContours) out << ' ' << e;
    out << "\npoints";
    for (const GlyphPoint& p : part.points) out << ' ' << number(p.x) << ' ' << number(p.y) << (p.onCurve ? " on" : " off");
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
    std::unique_ptr<ByteReader> font;
    std::map<uint32_t, GlyphLocation> locations;
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") {
        std::string path;
        words >> path;
        font = std::make_unique<ByteReader>(path);
        locations.clear();
      } else if (keyword == "glyph") {
        uint32_t id = 0;
        GlyphLocation at;
        words >> id >> at.offset >> at.length;
        locations[id] = at;
      } else if (keyword == "decode") {
        uint32_t id = 0;
        words >> id;
        if (!font) throw std::runtime_error("a `decode` line before the `font` line");
        write(output, id, resolveGlyph(*font, locations, id));
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
