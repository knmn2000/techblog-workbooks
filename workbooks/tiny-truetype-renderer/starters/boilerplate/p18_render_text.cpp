// Checkpoint 18 - Render a line of text
//
// Problem:  problems/18-render-text.md (also in the web problem book)
// Check:    .\check 18
//
// The capstone: everything from checkpoints 02-17 in one program. Only the picture
// is checked, so structure it however you like; copying in your own earlier
// solutions is the intended route. The input/output code at the bottom is provided.

#include <cstdint>
#include <fstream>
#include <iostream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#define CANVAS_PNG_IMPLEMENTATION
#include "NotImplemented.h"
#include "provided/BigEndian.h"   // optional: big-endian reads (checkpoint 01)
#include "provided/Canvas.h"      // Canvas: set(x, y, rgb), drawSpan(row, x0, x1, rgb), writePng(path)
#include "provided/SimpleGlyph.h" // optional: provided::readSimpleGlyph (checkpoint 07)

// Draws `text` (UTF-8) with the font at `fontPath`. The first glyph's origin is at
// pixel position (penX, baseline); `scale` is pixels per font unit; each glyph moves
// the pen right by its advance width times `scale`. Returns the pen x after the text.
double drawText(Canvas& canvas, const std::string& fontPath, const std::string& text, double penX,
                double baseline, double scale, RGB color) {
  // TODO: cmap, loca, hmtx, glyphs (compound ones too) and a non-zero fill
  // (see the problem page).
  throw NotImplemented("drawText");
}

// ---- Input/output (provided) -------------------------------------------------

// Usage: p18 <input-file> <output-png>
int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "usage: " << argv[0] << " <input-file> <output-png>\n";
    return 2;
  }
  std::ifstream input(argv[1]);
  if (!input) {
    std::cerr << "cannot open " << argv[1] << "\n";
    return 2;
  }
  try {
    std::string fontPath;
    std::unique_ptr<Canvas> canvas;
    double penX = 0, baseline = 0, scale = 1;
    RGB color{255, 255, 255};
    for (std::string line; std::getline(input, line);) {
      if (!line.empty() && line.back() == '\r') line.pop_back();
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") {  // font <path>
        words >> fontPath;
      } else if (keyword == "canvas") {  // canvas <width> <height>
        int w = 0, h = 0;
        words >> w >> h;
        canvas = std::make_unique<Canvas>(w, h);
      } else if (keyword == "pen") {  // pen <x> <baseline> <scale>
        words >> penX >> baseline >> scale;
      } else if (keyword == "color") {  // color <r> <g> <b>
        int r, g, b;
        words >> r >> g >> b;
        color = RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
      } else if (keyword == "text") {  // text <UTF-8 text to the end of the line>
        const std::string text = line.size() > 5 ? line.substr(5) : "";
        penX = drawText(*canvas, fontPath, text, penX, baseline, scale, color);
      }
    }
    if (!canvas || !canvas->writePng(argv[2])) throw std::runtime_error("cannot write the PNG");
  } catch (const NotImplemented& e) {
    std::cerr << "not implemented: " << e.what() << "\n";
    return 99;
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
