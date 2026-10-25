#pragma once
// ======================================================================================
// Assignment 06: Draw on a framebuffer
// Problem: problems/06-canvas.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   A picture in memory, one colour per pixel, with operations to paint a pixel, fill a
//   rectangle, draw a thick line and save a PNG. Outlines (08, 11), filled glyphs (14, 16,
//   17) and the line of text in 18 all end up drawn on it.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>  // uint8_t: one byte per colour channel in RGB
#include <string>   // std::string: the path writePng writes to
#include <vector>   // std::vector<RGB>: the pixels, row by row

struct RGB {
  uint8_t r = 0, g = 0, b = 0;
  bool operator==(const RGB&) const = default;
};

class FrameBufferCanvas {
 public:
  FrameBufferCanvas(int width, int height);  // every pixel starts black

  [[nodiscard]] int width() const { return width_; }
  [[nodiscard]] int height() const { return height_; }

  // One pixel; (0, 0) is the top-left corner. It ignores pixels outside the canvas.
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
