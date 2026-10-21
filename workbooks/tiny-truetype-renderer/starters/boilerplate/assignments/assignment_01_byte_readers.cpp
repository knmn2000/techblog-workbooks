// ======================================================================================
// Assignment 01: Read big-endian numbers
// Problem: problems/01-byte-readers.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The checker runs this program for assignment 01 as `build/solutions/assignment_01.exe
//   <input-file> <output-file>`. It reads a test input, calls your code and writes the
//   answer to the output file, and the checker compares that answer with the expected one.
//   Run `.\check 01`, or use Run and Submit in the book.
//
// Your job:
//   The Boilerplate gives you this program finished. You fill in the TODOs in this
//   assignment's other files.
//
// The other files of this assignment:
//   You also write src/font/ByteReader.h and src/font/ByteReader.cpp in this assignment;
//   each one gives its job at the top.
//   Include them by their path under src/, e.g. #include "font/ByteReader.h".
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

#include "font/ByteReader.h"

namespace {

// k / 16384 has at most 14 digits after the point, so 14 decimals print it without rounding.
std::string decimal(const double value) {
  std::ostringstream s;
  s << std::fixed << std::setprecision(14) << value;
  std::string text = s.str();
  text.erase(text.find_last_not_of('0') + 1);
  if (text.back() == '.') text.pop_back();
  return text == "-0" ? "0" : text;
}

// Runs one operation. Read operations write one line, `<op> <value>`.
// It reads the value before writing anything, so a read that fails writes nothing.
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
    std::getline(input, line);
    std::istringstream first(line);
    first >> keyword >> path;
    if (keyword != "file") throw std::runtime_error("the first line must be: file <path>");
    ByteReader reader(path);
    while (std::getline(input, line)) {
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
  } catch (const std::exception& e) {
    const std::string what = e.what();
    if (what.rfind("not implemented", 0) == 0) {  // a TODO in your project: the checker names it
      std::cerr << what << "\n";
      return 99;
    }
    std::cerr << "error: " << what << "\n";
    return 1;
  }
  return 0;
}
