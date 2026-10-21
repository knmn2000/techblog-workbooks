// ======================================================================================
// Assignment 05: Read the horizontal metrics
// Problem: problems/05-metrics.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This is the program the checker runs for assignment 05, as
//   `build/solutions/assignment_05.exe <input-file> <output-file>`: it reads a test input,
//   calls your code and writes the answer to the output file. Only that output is checked.
//   Check it with `.\check 05`, or Run and Submit in the book.
//
// Your job:
//   In the Boilerplate this program is already written: it reads the input, calls your
//   code and writes the answer. Your work is in this assignment's other files, where it
//   says TODO.
//
// The other files of this assignment:
//   This assignment also has you write src/font/Metrics.h and src/font/Metrics.cpp; each
//   says its job at the top.
//   Earlier files you can use: src/font/ByteReader.h and src/font/FontParser.h.
//   Include them by their path under src/, e.g. #include "font/Metrics.h".
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "font/Metrics.h"

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
    std::vector<std::string> queries;  // `font-metrics` or `glyph <id>`
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") words >> path;
      else if (keyword == "table") addTable(line, tables);
      else if (keyword == "font-metrics" || keyword == "glyph") queries.push_back(line);
    }
    ByteReader reader(path);

    const HorizontalMetrics metrics = loadHorizontalMetrics(reader, tables);
    for (const std::string& query : queries) {
      std::istringstream words(query);
      std::string keyword;
      std::size_t id = 0;
      words >> keyword >> id;
      if (keyword == "font-metrics") {
        output << "ascent " << metrics.ascent << " descent " << metrics.descent << '\n';
      } else if (id < metrics.glyphs.size()) {
        const GlyphMetric& g = metrics.glyphs[id];
        output << "glyph " << id << " advance " << g.advanceWidth << " lsb " << g.leftSideBearing << '\n';
      } else {
        output << "glyph " << id << " missing\n";  // never right: every glyph has metrics
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
