#pragma once
// Checkpoint 01: the numbers a font file is made of.

#include <cstdint>
#include <fstream>
#include <stdexcept>
#include <string>
#include <type_traits>

// Thrown when a read needs bytes past the end of the file.
struct UnexpectedEof : std::runtime_error {
  UnexpectedEof() : std::runtime_error("unexpected EOF") {}
};

// Reads a binary file from any position. Every number in a font is stored big-endian:
// most significant byte first.
class ByteReader {
 public:
  explicit ByteReader(const std::string& path);

  void jumpTo(uint32_t offset);    // to a position counted from the start of the file
  void skipBytes(uint32_t count);  // forward from the current position

  // An integer of 1 to 4 bytes; signed types are two's complement.
  template <typename T>
  T readBigEndian() {
    static_assert(std::is_integral_v<T> && sizeof(T) <= 4);
    uint64_t value = 0;
    for (std::size_t i = 0; i < sizeof(T); ++i) value = value << 8 | nextByte();
    if constexpr (std::is_signed_v<T>) {
      const uint64_t range = uint64_t{1} << (8 * sizeof(T));  // 2^bits
      if (value >= range / 2) return static_cast<T>(static_cast<int64_t>(value) - static_cast<int64_t>(range));
    }
    return static_cast<T>(value);
  }

  uint8_t readUint8() { return readBigEndian<uint8_t>(); }
  uint16_t readUint16() { return readBigEndian<uint16_t>(); }
  uint32_t readUint32() { return readBigEndian<uint32_t>(); }
  int8_t readInt8() { return readBigEndian<int8_t>(); }
  int16_t readInt16() { return readBigEndian<int16_t>(); }
  int32_t readInt32() { return readBigEndian<int32_t>(); }

  // A 2.14 fixed-point number: a signed 16-bit integer divided by 2^14.
  double readF2Dot14();

 private:
  uint8_t nextByte();  // throws UnexpectedEof at the end of the file

  std::ifstream file_;
};
