// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The reader's implementation: opening the file, moving around in it, and turning its
//   bytes into numbers. Every later assignment that reads the font runs through this code,
//   so a mistake here shows up everywhere.
//
// Your job:
//   Implement the reader: open the file in binary mode, move the position for jumps and
//   skips, and build each number from its bytes, most significant first, with two's
//   complement for the signed types. A read that needs a byte past the end of the file
//   must report it instead of returning a value. The Boilerplate has the declarations
//   written: fill in what's marked TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include "font/ByteReader.h"

ByteReader::ByteReader(const std::string& path) : file_(path, std::ios::binary) {
  if (!file_) throw std::runtime_error("cannot open " + path);
}

void ByteReader::jumpTo(const uint32_t offset) {
  // TODO: move the read position of file_. A jump must work even after a read ran past the end.
  throw std::logic_error("not implemented: jumpTo");
}

void ByteReader::skipBytes(const uint32_t count) {
  // TODO: move the read position of file_ forward.
  throw std::logic_error("not implemented: skipBytes");
}

double ByteReader::readF2Dot14() {
  // TODO: see "F2Dot14" on the problem page.
  throw std::logic_error("not implemented: readF2Dot14");
}

uint8_t ByteReader::nextByte() {
  // TODO: one byte with file_.get(); at the end of the file, throw UnexpectedEof.
  throw std::logic_error("not implemented: nextByte");
}
