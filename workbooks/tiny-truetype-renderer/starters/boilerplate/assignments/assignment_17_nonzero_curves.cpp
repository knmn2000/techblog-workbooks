// ======================================================================================
// Assignment 17: Fill a glyph: non-zero rule
// Problem: problems/17-nonzero-curves.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 17 as `build/solutions/assignment_17.exe
//   <input-file> <output-file>`. It reads a test input, calls your code and writes the
//   answer to the output file, and the checker compares that answer with the expected one.
//   Run `.\check 17`, or use Run and Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished: it reads the input, calls your code
//   and writes the answer. You fill in the TODOs in this assignment's other files.
//
// The other files of this assignment:
//   It adds to src/render/NonZero.h, which you started earlier: Keep the non-zero fill
//   function you declared in assignment 16. Your program now also passes it outlines with
//   off-curve points, so it has to handle curves. You have nothing new to declare unless
//   you add a helper for curves.
//   It adds to src/render/NonZero.cpp, which you started earlier: Make the non-zero fill
//   work for curved outlines. Every crossing on a curve needs the direction the curve runs
//   at that row. Once you split each curve where its y turns around, each piece runs one
//   way, and comparing its end's y with its start's y gives that direction. If your
//   `render/Scanline` from assignment 14 already splits curves and gives every crossing
//   its direction, your assignment 16 fill may pass as it is; otherwise add what's
//   missing, in `render/Scanline` or here.
//   Earlier files you can use: src/render/Scanline.h and src/utils/Geometry.h.
//   Include them by their path under src/, e.g. #include "render/NonZero.h".
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
#include <vector>

#include "render/NonZero.h"

int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "usage: " << argv[0] << " <input-file> <output-file.png>\n";
    return 2;
  }
  std::ifstream input(argv[1]);
  if (!input) {
    std::cerr << "cannot open " << argv[1] << "\n";
    return 2;
  }
  try {
    std::unique_ptr<FrameBufferCanvas> canvas;
    Placement place;
    RGB color{255, 255, 255};
    std::vector<GlyphComponent> outlines;  // each one filled on its own
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      if (!(words >> keyword)) continue;
      if (keyword == "canvas") {  // canvas <w> <h>
        int w = 0, h = 0;
        words >> w >> h;
        canvas = std::make_unique<FrameBufferCanvas>(w, h);
      } else if (keyword == "place") {  // place <x0> <baseline> <scale>
        words >> place.x0 >> place.baseline >> place.scale;
      } else if (keyword == "color") {  // color <r> <g> <b>
        int r = 0, g = 0, b = 0;
        words >> r >> g >> b;
        color = RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
      } else if (keyword == "outline") {  // then `ends ...` and `points x y on|off ...`
        outlines.emplace_back();
      } else if (keyword == "ends" && !outlines.empty()) {
        for (int e; words >> e;) outlines.back().endPtsOfContours.push_back(e);
      } else if (keyword == "points" && !outlines.empty()) {
        GlyphPoint p;
        for (std::string on; words >> p.x >> p.y >> on;) {
          p.onCurve = on == "on";
          outlines.back().points.push_back(p);
        }
      }
    }
    if (!canvas) throw std::runtime_error("no `canvas` line in the input");
    for (const GlyphComponent& outline : outlines) renderGlyphByNonZero(*canvas, outline, place, color);
    canvas->writePng(argv[2]);
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
