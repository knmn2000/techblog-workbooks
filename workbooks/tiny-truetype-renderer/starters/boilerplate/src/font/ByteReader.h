#pragma once
// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Your reader for big-endian numbers at any position in a font file: signed and unsigned
//   integers of 8, 16 and 32 bits, and F2Dot14 fixed point. The table directory, `cmap`,
//   `loca`, the metrics and the glyph outlines all get read through it.
//
// Your job:
//   Declare a reader that opens a binary file and tracks a current position. It needs
//   functions to jump to an absolute offset, skip forward, read each of the six integer
//   types (`u8` to `i32`) big-endian, and read an F2Dot14 as a floating-point number. Also
//   declare how a read reports running out of bytes, with an exception type for instance.
//   The Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>      // uint8_t to int32_t: what the six readers return
#include <fstream>      // std::ifstream file_: the open file
#include <stdexcept>    // std::runtime_error under UnexpectedEof; std::logic_error in the TODO
#include <string>       // std::string: the path the constructor takes
#include <type_traits>  // std::is_integral_v in readBigEndian's static_assert

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
    // TODO: read sizeof(T) bytes with nextByte(), most significant first, and build the
    // number. For a signed T, see "Signed numbers: two's complement" on the problem page.
    throw std::logic_error("not implemented: readBigEndian");
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
