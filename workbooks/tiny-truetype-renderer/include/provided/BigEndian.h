#pragma once
// Provided, optional: big-endian reads from a stream - what checkpoint 01 builds.
// If you've done checkpoint 01, use your own reader instead.

#include <cstdint>
#include <istream>
#include <stdexcept>
#include <string>

namespace be {

inline uint8_t u8(std::istream& in) {
  const int c = in.get();
  if (c == std::char_traits<char>::eof()) throw std::runtime_error("unexpected end of file");
  return static_cast<uint8_t>(c);
}

inline uint16_t u16(std::istream& in) {
  const uint16_t high = u8(in);
  return static_cast<uint16_t>(high << 8 | u8(in));
}

inline uint32_t u32(std::istream& in) {
  const uint32_t high = u16(in);
  return high << 16 | u16(in);
}

inline int8_t i8(std::istream& in) { return static_cast<int8_t>(u8(in)); }
inline int16_t i16(std::istream& in) { return static_cast<int16_t>(u16(in)); }
inline int32_t i32(std::istream& in) { return static_cast<int32_t>(u32(in)); }
inline float f2dot14(std::istream& in) { return static_cast<float>(i16(in)) / 16384.0f; }

}  // namespace be
