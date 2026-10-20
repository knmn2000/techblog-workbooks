// Checkpoint 02 - Read the table directory
//
// Problem:  problems/02-table-directory.md (also in the web problem book)
// Check:    .\check 02
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on readTableDirectory().

#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "NotImplemented.h"
#include "provided/BigEndian.h"  // optional: be::u8(file), be::u16(file), be::u32(file), ...

struct TableRecord {
  std::string tag;  // exactly 4 characters, trailing spaces included
  uint32_t checkSum = 0;
  uint32_t offset = 0;  // from the start of the file
  uint32_t length = 0;
};

// Returns every record of the font's table directory, in any order.
std::vector<TableRecord> readTableDirectory(std::ifstream& font) {
  // TODO: read the header, then one record per table (layout on the problem page).
  throw NotImplemented("readTableDirectory");
}

// ---- Input/output (provided) -------------------------------------------------

// Usage: p02 <input-file> <output-file>
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
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword, path;
      words >> keyword >> path;
      if (keyword != "font") continue;  // font <path>
      std::ifstream font(path, std::ios::binary);
      if (!font) throw std::runtime_error("cannot open font file " + path);
      const std::vector<TableRecord> tables = readTableDirectory(font);
      output << "tables " << tables.size() << '\n';
      for (const TableRecord& t : tables)
        output << "table \"" << t.tag << "\" " << t.checkSum << ' ' << t.offset << ' ' << t.length << '\n';
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
