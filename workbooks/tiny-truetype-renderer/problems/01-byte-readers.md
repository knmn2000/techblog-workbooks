# 01 · Read big-endian numbers

**Difficulty:** Easy · **Assignment** 1 of 18 · **Check:** `.\check 01`

**Tags**
- *Language:* [fixed-width integers](#primer/cstdint) (`uint8_t` ... `int32_t`) · [bit shifts and OR](#primer/bit-operations) · [two's complement](#primer/twos-complement) · [templates](#primer/templates) (optional) · [exceptions](#primer/exceptions)
- *Library:* [`std::ifstream`](#primer/fstream) in binary mode (`get`, `seekg`) · [`std::char_traits<char>::eof()`](#primer/string)
- *Concepts:* [big-endian byte order](#primer/big-endian) · [signed vs unsigned integers](#primer/integer-types) · [fixed-point numbers](#primer/f2dot14) (F2Dot14) · [file offsets](#primer/file-offset)

## Read in the blog first

You can pass using this page alone. For the background, read the blog's
"What is TrueType?" section, then
[Reading .ttf files](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Reading%20.ttf%20files).
That section has one paragraph, and the author's code follows it, below a link card.

## What you need

- [Header and source files](#primer/header-files): `ByteReader.h` declares the reader, and
  `ByteReader.cpp` defines its member functions as `ByteReader::jumpTo` and so on.
- [`#include`](#primer/include): the program includes the standard headers in angle brackets and
  your reader as `"font/ByteReader.h"`, by its path under `src/`. Each include's comment says
  what the file uses it for.
- [`main`, `argc` and `argv`](#primer/main): the program's `main` takes the input and output file
  names from `argv[1]` and `argv[2]`.
- [Namespaces and `std::`](#primer/namespaces): the program keeps its helpers `decimal` and `run`
  in an unnamed namespace, and standard names such as `std::string` carry the `std::` prefix.
- [Integer types](#primer/integer-types): the six readers return signed and unsigned types of 8,
  16 and 32 bits, and `get()` returns a plain `int`.
- [Two's complement](#primer/twos-complement): `readInt8`, `readInt16` and `readInt32` call your
  `readBigEndian` with a signed type, so it has to turn the value negative when the top bit is
  set. The entry shows how to do that without the arithmetic wrapping.
- [Integer promotion](#primer/integer-promotion): the program prints `+reader.readUint8()` so the
  byte comes out as a number, and a small type becomes an `int` before a shift.
- [Integer overflow](#primer/integer-overflow): a `jump` followed by `skip`s can pass 4294967295,
  more than a `uint32_t` holds.
- [Bit shifts and bitwise operators](#primer/bit-operations): you build each number from its
  bytes with shifts and OR.
- [`double` and floating point](#primer/floating-point): `readF2Dot14` returns a `double`, and
  `decimal` in the program turns it into text.
- [Integer division](#primer/integer-division): an F2Dot14 value is its 16-bit integer divided by
  16384, and dividing two integers in C++ drops the fraction.
- [`const`](#primer/const): parameters such as `const uint32_t offset` in `ByteReader.cpp` can't
  change inside the function.
- [References and `const` references](#primer/references): the constructor takes
  `const std::string& path`, and `run` takes `ByteReader& reader` because a read moves the
  reader's position.
- [Pointers and arrays](#primer/pointers): `argv` in the program's `main` is a `char**`, a list of
  C strings.
- [`auto`](#primer/auto): `run` keeps its `line` helper in an `auto` variable, and `line` takes
  `const auto& value` so it prints any of the read types.
- [Lambdas](#primer/lambdas): `line` is a lambda that writes `<op> <value>` to the output file.
- [Loops](#primer/loops): the program reads its input line by line with `std::getline`, and
  `readBigEndian` reads one byte per pass.
- [The conditional operator `?:`](#primer/conditional-operator): `decimal` returns `"0"` in place
  of `"-0"` with `?:`.
- [Structs and classes](#primer/struct-class): `ByteReader` is a class with a private
  `std::ifstream file_`, and `UnexpectedEof` is a struct.
- [Constructors and initializer lists](#primer/constructors): `ByteReader`'s constructor opens
  `file_` in its initializer list and throws when the file doesn't open.
- [`explicit`](#primer/explicit): `ByteReader(const std::string& path)` is `explicit`, so a string
  can't turn into a reader by accident.
- [Deriving from a class](#primer/inheritance): `UnexpectedEof` derives from `std::runtime_error`,
  and the program catches it by its own type before the general `std::exception`.
- [Exceptions](#primer/exceptions): `nextByte` throws `UnexpectedEof` at the end of the file, and
  the program catches it to write `eof` and stop.
- [Function templates](#primer/templates): `readBigEndian<T>` in `ByteReader.h` is one function
  for all six integer types.
- [`static_assert`](#primer/static-assert): `readBigEndian` starts with one that stops the build
  for a type that isn't an integer or is wider than 4 bytes.
- [`sizeof`](#primer/sizeof): the TODO in `readBigEndian` reads `sizeof(T)` bytes: 1, 2 or 4.
- [`<fstream>`](#primer/fstream): `ByteReader` reads the font through a `std::ifstream` opened in
  binary mode. You move it with `seekg` and read a byte with `get()`.
- [`<iostream>`](#primer/iostream): the program writes its usage line and errors to `std::cerr`,
  and `run` writes answers to the `std::ostream&` it is given.
- [`<string>`](#primer/string): the program reads each input line with `std::getline` and trims
  zeros with `find_last_not_of`, and `std::char_traits<char>::eof()` is what `get()` returns at
  the end.
- [`<sstream>`](#primer/sstream): the program splits each line into an operation and its number
  with a `std::istringstream`, and `decimal` writes into a `std::ostringstream`.
- [`<stdexcept>`](#primer/stdexcept): `UnexpectedEof` derives from `std::runtime_error`, and each
  TODO throws `std::logic_error("not implemented: ...")`.
- [`<exception>`](#primer/exception): `main` catches any other error as `std::exception`, which
  comes in with `<stdexcept>`, so the program doesn't include `<exception>` itself.
- [`<iomanip>`](#primer/iomanip): `decimal` prints an F2Dot14 value with `std::setprecision(14)`,
  then trims the trailing zeros.
- [`<cstdint>`](#primer/cstdint): the readers return `uint8_t` to `int32_t`, and a wider type
  gives you room to build a number before you know its sign.
- [`<type_traits>`](#primer/type-traits): the `static_assert` in `readBigEndian` tests
  `std::is_integral_v<T>`, and the same header can tell you whether `T` is signed.
- [Big-endian byte order](#primer/big-endian): each read puts the first byte on top, so `ff fe`
  is the `u16` 65534.
- [File offsets](#primer/file-offset): `jumpTo` counts its offset from byte 0 of the file, and
  `skipBytes` counts from the current position.
- [Fixed-point numbers and F2Dot14](#primer/f2dot14): `readF2Dot14` turns a signed 16-bit value
  into a fraction.
- [The C++ compiler](#primer/compiler): `.\check 01` needs g++ on your `PATH` to build the
  project. The entry says how to install it.
- [CMake](#primer/cmake): your first check configures the project with CMake, which turns
  `assignments/assignment_01_byte_readers.cpp` into the program `assignment_01`.
- [Python and `py -P`](#primer/python): `.\check 01` runs `tools/check.py`, so it needs Python
  3.11 or newer.
- [Running a program from the terminal](#primer/command-line): type `.\check 01` in the workbook
  folder, and paste a failing test's `reproduce:` line to run `assignment_01.exe` on that input.
- [The checker](#primer/checker): the first `.\check 01` creates this assignment's three files
  and stops, and later runs check your code against the 28 tests.
- [Exit codes](#primer/exit-codes): while a TODO still throws, the program exits with 99 and the
  checker names the function, such as `readBigEndian`, that you haven't written yet.

## Source material

- Microsoft, *OpenType specification*, [Data types](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#data-types).
  It lists every type and has the F2Dot14 table above.
- Apple, *TrueType Reference Manual*, [Data types](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html)
  (the table near the top of "Font files")
- cppreference: [`std::basic_istream::get`](https://en.cppreference.com/w/cpp/io/basic_istream/get)
  and [`seekg`](https://en.cppreference.com/w/cpp/io/basic_istream/seekg)
- The blog: [Reading .ttf files](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Reading%20.ttf%20files)

## Where this fits

A TrueType font stores every number big-endian. Your `ByteReader` is the first piece of your
project, and every later assignment that reads the font goes through it: assignment 02 for the
table directory, assignments 03 to 05 for the `cmap`, `loca` and metrics tables, and
assignments 07 and 09 for glyph outlines.

## The problem

Write a program that opens a binary file, runs a list of read and move operations on it, and
writes every number it reads.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The first line of the input file names the file to read. Every other line is one operation:

| Line | Meaning |
|---|---|
| `file <path>` | The binary file to read (first line only). The path is relative to the workbook folder and contains no spaces. |
| `u8`, `u16`, `u32` | Read an unsigned integer of 1, 2 or 4 bytes at the current position. |
| `i8`, `i16`, `i32` | Read a signed integer of 1, 2 or 4 bytes. |
| `f2dot14` | Read a 2-byte F2Dot14 number (see below). |
| `jump <offset>` | Move to byte `offset`, counted from the start of the file. Byte 0 is the first byte. |
| `skip <count>` | Move `count` bytes forward from the current position. |

The reader keeps a current position: the byte the next read starts at.

- The position starts at byte 0.
- Each read moves it forward by the number of bytes it read.
- A `jump` or `skip` may move the position to the end of the file or past it. The move itself
  succeeds, and the next read runs out of bytes.

### Output

- Each read operation writes one line, in input order: the operation's name, a space, and the
  value in decimal. For example `u16 65535`, `i16 -1` or `f2dot14 1.75`.
- `jump` and `skip` write nothing.
- F2Dot14 values have at most 14 digits after the decimal point, and the Boilerplate's
  output code prints all of them. If you write your own output code, the checker accepts any
  value within 0.000001 of the exact one.

If a read needs a byte past the end of the file, write the line `eof` in place of its value
and stop: your program runs no further operations. A read that ends on the last byte of the
file succeeds.

### Big-endian byte order

Big-endian means the most significant byte comes first, and TrueType stores every number
this way. The two bytes `12 34` hold `0x1234` = 4660 (a little-endian reader would get
`0x3412` = 13330 instead). With the bytes b0, b1, b2, b3 in file order:

- u16 = b0 × 256 + b1
- u32 = b0 × 2^24 + b1 × 2^16 + b2 × 2^8 + b3

| Operation | Bytes | Values |
|---|---|---|
| `u8` | 1 | 0 to 255 |
| `u16` | 2 | 0 to 65535 |
| `u32` | 4 | 0 to 4294967295 |
| `i8` | 1 | −128 to 127 |
| `i16` | 2 | −32768 to 32767 |
| `i32` | 4 | −2147483648 to 2147483647 |
| `f2dot14` | 2 | −2 to 1.99993896484375 |

### Signed numbers: two's complement

Two's complement is how the signed types store negative numbers. A signed read takes the
same bytes as the unsigned read of the same size. Call the unsigned result u and the size in
bits n (8, 16 or 32):

- If the top bit is 1 (u ≥ 2^(n−1)), the value is u − 2^n.
- Otherwise it is u.

| Bytes | Unsigned | Signed |
|---|---|---|
| `7f` | 127 | 127 |
| `80` | 128 | 128 − 256 = −128 |
| `ff` | 255 | 255 − 256 = −1 |
| `fe d4` | 65236 | 65236 − 65536 = −300 |
| `80 00 00 00` | 2147483648 | −2147483648 |

### F2Dot14

An F2Dot14 is a fixed-point number: 2 bits before the binary point and 14 after. Read the
2 bytes as an `i16`, then divide by 16384 (2^14). The OpenType specification gives these
examples:

| Bytes | As `i16` | Value | The spec rounds it to |
|---|---|---|---|
| `7f ff` | 32767 | 1.99993896484375 | 1.999939 |
| `70 00` | 28672 | 1.75 | 1.75 |
| `00 01` | 1 | 0.00006103515625 | 0.000061 |
| `00 00` | 0 | 0 | 0 |
| `ff ff` | −1 | −0.00006103515625 | −0.000061 |
| `80 00` | −32768 | −2 | −2 |

Fonts use F2Dot14 for the scale factors of compound glyphs (assignment 09) and for
variable-font axis coordinates.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** `u8`, `u16` and `u32` read 1, 2 and 4 bytes, most significant byte first, as
  non-negative numbers.
- **R2** `i8`, `i16` and `i32` read the same bytes as two's complement, so a set top bit
  gives a negative number.
- **R3** `f2dot14` is the `i16` value divided by 16384.
- **R4** `jump` moves to an absolute offset. `skip` moves forward from the current position.
  Each read moves forward by its own size.
- **R5** A read that needs bytes past the end of the file writes `eof`, and your program
  writes nothing after it.

## Examples

### Example 1: the same bytes, unsigned and signed (test `01-R2-same-bytes`)

The file holds the 4 bytes `ff fe ff ff`.

```
input:   file tests/01/data/01-R2-same-bytes.bin
         u16
         jump 0
         i16
         jump 0
         u32
         jump 0
         i32
         jump 0
         u8
         i8

output:  u16 65534
         i16 -2
         u32 4294901759
         i32 -65537
         u8 255
         i8 -2
```

`ff fe` is `0xfffe` = 65534. As an `i16`, 65534 ≥ 32768, so the value is 65534 − 65536 = −2.
The last two reads are `ff` (255) and then `fe` (254 − 256 = −2), because `u8` moved the
position on by one byte.

### Example 2: two fields of a real font (test `01-R4-font-head`)

```
input:   file fonts/JetBrainsMonoNerdFont-Bold.ttf
         jump 300
         skip 18
         u16
         skip 30
         i16

output:  u16 1000
         i16 1
```

The font's `head` table starts at byte 300 (assignment 02 shows how to find that). Its
`unitsPerEm` field is 18 bytes in, at byte 318. Reading it moves the position to 320, and
`skip 30` lands on byte 350, which is `head` + 50: the `indexToLocFormat` field that
assignment 04 needs.

### Example 3: running out of bytes (test `01-R5-eof-in-u32`)

The file holds the 5 bytes `01 02 03 04 05`.

```
input:   file tests/01/data/01-R5-eof-in-u32.bin
         u16
         u32
         u8

output:  u16 258
         eof
```

`u16` reads `01 02` = 258. The `u32` needs 4 bytes and the file has 3 left, so the program
writes `eof` and stops. It doesn't run the last `u8`, even though one byte remains.

## Constraints

- Offsets and counts are whole numbers from 0 to 4294967295. A `jump` followed by `skip`s can
  move the position past 4294967295, so keep the position in a 64-bit number (or let the stream
  do it): a 32-bit position would wrap around and read the wrong bytes.
- The files are hand-made files of up to 64 bytes (one is empty) and the two fonts in
  `fonts/` (2.4 MB and 9.6 MB).
- Each input has at most 40 operations.
- Each case has a 10-second limit. A correct solution finishes in milliseconds.
- There are 28 tests: hand-made files for each rule (sign boundaries, the spec's F2Dot14
  table, jumps and skips, every way to run out of bytes), header fields of both fonts,
  F2Dot14 values from Noto Sans JP's `avar` table, and 4 random files with random
  operations.

## Hints

<details><summary>Hint 1: where to start</summary>

Read one byte at a time with `get()`. It returns an `int`: 0 to 255 for a byte, or
`std::char_traits<char>::eof()` when there are no more bytes. Start the number at 0, and for
each byte shift what you have 8 bits left and OR the byte in.
</details>

<details><summary>Hint 2: the approach</summary>

One function can serve all six integer types (a function template, in C++). Loop once per
byte of the type, building the value in a wide unsigned variable such as `uint64_t`, and report
the end of the file (by throwing an exception, for example) as soon as `get()` reports it. For a
signed type, apply the two's complement rule to the finished value.

An F2Dot14 is a 16-bit signed read divided by 16384.0, a jump is
`seekg(offset, std::ios::beg)`, and a skip is `seekg(count, std::ios::cur)`. (In the
Boilerplate these are `readBigEndian`, `readF2Dot14`, `jumpTo` and `skipBytes`, and the end of
the file is the `UnexpectedEof` exception.)
</details>

<details><summary>Hint 3: the traps</summary>

- Compare `get()`'s result with EOF before turning it into a byte. Once cast, EOF looks like
  the byte `ff`.
- `char` may be signed. If you read into a `char` (with `read`), the byte `ff` becomes −1,
  and shifting a negative value spreads ones through the high bits. Convert to `uint8_t` first.
- The sign rule uses the full width: subtract 2^16 for an `i16`, not 2^15 or 2^8.
- Check for the end after every `get()` in a read. `file.eof()` is no help before a read: it
  turns true after a read has failed.
- A stream that has failed ignores `seekg` until you call `clear()`. Calling `clear()` at the
  start of your jump keeps your reader usable after an error.
- Printing a `uint8_t` with `<<` prints a character. Put `+` in front of it, or cast it to `int`, to print the number.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
read_big_endian(T):
    value = 0                               # wide and unsigned, e.g. uint64
    repeat size_of(T) times:
        c = file.get()
        if c is EOF: report "end of file"   # e.g. throw an exception
        value = (value << 8) | c
    n = 8 * size_of(T)
    if T is signed and value >= 2^(n-1):
        return value - 2^n                  # subtract in a signed type (int64), then convert to T
    return value

read_f2dot14():  return read_big_endian(int16) / 16384.0
jump_to(offset): file.clear(); file.seekg(offset, from the start)
skip(n):         file.seekg(n, from the current position)
```
</details>

## Checking your solution

```
.\check 01                         run every test
.\check 01 -Case 01-R2-same-bytes  one test, showing its full input, expected output and your output
.\check 01 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 01 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R2  Signed reads (i8, i16, i32): two's complement ........................    0 / 4   FAILED
      x 01-R2-i8  i8: 00 7f 80 ff 81 01
          line 3: expected `i8 -128`, got `i8 0`
          likely cause: R2 - Signed reads (i8, i16, i32): two's complement
          expected values from: Python struct (>B >b >H >h >I >i; F2Dot14 = >h / 16384 exactly)
          reproduce: build/solutions/assignment_01.exe build/cases/01/01-R2-i8.in build/cases/01/01-R2-i8.out
```

## After you pass: compare with the author's code

[The blog's byte readers](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Byte%20readers)
live in a `FontParser` class, which opens the font as a binary `std::ifstream` and keeps it
for every later step. `jumpTo` and `skipBytes` wrap `seekg`. A function template,
`readBeOrThrow<T>`, reads `sizeof(T)` bytes with `get()`, throws "unexpected EOF" at the end
of the file, assembles the bytes most significant first, and converts signed types from two's
complement by hand. `readUint8` to `readInt32` are one-line wrappers around it, and
`readF2Dot14` divides an `int16` by 2^14. Your `ByteReader` holds what the post keeps in
`FontParser`, and the Boilerplate's `readBigEndian` plays the part of `readBeOrThrow`. The
author's repository has the same code, plus a `static_assert` that `T` is an integer type.

The author's `readF2Dot14` returns a `float`, where the Boilerplate uses `double`. An F2Dot14
value needs 16 significant bits and a `float` has 24, so a `float` holds every one without
rounding and both give the same numbers.

Two details of the snippet differ from this page. If the file doesn't open, the constructor
prints "failed to open file" and carries on, so the first read throws "unexpected EOF" instead.
And `jumpTo` doesn't call `clear()`: after a read runs past the end, the stream stays failed and
later jumps do nothing. The author's program doesn't catch the exception, so neither shows
there, but a reader that recovers from errors needs the `clear()`.

Since C++20, the standard defines a conversion from an unsigned
value to a signed type of the same width as wrapping modulo 2^n, so
`static_cast<int16_t>(uint16_t{0xfffe})` is −2. Before C++20 the result was
implementation-defined, which is one reason to write the conversion out by hand as the author
does. Both versions give the same answers on these tests.
