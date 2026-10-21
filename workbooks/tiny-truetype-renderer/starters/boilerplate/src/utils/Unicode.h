#pragma once
// ======================================================================================
// Assignment 18: Render a line of text
// Problem: problems/18-render-text.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   It turns UTF-8 text into Unicode code points, the numbers a font's cmap maps to
//   glyphs. Your `TextRenderer` decodes every line of text with it.
//
// Your job:
//   Write a function that decodes a string of UTF-8 bytes into a list of code points, for
//   characters of 1 to 4 bytes (Output, step 1, lists the byte patterns). It is short
//   enough to write in the header itself. The Boilerplate gives you the declarations; fill
//   in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

// UTF-8 bytes to code points. A malformed byte becomes U+FFFD, the replacement character.
inline std::vector<uint32_t> utf8ToCodepoints(const std::string& text) {
  // TODO: see step 1, "Decode UTF-8", under "The problem" on the problem page.
  throw std::logic_error("not implemented: utf8ToCodepoints");
}
