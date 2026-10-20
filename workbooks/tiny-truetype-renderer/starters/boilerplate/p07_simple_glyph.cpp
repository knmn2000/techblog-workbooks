// Checkpoint 07 - Decode simple glyphs
//
// Problem:  problems/07-simple-glyph.md (also in the web problem book)
// Check:    .\check 07
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on decodeGlyph().

#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "NotImplemented.h"
#include "provided/BigEndian.h"  // optional: be::u8(file), be::u16(file), be::i16(file), ...

struct Point {
  int x = 0;
  int y = 0;
  bool onCurve = false;
};

struct DecodedGlyph {
  enum class Kind { Empty, Compound, Simple };
  Kind kind = Kind::Empty;

  // Only used when kind == Simple.
  int numberOfContours = 0;
  int xMin = 0, yMin = 0, xMax = 0, yMax = 0;
  std::vector<int> endPtsOfContours;  // in file order
  std::vector<Point> points;          // absolute coordinates in font units
};

// The glyph's record starts at byte `offset` of `file` and is `length` bytes long.
DecodedGlyph decodeGlyph(std::ifstream& file, uint32_t offset, uint32_t length) {
  // TODO: decode the record (layout and rules are on the problem page).
  throw NotImplemented("decodeGlyph");
}

// ---- Input/output (provided) -------------------------------------------------

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

// Usage: p07 <input-file> <output-file>
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
      if (keyword == "font") {  // font <path>: the file the following glyph lines refer to
        std::string path;
        words >> path;
        font = std::ifstream(path, std::ios::binary);
        if (!font) throw std::runtime_error("cannot open font file " + path);
      } else if (keyword == "glyph") {  // glyph <id> <offset> <length>
        uint32_t id = 0, offset = 0, length = 0;
        words >> id >> offset >> length;
        font.clear();  // forget any end-of-file state left by the previous glyph
        write(output, id, decodeGlyph(font, offset, length));
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
