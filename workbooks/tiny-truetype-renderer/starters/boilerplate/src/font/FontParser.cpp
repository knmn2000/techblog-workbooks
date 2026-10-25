// ======================================================================================
// Assignment 02: Read the table directory
// Problem: problems/02-table-directory.md (and in the problem book, with its Start here card)
//
// Why this file exists:
//   From the first bytes of the font, through your `ByteReader`, this file reads the table
//   directory. Later assignments look up their table's offset in these records.
//
// Your job:
//   Read `numTables` from the 12-byte header and skip the other header fields, then read
//   one 16-byte record per table, keeping each tag's 4 bytes as the font stores them. The
//   Boilerplate's `FontParser` constructor already opens the file and loads the directory.
//   Writing from scratch, how you wrap that in a font object is up to you. The Boilerplate
//   gives you the declarations; fill in each TODO.
//
// How to start:
//   This is the Boilerplate. To start from an empty file instead, choose From scratch in
//   the book (the empty files are in starters/blank/).
// ======================================================================================

#include "font/FontParser.h"  // readTableDirectory and FontParser (assignment 02), defined here

#include <stdexcept>  // std::logic_error for the "not implemented" TODO

std::vector<TableRecord> readTableDirectory(ByteReader& reader) {
  // TODO: read the header, then one record per table (layout on the problem page).
  throw std::logic_error("not implemented: readTableDirectory");
}

FontParser::FontParser(const std::string& path) : reader_(path) {
  for (const TableRecord& t : readTableDirectory(reader_)) tables_[t.tag] = t;
}
