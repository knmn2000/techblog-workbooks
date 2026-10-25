# 02 · Read the table directory

**Difficulty:** Easy · **Assignment** 2 of 18 · **Check:** `.\check 02`

**Tags**
- *Language:* [structs](#primer/struct-class) · [fixed-width unsigned integers](#primer/cstdint) (`uint16_t`, `uint32_t`) · [strings built from bytes](#primer/char) · [binary file I/O](#primer/fstream) (`seekg`, `get`)
- *Library:* [`std::ifstream`](#primer/fstream) in binary mode · [`std::vector`](#primer/vector) · [`std::string`](#primer/string) · [`std::map`](#primer/map)
- *Concepts:* [the sfnt container](#primer/table-directory) · [table tags](#primer/table-tag) · [offsets from the start of the file](#primer/file-offset) · [big-endian byte order](#primer/big-endian)

## Read in the blog first

You can pass using this page alone. For the background, read the blog's
[Offset table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Offset%20table)
section through the paragraph that starts "This is the structure of the". The author's code
follows that paragraph.

## What you need

- [TrueType and OpenType fonts](#primer/truetype): the first 4 bytes of the file are the scaler
  type, which says the font has TrueType outlines; `readTableDirectory` reads them and moves on.
- [The table directory](#primer/table-directory): the 12-byte header and the 16-byte records
  that `readTableDirectory` in `src/font/FontParser.cpp` reads.
- [Table tags](#primer/table-tag): the 4-byte name at the start of each record, which you keep
  with its trailing spaces and write between quotes.
- [`char` and `unsigned char`](#primer/char): the tag's 4 bytes come from your `ByteReader` as
  numbers, and `TableRecord::tag` is a `std::string`, so each byte has to become a `char`.
- [`<vector>`](#primer/vector): `readTableDirectory` returns the records in file order as a
  `std::vector<TableRecord>`, and the program writes one `table` line per element.
- [`<map>`](#primer/map): `Tables` in `src/font/FontParser.h` is a
  `std::map<std::string, TableRecord>` keyed by tag; `FontParser` fills it, and assignments 03
  to 05 look tables up in it with `at`.
- [Range-based `for`](#primer/range-for): the program writes the records with
  `for (const TableRecord& t : tables)`, and `FontParser`'s constructor copies them into the map
  with the same kind of loop.
- [The `nodiscard` attribute](#primer/nodiscard): `FontParser::tables()` in `FontParser.h`
  carries it, so the compiler warns about a call that throws the result away.
- [Compiling and linking](#primer/compile-and-link): from now on the build compiles several
  `.cpp` files, `ByteReader.cpp` and `FontParser.cpp` among them, and links them into each
  program; the checker reports a failure in either step as a Compile Error.
- [Compiler warnings](#primer/compiler-warnings): the checker lists the build's warnings before
  the tests; a signed and unsigned mix-up often shows up there first.
- [Ninja](#primer/ninja): CMake hands the build to Ninja, which recompiles only the files you
  changed since the last check.
- [The `build` folder](#primer/build-folder): the programs land in `build/solutions/`, and each
  test's input and your output in `build/cases/NN/`.
- [The study server](#primer/study-server): with `.\study` running, the book's Run and Submit
  buttons check your code without the terminal.

## Source material

- Apple, *TrueType Reference Manual*, [The font directory](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html)
  (the "offset subtable" and "table directory" tables)
- Microsoft, *OpenType specification*, [Organization of an OpenType font](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#organization-of-an-opentype-font)
  (TableDirectory and TableRecord)
- The blog: [Offset table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Offset%20table)

## Where this fits

A TrueType font is a set of tables (`cmap`, `glyf`, `head`, ...) packed into one file. The
table directory at the start of the file lists where each table is. Assignments 03 to 05
read the `cmap`, `loca` and metrics tables at the offsets you find here. Their inputs already
contain this assignment's output lines for the tables they need, so you can solve them without
finishing this one.

## The problem

Write a program that reads a font file's table directory and writes how many tables the font
has, then the record of every table.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file has one line:

| Line | Meaning |
|---|---|
| `font <path>` | The file to read. The path is relative to the workbook folder and contains no spaces. |

Some test files are real fonts. Others are hand-made files that hold only a table directory,
so their offsets may point past the end of the file. Your program doesn't need to follow any
offset.

### Output

```
tables <numTables>
table "<tag>" <checkSum> <offset> <length>
table "<tag>" <checkSum> <offset> <length>
...
```

- First the line `tables <numTables>`.
- Then one `table` line per record. The records may come in any order.
- Write the tag's 4 characters inside double quotes as the font stores them, including any
  spaces at the end: `"cvt "`, not `"cvt"`.
- The three numbers (`checkSum`, `offset`, `length`) are in decimal.

### The table directory

The directory starts at byte 0 of the file. All numbers are big-endian, and your
`ByteReader` from assignment 01 can read every field.

The first 12 bytes are the header, which Apple's manual calls the "offset subtable":

| Field | Type | Meaning |
|---|---|---|
| scaler type | uint32 | What kind of font this is: `0x00010000` or `'true'` for TrueType outlines |
| `numTables` | uint16 | How many table records follow |
| `searchRange` | uint16 | (the largest power of 2 that is ≤ `numTables`) × 16, an aid for binary search |
| `entrySelector` | uint16 | log2 of that power of 2 |
| `rangeShift` | uint16 | `numTables` × 16 − `searchRange` |

Of these five fields, your program needs `numTables`. Skip the other four, whatever they hold.

The table records follow from byte 12, `numTables` of them, 16 bytes each:

| Field | Type | Meaning |
|---|---|---|
| `tag` | 4 bytes | The table's name as 4 ASCII characters. A name shorter than 4 characters ends in spaces, as in `'cvt '`. |
| `checkSum` | uint32 | A checksum of the table's bytes |
| `offset` | uint32 | Where the table starts, in bytes from the start of the file |
| `length` | uint32 | The table's length in bytes |

Record k (counting from 0) starts at byte 12 + 16k.

A well-made font sorts the records by tag, byte by byte, so uppercase tags come before
lowercase ones. Your program can ignore that order.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** Your program reads `numTables` as the uint16 at byte 4 and writes it as
  `tables <numTables>` (it can be 0). It skips the scaler type before it and the 6 bytes of
  search fields after it, whatever they hold.
- **R2** Each record is 16 bytes: the tag, then `checkSum`, `offset` and `length` as
  big-endian uint32 values, which can be 2^31 or more.
- **R3** Your program writes the tag as its 4 bytes, trailing spaces included.

## Examples

### Example 1: a hand-made directory (test `02-R1-true-scaler`)

```
input:   font tests/02/data/02-R1-true-scaler.bin
```

The first 60 bytes:

```
74 72 75 65                  scaler type 'true'
00 03                        numTables = 3
ff ff ff ff ff ff            searchRange, entrySelector, rangeShift: skip them
63 6d 61 70                  tag "cmap"
11 11 11 11 00 00 00 40 00 00 00 08         checkSum 286331153, offset 64, length 8
67 6c 79 66                  tag "glyf"
22 22 22 22 00 00 00 48 00 00 00 04         checkSum 572662306, offset 72, length 4
68 65 61 64                  tag "head"
33 33 33 33 00 00 00 4c 00 00 00 04         checkSum 858993459, offset 76, length 4
```

```
output:  tables 3
         table "cmap" 286331153 64 8
         table "glyf" 572662306 72 4
         table "head" 858993459 76 4
```

The 6 bytes of search fields are all `ff` here, where a real font with 3 tables would hold 32,
1 and 16.
Your program skips them, so their values don't change the output.

### Example 2: tags that end in spaces (test `02-R3-spaces`)

```
input:   font tests/02/data/02-R3-spaces.bin

output:  tables 6
         table "A   " 1 108 4
         table "CFF " 2 112 4
         table "ab  " 3 116 4
         table "cvt " 4 120 4
         table "head" 5 124 4
         table "zzz " 6 128 4
```

The tag `A   ` is the byte `41` followed by three spaces (`20 20 20`). All four bytes are
part of the tag.

### Example 3: a real font (test `02-E2E-jetbrains`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf

output:  tables 18
         table "GDEF" 1324961447 2406324 670
         table "GPOS" 3088890585 2440700 19232
         table "GSUB" 3036347712 2406996 33702
         table "OS/2" 325127274 424 96
         table "PfEd" 383833929 2459932 568
         table "cmap" 2612855665 49020 11978
         table "cvt " 676859925 64812 168
         table "fpgm" 1647248255 61000 3596
         table "gasp" 16 2406316 8
         table "glyf" 810950304 113484 2068620
         table "head" 546057157 300 54
         table "hhea" 34418196 356 36
         table "hmtx" 1631122185 520 48500
         table "loca" 588705204 64980 48504
         table "maxp" 946608241 392 32
         table "name" 4079467112 2182104 2527
         table "post" 4288561555 2184632 221681
         table "prep" 2328730654 64596 214
```

The records follow tag order, and the tables sit in the file in a different order: `head`
comes first in the file (offset 300) but has the eleventh record.

## Constraints

- `numTables` is between 0 and 30 in the tests, and the tags in one file are all different.
- Tags are printable ASCII without `"`, and spaces appear only at the end.
- Each file holds the whole directory. Offsets and lengths may point anywhere, including past
  the end of the file.
- Each case has a 10-second limit. A correct solution finishes in milliseconds.
- There are 13 tests: hand-made directories for each rule, three small fonts built with
  fontTools (with and without the hinting tables, and with three tables removed), both real
  fonts, and 3 random directories.

## Hints

<details><summary>Hint 1: where to start</summary>

The answer comes from the first 12 + 16 × `numTables` bytes. Read the header fields in the
order the font stores them, then loop `numTables` times, reading one record per pass.
</details>

<details><summary>Hint 2: the approach</summary>

Seek to byte 0. Read and ignore a uint32 (the scaler type). Read the uint16 `numTables`.
Skip 6 bytes. Then, for each record, read 4 single bytes and append each one to a string as a
character, and read three uint32 values. Your `ByteReader` from assignment 01
does the byte order for you.
</details>

<details><summary>Hint 3: the traps</summary>

- Don't trim the tag. `"cvt "` and `"cvt"` are different answers.
- Read the tag byte by byte. If you read it as a uint32 and pull the characters out with
  shifts, start with the most significant byte, or you'll get `pamc` for `cmap`.
- Skip 6 bytes after `numTables`. If you skip 4 or 8, you read every record from the wrong
  position.
- `checkSum` and `offset` can be 2^31 or more. Keep them in an unsigned 32-bit (or wider)
  type.
- The search fields may be wrong. Don't use them to count the records.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
seek(0)
readUint32()                         # scaler type, not needed
numTables = readUint16()
skip(6)                              # searchRange, entrySelector, rangeShift
records = []
repeat numTables times:
    tag = 4 characters, one readUint8() each
    checkSum = readUint32()
    offset   = readUint32()
    length   = readUint32()
    add (tag, checkSum, offset, length) to records
write "tables", numTables
for each record: write 'table "' + tag + '"', checkSum, offset, length
```
</details>

## Checking your solution

```
.\check 02                         run every test
.\check 02 -Case 02-R3-spaces      one test, showing its full input, expected output and your output
.\check 02 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 02 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R3  Tags as the font stores them: 4 characters, trailing spaces kept ...........    0 / 2   FAILED
      x 02-R3-tiny-hinted  the 4-glyph font plus 'cvt ', fpgm, prep and gasp (14 tables)
          expected `table "cvt " 4292346576 544 8`, closest line written: `table "cvt" 4292346576 544 8` - differs in tag (15 lines written, 15 expected)
          likely cause: R3 - Tags as the font stores them: 4 characters, trailing spaces kept
          expected values from: Python struct, cross-checked against fontTools 4.67.0 SFNTReader
          reproduce: build/solutions/assignment_02.exe build/cases/02/02-R3-tiny-hinted.in build/cases/02/02-R3-tiny-hinted.out
```

Your lines may come in any order, so the checker looks for each expected line in your output.
If one is missing, it shows the closest line you wrote with the same keyword. Inside a quoted
tag, the checker compares every space.

## After you pass: compare with the author's code

[The blog's directory parser](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Parser%20for%20table%20directory)
runs in `FontParser`'s constructor, right after it opens the file. It skips the scaler type,
reads `numTables`, skips the three search fields, and then reads each record: the tag as 4
raw bytes turned into a string, followed by the checksum, offset and length. The records go
into a map keyed by tag, the field `directory`, so every later step finds its table by name,
for example the `cmap` table in assignment 03. The post calls it a hash map; the author's
repository declares it as a `std::map<std::string, Tag>`, where `Tag` is the record struct
(`checkSum`, `offset`, `length`, with the tag itself as the key). In your project the record
is `TableRecord`, the map is `Tables`, and `readTableDirectory` returns the records in file
order.

In the repository, the constructor goes on past the snippet: it throws "Could not find glyf
table" if there is no `glyf` record, then loads `loca`, `cmap` and `hmtx` (assignments 04, 03
and 05) before it returns.

The snippet doesn't check the scaler type or verify any
checksums. Neither matters for this workbook. A stricter parser would reject files whose
scaler type isn't `0x00010000` or `'true'` (an `'OTTO'` font stores CFF outlines instead of
`glyf`), and could check each table's sum of uint32 words against its `checkSum`.

The tag comes from `ifs.read`, whose result the snippet doesn't check, so in a file that ends
inside a tag, the rest of its 4-byte buffer stays uninitialised (the next `readUint32` then
throws). Later steps look
tables up with `directory["cmap"]` and the like. For a tag the font doesn't have, `operator[]`
adds an all-zero record, and the step reads from offset 0 of the file instead of reporting a
missing table. Looking records up with `at()` or `find()` turns that into an error.
