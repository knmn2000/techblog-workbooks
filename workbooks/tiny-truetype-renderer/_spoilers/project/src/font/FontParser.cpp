#include "font/FontParser.h"

std::vector<TableRecord> readTableDirectory(ByteReader& reader) {
  reader.jumpTo(0);
  reader.readUint32();  // scaler type: 0x00010000, 'true', ... (not needed)
  const uint16_t numTables = reader.readUint16();
  reader.skipBytes(6);  // searchRange, entrySelector, rangeShift

  std::vector<TableRecord> tables(numTables);
  for (TableRecord& t : tables) {
    for (int i = 0; i < 4; ++i) t.tag += static_cast<char>(reader.readUint8());
    t.checkSum = reader.readUint32();
    t.offset = reader.readUint32();
    t.length = reader.readUint32();
  }
  return tables;
}

FontParser::FontParser(const std::string& path) : reader_(path) {
  for (const TableRecord& t : readTableDirectory(reader_)) tables_[t.tag] = t;
}
