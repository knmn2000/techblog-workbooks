// Reference solution - checkpoint 02 (read the table directory).
// SPOILERS: try the checkpoint yourself first.

#include <cstdint>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "provided/BigEndian.h"

struct TableRecord {
  std::string tag;  // exactly 4 characters, trailing spaces included
  uint32_t checkSum = 0;
  uint32_t offset = 0;  // from the start of the file
  uint32_t length = 0;
};

std::vector<TableRecord> readTableDirectory(std::ifstream& font) {
  font.seekg(0);
  be::u32(font);  // scaler type: 0x00010000, 'true', ... (not needed)
  const uint16_t numTables = be::u16(font);
  font.seekg(6, std::ios::cur);  // searchRange, entrySelector, rangeShift

  std::vector<TableRecord> tables(numTables);
  for (TableRecord& t : tables) {
    for (int i = 0; i < 4; ++i) t.tag += static_cast<char>(be::u8(font));
    t.checkSum = be::u32(font);
    t.offset = be::u32(font);
    t.length = be::u32(font);
  }
  return tables;
}

// ---- Input/output (same as the starter) --------------------------------------

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
      if (keyword != "font") continue;
      std::ifstream font(path, std::ios::binary);
      if (!font) throw std::runtime_error("cannot open font file " + path);
      const std::vector<TableRecord> tables = readTableDirectory(font);
      output << "tables " << tables.size() << '\n';
      for (const TableRecord& t : tables)
        output << "table \"" << t.tag << "\" " << t.checkSum << ' ' << t.offset << ' ' << t.length << '\n';
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
