// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The finished command-line program: `tiny_ttf <font.ttf> "<text>" <out.png>` draws a
//   line of text with a TrueType font into a PNG sized to fit it, using your
//   `TextRenderer`. An optional fourth argument sets the text height in pixels (64 by
//   default).
//
// Your job:
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

// tiny_ttf: draws a line of text with a TrueType font and saves it as a PNG.
//
//   tiny_ttf <font.ttf> "<text>" <out.png> [pixel-height]
//
// The picture fits the text, with white glyphs on black; pixel-height (default 64) is the
// distance from the font's ascent to its descent.

#include <cmath>
#include <exception>
#include <iostream>
#include <string>

#include "TextRenderer.h"

int main(int argc, char** argv) {
  if (argc < 4 || argc > 5) {
    std::cerr << "usage: " << argv[0] << " <font.ttf> \"<text>\" <out.png> [pixel-height]\n";
    return 2;
  }
  try {
    const std::string fontPath = argv[1], text = argv[2], outPath = argv[3];
    const double pixelHeight = argc == 5 ? std::stod(argv[4]) : 64.0;

    TextRenderer renderer(fontPath);
    const HorizontalMetrics& m = renderer.metrics();
    const double scale = pixelHeight / (m.ascent - m.descent);
    const int margin = static_cast<int>(std::lround(pixelHeight / 4));
    const int width = static_cast<int>(std::ceil(renderer.measureText(text, scale))) + 2 * margin;
    const int height = static_cast<int>(std::ceil(pixelHeight)) + 2 * margin;

    FrameBufferCanvas canvas(width, height);
    renderer.drawText(canvas, text, margin, margin + m.ascent * scale, scale, RGB{255, 255, 255});
    canvas.writePng(outPath);
    std::cout << "wrote " << outPath << " (" << width << " x " << height << ")\n";
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
