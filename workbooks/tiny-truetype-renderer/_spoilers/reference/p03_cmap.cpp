// Reference solution - checkpoint 03 (map characters to glyphs, cmap format 12).
// SPOILERS: try the checkpoint yourself first.

#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

#include "provided/BigEndian.h"

struct TableRecord {
  uint32_t checkSum = 0;
  uint32_t offset = 0;  // from the start of the file
  uint32_t length = 0;
};
using Tables = std::map<std::string, TableRecord>;  // by tag, from the input's `table` lines

struct UnsupportedCmap : std::runtime_error {
  using std::runtime_error::runtime_error;
};

std::unordered_map<uint32_t, uint32_t> readCharacterMap(std::ifstream& font, const Tables& tables) {
  const uint32_t cmap = tables.at("cmap").offset;
  font.seekg(cmap);
  be::u16(font);  // version
  const uint16_t numberSubtables = be::u16(font);

  std::optional<uint32_t> subtable;  // offset from the start of cmap
  for (uint16_t i = 0; i < numberSubtables; ++i) {
    const uint16_t platformID = be::u16(font);
    const uint16_t encodingID = be::u16(font);
    const uint32_t offset = be::u32(font);
    if (platformID == 0 && encodingID == 4 && !subtable) subtable = offset;
  }
  if (!subtable) throw UnsupportedCmap("no platform 0 / encoding 4 subtable");

  font.seekg(cmap + *subtable);
  if (be::u16(font) != 12) throw UnsupportedCmap("the (0, 4) subtable is not format 12");
  font.seekg(10, std::ios::cur);  // reserved (uint16), length (uint32), language (uint32)
  const uint32_t nGroups = be::u32(font);

  std::unordered_map<uint32_t, uint32_t> glyphFor;
  for (uint32_t g = 0; g < nGroups; ++g) {
    const uint32_t startCharCode = be::u32(font);
    const uint32_t endCharCode = be::u32(font);
    const uint32_t startGlyphID = be::u32(font);
    for (uint64_t c = startCharCode; c <= endCharCode; ++c)  // both ends included
      glyphFor[static_cast<uint32_t>(c)] = startGlyphID + static_cast<uint32_t>(c - startCharCode);
  }
  return glyphFor;
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
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
