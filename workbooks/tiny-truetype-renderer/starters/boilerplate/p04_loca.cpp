// Checkpoint 04 - Locate glyph records (loca)
//
// Problem:  problems/04-loca.md (also in the web problem book)
// Check:    .\check 04
//
// Only your program's output is checked, so structure this however you like, or
// use another language or library (see README.md). The input/output code at the
// bottom is provided so you can focus on readGlyphLocations().

#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "NotImplemented.h"
#include "provided/BigEndian.h"  // optional: be::u16(file), be::i16(file), be::u32(file), ...

struct TableRecord {
  uint32_t checkSum = 0;
  uint32_t offset = 0;  // from the start of the file
  uint32_t length = 0;
};
using Tables = std::map<std::string, TableRecord>;  // by tag, from the input's `table` lines

struct GlyphLocation {
  uint32_t offset = 0;  // from the start of the file
  uint32_t length = 0;  // 0: the glyph has no outline
};

struct GlyphLocations {
  uint16_t numGlyphs = 0;             // from maxp
  bool longFormat = false;            // from head: indexToLocFormat == 1
  std::vector<GlyphLocation> glyphs;  // one per glyph id, numGlyphs of them
};

// Reads maxp, head and loca (tables.at("maxp").offset etc.) and works out where
// every glyph's record is inside the glyf table.
GlyphLocations readGlyphLocations(std::ifstream& font, const Tables& tables) {
  // TODO: see the problem page.
  throw NotImplemented("readGlyphLocations");
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

// Usage: p04 <input-file> <output-file>
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
    std::ifstream font(path, std::ios::binary);
    if (!font) throw std::runtime_error("cannot open font file " + path);

    const GlyphLocations loca = readGlyphLocations(font, tables);
    output << "glyphs " << loca.numGlyphs << " loca " << (loca.longFormat ? "long" : "short") << '\n';
    for (const uint32_t id : ids) {
      if (id >= loca.glyphs.size())
        throw std::runtime_error("glyph " + std::to_string(id) + " is missing: readGlyphLocations returned " +
                                 std::to_string(loca.glyphs.size()) + " glyphs");
      output << "glyph " << id << ' ' << loca.glyphs[id].offset << ' ' << loca.glyphs[id].length << '\n';
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
