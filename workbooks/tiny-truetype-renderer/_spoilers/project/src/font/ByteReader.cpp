#include "font/ByteReader.h"

ByteReader::ByteReader(const std::string& path) : file_(path, std::ios::binary) {
  if (!file_) throw std::runtime_error("cannot open " + path);
}

void ByteReader::jumpTo(const uint32_t offset) {
  file_.clear();  // a jump always starts from a clean state, even after reading past the end
  file_.seekg(offset, std::ios::beg);
}

void ByteReader::skipBytes(const uint32_t count) { file_.seekg(count, std::ios::cur); }

double ByteReader::readF2Dot14() { return readInt16() / 16384.0; }

uint8_t ByteReader::nextByte() {
  const int c = file_.get();
  if (c == std::char_traits<char>::eof()) throw UnexpectedEof();
  return static_cast<uint8_t>(c);
}
