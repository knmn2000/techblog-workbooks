#pragma once
// Checkpoint 18: text arrives as UTF-8 bytes; the font is looked up by code point.

#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>

// UTF-8 bytes to code points. A malformed byte becomes U+FFFD, the replacement character.
inline std::vector<uint32_t> utf8ToCodepoints(const std::string& text) {
  // TODO: see step 1, "Decode UTF-8", under "The problem" on the problem page.
  throw std::logic_error("not implemented: utf8ToCodepoints");
}
