// Checkpoint 01 - Read big-endian numbers
//
// Problem:  problems/01-byte-readers.md (also in the web problem book)
// Check:    .\check 01
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on the ByteReader functions marked TODO.
//
// This checkpoint is about writing the readers yourself, so don't include
// provided/BigEndian.h here. Later checkpoints may use it (or your own reader).

#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>

#include "NotImplemented.h"

// Throw this when a read needs bytes past the end of the file.
// The provided code catches it, writes `eof` and stops.
struct UnexpectedEof : std::runtime_error {
  UnexpectedEof() : std::runtime_error("unexpected EOF") {}
};

class ByteReader {
 public:
  explicit ByteReader(const std::string& path) : file_(path, std::ios::binary) {
    if (!file_) throw std::runtime_error("cannot open " + path);
  }

  // Moves to byte `offset`, counted from the start of the file.
  void jumpTo(uint32_t offset) {
    // TODO: move the read position of file_.
    throw NotImplemented("jumpTo");
  }

  // Moves `count` bytes forward from the current position.
  void skipBytes(uint32_t count) {
    // TODO: move the read position of file_.
    throw NotImplemented("skipBytes");
  }

  // Reads sizeof(T) bytes, most significant first, as a T (uint8_t ... int32_t).
  // Throws UnexpectedEof if the file ends before all the bytes are read.
  template <typename T>
  T readBigEndian() {
    // TODO: read the bytes one at a time with file_.get(), build the number,
    // and for signed T turn the bit pattern into a negative number when the
    // top bit is set (two's complement).
    throw NotImplemented("readBigEndian");
  }

  uint8_t readUint8() { return readBigEndian<uint8_t>(); }
  uint16_t readUint16() { return readBigEndian<uint16_t>(); }
  uint32_t readUint32() { return readBigEndian<uint32_t>(); }
  int8_t readInt8() { return readBigEndian<int8_t>(); }
  int16_t readInt16() { return readBigEndian<int16_t>(); }
  int32_t readInt32() { return readBigEndian<int32_t>(); }

  // Reads an F2Dot14: a 16-bit number with 14 fraction bits.
  double readF2Dot14() {
    // TODO: see "F2Dot14" on the problem page.
    throw NotImplemented("readF2Dot14");
  }

 private:
  std::ifstream file_;
};

// ---- Input/output (provided) -------------------------------------------------

namespace {

// k / 16384 has at most 14 digits after the point, so this prints it exactly.
std::string decimal(const double value) {
  std::ostringstream s;
  s << std::fixed << std::setprecision(14) << value;
  std::string text = s.str();
  text.erase(text.find_last_not_of('0') + 1);
  if (text.back() == '.') text.pop_back();
  return text == "-0" ? "0" : text;
}

// Runs one operation. Read operations write one line, `<op> <value>`.
// The value is read before anything is written, so a read that fails writes nothing.
// (The + in front of 8-bit values prints them as numbers, not characters.)
void run(ByteReader& reader, const std::string& op, std::istringstream& words, std::ostream& out) {
  const auto line = [&](const auto& value) { out << op << ' ' << value << '\n'; };
  if (op == "jump" || op == "skip") {
    uint32_t n = 0;
    words >> n;
    if (op == "jump") reader.jumpTo(n);
    else reader.skipBytes(n);
  } else if (op == "u8") {
    line(+reader.readUint8());
  } else if (op == "i8") {
    line(+reader.readInt8());
  } else if (op == "u16") {
    line(reader.readUint16());
  } else if (op == "i16") {
    line(reader.readInt16());
  } else if (op == "u32") {
    line(reader.readUint32());
  } else if (op == "i32") {
    line(reader.readInt32());
  } else if (op == "f2dot14") {
    line(decimal(reader.readF2Dot14()));
  } else if (!op.empty()) {
    throw std::runtime_error("unknown operation " + op);
  }
}

}  // namespace

// Usage: p01 <input-file> <output-file>
int main(int argc, char** argv) {
  if (argc != 3) {
    std::cerr << "usage: " << argv[0] << " <input-file> <output-file>\n";
    return 2;
  }
  std::ifstream input(argv[1]);
  std::ofstream output(argv[2]);
  if (!input || !output) {
    std::cerr << "cannot open " << argv[1] << " or " << argv[2] << "\n";
    return 2;
  }

  try {
    std::string line, keyword, path;
    std::getline(input, line);  // file <path>
    std::istringstream first(line);
    first >> keyword >> path;
    if (keyword != "file") throw std::runtime_error("the first line must be: file <path>");
    ByteReader reader(path);
    while (std::getline(input, line)) {  // one operation per line
      std::istringstream words(line);
      std::string op;
      words >> op;
      try {
        run(reader, op, words, output);
      } catch (const UnexpectedEof&) {
        output << "eof\n";  // a read ran past the end: report it and stop
        break;
      }
    }
  } catch (const NotImplemented& e) {
    std::cerr << "not implemented: " << e.what() << "\n";
    return 99;
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
