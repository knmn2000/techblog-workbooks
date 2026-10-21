// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   The code that reads the table directory from the first bytes of the file, through your
//   `ByteReader`. Every later step that needs a table starts from what it reads.
//
// Your job:
//   Implement the directory reader: read `numTables` from the 12-byte header, skipping the
//   other header fields, then read one 16-byte record per table, keeping the tag's 4 bytes
//   exactly as stored. If you declared a font object, have it open the file and load the
//   directory once. The Boilerplate has the declarations written: fill in what's marked
//   TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, press Blank in the
//   book's editor (the blank files are in starters/blank/).
// ======================================================================================

#include "font/FontParser.h"

std::vector<TableRecord> readTableDirectory(ByteReader& reader) {
  // TODO: read the header, then one record per table (layout on the problem page).
  throw std::logic_error("not implemented: readTableDirectory");
}

FontParser::FontParser(const std::string& path) : reader_(path) {
  for (const TableRecord& t : readTableDirectory(reader_)) tables_[t.tag] = t;
}
