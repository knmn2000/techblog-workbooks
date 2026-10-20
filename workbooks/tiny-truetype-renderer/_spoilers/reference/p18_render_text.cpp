// Reference solution - checkpoint 18 (render a line of text).
// SPOILERS: try the checkpoint yourself first. Most of the work is in common/.

#include <cstdio>
#include <fstream>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>

#define CANVAS_PNG_IMPLEMENTATION
#include "common/font.h"

int main(int argc, char** argv) {
  if (argc != 3) return 2;
  try {
    std::ifstream input(argv[1]);
    std::unique_ptr<font::Font> font;
    std::unique_ptr<Canvas> canvas;
    double penX = 0, baseline = 0, scale = 1;
    RGB color{255, 255, 255};
    for (std::string line; std::getline(input, line);) {
      if (!line.empty() && line.back() == '\r') line.pop_back();
      std::istringstream words(line);
      std::string key;
      words >> key;
      if (key == "font") {
        std::string path;
        words >> path;
        font = std::make_unique<font::Font>(path);
      } else if (key == "canvas") {
        int w, h;
        words >> w >> h;
        canvas = std::make_unique<Canvas>(w, h);
      } else if (key == "pen") {
        words >> penX >> baseline >> scale;
      } else if (key == "color") {
        int r, g, b;
        words >> r >> g >> b;
        color = RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
      } else if (key == "text") {
        const std::string text = line.size() > 5 ? line.substr(5) : "";
        for (const uint32_t cp : font::decodeUtf8(text)) {
          const uint16_t gid = font->glyphFor(cp);
          for (const fill::Outline& o : font->outlines(gid)) {
            fill::fillOutline(*canvas, o, {penX, baseline, scale}, fill::Rule::NonZero, color);
          }
          penX += font->advance(gid) * scale;
        }
      }
    }
    return canvas->writePng(argv[2]) ? 0 : 1;
  } catch (const std::exception& e) {
    std::fprintf(stderr, "error: %s\n", e.what());
    return 1;
  }
}
