// Reference solution - checkpoint 04 (locate glyph records with loca).
// SPOILERS: try the checkpoint yourself first.

#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "provided/BigEndian.h"

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
  uint16_t numGlyphs = 0;
  bool longFormat = false;
  std::vector<GlyphLocation> glyphs;  // one per glyph id
};

GlyphLocations readGlyphLocations(std::ifstream& font, const Tables& tables) {
  GlyphLocations result;
  font.seekg(tables.at("maxp").offset + 4);  // after the 4-byte version
  result.numGlyphs = be::u16(font);
  font.seekg(tables.at("head").offset + 50);
  result.longFormat = be::i16(font) == 1;  // indexToLocFormat: 0 short, 1 long

  // loca has numGlyphs + 1 entries: the last one marks where the last glyph ends.
  font.seekg(tables.at("loca").offset);
  std::vector<uint32_t> entries(result.numGlyphs + 1u);
  for (uint32_t& entry : entries) entry = result.longFormat ? be::u32(font) : 2u * be::u16(font);

  const uint32_t glyf = tables.at("glyf").offset;
  for (std::size_t i = 0; i < result.numGlyphs; ++i)
    result.glyphs.push_back({glyf + entries[i], entries[i + 1] - entries[i]});
  return result;
}

// ---- Input/output (same as the starter) --------------------------------------

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
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
