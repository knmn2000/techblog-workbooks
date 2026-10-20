// Checkpoint 03 - Map characters to glyphs (cmap format 12)
//
// Problem:  problems/03-cmap.md (also in the web problem book)
// Check:    .\check 03
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on readCharacterMap().

#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include "NotImplemented.h"
#include "provided/BigEndian.h"  // optional: be::u8(file), be::u16(file), be::u32(file), ...

struct TableRecord {
  uint32_t checkSum = 0;
  uint32_t offset = 0;  // from the start of the file
  uint32_t length = 0;
};
using Tables = std::map<std::string, TableRecord>;  // by tag, from the input's `table` lines

// Throw this when the font has no subtable this checkpoint supports.
// The provided code catches it and writes `unsupported`.
struct UnsupportedCmap : std::runtime_error {
  using std::runtime_error::runtime_error;
};

// Returns every (code point -> glyph id) pair of the font's platform 0 / encoding 4
// subtable, which must be in format 12. tables.at("cmap").offset is where cmap starts.
std::unordered_map<uint32_t, uint32_t> readCharacterMap(std::ifstream& font, const Tables& tables) {
  // TODO: find the subtable, check its format, and expand every group (problem page).
  throw NotImplemented("readCharacterMap");
}

// ---- Input/output (provided) -------------------------------------------------

namespace {

// table "<tag>" <checkSum> <offset> <length>
void addTable(const std::string& line, Tables& tables) {
  const std::size_t open = line.find('"');
  const std::size_t close = line.find('"', open + 1);
  if (open == std::string::npos || close == std::string::npos) throw std::runtime_error("bad line: " + line);
  TableRecord t;
  std::istringstream numbers(line.substr(close + 1));
  numbers >> t.checkSum >> t.offset >> t.length;
  tables[line.substr(open + 1, close - open - 1)] = t;
}

}  // namespace

// Usage: p03 <input-file> <output-file>
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
    std::ifstream font(path, std::ios::binary);
    if (!font) throw std::runtime_error("cannot open font file " + path);

    std::unordered_map<uint32_t, uint32_t> glyphFor;
    try {
      glyphFor = readCharacterMap(font, tables);
    } catch (const UnsupportedCmap&) {
      output << "unsupported\n";  // the whole output is this one line
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
  } catch (const NotImplemented& e) {
    std::cerr << "not implemented: " << e.what() << "\n";
    return 99;
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
