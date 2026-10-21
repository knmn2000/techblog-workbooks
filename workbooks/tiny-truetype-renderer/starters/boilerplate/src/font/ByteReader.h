#pragma once
// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Reading big-endian numbers from any position in a font file: unsigned and signed
//   integers of 8, 16 and 32 bits, and F2Dot14 fixed point. Every later assignment that
//   reads the font reads it through this: assignment 02 the table directory, 03 to 05 the
//   `cmap`, `loca` and metrics tables, and 07 and 09 the glyph outlines.
//
// Your job:
//   Declare a reader that opens a binary file and keeps a current position. It needs a way
//   to jump to an absolute offset, skip forward, read each of the six integer types (`u8`
//   to `i32`) big-endian, and read an F2Dot14 as a floating-point number, plus a way to
//   report that a read ran out of bytes (an exception type, for example). The Boilerplate
//   has the declarations written: fill in what's marked TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

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
