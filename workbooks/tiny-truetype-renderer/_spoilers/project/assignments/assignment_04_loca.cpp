// Assignment 04 (locate glyph records): prints where each glyph in a test input is.
// The locations are read by src/font/Loca.

#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "font/Loca.h"

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
    std::vector<uint32_t> ids;  // from the `glyph <id>` lines
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") {
        words >> path;
      } else if (keyword == "table") {
        addTable(line, tables);
      } else if (keyword == "glyph") {
        uint32_t id = 0;
        words >> id;
        ids.push_back(id);
      }
    }
    ByteReader reader(path);

    const GlyphLocations loca = loadGlyphLocations(reader, tables);
    output << "glyphs " << loca.numGlyphs << " loca " << (loca.longFormat ? "long" : "short") << '\n';
    for (const uint32_t id : ids) {
      if (id >= loca.glyphs.size())
        throw std::runtime_error("glyph " + std::to_string(id) + " is missing: loadGlyphLocations returned " +
                                 std::to_string(loca.glyphs.size()) + " glyphs");
      output << "glyph " << id << ' ' << loca.glyphs[id].offset << ' ' << loca.glyphs[id].length << '\n';
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
