// ======================================================================================
// Assignment 07: Decode simple glyphs
// Problem: problems/07-simple-glyph.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This is the program the checker runs for assignment 07, as
//   `build/solutions/assignment_07.exe <input-file> <output-file>`: it reads a test input,
//   calls your code and writes the answer to the output file. Only that output is checked.
//   Check it with `.\check 07`, or Run and Submit in the book.
//
// Your job:
//   In the Boilerplate this program is already written: it reads the input, calls your
//   code and writes the answer. Your work is in this assignment's other files, where it
//   says TODO.
//
// The other files of this assignment:
//   This assignment also has you write src/GlyphComponent.h, src/Glyph.h,
//   src/font/GlyphParser.h and src/font/GlyphParser.cpp; each says its job at the top.
//   Earlier files you can use: src/font/ByteReader.h.
//   Include them by their path under src/, e.g. #include "GlyphComponent.h".
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

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
    const std::string what = e.what();
    if (what.rfind("not implemented", 0) == 0) {  // a TODO in your project: the checker names it
      std::cerr << what << "\n";
      return 99;
    }
    std::cerr << "error: " << what << "\n";
    return 1;
  }
  return 0;
}
