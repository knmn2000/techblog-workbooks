// Checkpoint 07 (decode simple glyphs): prints each glyph in a test input.
// Glyphs are decoded by src/font/GlyphParser into the types in src/Glyph.h.

#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>

#include "font/GlyphParser.h"

namespace {

void write(std::ostream& out, const uint32_t id, const Glyph& g) {
  out << "glyph " << id;
  if (g.kind == Glyph::Kind::Empty) {
    out << " empty\n";
    return;
  }
  if (g.kind == Glyph::Kind::Compound) {
    out << " compound\n";
    return;
  }
  const BoundingRect& b = g.bounds;
  out << " contours " << g.numberOfContours << " bbox " << b.xMin << ' ' << b.yMin << ' ' << b.xMax << ' '
      << b.yMax << "\nends";
  const GlyphComponent& outline = g.components.front();
  for (const int end : outline.endPtsOfContours) out << ' ' << end;
  out << "\npoints";
  for (const GlyphPoint& p : outline.points)
    out << ' ' << static_cast<int>(p.x) << ' ' << static_cast<int>(p.y) << (p.onCurve ? " on" : " off");
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
    std::unique_ptr<ByteReader> font;
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") {
        std::string path;
        words >> path;
        font = std::make_unique<ByteReader>(path);
      } else if (keyword == "glyph") {
        uint32_t id = 0, offset = 0, length = 0;
        words >> id >> offset >> length;
        if (!font) throw std::runtime_error("a `glyph` line before the `font` line");
        write(output, id, readGlyph(*font, offset, length));
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
