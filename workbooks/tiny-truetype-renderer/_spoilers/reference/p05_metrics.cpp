// Reference solution - checkpoint 05 (read the horizontal metrics).
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

struct Metric {
  int advanceWidth = 0;
  int leftSideBearing = 0;
};

struct HorizontalMetrics {
  int ascent = 0;
  int descent = 0;
  std::vector<Metric> glyphs;  // one per glyph id
};

HorizontalMetrics readHorizontalMetrics(std::ifstream& font, const Tables& tables) {
  HorizontalMetrics m;
  const uint32_t hhea = tables.at("hhea").offset;
  font.seekg(hhea + 4);
  m.ascent = be::i16(font);
  m.descent = be::i16(font);
  font.seekg(hhea + 34);
  const uint16_t numberOfHMetrics = be::u16(font);
  font.seekg(tables.at("maxp").offset + 4);
  const uint16_t numGlyphs = be::u16(font);

  font.seekg(tables.at("hmtx").offset);
  for (uint16_t i = 0; i < numberOfHMetrics; ++i) {  // longHorMetric records
    const int advance = be::u16(font);
    const int lsb = be::i16(font);
    m.glyphs.push_back({advance, lsb});
  }
  // The remaining glyphs repeat the last advance; only their lsb is stored.
  const int lastAdvance = m.glyphs.empty() ? 0 : m.glyphs.back().advanceWidth;
  for (uint32_t i = numberOfHMetrics; i < numGlyphs; ++i) m.glyphs.push_back({lastAdvance, be::i16(font)});
  return m;
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
    std::vector<std::string> queries;  // `font-metrics` or `glyph <id>`
    for (std::string line; std::getline(input, line);) {
      std::istringstream words(line);
      std::string keyword;
      words >> keyword;
      if (keyword == "font") words >> path;
      else if (keyword == "table") addTable(line, tables);
      else if (keyword == "font-metrics" || keyword == "glyph") queries.push_back(line);
    }
    std::ifstream font(path, std::ios::binary);
    if (!font) throw std::runtime_error("cannot open font file " + path);

    const HorizontalMetrics metrics = readHorizontalMetrics(font, tables);
    for (const std::string& query : queries) {
      std::istringstream words(query);
      std::string keyword;
      std::size_t id = 0;
      words >> keyword >> id;
      if (keyword == "font-metrics") {
        output << "ascent " << metrics.ascent << " descent " << metrics.descent << '\n';
      } else if (id < metrics.glyphs.size()) {
        const Metric& g = metrics.glyphs[id];
        output << "glyph " << id << " advance " << g.advanceWidth << " lsb " << g.leftSideBearing << '\n';
      } else {
        output << "glyph " << id << " missing\n";  // never right: every glyph has metrics
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
