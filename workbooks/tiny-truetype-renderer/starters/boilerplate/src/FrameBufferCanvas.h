#pragma once
// Checkpoint 06: a picture in memory, a few ways to draw on it, and PNG output.

#include <cstdint>
#include <string>
#include <vector>

struct RGB {
  uint8_t r = 0, g = 0, b = 0;
  bool operator==(const RGB&) const = default;
};

class FrameBufferCanvas {
 public:
  FrameBufferCanvas(int width, int height);  // every pixel starts black

  [[nodiscard]] int width() const { return width_; }
  [[nodiscard]] int height() const { return height_; }

  // One pixel; (0, 0) is the top-left corner. Pixels outside the canvas are ignored.
  void set(int x, int y, RGB color);
  [[nodiscard]] RGB get(int x, int y) const;

  // A w x h rectangle centred on (cx, cy): columns cx - w/2 ... cx - w/2 + w - 1, rows likewise.
  void drawRect(int cx, int cy, int w, int h, RGB color);

  // A line from (ax, ay) to (bx, by), both ends included, drawn as thickness x thickness squares.
  void drawLine(int ax, int ay, int bx, int by, int thickness, RGB color);

  void writePng(const std::string& path) const;  // throws if the file can't be written

 private:
  int width_;
  int height_;
  std::vector<RGB> pixels_;  // row by row, top row first
};
