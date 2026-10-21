// Checkpoint 02 (Read the table directory): the program the checker runs.
//
// Problem:  problems/02-table-directory.md (also in the web problem book)
// Check:    .\check 02
//
// Boilerplate: the input and output are done here, and the project files declare what they
// need, named as the author names them. What's left to write is readTableDirectory, marked
// TODO in src/font/FontParser.cpp. Only the output is checked, so change anything you
// like.

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
