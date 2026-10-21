#include "font/FontParser.h"

std::vector<TableRecord> readTableDirectory(ByteReader& reader) {
  // TODO: read the header, then one record per table (layout on the problem page).
  throw std::logic_error("not implemented: readTableDirectory");
}

FontParser::FontParser(const std::string& path) : reader_(path) {
  for (const TableRecord& t : readTableDirectory(reader_)) tables_[t.tag] = t;
}
