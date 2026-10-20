#pragma once
// Reference input reading for the fill checkpoints (14, 16, 17). SPOILERS.
//
//   canvas <w> <h>
//   place <x0> <baseline> <scale>
//   color <r> <g> <b>
//   outline            (then `ends ...` and `points x y on|off ...`; repeatable)

#include <cstdio>
#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "fill.h"

namespace fill {

struct Scene {
  int width = 0, height = 0;
  Placement place;
  RGB color{255, 255, 255};
  std::vector<Outline> outlines;
};

inline Scene readScene(const std::string& path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error("cannot open " + path);
  Scene s;
  for (std::string line; std::getline(in, line);) {
    std::istringstream words(line);
    std::string key;
    words >> key;
    if (key == "canvas") {
      words >> s.width >> s.height;
    } else if (key == "place") {
      words >> s.place.x0 >> s.place.baseline >> s.place.scale;
    } else if (key == "color") {
      int r, g, b;
      words >> r >> g >> b;
      s.color = RGB{static_cast<uint8_t>(r), static_cast<uint8_t>(g), static_cast<uint8_t>(b)};
    } else if (key == "outline") {
      s.outlines.emplace_back();
    } else if (key == "ends") {
      for (int e; words >> e;) s.outlines.back().ends.push_back(e);
    } else if (key == "points") {
      Point p;
      std::string on;
      while (words >> p.x >> p.y >> on) {
        p.onCurve = on == "on";
        s.outlines.back().points.push_back(p);
      }
    }
  }
  return s;
}

inline int run(int argc, char** argv, const Rule rule) {
  if (argc != 3) return 2;
  try {
    const Scene s = readScene(argv[1]);
    Canvas canvas(s.width, s.height);
    for (const Outline& o : s.outlines) fillOutline(canvas, o, s.place, rule, s.color);
    return canvas.writePng(argv[2]) ? 0 : 1;
  } catch (const std::exception& e) {
    fprintf(stderr, "error: %s\n", e.what());
    return 1;
  }
}

}  // namespace fill
