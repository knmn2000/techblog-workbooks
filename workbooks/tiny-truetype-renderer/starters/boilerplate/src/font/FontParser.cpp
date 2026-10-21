// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   This file reads the table directory from the first bytes of the font through your
//   `ByteReader`. Each later assignment that needs a table looks up its offset in these
//   records.
//
// Your job:
//   Read `numTables` from the 12-byte header and skip the other header fields, then read
//   one 16-byte record per table and keep each tag's 4 bytes as the font stores them. If
//   you declared a font object, have it open the file and load the directory once. The
//   Boilerplate gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/FontParser.h"

std::vector<TableRecord> readTableDirectory(ByteReader& reader) {
  // TODO: read the header, then one record per table (layout on the problem page).
  throw std::logic_error("not implemented: readTableDirectory");
}

FontParser::FontParser(const std::string& path) : reader_(path) {
  for (const TableRecord& t : readTableDirectory(reader_)) tables_[t.tag] = t;
}
