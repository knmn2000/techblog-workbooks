// Reference solution - checkpoint 01 (read big-endian numbers).
// SPOILERS: try the checkpoint yourself first.

#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>

// Thrown when a read needs bytes past the end of the file.
struct UnexpectedEof : std::runtime_error {
  UnexpectedEof() : std::runtime_error("unexpected EOF") {}
};

class ByteReader {
 public:
  explicit ByteReader(const std::string& path) : file_(path, std::ios::binary) {
    if (!file_) throw std::runtime_error("cannot open " + path);
  }

  void jumpTo(const uint32_t offset) {
    file_.clear();  // a jump always starts from a clean state
    file_.seekg(offset, std::ios::beg);
  }

  void skipBytes(const uint32_t count) { file_.seekg(count, std::ios::cur); }

  template <typename T>
  T readBigEndian() {
    static_assert(std::is_integral_v<T> && sizeof(T) <= 4);
    uint64_t value = 0;
    for (std::size_t i = 0; i < sizeof(T); ++i) {
      const int c = file_.get();
      if (c == std::char_traits<char>::eof()) throw UnexpectedEof();
      value = value << 8 | static_cast<uint8_t>(c);  // most significant byte first
    }
    if constexpr (std::is_signed_v<T>) {
      const uint64_t range = uint64_t{1} << (8 * sizeof(T));  // 2^bits
      if (value >= range / 2) return static_cast<T>(static_cast<int64_t>(value) - static_cast<int64_t>(range));
    }
    return static_cast<T>(value);
  }

  uint8_t readUint8() { return readBigEndian<uint8_t>(); }
  uint16_t readUint16() { return readBigEndian<uint16_t>(); }
  uint32_t readUint32() { return readBigEndian<uint32_t>(); }
  int8_t readInt8() { return readBigEndian<int8_t>(); }
  int16_t readInt16() { return readBigEndian<int16_t>(); }
  int32_t readInt32() { return readBigEndian<int32_t>(); }

  double readF2Dot14() { return readInt16() / 16384.0; }

 private:
  std::ifstream file_;
};

// ---- Input/output (same as the starter) --------------------------------------

namespace {

// k / 16384 has at most 14 digits after the point, so this prints it exactly.
std::string decimal(const double value) {
  std::ostringstream s;
  s << std::fixed << std::setprecision(14) << value;
  std::string text = s.str();
  text.erase(text.find_last_not_of('0') + 1);
  if (text.back() == '.') text.pop_back();
  return text == "-0" ? "0" : text;
}

// Runs one operation. Read operations write one line, `<op> <value>`.
// The value is read before anything is written, so a read that fails writes nothing.
// (The + in front of 8-bit values prints them as numbers, not characters.)
void run(ByteReader& reader, const std::string& op, std::istringstream& words, std::ostream& out) {
  const auto line = [&](const auto& value) { out << op << ' ' << value << '\n'; };
  if (op == "jump" || op == "skip") {
    uint32_t n = 0;
    words >> n;
    if (op == "jump") reader.jumpTo(n);
    else reader.skipBytes(n);
  } else if (op == "u8") {
    line(+reader.readUint8());
  } else if (op == "i8") {
    line(+reader.readInt8());
  } else if (op == "u16") {
    line(reader.readUint16());
  } else if (op == "i16") {
    line(reader.readInt16());
  } else if (op == "u32") {
    line(reader.readUint32());
  } else if (op == "i32") {
    line(reader.readInt32());
  } else if (op == "f2dot14") {
    line(decimal(reader.readF2Dot14()));
  } else if (!op.empty()) {
    throw std::runtime_error("unknown operation " + op);
  }
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
    std::string line, keyword, path;
    std::getline(input, line);
    std::istringstream first(line);
    first >> keyword >> path;
    if (keyword != "file") throw std::runtime_error("the first line must be: file <path>");
    ByteReader reader(path);
    while (std::getline(input, line)) {
      std::istringstream words(line);
      std::string op;
      words >> op;
      try {
        run(reader, op, words, output);
      } catch (const UnexpectedEof&) {
        output << "eof\n";  // a read ran past the end: report it and stop
        break;
      }
    }
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 1;
  }
  return 0;
}
