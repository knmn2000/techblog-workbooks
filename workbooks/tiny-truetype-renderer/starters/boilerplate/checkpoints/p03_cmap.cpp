// Checkpoint 03 (Map characters to glyphs (cmap format 12)): the program the checker runs.
//
// Problem:  problems/03-cmap.md (also in the web problem book)
// Check:    .\check 03
//
// Boilerplate: the input and output are done here, and the project files declare what they
// need, named as the author names them. What's left to write is loadUnicodeToGlyphCodeMap,
// marked TODO in src/font/Cmap.cpp. Only the output is checked, so change anything you
// like.

#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "font/Cmap.h"

namespace {

// table "<tag>" <checkSum> <offset> <length>
void addTable(const std::string& line, Tables& tables) {
  const std::size_t open = line.find('"');
  const std::size_t close = line.find('"', open + 1);
  if (open == std::string::npos || close == std::string::npos) throw std::runtime_error("bad line: " + line);
  TableRecord t;
  t.tag = line.substr(open + 1, close - open - 1);
  std::istringstream numbers(line.substr(close + 1));
  numbers >> t.checkSum >> t.offset >> t.length;
  tables[t.tag] = t;
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
    std::string path;
    Tables tables;
    std::vector<std::string> queries;  // `count` or `lookup U+XXXX`
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") words >> path;
      else if (keyword == "table") addTable(line, tables);
      else if (keyword == "count" || keyword == "lookup") queries.push_back(line);
    }
    ByteReader reader(path);

    std::unordered_map<uint32_t, uint32_t> glyphFor;
    try {
      glyphFor = loadUnicodeToGlyphCodeMap(reader, tables);
    } catch (const UnsupportedCmap&) {
      output << "unsupported\n";
      return 0;
    }
    for (const std::string& query : queries) {
      std::istringstream words(query);
      std::string keyword, codePoint;
      words >> keyword >> codePoint;
      if (keyword == "count") {
        output << "count " << glyphFor.size() << '\n';
      } else {
        const auto found = glyphFor.find(std::stoul(codePoint.substr(2), nullptr, 16));  // skip "U+"
        output << "lookup " << codePoint << ' ';
        if (found == glyphFor.end()) output << "none\n";
        else output << found->second << '\n';
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
