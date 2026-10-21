// Checkpoint 02 (read the table directory): lists the tables of each font in a test input.
// The directory is read by src/font/FontParser.

#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "font/FontParser.h"

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
      ByteReader reader(path);
      const std::vector<TableRecord> tables = readTableDirectory(reader);
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
