#pragma once
// Checkpoint 02: the table directory, and the parser later steps read the font through.

#include <cstdint>
#include <map>
#include <string>
#include <vector>

#include "font/ByteReader.h"

// One entry of the table directory: where a table is in the file.
struct TableRecord {
  std::string tag;  // exactly 4 characters, trailing spaces included
  uint32_t checkSum = 0;
  uint32_t offset = 0;  // from the start of the file
  uint32_t length = 0;
};

using Tables = std::map<std::string, TableRecord>;  // by tag

// Reads the offset table and the table directory at the start of the file, in file order.
std::vector<TableRecord> readTableDirectory(ByteReader& reader);

// A font file opened for reading, with its table directory loaded.
class FontParser {
 public:
  explicit FontParser(const std::string& path);

  ByteReader& reader() { return reader_; }
  [[nodiscard]] const Tables& tables() const { return tables_; }

 private:
  ByteReader reader_;
  Tables tables_;
};
