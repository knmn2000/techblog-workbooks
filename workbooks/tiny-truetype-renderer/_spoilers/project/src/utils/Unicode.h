#pragma once
// Assignment 18: text arrives as UTF-8 bytes; the font is looked up by code point.

#include <cstdint>
#include <string>
#include <vector>

// UTF-8 bytes to code points. A malformed byte becomes U+FFFD, the replacement character.
inline std::vector<uint32_t> utf8ToCodepoints(const std::string& text) {
  std::vector<uint32_t> out;
  std::size_t i = 0;
  while (i < text.size()) {
    const auto b = static_cast<unsigned char>(text[i]);
    int extra = -1;  // continuation bytes after this one
    uint32_t cp = 0;
    if (b < 0x80) extra = 0, cp = b;
    else if ((b >> 5) == 0x6) extra = 1, cp = b & 0x1F;
    else if ((b >> 4) == 0xE) extra = 2, cp = b & 0x0F;
    else if ((b >> 3) == 0x1E) extra = 3, cp = b & 0x07;
    bool ok = extra >= 0 && i + extra < text.size();
    for (int k = 1; ok && k <= extra; ++k) {
      const auto next = static_cast<unsigned char>(text[i + k]);
      ok = (next >> 6) == 0x2;
      cp = (cp << 6) | (next & 0x3F);
    }
    if (!ok) {
      out.push_back(0xFFFD);
      ++i;
      continue;
    }
    out.push_back(cp);
    i += 1 + extra;
  }
  return out;
}
