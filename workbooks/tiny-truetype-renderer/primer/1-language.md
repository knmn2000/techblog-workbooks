# C++ language

The parts of the C++ language the project uses, from how files fit together to templates and
lambdas. Each entry assumes you can program a little in a language such as Python or JavaScript.

## Header and source files
<!--
id: header-files
also: .h file; .cpp file; declaration; definition; #pragma once; header guard; translation unit
code: #\s*pragma\s+once
-->
A C++ project splits its code into source files (`.cpp`) and header files (`.h`). The compiler
turns each `.cpp` into machine code on its own, without looking at the other `.cpp` files. To
call a function written in another file, a source file needs its declaration: the name, the
parameter types and the return type, with no body. The definition, with the body, lives in one
`.cpp`. A header collects declarations so that every file that needs them can include them.

```cpp
// Ruler.h
#pragma once
int inches(int cm);                       // declaration

// Ruler.cpp
#include "Ruler.h"
int inches(int cm) { return cm * 10 / 254; }  // definition
```

`#pragma once` as the first line tells the compiler to read the header once per `.cpp`, even
when two other headers both include it. It isn't part of the C++ standard, but GCC, Clang and
MSVC all support it. Older code does the same with a header guard (`#ifndef` / `#define` /
`#endif`).

For a class, the header declares the class and its member functions, and the `.cpp` defines
them with the class name in front: `void ByteReader::jumpTo(uint32_t offset) { ... }`.

