# 02 · Read the table directory

**Difficulty:** Easy · **Assignment** 2 of 18 · **Check:** `.\check 02`

**Tags**
- *Language:* [structs](#primer/struct-class) · [fixed-width unsigned integers](#primer/cstdint) (`uint16_t`, `uint32_t`) · [strings built from bytes](#primer/char) · [binary file I/O](#primer/fstream) (`seekg`, `get`)
- *Library:* [`std::ifstream`](#primer/fstream) in binary mode · [`std::vector`](#primer/vector) · [`std::string`](#primer/string) · [`std::map`](#primer/map)
- *Concepts:* [the sfnt container](#primer/table-directory) · [table tags](#primer/table-tag) · [offsets from the start of the file](#primer/file-offset) · [big-endian byte order](#primer/big-endian)

## Read in the blog first

Optional background: the blog's
[Offset table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Offset%20table) section,
down to the paragraph that begins "This is the structure of the". The author's code comes right
after it.

## Learning material

- [TrueType and OpenType fonts](#primer/truetype): the first 4 bytes of the file are the scaler
  type, which marks TrueType outlines. `readTableDirectory` reads them and moves on.
- [The table directory](#primer/table-directory): the 12-byte header and 16-byte records read by
  `readTableDirectory` in `src/font/FontParser.cpp`.
- [Table tags](#primer/table-tag): the 4-byte name opening each record. You keep trailing spaces
  and print the tag between quotes.
- [`char` and `unsigned char`](#primer/char): your `ByteReader` returns the tag's bytes as
  numbers, but `TableRecord::tag` is a `std::string`, so each byte has to become a `char`.
- [`<vector>`](#primer/vector): `readTableDirectory` returns a `std::vector<TableRecord>` in file
  order, and the program prints a `table` line per element.
- [`<map>`](#primer/map): `Tables` in `src/font/FontParser.h` is a
  `std::map<std::string, TableRecord>` keyed by tag. `FontParser` fills it; assignments 03 to 05
  fetch tables from it with `at`.
- [Range-based `for`](#primer/range-for): the program prints records with
  `for (const TableRecord& t : tables)`, and `FontParser`'s constructor copies them into the map
  with a loop of the same shape.
- [The `nodiscard` attribute](#primer/nodiscard): `FontParser::tables()` in `FontParser.h` has
  it, so a call that drops the result gets a compiler warning.
- [Compiling and linking](#primer/compile-and-link): from here the build compiles several `.cpp`
  files (`ByteReader.cpp`, `FontParser.cpp` and others) and links them into each program. A
  failure in either step shows up as a Compile Error.
- [Compiler warnings](#primer/compiler-warnings): the checker prints the build's warnings ahead
  of the tests, and a signed/unsigned mix-up often turns up there first.
- [Ninja](#primer/ninja): CMake passes the build to Ninja, which recompiles only what changed
  since your last check.
- [The `build` folder](#primer/build-folder): programs land in `build/solutions/`, and each
  test's input and your output in `build/cases/NN/`.
- [The study server](#primer/study-server): run `.\study` and the book's Run and Submit buttons
  check your code without a terminal.

## Source material

- Apple, *TrueType Reference Manual*, [The font directory](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html)
  (the "offset subtable" and "table directory" tables)
- Microsoft, *OpenType specification*, [Organization of an OpenType font](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#organization-of-an-opentype-font)
  (TableDirectory and TableRecord)
- The blog: [Offset table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Offset%20table)

## Where this fits

A TrueType font is a pile of tables (`cmap`, `glyf`, `head`, ...) in one file, and the table
directory at the front says where each one starts. Assignments 03 to 05 read `cmap`, `loca` and
the metrics at offsets you produce here. Their inputs already carry the lines for the tables
they need, so none of them waits on this one.

## The problem

Read a font file's table directory, then write the number of tables followed by one record per
table.

### Input

Same command line as ever, `<program> <input-file> <output-file>`, started from the workbook folder.
The input file has one line:

| Line | Meaning |
|---|---|
| `font <path>` | The file to read. The path is relative to the workbook folder and contains no spaces. |

Some test files are real fonts. The rest are hand-made and hold nothing but a directory, so
their offsets can point past the end of the file. That doesn't matter, because your program
never follows an offset.

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

It starts at byte 0 of the file. Every number is big-endian, so the `ByteReader` from
assignment 01 reads all of the fields.

The first 12 bytes are the header, which Apple's manual calls the "offset subtable":

| Field | Type | Meaning |
|---|---|---|
| scaler type | uint32 | What kind of font this is: `0x00010000` or `'true'` for TrueType outlines |
| `numTables` | uint16 | How many table records follow |
| `searchRange` | uint16 | (the largest power of 2 that is ≤ `numTables`) × 16, an aid for binary search |
| `entrySelector` | uint16 | log2 of that power of 2 |
| `rangeShift` | uint16 | `numTables` × 16 − `searchRange` |

You need `numTables` and nothing else from these five. Skip the others, whatever they hold.

The table records follow from byte 12, `numTables` of them, 16 bytes each:

| Field | Type | Meaning |
|---|---|---|
| `tag` | 4 bytes | The table's name as 4 ASCII characters. A name shorter than 4 characters ends in spaces, as in `'cvt '`. |
| `checkSum` | uint32 | A checksum of the table's bytes |
| `offset` | uint32 | Where the table starts, in bytes from the start of the file |
| `length` | uint32 | The table's length in bytes |

Record k (counting from 0) starts at byte 12 + 16k.

Well-made fonts sort the records by tag, byte by byte, so uppercase tags come before
lowercase ones. You can ignore that order.

## Requirements

Each test targets one requirement, so a failure report can show passes requirement by requirement.
If the difference points somewhere specific, a `likely cause` line names the requirement
(R1, R2 or R3) it points to.

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

The search fields are all `ff` here, where a real 3-table font would hold 32, 1 and 16. The
program skips them, so it makes no difference.

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

The tag `A   ` is the byte `41` and then three spaces (`20 20 20`). All four bytes belong to
the tag.

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

The records are in tag order and the tables sit in the file in another: `head` is the first
table in the file (offset 300) but the eleventh record.

## Constraints

- `numTables` is between 0 and 30 in the tests, and the tags in one file are all different.
- Tags are printable ASCII without `"`, and spaces appear only at the end.
- Each file holds the whole directory. Offsets and lengths may point anywhere, past the end of
  the file included.
- A case times out after 10 seconds. A correct solution finishes in milliseconds.
- 13 tests: hand-made directories for each rule, three small fonts built with
  fontTools (with and without the hinting tables, and with three tables removed), both real
  fonts, and 3 random directories.

## Hints

<details><summary>Hint 1: where to start</summary>

The first 12 + 16 × `numTables` bytes hold all you need. Read the header fields in
the order the font stores them, then loop `numTables` times and read one record per pass.
</details>

<details><summary>Hint 2: the approach</summary>

Seek to byte 0. Read and discard a uint32 (the scaler type). Read the uint16 `numTables`.
Skip 6 bytes. Then, for each record, read 4 single bytes and append each to a string as a
character, followed by three uint32 values. Your `ByteReader` from assignment 01 takes care of
the byte order.
</details>

<details><summary>Hint 3: the traps</summary>

- Don't trim the tag. `"cvt "` and `"cvt"` are different answers.
- Read the tag byte by byte. If you read a uint32 and pull the characters out with shifts,
  start from the most significant byte or `cmap` comes out as `pamc`.
- Skip 6 bytes after `numTables`. Skip 4 or 8 and you read every record from the wrong place.
- `checkSum` and `offset` can be 2^31 or more, so keep them in an unsigned 32-bit (or wider)
  type.
- The search fields can be wrong. Don't use them to count the records.
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

The checker prints this for a failing test:

```
  R3  Tags as the font stores them: 4 characters, trailing spaces kept ...........    0 / 2   FAILED
      x 02-R3-tiny-hinted  the 4-glyph font plus 'cvt ', fpgm, prep and gasp (14 tables)
          expected `table "cvt " 4292346576 544 8`, closest line written: `table "cvt" 4292346576 544 8` - differs in tag (15 lines written, 15 expected)
          likely cause: R3 - Tags as the font stores them: 4 characters, trailing spaces kept
          expected values from: Python struct, cross-checked against fontTools 4.67.0 SFNTReader
          reproduce: build/solutions/assignment_02.exe build/cases/02/02-R3-tiny-hinted.in build/cases/02/02-R3-tiny-hinted.out
```

Output order doesn't matter: the checker looks for each expected line anywhere in your output.
For a missing line it shows the closest line you wrote with the same keyword. Inside a quoted
tag, the checker compares every space.

## After you pass: compare with the author's code

[The blog's directory parser](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Parser%20for%20table%20directory)
runs in `FontParser`'s constructor, straight after the file opens. It skips the scaler
type, reads `numTables`, skips the three search fields, then reads each record: the tag as 4
raw bytes turned into a string, followed by checksum, offset and length. Records go into a map
keyed by tag, the field `directory`, so later steps can find a table by name (assignment 03
fetches `cmap` that way). The post calls it a hash map, but the author's repository declares a
`std::map<std::string, Tag>`, where `Tag` is the record struct (`checkSum`, `offset`, `length`,
with the tag itself as the key). In your project the record is `TableRecord`, the map is
`Tables`, and `readTableDirectory` returns the records in file order.

The repository's constructor goes on past the snippet. It throws "Could not find glyf table"
when there's no `glyf` record, then loads `loca`, `cmap` and `hmtx` (assignments 04, 03 and 05)
before returning.

The snippet checks neither the scaler type nor any checksum, and for this workbook that costs
nothing. A stricter parser would reject files whose scaler type isn't `0x00010000` or `'true'`
(an `'OTTO'` font stores CFF outlines instead of `glyf`), and could compare each table's sum of
uint32 words with its `checkSum`.

The tag comes from `ifs.read`, whose result the snippet doesn't check. In a file that ends
inside a tag, the rest of its 4-byte buffer stays uninitialised (the next `readUint32` then
throws). Later steps look tables up with `directory["cmap"]` and the like, and for a tag the
font lacks, `operator[]` adds an all-zero record, so the step reads from offset 0 of the file
instead of reporting a missing table. `at()` or `find()` would turn that into an error.
