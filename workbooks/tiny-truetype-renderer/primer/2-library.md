# C++ standard library

The headers the project includes, and the types and functions it uses from each, in the order
the assignments first use them. The last entry is the one library from outside the standard
that the project bundles, for writing PNG files.

## `<fstream>`: reading files
<!--
id: fstream
also: std::ifstream; ifstream; std::ofstream; ofstream; file stream; seekg; binary mode
code: #\s*include\s*<fstream>|\bstd::[io]?fstream\b
-->
`<fstream>` declares the file streams. `std::ifstream` opens a file for reading, and you read
from it the same way you read from `std::cin`. `std::ofstream` opens one for writing, and you
write to it with `<<` the way you write to `std::cout` (see [`<iostream>`](#primer/iostream)).
Test a stream after opening it: `if (!input)` is true when the file couldn't be opened. Four
things matter for a font file:

- Open it in binary mode, `std::ifstream file(path, std::ios::binary)`. Without it, Windows
  turns the bytes 0x0D 0x0A into one 0x0A as it reads and can stop at a 0x1A byte, taking it
  for the end of the file, so every offset after that is off.
- `file.get()` reads one byte as an `int` from 0 to 255, or returns
  `std::char_traits<char>::eof()` when nothing is left (the [`<string>`](#primer/string) entry
  says what that value is).
- `file.seekg` moves the read position. Its second argument says where to count from:
  `std::ios::beg` is the start of the file, `std::ios::cur` the current position and
  `std::ios::end` the end. `file.seekg(100, std::ios::beg)` goes to byte 100,
  `file.seekg(6, std::ios::cur)` moves 6 bytes forward, and `file.seekg(-4, std::ios::end)`
  goes to 4 bytes before the end. With one argument, `file.seekg(100)`, it counts from the
  start. A font's tables give positions as [offsets](#primer/file-offset) from the start of
  the file, so a parser jumps around with `seekg` rather than reading from front to back.
- Reading past the end puts the stream in a failed state, and a failed stream ignores `seekg`.
  Call `file.clear()` first to make it usable again.

```cpp
std::ifstream file("font.ttf", std::ios::binary);
file.seekg(4, std::ios::beg);  // to byte 4, the fifth byte
int a = file.get();            // that byte, 0..255; the position moves on to 5
file.seekg(2, std::ios::cur);  // past bytes 5 and 6
int b = file.get();            // byte 7
```

Assignment 01's `ByteReader` (`src/font/ByteReader.h` and `.cpp`) holds a `std::ifstream`
opened in binary mode, and every later assignment that reads the font goes through it. Each
assignment's program also reads its test input, a text file, with `std::ifstream`, and most
write their answer with `std::ofstream`.

Learn more:
- [std::basic_ifstream](https://en.cppreference.com/w/cpp/io/basic_ifstream) on cppreference
- [std::basic_istream::seekg](https://en.cppreference.com/w/cpp/io/basic_istream/seekg) on
  cppreference, with both forms and why a failed stream won't seek
- [Basic file I/O](https://www.learncpp.com/cpp-tutorial/basic-file-io/) on learncpp.com, with
  the file modes

## `<iostream>`: the console streams
<!--
id: iostream
also: std::cout; std::cerr; std::cin; cout; cerr; console output; standard error
code: #\s*include\s*<iostream>|\bstd::(cout|cerr|cin|clog)\b
-->
`<iostream>` gives you the streams connected to the terminal: `std::cin` reads what is typed,
`std::cout` writes normal output and `std::cerr` writes error messages. `<<` sends a value to an
output stream and returns the stream, so you can chain several values in one statement. The
header also brings in the general stream types `std::istream` and `std::ostream`, which a
function can take as a parameter so that it works with the console, a file or a string alike.

```cpp
std::cerr << "cannot open " << path << "\n";
std::cout << "wrote " << width << " x " << height << "\n";
```

Every assignment's program (`assignments/assignment_NN_*.cpp`) includes it. They print a usage
line or an error to `std::cerr` and return an [exit code](#primer/exit-codes): 2 for wrong
arguments, 1 for an error, and 99 when a TODO in your code threw "not implemented", which the
[checker](#primer/checker) reports by name. The answers go to the output file. Assignment 01's
`run` takes a `std::ostream&`, and the program passes it its `std::ofstream`.

Learn more:
- [Standard library header &lt;iostream&gt;](https://en.cppreference.com/w/cpp/header/iostream)
  on cppreference
- [Introduction to iostream: cout, cin, and endl](https://www.learncpp.com/cpp-tutorial/introduction-to-iostream-cout-cin-and-endl/)
  on learncpp.com

## `<string>`: text
<!--
id: string
also: std::string; std::getline; getline; std::to_string; std::stoi; std::stod; std::stoul; substr; npos
code: #\s*include\s*<string>|\bstd::(string|getline|to_string|sto(i|l|ul|ll|ull|f|d|ld))\b
-->
`std::string` holds a piece of text that can grow, like a string in Python, except that you can
change it in place. The member functions the workbook uses:

- `s += 'x'` appends a character, and `s.substr(pos, n)` copies `n` characters from position
  `pos`.
- `s.find('"')` returns the position of the first `"`, and `s.find('"', from)` starts looking at
  position `from`. Both return `std::string::npos` when there is none (see
  [`std::size_t`](#primer/size-t)). `s.rfind("font ", 0) == 0` tests whether `s` starts with
  `"font "`.
- `s.find_last_not_of('0')` returns the position of the last character that isn't `'0'`, or
  `npos` when every character is.
- `s.erase(pos)` removes everything from position `pos` to the end.
- `s.back()` is the last character and `s.pop_back()` removes it. Both need a string that isn't
  empty.

```cpp
std::string text = "2.50000000000000";
text.erase(text.find_last_not_of('0') + 1);  // "2.5": cut after the last character that isn't 0
// "2.00000000000000" would become "2." here, so:
if (text.back() == '.') text.pop_back();     // drop a point left at the end
```

The header also declares `std::getline(stream, line)`, which reads one line without its newline
and returns the stream, which tests false when no line is left. And it has the conversions
between text and numbers: `std::to_string(42)` gives `"42"`, and `std::stoi` and `std::stod`
read an `int` and a `double` from the start of a string. `std::stoul(text, nullptr, 16)` reads
an `unsigned long` in base 16, so `"1F600"` gives 128512. Its second argument is a pointer to a
`std::size_t` where it stores how many characters it used, which tells you where the number
ended; pass `nullptr` when you don't need that. The third is the base (see
[hexadecimal](#primer/hex-literals)). Each of these throws `std::invalid_argument` when the text
doesn't start with a number.

```cpp
for (std::string line; std::getline(input, line);) { /* one line, without the newline */ }
int n = std::stoi("42");             // "42" -> 42
std::size_t used = 0;
unsigned long c = std::stoul("1F600 rest", &used, 16);  // 128512, used is 5
```

`std::char_traits<char>` is a traits class: a class that collects facts and helper functions
about one type, here `char`, for the string and stream classes to use. Its `eof()` returns the
`int` that marks the end of input, -1 with every common compiler. A stream's `get()` returns an
`int` so that it can hold every byte, 0 to 255, and this one extra value, which no byte can be.
`<string>` declares it, and the stream headers bring it in too.

Assignment 01 uses the header first: `ByteReader`'s constructor takes the font's path as a
`const std::string&`, the program reads its input with `std::getline`, and its `decimal`
function trims zeros as above. Assignment 03's program reads the `1F600` of `U+1F600` with
`std::stoul`.

Learn more:
- [std::basic_string](https://en.cppreference.com/w/cpp/string/basic_string) on cppreference,
  listing its member functions
- [std::stoul](https://en.cppreference.com/w/cpp/string/basic_string/stoul) on cppreference,
  with the `pos` argument
- [std::char_traits](https://en.cppreference.com/w/cpp/string/char_traits) on cppreference
- [Introduction to std::string](https://www.learncpp.com/cpp-tutorial/introduction-to-stdstring/)
  on learncpp.com

## `<sstream>`: parsing text
<!--
id: sstream
also: std::istringstream; istringstream; std::ostringstream; ostringstream; string stream; stringstream
code: #\s*include\s*<sstream>|\bstd::(i|o)?stringstream\b
-->
`<sstream>` declares streams that read from or write to a `std::string` instead of a file.
`std::istringstream words(line)` lets you take a line apart with `>>`, which skips spaces and
reads one word or number at a time, converted to the type of the variable you read into. When
there is nothing more to read, or the text isn't a number, the stream tests false.
`std::ostringstream` goes the other way: you write into it with `<<` and get the text back
with `.str()`.

```cpp
std::istringstream words("rect 10 20 4 4");
std::string keyword;
int x = 0, y = 0;
words >> keyword >> x >> y;  // "rect", 10, 20
```

All 18 assignment programs read their test input this way: one `std::getline` per line, then a
`std::istringstream` over the line to split it into a keyword and its numbers. Assignment 01's
program also uses a `std::ostringstream` to turn an F2Dot14 value into text (see
[`<iomanip>`](#primer/iomanip)).

Learn more:
- [std::basic_istringstream](https://en.cppreference.com/w/cpp/io/basic_istringstream) on
  cppreference
- [Stream classes for strings](https://www.learncpp.com/cpp-tutorial/stream-classes-for-strings/)
  on learncpp.com

## `<stdexcept>`: standard error types
<!--
id: stdexcept
also: std::runtime_error; runtime_error; std::logic_error; logic_error; std::out_of_range; std::invalid_argument; exception types
code: #\s*include\s*<stdexcept>|\bstd::(runtime_error|logic_error|out_of_range|invalid_argument|domain_error|length_error|range_error|overflow_error|underflow_error)\b
-->
`<stdexcept>` declares the standard exception classes you throw when something goes wrong. Each
one carries a message, given when you create it and returned later by `what()`. They come in two
families: `std::logic_error` for a mistake in the program (with `std::out_of_range` and
`std::invalid_argument` among its kinds) and `std::runtime_error` for a problem with the data,
such as a file that can't be opened. All of them derive from `std::exception` (see
[`<exception>`](#primer/exception)). How `throw`, `try` and `catch` work is covered in
[Exceptions](#primer/exceptions), and deriving your own type in
[Deriving from a class](#primer/inheritance).

```cpp
struct UnexpectedEof : std::runtime_error {
  UnexpectedEof() : std::runtime_error("unexpected EOF") {}
};
throw std::runtime_error("cannot open " + path);
```

Every TODO in the Boilerplate throws `std::logic_error("not implemented: <name>")`, so a program
that reaches code you haven't written yet stops and names it. Assignment 01's `ByteReader.h`
declares `UnexpectedEof`, derived from `std::runtime_error`, for a read past the end of the
file, and assignment 03's `Cmap.h` declares `UnsupportedCmap` for a font without a format 12
subtable. Two library calls throw types from this header: `std::map::at` throws
`std::out_of_range` for a key the map doesn't have (see [`<map>`](#primer/map)), and `std::stoi`
throws `std::invalid_argument` for text that isn't a number.

Learn more:
- [std::runtime_error](https://en.cppreference.com/w/cpp/error/runtime_error) on cppreference
- [Standard library header &lt;stdexcept&gt;](https://en.cppreference.com/w/cpp/header/stdexcept)
  on cppreference, listing all nine classes
- [Exceptions, classes, and inheritance](https://www.learncpp.com/cpp-tutorial/exceptions-classes-and-inheritance/)
  on learncpp.com

## `<exception>`: the base of all exceptions
<!--
id: exception
also: std::exception; what(); catch std::exception
code: #\s*include\s*<exception>|\bstd::exception\b
-->
`<exception>` declares `std::exception`, the class every standard exception derives from. You
rarely include it yourself: [`<stdexcept>`](#primer/stdexcept) brings `std::exception` in,
because its own classes derive from it, so a file that includes `<stdexcept>` can already use
it. Page 01 lists `<exception>` for the `catch` in its program, which gets `std::exception`
that way.

`std::exception` has a member function `what()` that returns the exception's message as a C
string. Because `std::runtime_error`, `std::logic_error` and the rest all derive from it, one
`catch (const std::exception& e)` catches any of them, including your own types derived from
`std::runtime_error`, and `e.what()` gives you the message of whichever one was thrown.

```cpp
try {
  run();
} catch (const std::exception& e) {
  std::cerr << "error: " << e.what() << "\n";
}
```

Every assignment's program wraps its work in a `catch (const std::exception& e)` like this,
starting with assignment 01. A message that starts with "not implemented" means a TODO you
haven't filled in (exit code 99), and anything else is an error (exit code 1). Only
`src/main.cpp`, the command-line renderer of assignment 18, includes `<exception>` by name,
because it uses nothing from `<stdexcept>`.

Learn more:
- [std::exception](https://en.cppreference.com/w/cpp/error/exception) on cppreference, with the
  tree of standard exception classes
- [Exceptions, classes, and inheritance](https://www.learncpp.com/cpp-tutorial/exceptions-classes-and-inheritance/)
  on learncpp.com

## `<iomanip>`: formatting numbers
<!--
id: iomanip
also: std::setprecision; setprecision; std::fixed; std::setw; stream manipulators
code: #\s*include\s*<iomanip>|\bstd::(setprecision|setw|setfill|setbase)\b
-->
`<iomanip>` declares stream manipulators that take an argument. A manipulator is something you
send to a stream with `<<` that changes how the stream writes what follows instead of writing
text itself. `std::setprecision(n)` sets how many digits a [floating-point](#primer/floating-point)
number gets. On its own it counts significant digits; after `std::fixed` (declared in `<ios>`,
which `<iostream>` and `<sstream>` bring in) it counts the digits after the decimal point.

```cpp
std::ostringstream s;
s << std::fixed << std::setprecision(3) << 0.5;  // "0.500"
```

Only assignment 01 uses it, in the Boilerplate program `assignment_01_byte_readers.cpp`. Its
`decimal` function prints an [F2Dot14](#primer/f2dot14) value, a 16-bit integer k divided by
16384, with `std::fixed << std::setprecision(14)`, then removes the trailing zeros (see
[`<string>`](#primer/string)). 16384 is 2 to the 14th, so k / 16384 has at most 14 digits after
the point and 14 decimals print it without rounding. The later programs format their numbers
with `std::snprintf` instead (see [`<cstdio>`](#primer/cstdio)).

Learn more:
- [std::setprecision](https://en.cppreference.com/w/cpp/io/manip/setprecision) on cppreference
- [Output with ostream and ios](https://www.learncpp.com/cpp-tutorial/output-with-ostream-and-ios/)
  on learncpp.com, covering `std::fixed` and `std::setprecision`

## `<cstdint>`: integers of a known width
<!--
id: cstdint
also: uint8_t; uint16_t; uint32_t; int16_t; int32_t; uint64_t; int64_t; fixed-width integer types
code: #\s*include\s*<cstdint>|\b(std::)?u?int(8|16|32|64)_t\b
-->
`<cstdint>` declares integer types whose size the name tells you: `uint8_t`, `uint16_t`,
`uint32_t` and `uint64_t` are unsigned and 8, 16, 32 and 64 bits wide, and `int8_t` to `int64_t`
are their signed versions. The plain `int` and `long` have sizes that depend on the compiler and
platform, so a program that reads a binary format uses these instead. How the types store their
values is covered in [Integer types](#primer/integer-types), and the signed ones in
[Two's complement](#primer/twos-complement).

The header declares them in the `std` namespace, as `std::uint32_t`. The workbook writes them
without `std::`, as most C++ code does; GCC, Clang and MSVC declare them under both names,
which the standard allows but doesn't require (see [namespaces](#primer/namespaces)).

```cpp
uint16_t numTables = reader.readUint16();  // a 16-bit field from the font
int16_t xMin = reader.readInt16();         // a signed one
```

Assignment 01 uses it first: `ByteReader.h` returns each font field in the type of its width,
from `readUint8` to `readInt32`, and page 01's hints suggest a `uint64_t`, wider than any of
them, while you build a number. From then on most headers include it, for fields such as the
offsets and lengths in `TableRecord` (02) and the colour channels of `RGB`, one `uint8_t` each
(06).

Learn more:
- [Fixed width integer types](https://en.cppreference.com/w/cpp/types/integer) on cppreference
- [Fixed-width integers and size_t](https://www.learncpp.com/cpp-tutorial/fixed-width-integers-and-size-t/)
  on learncpp.com

## `<type_traits>`: questions about types
<!--
id: type-traits
also: std::is_integral_v; is_integral; std::is_signed_v; is_signed; type traits
code: #\s*include\s*<type_traits>|\bstd::is_(integral|signed|unsigned|same|floating_point|arithmetic)(_v)?\b
-->
`<type_traits>` answers questions about types while the program compiles. Each answer is a
constant, so you can use it where the compiler needs a value it knows before the program runs.
`std::is_integral_v<T>` is `true` when `T` is an integer type (including `char` and `bool`), and
`std::is_signed_v<T>` is `true` when `T` can hold negative numbers. The header has many more,
such as `std::is_same_v<A, B>`.

```cpp
static_assert(std::is_integral_v<uint16_t>);  // compiles
static_assert(std::is_signed_v<int16_t>);     // compiles
static_assert(std::is_signed_v<uint8_t>);     // compile error: it's unsigned
```

The workbook uses it in assignment 01's `ByteReader.h`. `readBigEndian<T>` is a
[template](#primer/templates), one function written for any integer type `T`, and its first line
is `static_assert(std::is_integral_v<T> && sizeof(T) <= 4)`, which stops the build if someone
asks for a `double` or an 8-byte integer (see [`static_assert`](#primer/static-assert) and
[`sizeof`](#primer/sizeof)). The same function has to treat signed and unsigned types
differently, and a trait such as `std::is_signed_v<T>` is how a template asks which kind `T` is;
page 01 pairs it with [`if constexpr`](#primer/if-constexpr).

Learn more:
- [Standard library header &lt;type_traits&gt;](https://en.cppreference.com/w/cpp/header/type_traits)
  on cppreference, listing the traits
- [std::is_integral](https://en.cppreference.com/w/cpp/types/is_integral) on cppreference

## `<vector>`: a growable array
<!--
id: vector
also: std::vector; vector; push_back; emplace_back; reserve; resize; dynamic array
code: #\s*include\s*<vector>|\bstd::vector\b
-->
`std::vector<T>` is an array of `T` that can grow, like a Python list whose elements all have
the same type. The elements sit next to each other in memory. `v.push_back(x)` adds `x` at the
end, `v.size()` counts the elements, `v[i]` reads one without checking the index (`v.at(i)`
checks it and throws), and `for (const T& x : v)` visits them in order (see
[range-based `for`](#primer/range-for)). `std::vector<T> v(n)` starts with `n` default-made
elements, `resize(n)` changes the count, and `reserve(n)` sets aside room for `n` without adding
any.

```cpp
std::vector<int> ends;
ends.push_back(3);
ends.push_back(7);
for (int e : ends) std::cout << e << "\n";
```

Assignment 02 uses it first: `readTableDirectory` returns the table records in file order as a
`std::vector<TableRecord>`. Assignment 06's `FrameBufferCanvas` keeps its pixels in one
`std::vector<RGB>`, row by row (see [Framebuffer](#primer/framebuffer)), and `writePng` hands
`pixels_.data()`, a [pointer](#primer/pointers) to the first element, to the PNG writer (see
[`stb_image_write.h`](#primer/stb-image-write)).

Learn more:
- [std::vector](https://en.cppreference.com/w/cpp/container/vector) on cppreference
- [Introduction to std::vector and list constructors](https://www.learncpp.com/cpp-tutorial/introduction-to-stdvector-and-list-constructors/)
  on learncpp.com

## `<map>`: a sorted map
<!--
id: map
also: std::map; map; ordered map; sorted dictionary; red-black tree
code: #\s*include\s*<map>|\bstd::map\b
-->
`std::map<K, V>` stores values under keys, like a Python dict, and keeps the keys sorted. It is
usually built as a balanced binary tree, so finding a key takes about log2(n) steps: 20 for a
million entries. Three ways to look up a key behave differently:

- `m[key]` returns the value, and inserts a default value first if the key isn't there. Use it
  to store: `m[key] = value`.
- `m.at(key)` throws `std::out_of_range` if the key isn't there.
- `m.find(key)` returns an [iterator](#primer/iterators), equal to `m.end()` if the key isn't
  there.

Because `m[key]` may insert, it doesn't compile on a [`const`](#primer/const) map. That includes
a map a function receives as a `const std::map<K, V>&` (see [references](#primer/references)),
the usual way to pass a map the function only reads. Such a function looks keys up with `at` or
`find`.

```cpp
std::map<std::string, int> offsets;
offsets["cmap"] = 0x1C4;                  // fine: offsets isn't const

int cmapOffset(const std::map<std::string, int>& offsets) {
  return offsets.at("cmap");              // offsets["cmap"] would not compile here
}
```

Assignment 02 stores the table directory as `Tables`, a `std::map<std::string, TableRecord>`
keyed by tag, in `FontParser.h`. From assignment 03 on, the functions you write receive it as a
`const Tables&`, so they find a table with `at` or `find`. Assignment 09's `resolveGlyph`
receives the glyph locations as a `const std::map<uint32_t, GlyphLocation>&` in the same way.
The blog post calls the directory a hash map; for the 10 to 20 tables a font has, either kind
is fine, and [`<unordered_map>`](#primer/unordered-map) has the difference.

Learn more:
- [std::map](https://en.cppreference.com/w/cpp/container/map) on cppreference
- [std::map's subscript operator](https://en.cppreference.com/w/cpp/container/map/operator_at)
  on cppreference, which inserts a missing key
- [Red-black tree](https://en.wikipedia.org/wiki/Red%E2%80%93black_tree) on Wikipedia, the tree
  most implementations use

## `<unordered_map>`: a hash map
<!--
id: unordered-map
also: std::unordered_map; unordered_map; hash map; hash table; dictionary
code: #\s*include\s*<unordered_map>|\bstd::unordered_map\b
-->
`std::unordered_map<K, V>` stores values under keys like [`std::map`](#primer/map), with the
same `[]`, `at` and `find`, but as a hash table. It turns each key into a number (its hash) that
picks a bucket, so a lookup takes the same short time on average however many entries there
are, where `std::map` takes about log2(n) steps. The cost is order: iterating visits the keys in
no particular sequence. Use `std::map` when you need the keys sorted and `std::unordered_map`
when you only look keys up.

```cpp
std::unordered_map<uint32_t, uint32_t> glyphFor;
glyphFor[0x41] = 36;                    // 'A' -> glyph 36
bool known = glyphFor.find(0x42) != glyphFor.end();
```

Assignment 03's `loadUnicodeToGlyphCodeMap` in `Cmap.h` returns a
`std::unordered_map<uint32_t, uint32_t>` from [code point](#primer/code-point) to
[glyph id](#primer/glyph-id), and its program answers `count` with `size()` and `lookup U+XXXX`
with `find`. Page 03 says a `std::map`, or a sorted `std::vector` searched with binary search,
works too. Assignment 18's `TextRenderer` keeps the same map to find the glyph for each
character of its text.

Learn more:
- [std::unordered_map](https://en.cppreference.com/w/cpp/container/unordered_map) on cppreference
- [Hash table](https://en.wikipedia.org/wiki/Hash_table) on Wikipedia, with how buckets and
  collisions work

## `<optional>`: a value that may be missing
<!--
id: optional
also: std::optional; optional; std::nullopt; nullopt; maybe value
code: #\s*include\s*<optional>|\bstd::(optional|nullopt)\b
-->
`std::optional<T>` holds either a `T` or nothing, like a value that may be `None` in Python.
It tests false when empty, `*opt` or `opt->member` reaches the value inside, and
`return std::nullopt;` returns an empty one. `opt.emplace(args)` builds the value in place, which
lets you create an object later than the line that declares it. It arrived in C++17; the
project builds as C++20.

```cpp
std::optional<int> firstNegative(const std::vector<int>& v) {
  for (int x : v) if (x < 0) return x;
  return std::nullopt;
}
```

Page 03 suggests one for a search that may come up empty: while you scan the `cmap` encoding
records, an empty `std::optional` can stand for "no (0, 4) record yet" without a made-up offset.
Assignment 06's program declares `std::optional<FrameBufferCanvas> canvas` and calls
`canvas.emplace(w, h)` when it reads the `canvas` line, because the size isn't known before
then. In assignment 12, `segmentsIntersect` in `src/utils/Geometry.h` returns a
`std::optional<Vec2>`: the crossing point, or `std::nullopt` when the segments don't cross.

Learn more:
- [std::optional](https://en.cppreference.com/w/cpp/utility/optional) on cppreference
- [std::optional](https://www.learncpp.com/cpp-tutorial/stdoptional/) on learncpp.com

## `std::size_t`: sizes and indexes
<!--
id: size-t
also: size_t; std::size_t; <cstddef>; cstddef; std::string::npos; npos; size type; size()
code: \bstd::size_t\b|\bsize_t\b|#\s*include\s*<cstddef>
-->
`std::size_t` is the unsigned integer type the standard library uses for sizes and positions.
`v.size()` on a vector, `s.size()` on a string and [`sizeof(x)`](#primer/sizeof) all give you
one, and `v[i]` takes one. It is wide enough to count the bytes of the largest object your
program can hold, so it has 64 bits on a 64-bit system, and it can't be negative. The header that
defines it is `<cstddef>`, but `<string>`, `<vector>` and most others bring it in too.

Being unsigned has two consequences you'll meet:

- Mixing it with `int` in a comparison converts the `int` to unsigned, so -1 becomes a huge
  number and `i < v.size()` can be true or false for the wrong reason. The compiler warns about
  this as a signed/unsigned comparison (see [compiler warnings](#primer/compiler-warnings)).
  Loop over a container with a `std::size_t` index, or with a
  [range-based `for`](#primer/range-for).
- Subtracting past zero wraps around instead of going negative: `v.size() - 1` is about
  18 quintillion when `v` is empty. Write `i + 1 < v.size()` rather than `i < v.size() - 1`.

```cpp
const std::size_t open = line.find('"');      // a position in the string
if (open == std::string::npos) return false;  // npos, the largest size_t, means "not found"
for (std::size_t i = 0; i + 2 < words.size(); i += 3) { /* words[i] .. words[i + 2] */ }
```

You meet it first in assignment 01: `sizeof(T)` in `readBigEndian` is a `std::size_t`, so a
counter you compare with it should be one too. The programs of 03, 04 and 05 find the quotes
around a table's tag with `line.find('"')`. Assignment 06's `FrameBufferCanvas` sizes its pixel
vector with `static_cast<std::size_t>(width) * height`, converting before it multiplies so the
product can't [overflow](#primer/integer-overflow) an `int`.

Learn more:
- [std::size_t](https://en.cppreference.com/w/cpp/types/size_t) on cppreference
- [Fixed-width integers and size_t](https://www.learncpp.com/cpp-tutorial/fixed-width-integers-and-size-t/)
  on learncpp.com
- [std::basic_string::npos](https://en.cppreference.com/w/cpp/string/basic_string/npos) on
  cppreference

## Iterators: `begin()`, `end()` and `find()`
<!--
id: iterators
also: iterator; begin; end; it->second; find() == end(); past-the-end; const_iterator
code: \.c?(begin|end)\(\)|::(const_)?iterator\b
-->
An iterator marks a position in a container (a vector, a map, a string) and lets you step from
one element to the next. It behaves like a [pointer](#primer/pointers): `*it` is the element it
points at, `++it` moves to the next one, and `it->member` reaches a member of that element.
Every container has `begin()`, the position of its first element, and `end()`, the position one
past its last. `end()` doesn't point at an element, so never read through it; it marks where to
stop.

Library functions describe a range of elements as two iterators, a start and a stop:
`std::sort(v.begin(), v.end())` sorts the whole vector, and `v.erase(v.begin())` removes the
first element. A search that can fail returns `end()` when it finds nothing:

```cpp
const auto found = glyphFor.find(0x41);  // an iterator into the map
if (found == glyphFor.end()) {
  // 'A' isn't in the map
} else {
  uint32_t glyph = found->second;         // a map element is a pair: ->first is the key
}
```

For a map, the element an iterator points at is a key and value pair, so `it->first` is the key
and `it->second` the value. A [range-based `for`](#primer/range-for) uses `begin()` and `end()`
for you, which is why most loops in the workbook never name an iterator.

The workbook meets them in assignment 03, whose program looks a code point up with
`glyphFor.find(...)` and prints `none` when the result equals `glyphFor.end()`. The programs of
08 and 11 drop the first word of a line with `words.erase(words.begin())`, and from assignment
13 on you pass `begin()` and `end()` to `std::sort` (see [`<algorithm>`](#primer/algorithm)).

Learn more:
- [Introduction to iterators](https://www.learncpp.com/cpp-tutorial/introduction-to-iterators/)
  on learncpp.com
- [Iterator library](https://en.cppreference.com/w/cpp/iterator) on cppreference
- [std::map::find](https://en.cppreference.com/w/cpp/container/map/find) on cppreference

## `<cmath>`: math functions
<!--
id: cmath
also: std::lround; lround; std::llround; std::round; std::sqrt; std::ceil; std::floor; std::hypot; std::isnan; std::isinf; std::copysign; rounding
code: #\s*include\s*<cmath>|\bstd::(l?l?round|ceil|floor|trunc|sqrt|hypot|copysign|isnan|isinf|fabs|pow)\b
-->
`<cmath>` has the math functions for [floating-point](#primer/floating-point) numbers:
`std::sqrt`, `std::hypot(dx, dy)` (the length of a vector, the square root of dx² + dy²),
`std::abs`, `std::floor` and `std::ceil` (round down and up), `std::copysign`, and the tests
`std::isnan` and `std::isinf`.

Rounding needs care when you turn a coordinate into a pixel. Converting a `double` to `int` with
`static_cast<int>` cuts off the fraction, so 2.9 becomes 2 and -2.9 becomes -2 (see
[converting a float to an int](#primer/float-to-int)). `std::round` rounds to the nearest whole
number, with halves going away from zero (2.5 to 3, -2.5 to -3), and returns a `double`.
`std::lround` does the same and returns a `long`, and `std::llround` a `long long`.

```cpp
int a = static_cast<int>(2.9);              // 2
int b = static_cast<int>(std::lround(2.9)); // 3
```

Assignment 06 needs it first: the points of a line come out as fractions, and page 06 rounds
them to the nearest pixel with `std::lround`. Later, the programs of 10, 12, 13 and 15 print
`nan` and `inf` after testing with `std::isnan` and `std::isinf`, and `src/main.cpp` (18) sizes
its picture with `std::ceil`.

Learn more:
- [Standard library header &lt;cmath&gt;](https://en.cppreference.com/w/cpp/header/cmath) on
  cppreference
- [std::round, std::lround, std::llround](https://en.cppreference.com/w/cpp/numeric/math/round)
  on cppreference, with the halfway cases

## `<algorithm>`: sorting, min and max
<!--
id: algorithm
also: std::sort; sort; std::min; std::max; std::clamp; std::find_if; std::rotate; algorithms
code: #\s*include\s*<algorithm>|\bstd::(sort|stable_sort|min|max|minmax|clamp|find|find_if|rotate|reverse|fill|lower_bound|upper_bound|binary_search)\b
-->
`<algorithm>` has ready-made functions that work on a range of elements, given as two
[iterators](#primer/iterators) such as `v.begin()` and `v.end()`.
`std::sort(v.begin(), v.end())` sorts in ascending order; a third argument, a function that says
whether `a` goes before `b`, sorts by anything else, and is often written as a
[lambda](#primer/lambdas). `std::min(a, b)` and `std::max(a, b)` return the smaller or larger
value (both of the same type), `std::min({a, b, c})` takes a list, and `std::clamp(x, lo, hi)`
limits `x` to a range. `std::find_if` finds the first element that passes a test, and
`std::rotate` shifts elements around so a chosen one comes first.

```cpp
std::vector<double> xs = {4.5, 1.0, 3.2};
std::sort(xs.begin(), xs.end());  // 1.0 3.2 4.5
int col = std::clamp(x, 0, width - 1);
std::sort(people.begin(), people.end(),
          [](const Person& a, const Person& b) { return a.age < b.age; });  // by age
```

Nothing in the Boilerplate includes it; you include it where your own code needs it. Page 06
suggests `std::min` and `std::max` when `drawRect` has to keep a rectangle inside the canvas
(see [Clipping](#primer/clipping)). From assignment 13 on you sort values, and in 14
`forEachRow` hands each row's crossings over sorted by x (see
[Scanline filling](#primer/scanline)). A struct such as `Crossing` has no `<` of its own, so
sorting it takes the third argument.

Learn more:
- [std::sort](https://en.cppreference.com/w/cpp/algorithm/sort) on cppreference
- [Algorithms library](https://en.cppreference.com/w/cpp/algorithm) on cppreference, grouping
  the functions by job
- [Introduction to standard library algorithms](https://www.learncpp.com/cpp-tutorial/introduction-to-standard-library-algorithms/)
  on learncpp.com

## `<utility>`: pairs, swap and move
<!--
id: utility
also: std::pair; pair; std::swap; swap; std::move; move
code: #\s*include\s*<utility>|\bstd::(pair|make_pair|swap|move)\b
-->
`<utility>` holds small general tools. `std::pair<A, B>` groups two values, reached as `.first`
and `.second`, which is handy for returning two things from a function. `std::swap(a, b)`
exchanges two variables. `std::move(x)` marks `x` as no longer needed, so that copying it into
a container or another variable may take over its memory instead of duplicating it.

```cpp
std::pair<int, int> pixel = {12, 40};
int x = pixel.first, y = pixel.second;
std::swap(x, y);  // x is 40, y is 12
```

Page 06 lists `std::swap` for line drawing. A loop that steps along one axis from the smaller
coordinate to the larger is easier to write once, and swapping values lets the same loop serve
lines given in either direction and steep lines as well as shallow ones (see
[Drawing a line](#primer/line-drawing)). The Boilerplate itself doesn't include `<utility>`.

Learn more:
- [Standard library header &lt;utility&gt;](https://en.cppreference.com/w/cpp/header/utility) on
  cppreference
- [std::pair](https://en.cppreference.com/w/cpp/utility/pair) on cppreference

## `<cstdlib>`: C general utilities
<!--
id: cstdlib
also: std::abs; abs; std::exit; EXIT_SUCCESS; EXIT_FAILURE; C standard library
code: #\s*include\s*<cstdlib>|\bstd::(exit|abort|getenv|strtol|strtoul|strtod|atoi|labs|llabs)\b|\bEXIT_(SUCCESS|FAILURE)\b
-->
`<cstdlib>` is the C++ version of C's `stdlib.h`, a mix of general functions from C: `std::abs`
for integers, `std::exit` to end the program, `EXIT_SUCCESS` and `EXIT_FAILURE`, conversions
such as `std::strtol`, and memory functions. `<cstdlib>`, `<cstdint>`, `<cstdio>` and `<cmath>` all
come from C headers this way (`stdlib.h`, `stdint.h`, `stdio.h`, `math.h`), with the names
placed in namespace `std`.

`std::abs` returns the absolute value: `std::abs(-7)` is 7. The integer versions are declared
in `<cstdlib>`, and [`<cmath>`](#primer/cmath) declares them as well as the floating-point ones,
so with `<cmath>` included you get every overload.

```cpp
#include <cstdlib>
int dx = std::abs(bx - ax);  // horizontal distance
```

Page 06 lists it for line drawing: comparing the absolute differences in x and in y between a
line's ends tells you whether the line is steep, that is, whether it moves more rows than
columns (see [Drawing a line](#primer/line-drawing)). The programs return their exit codes
(0, 1, 2 and 99) from `main` directly, so they use nothing else from this header.

Learn more:
- [std::abs(int)](https://en.cppreference.com/w/cpp/numeric/math/abs) on cppreference, which
  lists both headers
- [Standard library header &lt;cstdlib&gt;](https://en.cppreference.com/w/cpp/header/cstdlib) on
  cppreference

## `stb_image_write.h`: writing PNG files
<!--
id: stb-image-write
also: stb; stbi_write_png; STB_IMAGE_WRITE_IMPLEMENTATION; single-header library; header-only library; PNG
code: #\s*include\s*"(stb/)?stb_image_write\.h"|\bstbi_write_png\b|\bSTB_IMAGE_WRITE_IMPLEMENTATION\b
-->
The C++ standard library can't write images, so the workbook bundles `stb_image_write.h`
(version 1.16) by Sean Barrett, a C library in the public domain (or MIT, your choice), kept in
`third_party/stb/`. Setting up your project copies it into your own `third_party/`, which
[CMake](#primer/cmake) puts on the include path.

It is a single-header library: one `.h` file holds both the declarations and the code (see
[header files](#primer/header-files)). Included normally, it gives you only the declarations,
like any header. In one `.cpp` file, and only one, you write
`#define STB_IMAGE_WRITE_IMPLEMENTATION` before the `#include` (see
[the preprocessor](#primer/preprocessor)), and in that file the header also compiles the
functions' code. Define it in no file and the linker can't find `stbi_write_png`; define it in
two and the linker finds two copies (see [compiling and linking](#primer/compile-and-link)).

```cpp
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"
// rgb: width * height * 3 bytes, row by row from the top
stbi_write_png("out.png", width, height, 3, rgb, width * 3);
```

Assignment 06's `src/FrameBufferCanvas.cpp` does this; the Boilerplate already contains it.
The arguments are the file name, the size, 3 channels (red, green, blue), a pointer to the
pixels, and the bytes per row. It returns 0 if it couldn't write the file, and `writePng` then
throws. The `#pragma GCC diagnostic` lines around the include turn off GCC and Clang warnings
for this outside code, and `static_assert(sizeof(RGB) == 3)` checks that the canvas's
`std::vector<RGB>` is 3 bytes per pixel with no padding, the layout the writer reads (see
[Pixels and RGB colour](#primer/pixel)). Every later drawing assignment saves its picture
through `writePng`, and page 06 allows a [binary PPM](#primer/ppm) instead.

Learn more:
- [stb](https://github.com/nothings/stb) on GitHub, whose FAQ explains how to use the
  single-file libraries
- [Header-only](https://en.wikipedia.org/wiki/Header-only) on Wikipedia

## `<memory>`: `std::unique_ptr`
<!--
id: memory
also: std::unique_ptr; unique_ptr; std::make_unique; make_unique; smart pointer
code: #\s*include\s*<memory>|\bstd::(unique_ptr|make_unique|shared_ptr|make_shared)\b
-->
`<memory>` has the smart pointers. A [pointer](#primer/pointers) is a variable that holds the
address of an object somewhere else in memory. `std::unique_ptr<T>` is a pointer that owns its
object: when the `unique_ptr` goes away or gets a new object, it deletes the old one, so you
don't free memory by hand. It starts empty (`nullptr`) and tests false until you give it an
object, which you create with `std::make_unique<T>(arguments)`. `*p` is the object and `p->f()`
calls a member function on it. A `unique_ptr` can't be copied, only moved, because two owners
would both delete the object.

```cpp
std::unique_ptr<ByteReader> font;            // empty
font = std::make_unique<ByteReader>(path);   // opens the file
if (font) readGlyph(*font, offset, length);  // pass the object itself
```

The workbook uses it for an object that can't exist before the input says how to make it.
Assignment 07's program reads `font <path>` from its input and only then creates
`std::make_unique<ByteReader>(path)`; before that `font` is empty, and a `glyph` line that comes
first is an error. From 08 on the programs hold their `FrameBufferCanvas` this way until the
`canvas` line gives its size. Assignment 06 solves the same problem with
[`std::optional`](#primer/optional), which keeps the object inside itself instead of elsewhere in
memory.

Learn more:
- [std::unique_ptr](https://en.cppreference.com/w/cpp/memory/unique_ptr) on cppreference
- [std::unique_ptr](https://www.learncpp.com/cpp-tutorial/stdunique_ptr/) on learncpp.com

## `<cstdio>`: `printf`-style formatting
<!--
id: cstdio
also: std::snprintf; snprintf; printf; format string; %.4f
code: #\s*include\s*<cstdio>|\bstd::(printf|sprintf|snprintf|fprintf|puts|fopen|fclose)\b
-->
`<cstdio>` is C's input and output library, the C++ version of `stdio.h`. Its `printf` family
formats numbers with a format string: each `%` starts a placeholder that the next argument fills
in. `%d` prints an integer, and `%.4f` a [floating-point](#primer/floating-point) number with 4
digits after the point, rounded (3.14159 prints as `3.1416`).
`std::snprintf(buf, size, format, ...)` writes the result into a `char` array instead of the
console, and writes at most `size - 1` characters plus the 0 byte that ends a C string, so it
can't run past the array.

```cpp
char buf[32];
std::snprintf(buf, sizeof buf, "%.4f", 2.5);  // "2.5000"
std::string text = buf;
```

The programs for assignments 09, 10, 12, 13 and 15 use it in their `number` function, which
prints each coordinate the checker compares. It formats the value with `"%.4f"`, copies it into
a `std::string`, removes trailing zeros and a trailing point, and turns `-0` into `0`, so 2.5000
prints as `2.5` and 3.0000 as `3`. Assignment 01 formats its number with a string stream
instead (see [`<iomanip>`](#primer/iomanip)).

Learn more:
- [std::printf, std::snprintf and related functions](https://en.cppreference.com/w/cpp/io/c/fprintf)
  on cppreference, with the table of format codes

## `<functional>`: `std::function`
<!--
id: functional
also: std::function; function object; callback
code: #\s*include\s*<functional>|\bstd::function\b
-->
`<functional>` declares `std::function`, a variable that holds something you can call: a
function, or a [lambda](#primer/lambdas), a function written inline where it is used. The type in
angle brackets gives the call's shape, return type first: `std::function<void(int, double)>`
takes an `int` and a `double` and returns nothing. You call it like a function. A parameter of
this type lets the caller pass in the code to run at some point, often called a callback.

```cpp
void forEachSquare(int n, const std::function<void(int)>& visit) {
  for (int i = 0; i < n; ++i) visit(i * i);
}
forEachSquare(3, [](int sq) { std::cout << sq << "\n"; });  // 0 1 4
```

Assignment 14 uses it in `src/render/Scanline.h`. `forEachRow(edges, height, visit)` walks the
picture row by row and calls `visit(row, crossings)` with each row's crossings sorted by x. The
visit parameter is a `std::function<void(int row, const std::vector<Crossing>& crossings)>`.
Your [even-odd](#primer/even-odd) fill in 14 and your [non-zero](#primer/nonzero) fill in 16
each pass their own visit function, so both share the same [scanline](#primer/scanline) code.

Learn more:
- [std::function](https://en.cppreference.com/w/cpp/utility/functional/function) on cppreference
- [Function pointers](https://www.learncpp.com/cpp-tutorial/function-pointers/) on learncpp.com,
  with a section on `std::function`
