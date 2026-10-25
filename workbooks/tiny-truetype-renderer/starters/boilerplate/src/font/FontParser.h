#pragma once
// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   Every table in the font gets a record: tag, checksum, offset and length (`cmap`,
//   `glyf`, `loca` and the rest). Assignments 03 to 05 find their tables by tag in these
//   records, and 18 opens the font through them.
//
// Your job:
//   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
//   in this assignment's other files.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include <cstdint>  // uint32_t: checkSum, offset and length
#include <map>      // std::map behind Tables, the records by tag
#include <string>   // std::string: the tag, and the path FontParser opens
#include <vector>   // std::vector<TableRecord>, what readTableDirectory returns

#include "font/ByteReader.h"  // ByteReader (assignment 01): what the directory is read with

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