Most assignments add a pair: `ByteReader.h` and `ByteReader.cpp` in 01, then `FontParser` in
02 and `Cmap` in 03. A few later files are only a header, such as `Geometry.h` (10), whose
functions must then be [`inline`](#primer/inline). Every header in the project starts with
`#pragma once`.

Learn more:
- [Header files](https://www.learncpp.com/cpp-tutorial/header-files/) on learncpp.com
- [Header guards](https://www.learncpp.com/cpp-tutorial/header-guards/) on learncpp.com, with
  `#pragma once` at the end
- [Forward declarations and definitions](https://www.learncpp.com/cpp-tutorial/forward-declarations/)
  on learncpp.com

## `#include`: `<...>` and `"..."`
<!--
id: include
also: include directive; include path; include directories; angle brackets; quotes
code: #\s*include\b
-->
`#include` copies the text of another file into the current one before the compiler reads it.
That is how a `.cpp` gets the declarations in a [header](#primer/header-files).

The two spellings search in different places:

- `#include <vector>` with angle brackets is for the standard library and other installed
  libraries. The compiler searches its own include directories.
- `#include "font/ByteReader.h"` with quotes is for your own headers. The compiler looks in the
  folder of the file being compiled first, then in the include directories it was given.

The project's `CMakeLists.txt` gives the compiler two include directories, `src/` and
`third_party/`. So every file names a project header by its path under `src/`, whichever
folder it sits in: `assignments/assignment_03_cmap.cpp` and `src/font/Cmap.cpp` both write
`#include "font/Cmap.h"`. A wrong path stops the build with an error such as
`fatal error: ByteReader.h: No such file or directory`.

Include a header for each name a file uses: [`<string>`](#primer/string) for `std::string`,
[`<vector>`](#primer/vector) for `std::vector`. A file that compiles because another header happened to include `<string>` can
break when that header changes. The library part of the primer has one entry per standard
header the project includes.

Each file lists its includes at the top, and each assignment's Start here card lists
the earlier headers you can include. `src/FrameBufferCanvas.cpp` (06) also includes
[`stb_image_write.h`](#primer/stb-image-write) from `third_party/`, in a special way described under
[`#define` and `#pragma`](#primer/preprocessor).

Learn more:
- [Source file inclusion](https://en.cppreference.com/w/cpp/preprocessor/include) on cppreference
- [Introduction to the preprocessor](https://www.learncpp.com/cpp-tutorial/introduction-to-the-preprocessor/)
  on learncpp.com

## `#define` and `#pragma`
<!--
id: preprocessor
also: preprocessor; macro; #define; #pragma GCC diagnostic; STB_IMAGE_WRITE_IMPLEMENTATION; single-header library
code: #\s*define\b|#\s*pragma\s+GCC\b
-->
Lines that start with `#` are for the preprocessor, a step that edits the text of a file before
the compiler proper reads it. [`#include`](#primer/include) is one; `#define` and `#pragma` are
two more.

`#define NAME` defines a macro, a name the preprocessor knows about. Code can then test for it
with `#ifdef NAME`. The project uses this once, for
[stb_image_write](#primer/stb-image-write), a library that comes as a single header. Included normally, the header gives only declarations. With
`STB_IMAGE_WRITE_IMPLEMENTATION` defined first, it also gives the function bodies:

```cpp
#define STB_IMAGE_WRITE_IMPLEMENTATION
#include "stb_image_write.h"   // declarations and definitions
```

Do this in one `.cpp` file only. Two files doing it would each define the same functions, and
the linker would stop with "multiple definition".

`#pragma` passes an instruction to the compiler. `#pragma GCC diagnostic push`, then
`#pragma GCC diagnostic ignored "-Wall"`, turns off the listed warnings until the matching
`#pragma GCC diagnostic pop`. The project wraps the stb include this way so that the library's
own warnings don't bury yours. Clang understands the same lines.

`src/FrameBufferCanvas.cpp` (assignment 06) holds both: the `#define` and the warning pragmas
around the include. For your own constants, use [`constexpr`](#primer/constexpr) instead of
`#define`: a `constexpr` value has a type and follows the usual scope rules.

Learn more:
- [Introduction to the preprocessor](https://www.learncpp.com/cpp-tutorial/introduction-to-the-preprocessor/)
  on learncpp.com
- [Diagnostic pragmas](https://gcc.gnu.org/onlinedocs/gcc/Diagnostic-Pragmas.html) in the GCC manual
- [stb](https://github.com/nothings/stb) on GitHub, the home of stb_image_write

## `inline` functions
<!--
id: inline
also: inline function; one definition rule; ODR; function defined in a header; multiple definition
code: \binline\b
-->
A function normally has its definition in one `.cpp` file. If you write the whole function in a
header instead, every `.cpp` that includes the header gets its own copy, and the linker stops
with an error such as `multiple definition of 'half(double)'`. Marking the function `inline`
tells the compiler and linker that these copies are one function and they may keep any one of
them. (The keyword once asked the compiler to paste the body in at each call; today its main
effect is this permission to define a function in a header.)

```cpp
// Units.h
#pragma once
inline double half(double v) { return v / 2; }   // fine in any number of .cpp files
```

Two kinds of function need no keyword: a member function written inside its class body is
inline already, and a function template may also be defined in a header.

In `src/font/ByteReader.h` (01), `readUint8` to `readInt32` are written inside the class, so
they are inline without the keyword. The first header made only of functions is
`src/utils/Geometry.h` (10): the project has no `Geometry.cpp`, so `lerp` and the `Vec2`
operators are each marked `inline`.

Learn more:
- [Inline functions and variables](https://www.learncpp.com/cpp-tutorial/inline-functions-and-variables/)
  on learncpp.com
- [inline specifier](https://en.cppreference.com/w/cpp/language/inline) on cppreference

## `main`, `argc` and `argv`
<!--
id: main
also: main function; command-line arguments; argc; argv; entry point; return value of main
code: \bint\s+main\s*\(
-->
A C++ program starts in a function called `main`. To read its command-line arguments, `main`
takes two parameters: `argc`, the number of words on the command line, and `argv`, those words
as C strings ([`char**`](#primer/pointers), a list of pointers to characters). `argv[0]` is the
program itself, so a program run as `assignment_07 in.txt out.txt` gets `argc == 3`, with
`argv[1]` = `"in.txt"` and `argv[2]` = `"out.txt"`.

```cpp
int main(int argc, char** argv) {
  if (argc != 2) { std::cerr << "usage: " << argv[0] << " <name>\n"; return 2; }
  const std::string name = argv[1];    // a C string converts to std::string
  std::cout << "hello " << name << "\n";
  return 0;
}
```

The number `main` returns becomes the program's [exit code](#primer/exit-codes): 0 for
success, anything else for a failure. Leaving `main` without a `return` returns 0.

Every assignment has a program in `assignments/`, starting with
`assignments/assignment_01_byte_readers.cpp`. Its `main`, which the Boilerplate gives you,
checks for two arguments (the input file and the output file the checker passes), returns 2
when they're missing or can't be opened, catches errors and returns 1 or 99, and returns 0 when
it has written the answer. In assignment 18 you add `src/main.cpp`, the finished `tiny_ttf`
program.

Learn more:
- [Command line arguments](https://www.learncpp.com/cpp-tutorial/command-line-arguments/) on
  learncpp.com
- [Main function](https://en.cppreference.com/w/cpp/language/main_function) on cppreference

## Namespaces and `std::`
<!--
id: namespaces
also: namespace; std::; scope resolution operator; ::; anonymous namespace; unnamed namespace; using namespace; using alias; type alias
code: \bnamespace\b|\bstd::\w|\busing\s+\w+\s*=
-->
A namespace groups names so that two libraries can both have a `sort` without a clash. You
reach a name inside one with `::`, the scope resolution operator. Everything in the standard
library is in the namespace `std`, which is why the code writes
[`std::vector`](#primer/vector), [`std::string`](#primer/string) and
[`std::sort`](#primer/algorithm).

Namespaces have three more uses here:

- An unnamed namespace, `namespace { ... }`, makes its contents private to the `.cpp` file.
  Two files can then each have a helper called `number` without the linker seeing two
  definitions.
- `using Tables = std::map<std::string, TableRecord>;` gives a type a shorter second name, a
  type alias.
- `using namespace name;` inside a function lets it call that namespace's names without the
  prefix.

```cpp
namespace {                                     // only this file sees `twice`
int twice(int x) { return 2 * x; }
}
using Names = std::vector<std::string>;         // an alias
```

Avoid `using namespace std;` in a header: every file that includes the header would get all of
`std`'s names, and they can collide with yours.

Assignment 01's program puts its helpers, `decimal` and `run`, in an unnamed namespace, and the
later programs do the same. Your own `.cpp` files can keep their helpers private this way too.
`src/font/FontParser.h` (02) declares the `Tables` alias, a
[`std::map`](#primer/map) from each table's tag to its record.

Learn more:
- [Naming collisions and an introduction to namespaces](https://www.learncpp.com/cpp-tutorial/naming-collisions-and-an-introduction-to-namespaces/)
  on learncpp.com
- [Unnamed and inline namespaces](https://www.learncpp.com/cpp-tutorial/unnamed-and-inline-namespaces/)
  on learncpp.com
- [Namespaces](https://en.cppreference.com/w/cpp/language/namespace) on cppreference

## Integer types: signed and unsigned
<!--
id: integer-types
also: int; unsigned; long; long long; short; signed vs unsigned; sign-compare
code: \b(int|unsigned|short|long)\b
-->
C++ has several integer types, and each has a fixed number of bits on a given machine. Unlike
Python's integers, they can't grow:

| Type | Bits on the workbook's platforms |
|---|---|
| `char` | 8 |
| `short` | 16 |
| `int` | 32 (the standard only promises at least 16) |
| `long` | 32 on Windows, 64 on 64-bit Linux and macOS |
| `long long` | 64 |

Each comes in a signed version, which holds negative numbers ([two's
complement](#primer/twos-complement)), and an `unsigned` one: 32 bits hold −2147483648 to
2147483647 signed, or 0 to 4294967295 unsigned. Because the sizes differ between systems, the
font code uses the fixed-width names `uint16_t`, `int32_t` and so on, covered under
[`<cstdint>`](#primer/cstdint). [`std::size_t`](#primer/size-t) is the unsigned type for sizes
and indexes: `v.size()` returns one, and it has 64 bits on a 64-bit system.

Mixing signed and unsigned values is the classic trap. In `-1 < 1u` the −1 is converted to
unsigned first, becomes 4294967295, and the comparison is false. GCC warns about such
comparisons ("comparison of integer expressions of different signedness"). Subtraction has the
same problem: when `v` is empty, `v.size() - 1` is about 1.8 × 10^19, not −1. A loop
condition written as `i + 1 < v.size()` instead of `i < v.size() - 1` stays correct for an
empty vector.

The font's fields are unsigned or signed by the specification: offsets and counts are
unsigned, coordinates and `descent` are signed. Assignment 01 reads both kinds. The canvas (06)
uses `int` for pixel coordinates, since a line can start off the picture at a negative
position.

Learn more:
- [Signed integers](https://www.learncpp.com/cpp-tutorial/signed-integers/) on learncpp.com
- [Unsigned integers, and why to avoid them](https://www.learncpp.com/cpp-tutorial/unsigned-integers-and-why-to-avoid-them/)
  on learncpp.com
- [Fundamental types](https://en.cppreference.com/w/cpp/language/types) on cppreference, with
  the sizes on each data model

## Two's complement
<!--
id: twos-complement
also: two's complement; negative numbers in binary; sign bit; signed integer representation
-->
Two's complement is how computers store negative integers. An n-bit pattern read as unsigned
means a number from 0 to 2^n − 1. Read as signed, the patterns from 0 to 2^(n−1) − 1 mean the
same numbers, and each pattern from 2^(n−1) up means its unsigned value minus 2^n. So the top
bit tells you the sign.

For 8 bits: `0x7F` is 127 either way, `0x80` is 128 unsigned and 128 − 256 = −128 signed, and
`0xFF` is 255 unsigned and −1 signed. For 16 bits, `0xFFF6` is 65526 unsigned and
65526 − 65536 = −10 signed.

In C++ there are two ways to turn an n-bit unsigned value into the signed one. Either do the
subtraction in a signed type wide enough for the result, such as `int64_t`, or convert the
value to the signed type of the same width, `intN_t`:

```cpp
const uint16_t raw = 0xFFF6;                  // 65526, two bytes from a file
int64_t a = raw;                              // 65526, now in a signed type
if (a >= 0x8000) a -= 0x10000;                // -10: the subtraction is signed
const int16_t b = static_cast<int16_t>(raw);  // -10 as well
```

Don't subtract in an unsigned type. With `uint32_t x = 0xFFF6;`, `x - 0x10000` wraps around
to 4294967286 instead of giving −10 (see [integer overflow](#primer/integer-overflow)).

`static_cast<int16_t>(uint16_t{0xFFFE})` is guaranteed to give −2 since C++20, which requires
signed integers to be two's complement and defines the conversion as keeping the bits. Before
C++20 the result of converting a value that doesn't fit into a signed type was
implementation-defined (each compiler chose, and GCC, Clang and MSVC all gave −2). This project
compiles as C++20, so both ways above are fine.

Adding works the same for both readings, which is why hardware uses this scheme: −1 + 1 is
`0xFF` + `0x01`, which wraps to `0x00`.

TrueType stores signed fields this way, [big-endian](#primer/big-endian). Assignment 01 asks you
to build the signed readers (`readInt8`, `readInt16`, `readInt32`) in `src/font/ByteReader.h`
from the bytes, and later assignments read signed fields through them, such as `descent` (05)
and the point coordinates of glyph outlines (07). An [F2Dot14](#primer/f2dot14) (01) is a signed
16-bit number divided by 16384.

Learn more:
- [Two's complement](https://en.wikipedia.org/wiki/Two%27s_complement) on Wikipedia, with
  tables for 3 and 8 bits
- [Signed integers](https://www.learncpp.com/cpp-tutorial/signed-integers/) on learncpp.com

## Integer promotion
<!--
id: integer-promotion
also: integral promotion; usual arithmetic conversions; implicit conversion; unary plus; printing uint8_t; 2u
code: \(\+\w|\b\d+u\b
-->
C++ doesn't do arithmetic on types smaller than `int`. Before `+`, `*`, `<<` or a comparison,
a `char`, `uint8_t`, `int8_t`, `uint16_t`, `int16_t` or `bool` is first converted to `int`. This
is integer promotion. Then, if the two sides still differ, the usual arithmetic conversions
pick a common type: `int` with `unsigned` gives `unsigned`, any integer with `double` gives
`double`.

```cpp
uint8_t a = 200, b = 100;
auto sum = a + b;            // int 300, not 44: both were promoted first
uint8_t c = a + b;           // 44: the int 300 cut back to 8 bits
uint8_t byte = 65;
std::cout << byte;           // prints A: uint8_t is a character type
std::cout << +byte;          // prints 65: unary + promotes it to int
```

Three places in the workbook depend on it:

- Assignment 01's program prints `+reader.readUint8()` and `+reader.readInt8()`. Without the
  `+`, `<<` would print the byte as a character.
- When you shift bytes into a number (01), a promoted `uint8_t` is a signed `int`, and
  `byte << 24` can reach the sign bit. Shift inside a wide unsigned variable, or cast the
  byte to `uint32_t` before shifting.
- In the short [`loca`](#primer/loca) format (04) each entry is a 16-bit number holding half
  the offset. The doubled offset can pass 65535, so it needs a type of at least 32 bits:
  stored back in a `uint16_t`, it would be cut to 16 bits.

Learn more:
- [Floating-point and integral promotion](https://www.learncpp.com/cpp-tutorial/floating-point-and-integral-promotion/)
  on learncpp.com
- [Arithmetic conversions](https://www.learncpp.com/cpp-tutorial/arithmetic-conversions/) on
  learncpp.com
- [Implicit conversions](https://en.cppreference.com/w/cpp/language/implicit_conversion) on
  cppreference

## Integer overflow
<!--
id: integer-overflow
also: overflow; wraparound; wrap around; modulo 2^n; undefined behaviour; undefined behavior; UB; narrowing
-->
An integer type has a fixed number of bits, so some results don't fit. What happens depends on
the type:

- Unsigned arithmetic wraps around modulo 2^n. For a `uint32_t`, 4294967295 + 1 is 0, and
  0 − 1 is 4294967295. The standard defines this, and code can rely on it.
- Signed overflow, such as `int` 2147483647 + 1, is undefined behaviour: the standard gives the
  program no meaning at all. The compiler's optimiser, the part that rewrites your code to run
  faster, may assume it never happens, so the result can be anything, including code that
  seems to work until you change the build settings.
- Storing a value in a narrower type keeps the low bits: 300 stored in a `uint8_t` becomes 44
  (300 − 256).

```cpp
uint32_t pos = 4294967295u;
pos += 2;                   // 1: wrapped, and the program reads the wrong bytes
uint64_t wide = 4294967295u;
wide += 2;                  // 4294967297: fits
```

The workbook meets this from the start. In 01 a `jump` followed by `skip`s can pass
4294967295, so the position must not live in a 32-bit variable (the stream's own position is
64-bit). In 03 you loop over the code points of each [`cmap`](#primer/cmap) group: a
`uint32_t` loop variable can never be greater than 4294967295, so a loop that stops when it
passes a group ending there never stops. And [`size() - 1`](#primer/integer-types) on an empty
vector wraps.

Learn more:
- [Unsigned integers, and why to avoid them](https://www.learncpp.com/cpp-tutorial/unsigned-integers-and-why-to-avoid-them/)
  on learncpp.com, on wraparound
- [Arithmetic operators: overflows](https://en.cppreference.com/w/cpp/language/operator_arithmetic#Overflows)
  on cppreference
- [Integer overflow](https://en.wikipedia.org/wiki/Integer_overflow) on Wikipedia

## Hexadecimal literals
<!--
id: hex-literals
also: hexadecimal; hex; 0x; base 16; integer literal; unsigned literal suffix
code: \b0[xX][0-9A-Fa-f]+\b
-->
A number written with `0x` in front is in hexadecimal, base 16: the digits are 0 to 9 and then
A to F for 10 to 15. Each hex digit stands for 4 bits, so two digits make one byte, which is
why binary formats are described in hex. `0x1F` is 1 × 16 + 15 = 31, binary `0001 1111`. Case
doesn't matter: `0xff` and `0xFF` are the same number.

```cpp
const uint8_t mask = 0x3F;      // 0011 1111: the low six bits
const uint32_t big = 0x10000;   // 65536 = 2^16
uint32_t cp = 0xFFFD;           // U+FFFD, the replacement character
```

A suffix changes the type of a literal: `2u` is `unsigned`, `1ULL` is `unsigned long long`. A
literal without a suffix is an `int` when it fits.

The problem pages write bytes in hex (`ff fe ff ff` in 01) and Unicode
[code points](#primer/code-point) as U+ and hex digits (03). To parse a hex string at run time,
as assignment 03's program does with the digits after `U+`, use
[`std::stoul(text, nullptr, 16)`](#primer/string). Later, hex constants stand for bit flags,
such as the [glyph flags](#primer/glyph-flags) of 07.

Learn more:
- [Numeral systems (decimal, binary, hexadecimal, and octal)](https://www.learncpp.com/cpp-tutorial/numeral-systems-decimal-binary-hexadecimal-and-octal/)
  on learncpp.com
- [Integer literal](https://en.cppreference.com/w/cpp/language/integer_literal) on
  cppreference

## Bit shifts and bitwise operators
<!--
id: bit-operations
also: bit shift; <<; >>; bitwise AND; bitwise OR; &; |; bit mask; bit flags; masking
code: (<<|>>)\s*\(?\d|[\w)]\s+[&|]\s+[\w(]
-->
These operators work on the bits of an integer:

- `x << n` shifts the bits left by n places, which multiplies by 2^n: `0x12 << 8` is
  `0x1200`. `x >> n` shifts right and drops the low bits: `0xE3 >> 4` is `0x0E`.
- `a | b` (OR) sets each bit that is set in either: `0x1200 | 0x34` is `0x1234`.
- `a & b` (AND) keeps only the bits set in both. With a mask, a constant whose set bits pick
  the ones you want, it tests or extracts bits: `flag & 0x01` is nonzero when bit 0 is set, and
  `byte & 0x3F` keeps the low six bits.

```cpp
uint32_t value = 0;
for (uint8_t b : {0x12, 0x34}) value = (value << 8) | b;  // 0x1234
const bool onCurve = (flags & 0x01) != 0;                 // test one bit
```

Watch the precedence: `==` binds tighter than `&`, so `flags & 0x01 == 0` means
`flags & (0x01 == 0)`. Put the `&` in parentheses (GCC warns about this one). Shifting by as
many bits as the type has, or more, is undefined, and shifts of negative numbers are easy to get
wrong: shift unsigned values, by less than their width. On [`std::cout`](#primer/iostream) the
same `<<` symbol means "write", and the types decide which one you get.

Assignment 01 builds each [big-endian](#primer/big-endian) number from its bytes in
`src/font/ByteReader.h`, which is work for shifts and OR. Assignment 07 tests the
[flag bits](#primer/glyph-flags) of every point with `&`, and 18 picks apart the byte patterns
of [UTF-8](#primer/utf-8) with shifts and masks.

Learn more:
- [Bitwise operators](https://www.learncpp.com/cpp-tutorial/bitwise-operators/) on learncpp.com
- [Bit manipulation with bitwise operators and bit masks](https://www.learncpp.com/cpp-tutorial/bit-manipulation-with-bitwise-operators-and-bit-masks/)
  on learncpp.com

## `char` and `unsigned char`
<!--
id: char
also: char; unsigned char; signed char; character; byte; char signedness; character literal
code: \bunsigned\s+char\b|static_cast<char>
-->
A `char` is one byte, and C++ uses it for text: a `std::string` is a sequence of `char`s, and
`'A'` is a character literal with the value 65. Whether a plain `char` is signed (−128 to 127)
or unsigned (0 to 255) is up to the platform. It is signed on x86 Windows, Linux and macOS and
on Apple's ARM chips, and unsigned on ARM Linux. `unsigned char` and `signed char` are always
what they say, and `uint8_t` is `unsigned char` on these compilers.

The difference shows with bytes of 0x80 and above. Read into a signed `char`, the byte `0xE3`
is −29, so `c >= 0xC0` is false and `c >> 5` is −1. Convert to `unsigned char` before you
compare or shift:

```cpp
std::string text = "\xE3\x81\x82";            // three bytes of UTF-8
for (char c : text) {
  const auto b = static_cast<unsigned char>(c); // 0xE3, 0x81, 0x82
  std::cout << (b >> 4) << ' ';                 // 14 8 8
}
```

For the same reason a byte read with [`std::ifstream::get()`](#primer/fstream) comes back as
an `int` from 0 to 255 (or end-of-file), never as a negative `char`, and assignment 01's hints
warn against reading bytes into a `char`.

In assignment 02 a [table tag](#primer/table-tag) is four bytes that you turn into the four
characters of a `std::string`, so each byte becomes a `char`. Assignment 18 decodes
[UTF-8](#primer/utf-8) text, where every byte from 0x80 up has to be read as unsigned.

Learn more:
- [Chars](https://www.learncpp.com/cpp-tutorial/chars/) on learncpp.com
- [Fundamental types: character types](https://en.cppreference.com/w/cpp/language/types#Character_types)
  on cppreference

## `double` and floating-point arithmetic
<!--
id: floating-point
also: double; float; floating point; IEEE 754; nan; NaN; infinity; inf; rounding error; epsilon; tolerance
code: \b(double|float)\b
-->
`double` holds numbers with a fractional part, in 64 bits (IEEE 754): about 15 to 16
significant decimal digits, from about 10^−308 to 10^308. `float` has 32 bits and about 7
digits. Most decimal fractions have no exact binary form, so results carry small errors:
`0.1 + 0.2 == 0.3` is false. Compare with a tolerance instead of `==` when values come out of
arithmetic.

```cpp
double a = 0.1 + 0.2;                       // 0.30000000000000004
bool same = std::abs(a - 0.3) < 1e-9;      // true
double half = 3 / 2;                        // 1: integer division, then converted
double good = 3 / 2.0;                      // 1.5: one double makes it all double
```

Dividing a nonzero `double` by zero gives infinity (`inf`), and 0.0 / 0.0 gives `nan`, "not a
number", on the compilers the workbook uses. A `nan` compares unequal to everything, itself
included, so test for it with [`std::isnan`](#primer/cmath). (Integer division by zero is
different: the program crashes.)

The first `double` you meet is the [F2Dot14](#primer/f2dot14) reader of 01: `readF2Dot14`
returns one. Glyph points (07) and the curve maths of `src/utils/Geometry.h` (10 on) are
`double` too, and some later assignments divide by numbers that can be zero or very close to
it, which calls for a [tolerance](#primer/epsilon). Pixels are integers, so values become `int`
at the end; see [converting to an integer](#primer/float-to-int).

Learn more:
- [Floating point numbers](https://www.learncpp.com/cpp-tutorial/floating-point-numbers/) on
  learncpp.com
- [Relational operators and floating point comparisons](https://www.learncpp.com/cpp-tutorial/relational-operators-and-floating-point-comparisons/)
  on learncpp.com
- [The Floating-Point Guide](https://floating-point-gui.de/), a short explanation of why
  0.1 + 0.2 isn't 0.3

## Integer division and `%`
<!--
id: integer-division
also: integer division; division truncates; remainder; modulo; %; wrapping an index
code: [\w)\]]\s*%\s*[\w(]|/\s*\d+\.\d
-->
When both sides of `/` are integers, C++ does integer division: the result is an integer, and
the fraction is dropped, rounding toward zero. `7 / 2` is 3 and `-7 / 2` is −3. If either side
is a `double`, the division is a floating-point one: `7 / 2.0` is 3.5. Dividing an integer by
zero crashes the program.

`%` gives the remainder of integer division, with the sign of the left side: `7 % 3` is 1,
`-7 % 2` is −1. Its most common use is wrapping an index back to the start of a list:

```cpp
const int n = 4;               // points 0..3 in a closed contour
for (int i = 0; i < n; ++i) {
  int next = (i + 1) % n;      // 1, 2, 3, then 0
}
double slope = static_cast<double>(dy) / dx;   // not dy / dx, which drops the fraction
```

An [F2Dot14](#primer/f2dot14) (01) is a 16-bit integer divided by 16384, and the result has a
fraction, so that division has to happen in floating point. In assignment 06, `cx - w / 2` in
`drawRect` uses integer division on purpose, so an even width puts the extra column on the
left. The slope of a line must not: the page warns that `(by - ay) / (bx - ax)` with `int`s
loses the fraction. From 08 on, walking a closed [contour](#primer/contour) needs the last point
to join the first, which `%` or the [conditional operator](#primer/conditional-operator) gives
you.

Learn more:
- [Arithmetic operators](https://www.learncpp.com/cpp-tutorial/arithmetic-operators/) on
  learncpp.com, with integer division
- [Remainder and exponentiation](https://www.learncpp.com/cpp-tutorial/remainder-and-exponentiation/)
  on learncpp.com

## Converting a floating-point number to an integer
<!--
id: float-to-int
also: truncation; rounding; round to nearest; truncate toward zero; lround; floor; ceil; float to int
code: static_cast<(int|long long)>\(\s*std::|\bstd::l?lround\b
-->
Converting a `double` to an `int`, with a cast or by assigning it, truncates toward zero: it
drops the fraction. `2.7` becomes 2 and `-2.7` becomes −2. That is rarely what you want for a
[pixel](#primer/pixel) position. The [`<cmath>`](#primer/cmath) functions give the other
choices:

| Function | 2.5 | 2.4 | −2.5 | Returns |
|---|---|---|---|---|
| `static_cast<int>(x)` | 2 | 2 | −2 | `int` |
| `std::lround(x)` (nearest, halves away from zero) | 3 | 2 | −3 | `long` |
| `std::floor(x)` (down) | 2 | 2 | −3 | `double` |
| `std::ceil(x)` (up) | 3 | 3 | −2 | `double` |

`std::floor` and `std::ceil` still return a `double`, so cast the result:
`static_cast<int>(std::ceil(x))`. Round once, at the end. Rounding each step of a calculation
lets the errors add up. GCC with the project's warnings doesn't warn when an assignment
truncates a `double` into an `int`, so the cast is your reminder that it happens.

The conversion is only defined when the result fits. Converting 1e12, or a NaN, to an `int` is
undefined behaviour: the program may produce any number, and the compiler's optimiser (the
part that rewrites code to run faster) may assume it never happens. So clamp first, then
convert: `static_cast<int>(std::clamp(x, 0.0, double(width)))`, never the other way round.
[`std::clamp`](#primer/algorithm) limits a value to a range.

Assignment 06 is the first to round: each point of a line goes to the nearest pixel with
`std::lround` (the page says truncating also passes, since the checker forgives one pixel along
an edge). From 08 on, glyph points in [font units](#primer/font-units) become pixels, and
`src/main.cpp` (18) sizes the picture with `std::ceil` so the text fits.

Learn more:
- [Numeric conversions](https://www.learncpp.com/cpp-tutorial/numeric-conversions/) on
  learncpp.com
- [std::round, std::lround, std::llround](https://en.cppreference.com/w/cpp/numeric/math/round)
  on cppreference

## `static_cast` and other casts
<!--
id: static-cast
also: cast; type conversion; explicit conversion; C-style cast; functional cast; static_cast
code: \bstatic_cast\s*<
-->
A cast converts a value to another type on purpose. `static_cast<T>(x)` is the one you'll use:
it converts between number types and other related types, and the compiler rejects it when
the conversion makes no sense (an `int` to a `std::string`, say).

C++ also accepts the C forms, `(int)x` and `int(x)`. Avoid them. A C-style cast tries several
kinds of conversion in turn, including two that `static_cast` refuses: reading an object's
bytes as if they were a different type, and dropping `const` so that something marked
read-only can be changed. A typo can then compile into something you didn't mean, and the casts
are hard to search for. `static_cast` says which conversion you meant.

```cpp
int r = 200;
uint8_t red = static_cast<uint8_t>(r);              // say that you meant to narrow
double slope = static_cast<double>(dy) / dx;        // divide in floating point
std::size_t i = static_cast<std::size_t>(y) * width + x;   // multiply in 64 bits
```

The third line shows a cast that changes the arithmetic: with `int`s, `y * width` is computed in
32 bits and can overflow before it reaches the `std::size_t`.

The readers you write in 01 and 02 turn bytes into numbers and characters of other types,
which is where a cast says what you meant. The first casts in the Boilerplate are in 06: the
program reads a colour as three `int`s and builds an `RGB` with `static_cast<uint8_t>`, since
[brace initialization](#primer/brace-init) refuses to narrow silently, and
`src/FrameBufferCanvas.cpp` computes a pixel's index with
`static_cast<std::size_t>(y) * width_ + x`. For casts from `double` to `int`, see
[converting to an integer](#primer/float-to-int).

Learn more:
- [Explicit type conversion (casting) and static_cast](https://www.learncpp.com/cpp-tutorial/explicit-type-conversion-casting-and-static-cast/)
  on learncpp.com
- [static_cast conversion](https://en.cppreference.com/w/cpp/language/static_cast) on
  cppreference

## `const`
<!--
id: const
also: const; constant; read-only; const parameter; const member function; const object
code: \bconst\b
-->
`const` marks something you promise not to change, and the compiler holds you to it. It
appears in four places in the project:

- A constant variable: `const std::string what = e.what();`. Once set, assigning to it is a
  compile error. Marking every value that doesn't change makes the ones that do
  stand out.
- A parameter: `void set(const int x, const int y, ...)`. The function can't change its copy.
  The headers leave this `const` out of their declarations; it only matters in the definition.
- A [const reference](#primer/references) parameter, `const std::string& path`: no copy, and
  no changes through it.
- A const member function, with `const` after the parameter list:

```cpp
class Canvas {
 public:
  int width() const { return width_; }   // promises not to change the object
  void clear();                          // may change it
 private:
  int width_ = 0;
};
```

Through a `const Canvas&` you can call `width()` but not `clear()`. So a function that only
reads, such as `FrameBufferCanvas::get` (06), is marked `const`, and a function given a
`const` object can still use it. Writing to a member inside a `const` member function is a
compile error.

`const` is in nearly every file, starting with 01: `ByteReader.cpp` defines
`jumpTo(const uint32_t offset)`, and 01's program keeps the error message in
`const std::string what`. The Boilerplate headers already mark the reading member functions,
such as `tables()` in `src/font/FontParser.h` (02) and `width()`, `height()` and `get()` in
`src/FrameBufferCanvas.h` (06).

Learn more:
- [Constant variables (named constants)](https://www.learncpp.com/cpp-tutorial/constant-variables-named-constants/)
  on learncpp.com
- [Const class objects and const member functions](https://www.learncpp.com/cpp-tutorial/const-class-objects-and-const-member-functions/)
  on learncpp.com

## References and `const` references
<!--
id: references
also: reference; &; const reference; const&; pass by reference; pass by const reference; lvalue reference
code: [\w>]&(?!&)[\s),]
-->
A reference is a second name for an existing object, written with `&` after the type. Changing
it changes the original. As a function parameter, a reference lets the function work on the
caller's object instead of a copy:

```cpp
void addOne(int& n) { n += 1; }               // changes the caller's variable
void show(const std::string& s) { std::cout << s; }  // no copy, read-only

int count = 1;
addOne(count);                                 // count is now 2
```

Use a plain reference, `T&`, when the function must change the object. Use a `const`
reference, `const T&`, for anything large that it only reads: a `std::string`, a
`std::vector` or a struct of vectors. Small values such as `int`, `double` or a two-`double`
`Vec2` are as cheap to copy as to refer to, so they go by value.

Every font-reading function in the project takes `ByteReader& reader`. Reading moves the file position, and
that change must reach the caller. A copy isn't possible anyway: a `ByteReader` holds an
`std::ifstream`, which can't be copied, so passing one by value is a compile error. Tables,
outlines and placements arrive as `const Tables&`, `const GlyphComponent&` and
`const Placement&` (03 to 18). A member function can return a reference too:
`ByteReader& reader()` in `src/font/FontParser.h` (02) hands out the parser's own reader.

A reference must refer to something that outlives it. A reference to a vector element becomes
invalid when the vector grows and moves its elements, and a reference to a local variable
returned from a function refers to nothing.

Learn more:
- [Lvalue references](https://www.learncpp.com/cpp-tutorial/lvalue-references/) on learncpp.com
- [Pass by const lvalue reference](https://www.learncpp.com/cpp-tutorial/pass-by-const-lvalue-reference/)
  on learncpp.com
- [Reference declaration](https://en.cppreference.com/w/cpp/language/reference) on cppreference

## Pointers and arrays
<!--
id: pointers
also: pointer; *; ->; nullptr; char**; raw array; C array; C string; data(); c_str()
code: \bchar\s*\*\*|->|\bnullptr\b|\.data\(\)|\.c_str\(\)|\bchar\s+\w+\[\d+\]
-->
A pointer holds the memory address of an object. `T*` is "pointer to T"; `*p` reaches the
object it points to, and `p->member` is short for `(*p).member`. `nullptr` is the pointer that
points to nothing. The project's own code needs no `new` or `delete`: standard containers and
`std::unique_ptr` manage memory for it. You meet pointers at a few edges:

- `char** argv` in [`main`](#primer/main) is a pointer to a list of `char*`, and each `char*`
  points to the first character of a C string, a run of characters ending in a zero byte.
- A raw array, `char text[64];`, is a fixed block of 64 `char`s. Passed to a function, it turns
  into a pointer to its first element. The programs of 09, 10, 12, 13 and 15 format numbers
  into one with `std::snprintf(text, sizeof text, "%.4f", v)`.
- C libraries such as stb_image_write take pointers: `pixels_.data()` is a pointer to the first
  element of the vector and `path.c_str()` a C string version of a `std::string`, both passed to
  `stbi_write_png` in `src/FrameBufferCanvas.cpp` (06).
- `->` also works on iterators and smart pointers: `it->second` after a map lookup (09, 18), and
  `canvas->writePng(...)` on the `std::unique_ptr<FrameBufferCanvas>` that the programs of 06,
  08, 11, 14, 16, 17 and 18 create once the input gives the canvas size.

```cpp
int value = 5;
int* p = &value;     // & here means "address of"
*p = 7;              // value is now 7
const char* name = "font.ttf";   // a C string
```

Reading through a pointer that is `nullptr` or points outside its object crashes the program;
on Windows the checker reports an access violation. The reference `src/font/GlyphParser.cpp`
(07) also uses a pointer to member, `double GlyphPoint::*axis`, to read x and y with one
function; you can write two loops instead.

Learn more:
- [Introduction to pointers](https://www.learncpp.com/cpp-tutorial/introduction-to-pointers/)
  on learncpp.com
- [Null pointers](https://www.learncpp.com/cpp-tutorial/null-pointers/) on learncpp.com
- [Pointer declaration](https://en.cppreference.com/w/cpp/language/pointer) on cppreference

## `auto` and structured bindings
<!--
id: auto
also: auto; type deduction; const auto&; structured binding; auto [a, b]
code: \bauto\b
-->
`auto` in place of a type tells the compiler to take the type from the initializer. It saves
writing long names such as iterator types:

```cpp
const auto it = glyphs.find(codePoint);   // an iterator into a std::unordered_map
const auto [x, y] = pixelOf(point);       // unpacks a std::pair<int, int>
for (const auto& outline : outlines) { }  // no copies
```

The variable still has one fixed type, decided at compile time; `auto` only spares you from
spelling it. Plain `auto` makes a copy and drops `const` and references, so write
`const auto&` when you want to refer to an existing object without copying it. A
[lambda](#primer/lambdas) has a type with no name you can write, so a variable that holds one is
declared `auto`, and a lambda parameter declared `auto` accepts any type.

The second line is a structured binding: `auto [a, b] = ...` unpacks a pair or the members of a
struct into named variables.

Use `auto` where the type is clear from the right-hand side or too long to be useful. For
numbers, write the type: `auto n = reader.readUint16();` hides whether `n` is 16 or 32 bits.

The reference uses `auto` for map lookups (`src/TextRenderer.cpp`, 18; `src/font/CompoundGlyph.cpp`,
09), for lambdas (`src/render/Outline.cpp`, 11; `src/render/Scanline.cpp`, 14; assignment 01's
program, where `line` takes `const auto& value`), for bytes in `src/utils/Unicode.h` (18), and
for structured bindings in `src/render/Outline.cpp` (08), where `const auto [ax, ay] =
pixelOf(...)` unpacks a point.

Learn more:
- [Type deduction for objects using the auto keyword](https://www.learncpp.com/cpp-tutorial/type-deduction-for-objects-using-the-auto-keyword/)
  on learncpp.com
- [Structured binding declaration](https://en.cppreference.com/w/cpp/language/structured_binding)
  on cppreference

## `for`, `while` and `do`-`while` loops
<!--
id: loops
also: for loop; while loop; do while; nested loops; break; continue; ++i
code: \b(for|while)\s*\(|\bdo\s*\{
-->
C++ has three loops. The counting loop has three parts in its parentheses: what to do once
before starting, the condition checked before each pass, and the step after each pass.
Python's `for i in range(n)` is

```cpp
for (int i = 0; i < n; ++i) { /* body */ }

while (flags.size() < numPoints) { /* checks first, may run 0 times */ }

do { /* runs at least once */ } while (flags & MORE_COMPONENTS);
```

`++i` adds one to `i`. `break` leaves the loop and `continue` skips to the next pass. Any of the
three parts of a `for` may be empty, and the first may declare something other than a
counter: assignment programs read their input with
`for (std::string line; std::getline(input, line);)`, which runs until the input ends.

Loops inside loops are common here. `drawRect` (06) loops over rows, then columns. Assignment
03 loops over the `cmap` groups and, inside, over the code points of each group. Assignment 07
reads flags with a `while`, since a repeat flag can add several at once. Assignment 09's
compound glyph is a list of records that ends at the first record without `MORE_COMPONENTS`, a
natural `do`-`while`, as the reference `src/font/CompoundGlyph.cpp` writes it. The fills (14, 16,
17) loop over pixel rows and, inside, over the crossings of each row. For a loop over every
element of a container, see [range-based `for`](#primer/range-for).

Learn more:
- [For statements](https://www.learncpp.com/cpp-tutorial/for-statements/) on learncpp.com
- [Introduction to loops and while statements](https://www.learncpp.com/cpp-tutorial/introduction-to-loops-and-while-statements/)
  on learncpp.com
- [Do while statements](https://www.learncpp.com/cpp-tutorial/do-while-statements/) on
  learncpp.com

## Range-based `for`
<!--
id: range-for
also: range-based for; for each; for (x : v); foreach
code: \bfor\s*\([^;]*[^:]:[^:][^;]*\)
-->
A range-based `for` visits each element of a container in order, like Python's
`for x in items`. How you declare the loop variable decides whether you get a copy:

```cpp
for (int e : ends) { }                      // a copy of each element
for (const GlyphPoint& p : points) { }      // a read-only reference: no copy
for (GlyphPoint& p : points) { p.x += 10; } // a reference: changes the vector
```

Use `const T&` (or `const auto&`) for anything bigger than a number. Use `T&` when the loop
changes the elements. Don't add elements to the container or remove them inside the loop: the
loop's position would no longer be valid. When you need the index as well, for example to look
at the next point, use the counting [`for`](#primer/loops).

The loop works with anything that has `begin()` and `end()`: `std::vector`, `std::map`,
`std::string`, and a list in braces such as `{0x12, 0x34}`.

The reference uses it throughout. `src/font/FontParser.cpp` (02) fills each record with
`for (TableRecord& t : tables)`, and `src/font/Loca.cpp` (04) fills the entries with
`for (uint32_t& entry : entries)`. `src/render/Outline.cpp` (08) walks the contours with
`for (const int last : outline.endPtsOfContours)`, the picture programs (14, 16, 17) fill each
outline with `for (const GlyphComponent& outline : outlines)`, and `src/TextRenderer.cpp` (18)
draws each code point of the text with `for (const uint32_t cp : utf8ToCodepoints(text))`.

Learn more:
- [Range-based for loops (for-each)](https://www.learncpp.com/cpp-tutorial/range-based-for-loops-for-each/)
  on learncpp.com
- [Range-based for loop](https://en.cppreference.com/w/cpp/language/range-for) on cppreference

## The conditional operator `?:`
<!--
id: conditional-operator
also: ternary operator; ?:; conditional expression; inline if
code: \s\?\s[^;]*\s:\s
-->
`condition ? a : b` is an expression whose value is `a` when the condition is true and `b`
otherwise, like Python's `a if condition else b`. It fits where an `if` statement can't, such as
an initializer or an argument:

```cpp
const int next = i == last ? first : i + 1;
std::cout << (p.onCurve ? " on" : " off");   // parentheses needed inside <<
```

Both branches are converted to one common type. `x > 0 ? 1 : 0.5` is a `double` either way, and
mixing a signed and an unsigned branch converts the signed one to unsigned. The operator has
low precedence, so put it in parentheses when it sits inside a larger expression, in particular
after `<<`. Nested `?:` gets hard to read; use `if` when there are more than two cases.

The reference uses it for short choices. `src/font/Loca.cpp` (04) reads a long or short entry
with `result.longFormat ? reader.readUint32() : 2u * reader.readUint16()`.
`src/font/GlyphParser.cpp` (07) chooses the glyph kind and the sign of a delta,
`src/render/Outline.cpp` (08) wraps the last point of a contour to the first, and
`src/TextRenderer.cpp` (18) returns glyph 0 when the `cmap` has no entry. `src/main.cpp` (18)
takes the optional fourth argument with `argc == 5 ? std::stod(argv[4]) : 64.0`.

Learn more:
- [The conditional operator](https://www.learncpp.com/cpp-tutorial/the-conditional-operator/)
  on learncpp.com
- [Conditional operator](https://en.cppreference.com/w/cpp/language/operator_other#Conditional_operator)
  on cppreference

## Structs and classes
<!--
id: struct-class
also: struct; class; member; data member; member function; method; public; private; default member initializer
code: ^\s*(struct|class)\s+\w+
-->
A struct or class defines a new type made of members: data (fields) and functions that work
on them (member functions, which Python calls methods). The two keywords differ in one way:
members of a `struct` are public by default, members of a `class` private. The project uses
`struct` for plain bundles of data and `class` for types that keep their data private behind
member functions.

```cpp
struct Point {
  double x = 0;              // default member initializers
  double y = 0;
};                           // the semicolon is required

class Counter {
 public:
  void add() { ++count_; }
  int count() const { return count_; }
 private:
  int count_ = 0;            // only member functions can reach it
};
```

`= 0` after a member gives it a starting value, so `Point p;` is (0, 0). Without one, an `int`
or `double` member of a local variable starts with whatever was in memory. Members are reached
with `.`: `p.x`. A member function can be written inside the class or declared there and
defined in the `.cpp` as `int Counter::count() const { ... }`. The trailing `_` on private
members (`width_`, `file_`) is this project's naming habit, not a rule of the language.

Most assignments add a type. Structs: `TableRecord` (02), `GlyphLocation` and `GlyphLocations`
(04), `GlyphMetric` and `HorizontalMetrics` (05), `RGB` (06), `GlyphPoint`, `GlyphComponent`,
`BoundingRect` and `Glyph` (07), `Placement` and `OutlineStyle` (08), `Vec2` (10), `EdgePiece`
and `Crossing` (14). Classes: `ByteReader` (01), `FontParser` (02), `FrameBufferCanvas` (06) and
`TextRenderer` (18).

Learn more:
- [Introduction to structs, members, and member selection](https://www.learncpp.com/cpp-tutorial/introduction-to-structs-members-and-member-selection/)
  on learncpp.com
- [Introduction to classes](https://www.learncpp.com/cpp-tutorial/introduction-to-classes/) on
  learncpp.com
- [Default member initialization](https://www.learncpp.com/cpp-tutorial/default-member-initialization/)
  on learncpp.com

## Constructors and member initializer lists
<!--
id: constructors
also: constructor; member initializer list; initializer list; mem-initializer; default constructor
code: (^|\))\s*:\s*[\w:]+\s*[({]
-->
A constructor is the member function that sets up a new object. It has the class's name and no
return type, and it runs when the object is created: `ByteReader reader(path);` calls
`ByteReader(const std::string&)`. If it can't build a working object, it throws an
[exception](#primer/exceptions), so no half-made object exists.

The member initializer list, after a `:` and before the body, gives each member its first value:

```cpp
class Canvas {
 public:
  Canvas(int w, int h) : width_(w), height_(h), pixels_(w * h) {}
 private:
  int width_;
  int height_;
  std::vector<RGB> pixels_;
};
```

Assigning in the body instead (`width_ = w;`) first builds each member with its default and
then overwrites it. For some members that isn't possible: a member with no default
constructor, such as the `ByteReader` inside `FontParser`, a `const` member and a reference
member must be set in the list. Members are initialized in the order they are declared in the
class, whatever order the list gives, and GCC's `-Wall` warns when the two orders differ.

`ByteReader`'s constructor (01) opens its `std::ifstream` member in the list with
`file_(path, std::ios::binary)` and throws when the file doesn't open. `FontParser` (02)
creates its `reader_(path)` in the list and reads the table directory in the body.
`FrameBufferCanvas` (06) sets its size and allocates every pixel in the list. The reference
`TextRenderer` (18) loads the `cmap` and the metrics in its list, and the exception type
`UnexpectedEof` (01) passes its message to its [base class](#primer/inheritance) there.

Learn more:
- [Introduction to constructors](https://www.learncpp.com/cpp-tutorial/introduction-to-constructors/)
  on learncpp.com
- [Constructor member initializer lists](https://www.learncpp.com/cpp-tutorial/constructor-member-initializer-lists/)
  on learncpp.com
- [Constructors and member initializer lists](https://en.cppreference.com/w/cpp/language/constructor)
  on cppreference

## `explicit`
<!--
id: explicit
also: explicit constructor; converting constructor; implicit conversion
code: \bexplicit\b
-->
A constructor that takes one argument also tells the compiler how to convert that argument's
type into the class, and the compiler will do it without being asked. With
`ByteReader(const std::string&)`, a `std::string` could quietly turn into a `ByteReader`, which
opens a file, wherever a `ByteReader` is expected. `explicit` in front of the constructor turns
that off: the object can then only be made by naming the class.

```cpp
class Reader {
 public:
  explicit Reader(const std::string& path);
};
Reader a("font.ttf");        // fine: the constructor is called by name
Reader b = std::string("x"); // compile error: no silent conversion
```

The rule of thumb: mark every one-argument constructor `explicit` unless the conversion is
something you want to happen on its own (a `double` turning into a fraction type, say).
Constructors with two or more arguments don't need it in this project.

Three classes in the Boilerplate have one: `ByteReader(const std::string& path)` in
`src/font/ByteReader.h` (01), `FontParser(const std::string& path)` in
`src/font/FontParser.h` (02) and `TextRenderer(const std::string& fontPath)` in
`src/TextRenderer.h` (18). All three open a font file, which is not something to do by
accident.

Learn more:
- [Converting constructors and the explicit keyword](https://www.learncpp.com/cpp-tutorial/converting-constructors-and-the-explicit-keyword/)
  on learncpp.com
- [explicit specifier](https://en.cppreference.com/w/cpp/language/explicit) on cppreference

## Brace initialization
<!--
id: brace-init
also: list initialization; uniform initialization; aggregate initialization; {}; braces; narrowing conversion
code: \w\{|\breturn\s*\{|[(,=]\s*\{
-->
Braces create a value from a list of parts. For a struct with public members and no
constructor (an aggregate), the values fill the members in declaration order, and members you
leave out keep their default:

```cpp
RGB white{255, 255, 255};
Vec2 sum(Vec2 a, Vec2 b) { return {a.x + b.x, a.y + b.y}; }  // the return type is known
metrics.push_back({advance, lsb});                         // builds a GlyphMetric in place
uint64_t one = uint64_t{1};
Placement place{penX, baseline, scale};
```

Braces also call constructors (`std::vector<double> roots = {q / a, c / q};` makes a vector of
two elements), and `{}` alone gives the default value: `Affine{}` in the reference is the
identity transform.

Unlike `()` or `=`, braces refuse narrowing conversions, ones that can lose information, such
as `int` to `uint8_t` or `double` to `int`. `RGB{r, g, b}` with `int` variables is an error in
Clang and a `-Wnarrowing` warning in GCC. Cast first: `RGB{static_cast<uint8_t>(r), ...}`.

The picture programs (06, 08, 11, 14, 16, 17, 18) build colours this way. The `Vec2`
operators in `src/utils/Geometry.h` (10) return `{...}`, `src/font/Loca.cpp` (04) and
`src/font/Metrics.cpp` (05) push records with `push_back({...})`, `src/render/Outline.cpp` (11)
names its marker colours `ON_CURVE_COLOR{255, 0, 0}` and so on, and `src/TextRenderer.cpp` (18) places each
glyph with `Placement{penX, baseline, scale}`.

Learn more:
- [Struct aggregate initialization](https://www.learncpp.com/cpp-tutorial/struct-aggregate-initialization/)
  on learncpp.com
- [Narrowing conversions, list initialization, and constexpr initializers](https://www.learncpp.com/cpp-tutorial/narrowing-conversions-list-initialization-and-constexpr-initializers/)
  on learncpp.com
- [List-initialization](https://en.cppreference.com/w/cpp/language/list_initialization) on
  cppreference

## Deriving from a class
<!--
id: inheritance
also: inheritance; base class; derived class; subclass; inheriting constructors; using Base::Base
code: ^\s*(struct|class)\s+\w+\s*:\s*(public\s+)?[\w:]+
-->
A class can be built on top of another, its base class, and inherit its members, as in Python's
`class UnexpectedEof(RuntimeError)`. The base goes after a colon:

```cpp
struct NotFound : std::runtime_error {
  NotFound() : std::runtime_error("not found") {}  // sets the base's message
};
struct BadFormat : std::runtime_error {
  using std::runtime_error::runtime_error;  // reuse the base's constructors
};
```

With `struct` the base is public by default, so code outside can treat a `NotFound` as a
`std::runtime_error`. (With `class` you would write `class NotFound : public std::runtime_error`.)
A constructor of the derived class sets up its base in the
[member initializer list](#primer/constructors). `using Base::Base;` inherits the base's
constructors, so `BadFormat("format 4")` passes its message straight through.

The project uses inheritance for one job: its own exception types. Each derives from
`std::runtime_error`, which in turn derives from `std::exception`. A `catch` for a base class
also catches every class derived from it, so the assignment programs' final
`catch (const std::exception& e)` catches them all, while assignment 01's program catches
`UnexpectedEof` alone first to print `eof`. The Boilerplate declares `UnexpectedEof` in
`src/font/ByteReader.h` (01) and `UnsupportedCmap`, with the `using` line, in
`src/font/Cmap.h` (03). The project has no virtual functions of its own.

Learn more:
- [Basic inheritance in C++](https://www.learncpp.com/cpp-tutorial/basic-inheritance-in-c/) on
  learncpp.com
- [Exceptions, classes, and inheritance](https://www.learncpp.com/cpp-tutorial/exceptions-classes-and-inheritance/)
  on learncpp.com
- [Derived classes](https://en.cppreference.com/w/cpp/language/derived_class) on cppreference

## `enum class`
<!--
id: enum-class
also: enum; enumeration; scoped enumeration; enum class
code: \benum\s+class\b
-->
An `enum class` defines a type with a fixed set of named values. Each value is reached through
the type's name, and it doesn't turn into an integer on its own:

```cpp
enum class Kind { Empty, Simple, Compound };

Kind k = Kind::Simple;
if (k == Kind::Compound) { /* ... */ }
int n = k;                      // compile error
int m = static_cast<int>(k);    // 1, when you need the number
```

That makes it safer than a plain `int` code (0 for empty, 1 for simple...) or the older
unscoped `enum`, whose names spill into the surrounding scope and convert to `int` silently.
With `-Wall`, GCC warns when a `switch` over an `enum class` has no `default` and misses a
value.

`src/Glyph.h` (07) declares `enum class Kind { Empty, Simple, Compound };` inside `struct Glyph`,
so its full names are `Glyph::Kind::Empty` and so on, and `Kind kind = Kind::Empty;` gives every
new `Glyph` the empty kind. Your `readGlyph` (07) sets the kind from `numberOfContours`
(negative means compound), and `resolveGlyph` (09) tests it to decide whether to draw a glyph
or read its components.

Learn more:
- [Scoped enumerations (enum classes)](https://www.learncpp.com/cpp-tutorial/scoped-enumerations-enum-classes/)
  on learncpp.com
- [Enumeration declaration](https://en.cppreference.com/w/cpp/language/enum) on cppreference

## Operator overloading
<!--
id: operator-overloading
also: operator overloading; operator+; operator==; operator*; = default; defaulted comparison
code: \boperator\s*[^\w\s(]
-->
You can give `+`, `-`, `*`, `==` and most other operators a meaning for your own types by
writing a function named `operator+` and so on. Then `a + b` on two points calls it:

```cpp
struct Vec2 { double x = 0, y = 0; };
inline Vec2 operator+(Vec2 a, Vec2 b) { return {a.x + b.x, a.y + b.y}; }
inline Vec2 operator*(Vec2 v, double s) { return {v.x * s, v.y * s}; }

Vec2 mid = (p + q) * 0.5;
```

Each overload covers one order of arguments. With only `operator*(Vec2, double)`, `p * 2.0`
works but `2.0 * p` doesn't compile; write the scalar on the right or add the second overload.

Since C++20, `bool operator==(const RGB&) const = default;` asks the compiler to write `==` for
you, comparing member by member, and `!=` comes with it.

Assignment 10's `src/utils/Geometry.h` declares `+`, `-` and `*` for `Vec2`, so lerp reads like
the formula: `a + (b - a) * t`. Assignments 11 to 15 use the same operators for curves and
intersections, for example `A * (t * t) + B * t + C` in the reference for 13.
`src/FrameBufferCanvas.h` (06) gives `RGB` a defaulted `==`, so the picture code can compare
colours. You also use overloads written by others: `<<` and `>>` on streams and `[]` on vectors
and maps.

Learn more:
- [Introduction to operator overloading](https://www.learncpp.com/cpp-tutorial/introduction-to-operator-overloading/)
  on learncpp.com
- [Overloading operators using normal functions](https://www.learncpp.com/cpp-tutorial/overloading-operators-using-normal-functions/)
  on learncpp.com
- [Default comparisons](https://en.cppreference.com/w/cpp/language/default_comparisons) on
  cppreference

## `[[nodiscard]]`
<!--
id: nodiscard
also: nodiscard; attribute; ignoring return value; warn_unused_result
code: \[\[nodiscard\]\]
-->
`[[nodiscard]]` before a function is an attribute, a note to the compiler, saying that calling
the function and ignoring its result is a mistake. If you do, the compiler
warns: "ignoring return value of ..., declared with attribute 'nodiscard'".

```cpp
[[nodiscard]] int width() const { return width_; }

canvas.width();               // warning: the result goes nowhere
int w = canvas.width();       // fine
```

It suits functions that only compute a value and change nothing, such as getters. A bare call
to one does nothing, so it is usually a slip, for example writing `glyph.bounds();` where you
meant to use the bounds. Functions called for what they do, such as `readUint32()` used to skip
a field, don't get it: the reference calls `reader.readUint32();` and ignores the result on
purpose to step over the scaler type in the table directory (02).

The Boilerplate headers mark their getters: `width()`, `height()` and `get()` in
`src/FrameBufferCanvas.h` (06), `tables()` in `src/font/FontParser.h` (02), and
`measureText`, `metrics`, `glyphFor` and `advance` in `src/TextRenderer.h` (18). The reference
`src/font/CompoundGlyph.cpp` (09) marks `Affine::after`, which combines two transforms and
returns the result. The attribute changes no behaviour, so you can leave it out of your own
code.

Learn more:
- [C++ attribute: nodiscard](https://en.cppreference.com/w/cpp/language/attributes/nodiscard)
  on cppreference
- [Attribute specifier sequence](https://en.cppreference.com/w/cpp/language/attributes) on
  cppreference

## Exceptions
<!--
id: exceptions
also: exception; throw; try; catch; std::exception; what(); uncaught exception; terminate; abort
code: \bthrow\b|\btry\s*\{|\bcatch\s*\(
-->
An exception reports an error that the current function can't handle. `throw` creates an error
object and leaves the function at once, and every function above it, until a `try` block with
a matching `catch` is found. Code after the `throw` doesn't run.

```cpp
try {
  if (!file) throw std::runtime_error("cannot open font.ttf");
  readEverything();
} catch (const std::exception& e) {      // catches runtime_error and its relatives
  std::cerr << "error: " << e.what() << "\n";
  return 1;
}
```

Catch by `const` reference, and order the `catch` blocks from the most specific type to the
most general. `e.what()` returns the message given to the constructor.

If nothing catches an exception, the program calls `std::terminate`, which stops it with
`abort()`. With GCC you see `terminate called after throwing an instance of
'std::runtime_error'` and the message; on Windows the exit code is 3, on macOS and Linux the
program dies from the signal SIGABRT. The checker reports either as a Runtime Error.

The workbook uses exceptions in three ways:

- Errors in the font: `ByteReader` throws `UnexpectedEof` past the end of the file (01), which
  assignment 01's program catches to print `eof`; `UnsupportedCmap` (03) for a font without a
  format 12 `cmap`; `std::runtime_error` when a file can't be opened or written (01, 06).
  `tables.at("cmap")` throws `std::out_of_range` when a font has no such table (03 to 05).
- The Boilerplate's TODOs throw `std::logic_error("not implemented: ...")`.
- Every assignment program catches `std::exception` in `main`. It returns
  [exit code](#primer/exit-codes) 99 for a "not implemented" message, which the checker turns
  into "Not implemented yet", and 1 for anything else.

Learn more:
- [Basic exception handling](https://www.learncpp.com/cpp-tutorial/basic-exception-handling/)
  on learncpp.com
- [Uncaught exceptions and catch-all handlers](https://www.learncpp.com/cpp-tutorial/uncaught-exceptions-catch-all-handlers/)
  on learncpp.com
- [Exceptions](https://en.cppreference.com/w/cpp/language/exceptions) on cppreference

## Function templates
<!--
id: templates
also: template; function template; typename T; template parameter; generic function; instantiation
code: \btemplate\s*<
-->
A function template is a function with a type left open. You write it once with a placeholder,
usually `T`, and the compiler writes a separate function for each type you use it with:

```cpp
template <typename T>
T largest(T a, T b) { return a > b ? a : b; }

largest(3, 7);                 // T is int
largest(2.5, 1.0);             // T is double
largest<uint16_t>(300, 40);    // T named explicitly
```

The compiler works out `T` from the arguments when it can. When `T` appears only in the return
type, you name it in angle brackets, as in `readBigEndian<uint16_t>()`. Since the compiler
needs the body to generate each version, a template is defined in the header, not in a `.cpp`.
A template that doesn't compile for some type gives its error only when that type is used, and
GCC's messages for it can be long; read the first error and the line marked "required from
here".

You have used templates already: `std::vector<int>` and `std::map<std::string, TableRecord>`
are class templates.

Assignment 01's tags mark templates as optional. The Boilerplate's `src/font/ByteReader.h`
declares one, `template <typename T> T readBigEndian()`, which reads `sizeof(T)` bytes and
serves all six integer types, and `readUint8` to `readInt32` call it. You may instead write six
separate functions; the tests only see the numbers. The reference template uses
[`static_assert`](#primer/static-assert) and [`if constexpr`](#primer/if-constexpr) to handle
the types.

Learn more:
- [Function templates](https://www.learncpp.com/cpp-tutorial/function-templates/) on
  learncpp.com
- [Function template instantiation](https://www.learncpp.com/cpp-tutorial/function-template-instantiation/)
  on learncpp.com
- [Function template](https://en.cppreference.com/w/cpp/language/function_template) on
  cppreference

## `if constexpr`
<!--
id: if-constexpr
also: constexpr if; compile-time if; if constexpr
code: \bif\s+constexpr\b
-->
`if constexpr (condition)` is an `if` whose condition the compiler decides while compiling.
The branch that isn't taken is thrown away for that version of the code. It is useful in a
[template](#primer/templates), where the condition depends on the type:

```cpp
template <typename T>
T fromUnsigned(uint64_t value) {
  if constexpr (std::is_signed_v<T>) {
    // only compiled for int8_t, int16_t, int32_t ...
  }
  return static_cast<T>(value);
}
```

The condition must be known at compile time: a type trait such as `std::is_signed_v<T>` (from
`<type_traits>`), a `sizeof`, or a [`constexpr`](#primer/constexpr) value. A plain `if` with the
same condition would often work too, since the compiler drops a branch that can never run. The
difference is that with `if constexpr` the dropped branch doesn't even have to compile for that
type, so it can use operations the type doesn't support, and the code says that the choice is
made per type.

The reference `readBigEndian` in `src/font/ByteReader.h` (01) applies the
[two's complement](#primer/twos-complement) rule inside `if constexpr (std::is_signed_v<T>)`,
so the unsigned readers contain no sign handling at all. The Boilerplate leaves the body to
you, and a plain `if` or six separate functions work as well.

Learn more:
- [Constexpr if statements](https://www.learncpp.com/cpp-tutorial/constexpr-if-statements/) on
  learncpp.com
- [if statement: constexpr if](https://en.cppreference.com/w/cpp/language/if#Constexpr_if) on
  cppreference

## `static_assert`
<!--
id: static-assert
also: static assertion; compile-time check; static_assert
code: \bstatic_assert\b
-->
`static_assert(condition, "message")` checks a condition while the program compiles. If it is
false, the build stops with the message. It costs nothing when the program runs, because by
then the check has already passed. The message is optional since C++17.

```cpp
static_assert(sizeof(int) == 4, "this code assumes a 32-bit int");

template <typename T>
T readNumber() {
  static_assert(std::is_integral_v<T>, "readNumber needs an integer type");
  // ...
}
```

Use it to write down an assumption the code depends on, so that a change that breaks the
assumption fails at once with a clear message instead of giving wrong numbers later. The
condition has to be known at compile time: sizes, type traits, `constexpr` values. For checks
on values that only exist while the program runs, use an `if` and an
[exception](#primer/exceptions) (or `assert` from `<cassert>`).

The project has two. The Boilerplate's `readBigEndian` template in `src/font/ByteReader.h` (01)
starts with `static_assert(std::is_integral_v<T> && sizeof(T) <= 4)`, so
`readBigEndian<double>()` or a 64-bit type fails to compile instead of reading garbage.
`src/FrameBufferCanvas.cpp` (06) checks `static_assert(sizeof(RGB) == 3, ...)`: stb_image_write
reads the pixel vector as tightly packed bytes, three per pixel, and would draw a scrambled
picture if the compiler padded `RGB` to four.

Learn more:
- [Assert and static_assert](https://www.learncpp.com/cpp-tutorial/assert-and-static_assert/)
  on learncpp.com
- [static_assert declaration](https://en.cppreference.com/w/cpp/language/static_assert) on
  cppreference

## `sizeof`
<!--
id: sizeof
also: sizeof; size in bytes; object size; padding
code: \bsizeof\b
-->
`sizeof` gives the size of a type or an object in bytes, worked out by the compiler. It needs
parentheses around a type and accepts them around an expression:

```cpp
sizeof(uint16_t)     // 2
sizeof(int32_t)      // 4
char text[64];
sizeof text          // 64: the whole array
sizeof(std::vector<int>)   // 24 with 64-bit GCC: the vector's bookkeeping, not its elements
```

The result is a `std::size_t`. Because the compiler knows it, `sizeof` can go in
[`static_assert`](#primer/static-assert) and in `if constexpr`. Two things to know: the size of
a struct can be more than the sum of its members, since the compiler may add padding to align
them; and `sizeof` of a container is the size of the container object, so use `.size()` for
the number of elements.

In a [template](#primer/templates), `sizeof(T)` tells the code how many bytes the type has. The
`readBigEndian<T>` in `src/font/ByteReader.h` (01) reads `sizeof(T)` bytes, so one function
reads 1, 2 or 4 bytes for the six integer types, and the reference computes 2^bits as
`uint64_t{1} << (8 * sizeof(T))`. `src/FrameBufferCanvas.cpp` (06) checks
`sizeof(RGB) == 3`. The programs of assignments 10, 12, 13 and 15 format numbers into a `char text[64]`
buffer (09's into a `char buf[32]`) and pass its `sizeof` to `std::snprintf`, so it never
writes past the end.

Learn more:
- [Object sizes and the sizeof operator](https://www.learncpp.com/cpp-tutorial/object-sizes-and-the-sizeof-operator/)
  on learncpp.com
- [sizeof operator](https://en.cppreference.com/w/cpp/language/sizeof) on cppreference

## `constexpr`
<!--
id: constexpr
also: constexpr; compile-time constant; constant expression; named constant
code: ^\s*(static\s+)?constexpr\b
-->
`constexpr` on a variable means its value is fixed when the program compiles. It is a constant
the compiler can use anywhere a compile-time value is needed: an array size, a
[`static_assert`](#primer/static-assert), an [`if constexpr`](#primer/if-constexpr). A
`constexpr` variable is also `const`.

```cpp
constexpr uint8_t REPEAT_FLAG = 0x08;     // a named bit instead of a bare 0x08
constexpr double kOneOver2To14 = 1.0 / 16384;

if (flag & REPEAT_FLAG) { /* ... */ }
```

Named constants make bit tests readable: `flag & REPEAT_FLAG` says what it checks, where
`flag & 0x08` sends you to the specification. Prefer `constexpr` to a `#define` macro: it has a
type, it obeys namespaces and scopes, and the debugger knows its name. A constant used in one
`.cpp` file goes in an unnamed [namespace](#primer/namespaces) at the top of that file.

Functions can be `constexpr` too, so the compiler can run them at compile time; the project
doesn't need that.

The reference names the flag bits this way. `src/font/GlyphParser.cpp` (07) declares
`ON_CURVE_POINT`, `X_SHORT_VECTOR`, `Y_SHORT_VECTOR`, `REPEAT_FLAG`, `X_IS_SAME_OR_POSITIVE` and
`Y_IS_SAME_OR_POSITIVE` as `constexpr uint8_t`, with values from `0x01` to `0x20`.
`src/font/CompoundGlyph.cpp` (09) declares the component flags, such as `ARG_1_AND_2_ARE_WORDS`
and `MORE_COMPONENTS`, as `constexpr uint16_t`. The names follow Apple's and Microsoft's
specifications, so you can look each one up.

Learn more:
- [Constexpr variables](https://www.learncpp.com/cpp-tutorial/constexpr-variables/) on
  learncpp.com
- [constexpr specifier](https://en.cppreference.com/w/cpp/language/constexpr) on cppreference

## Lambdas
<!--
id: lambdas
also: lambda; lambda expression; anonymous function; closure; capture; [&]; comparator
code: \[[&=]?\]\s*\(
-->
A lambda is a function written in the middle of an expression, like Python's `lambda` or a
JavaScript arrow function. Its parts are the capture list in square brackets, the parameters
and the body:

```cpp
std::sort(crossings.begin(), crossings.end(),
          [](const Crossing& a, const Crossing& b) { return a.x < b.x; });

int total = 0;
const auto add = [&](int n) { total += n; };   // [&]: uses `total` by reference
add(5);                                         // total is now 5
```

The capture list says which local variables the body may use. `[]` captures nothing, `[&]`
captures everything it uses by reference, so changes reach the original, and `[=]` takes
copies. A lambda that outlives the function it was written in must not capture by reference,
since the variables are gone; in this project every lambda is used before its function returns.
Store a lambda in an [`auto`](#primer/auto) variable or pass it straight to a function. A
function that receives one either is a template or takes a `std::function`, as `forEachRow`
does.

The reference uses them in four ways. In `src/render/Scanline.cpp` (14) a lambda tells
`std::sort` to order crossings by x, and another tells `std::find_if` to find an on-curve point.
`src/render/EvenOdd.cpp` (14) and `src/render/NonZero.cpp` (16) hand `forEachRow` a lambda
with `[&]` that fills each row's spans on the canvas. `src/render/Outline.cpp` (11) defines
small helpers inside a function, `at(k)` and `on(k)`, that wrap an index around the contour.
And assignment 01's program uses `line` to write `<op> <value>`.

Learn more:
- [Introduction to lambdas (anonymous functions)](https://www.learncpp.com/cpp-tutorial/introduction-to-lambdas-anonymous-functions/)
  on learncpp.com
- [Lambda captures](https://www.learncpp.com/cpp-tutorial/lambda-captures/) on learncpp.com
- [Lambda expressions](https://en.cppreference.com/w/cpp/language/lambda) on cppreference

## Recursion
<!--
id: recursion
also: recursive function; base case; call stack; stack overflow; depth-first
-->
A recursive function calls itself on a smaller part of the problem, until it reaches a case it
can answer directly, the base case. Each call gets its own local variables on the call stack,
and the calls finish in reverse order.

```cpp
int digits(unsigned n) {
  if (n < 10) return 1;          // base case
  return 1 + digits(n / 10);     // a smaller problem
}
```

Recursion fits data that contains smaller copies of itself. A compound glyph is such data: it
is a list of components, and each component is another glyph, which may itself be compound.
To draw one, you resolve each component the same way, depth first, and the simple and empty
glyphs are the base cases. The transforms of the levels combine on the way down.

Every call uses some stack memory, and the stack is limited, to a few megabytes by default.
A call that never reaches a base case runs out of stack and crashes; on Windows the checker
reports a stack overflow. A corrupt font could make a glyph
contain itself, so a resolver should stop at some depth. The reference
`src/font/CompoundGlyph.cpp` (09) throws when nesting passes 16 levels.

Assignment 09 is the recursive one: `resolveGlyph` reads a compound glyph's component
records, then resolves each component with the transforms combined. Assignment 18 calls it for
every character. You can also do the same with a loop and a stack of your own; the tests only
see the outlines.

Learn more:
- [Recursion](https://www.learncpp.com/cpp-tutorial/recursion/) on learncpp.com
- [Recursion (computer science)](https://en.wikipedia.org/wiki/Recursion_%28computer_science%29) on
  Wikipedia
