#pragma once
// ======================================================================================
// Assignment 06: Draw on a framebuffer
// Problem: problems/06-canvas.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   A picture in memory, one colour per pixel, with three ways to draw on it (one pixel, a
//   filled rectangle, a thick line) and a way to save it as a PNG. Every picture from
//   assignment 08 on is drawn on it: outlines in 08 and 11, filled glyphs in 14, 16 and
//   17, and a line of text in 18.
//
// Your job:
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

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
