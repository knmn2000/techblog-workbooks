#pragma once
// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Opening a font and reading its table directory: the tag, checksum, offset and length
//   of every table (`cmap`, `glyf`, `loca`, ...). Assignments 03 to 05 find their tables
//   by tag in these records, and assignment 18 opens the font through it.
//
// Your job:
//   In the Boilerplate this file is already written: the declarations, named as the author
//   names them. Your work is in this assignment's other files, where it says TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

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
