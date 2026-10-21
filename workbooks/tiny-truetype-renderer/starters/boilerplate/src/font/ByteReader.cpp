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
