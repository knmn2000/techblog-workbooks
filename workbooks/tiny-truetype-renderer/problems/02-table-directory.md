# 02 · Read the table directory

**Difficulty:** Easy · **Assignment** 2 of 18 · **Check:** `.\check 02`

**Tags**
- *Language:* structs · fixed-width unsigned integers (`uint16_t`, `uint32_t`) · strings built from bytes · binary file I/O (`seekg`, `get`)
- *Library:* `std::ifstream` in binary mode · `std::vector` · `std::string` (optionally `std::unordered_map`)
- *Concepts:* the sfnt container · table tags · offsets from the start of the file · big-endian byte order

## Read in the blog first

This page is complete on its own; the blog tells the story behind it. Read the blog's
[Offset table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Offset%20table)
section through the paragraph that starts "This is the structure of the". The author's code
comes right after it.

## Where this fits

A TrueType font is a set of **tables** (`cmap`, `glyf`, `head`, ...) packed into one file. The
**table directory** at the start of the file says where each table is. Assignments 03 to 05
read the `cmap`, `loca` and metrics tables at the offsets you find here. Their inputs already
contain this assignment's output lines for the tables they need, so you can also do them
without this one.

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
so their offsets may point past the end of the file. You never need to follow an offset.

### Output

```
tables <numTables>
table "<tag>" <checkSum> <offset> <length>
table "<tag>" <checkSum> <offset> <length>
...
```

- First the line `tables <numTables>`.
- Then one `table` line per record. The records may come in any order.
- Write the tag's 4 characters inside double quotes, exactly as stored, including any spaces
  at the end: `"cvt "`, not `"cvt"`.
- The three numbers (`checkSum`, `offset`, `length`) are in decimal.

### The table directory

The directory starts at byte 0 of the file. All numbers are **big-endian**, and your
`ByteReader` from assignment 01 can read every field.

**Header** (the "offset subtable"), 12 bytes:

| Field | Type | Meaning |
|---|---|---|
| scaler type | uint32 | What kind of font this is: `0x00010000` or `'true'` for TrueType outlines. You don't need it. |
| `numTables` | uint16 | How many table records follow |
| `searchRange` | uint16 | (the largest power of 2 that is ≤ `numTables`) × 16. A binary-search aid. Skip it. |
| `entrySelector` | uint16 | log2 of that power of 2. Skip it. |
| `rangeShift` | uint16 | `numTables` × 16 − `searchRange`. Skip it. |

**Table records**: `numTables` of them, 16 bytes each, starting at byte 12:

| Field | Type | Meaning |
|---|---|---|
| `tag` | 4 bytes | The table's name as 4 ASCII characters. Shorter names are padded with spaces at the end, as in `'cvt '`. |
| `checkSum` | uint32 | A checksum of the table's bytes |
| `offset` | uint32 | Where the table starts, in bytes from the start of the file |
| `length` | uint32 | The table's length in bytes |

So record k (counting from 0) starts at byte 12 + 16k.

In a well-made font the records are sorted by tag, byte by byte, so uppercase tags come
before lowercase ones. You don't need to rely on that.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement
the difference most likely comes from.

- **R1** `numTables` is the uint16 at byte 4, written as `tables <numTables>` (it can be 0).
  The scaler type before it and the 6 bytes of search fields after it are skipped, whatever
  they hold.
- **R2** Each record is 16 bytes: the tag, then `checkSum`, `offset` and `length` as
  big-endian uint32 values, which can be 2^31 or more.
- **R3** The tag is written exactly as its 4 bytes, trailing spaces included.

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

The search fields hold nonsense here (a real font with 3 tables would have 32, 1 and 16).
That doesn't matter, because they are skipped.

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

Notice that the records are sorted by tag, not by offset: `head` is the first table in the
file (offset 300) but the eleventh record.

## Constraints

- `numTables` is between 0 and 30 in the tests, and the tags in one file are all different.
- Tags are printable ASCII and never contain `"`. Spaces only appear at the end.
- The directory itself is always complete. Offsets and lengths may point anywhere.
- Each case has a 10-second limit. A correct solution takes milliseconds.
- There are 13 tests: hand-made directories for each rule, three small fonts built with
  fontTools (with and without the hinting tables, and with three tables removed), both real
  fonts, and 3 random directories.

## Source material

- Apple, *TrueType Reference Manual*, [The font directory](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html)
  (the "offset subtable" and "table directory" tables)
- Microsoft, *OpenType specification*, [Organization of an OpenType font](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#organization-of-an-opentype-font)
  (TableDirectory and TableRecord)
- The blog: [Offset table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Offset%20table)

## Hints

<details><summary>Hint 1: where to start</summary>

Everything you need is in the first 12 + 16 × `numTables` bytes. Read the header fields in
the order they are stored, then loop `numTables` times, reading one record per pass.
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
- Skip exactly 6 bytes after `numTables`. If you skip 4 or 8, every record is misaligned.
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
  R3  Tags exactly as stored: 4 characters, trailing spaces kept ...........    0 / 2   FAILED
      x 02-R3-tiny-hinted  the 4-glyph font plus 'cvt ', fpgm, prep and gasp (14 tables)
          expected `table "cvt " 4292346576 544 8`, closest line written: `table "cvt" 4292346576 544 8` - differs in tag (15 lines written, 15 expected)
          likely cause: R3 - Tags exactly as stored: 4 characters, trailing spaces kept
          expected values from: Python struct, cross-checked against fontTools 4.67.0 SFNTReader
          reproduce: build/solutions/assignment_02.exe build/cases/02/02-R3-tiny-hinted.in build/cases/02/02-R3-tiny-hinted.out
```

The lines may be in any order, so the checker looks for each expected line in your output and,
when one is missing, shows the closest line you wrote with the same keyword. Spaces inside a
quoted tag are kept exactly.

## After you pass: compare with the author's code

[The blog's directory parser](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Parser%20for%20table%20directory)
runs in `FontParser`'s constructor, right after the file is opened. It skips the scaler type,
reads `numTables`, skips the three search fields, and then reads each record: the tag as 4
raw bytes turned into a string, followed by the checksum, offset and length. The records go
into an `unordered_map` keyed by tag, so every later step finds its table by name, for
example the `cmap` table in assignment 03.

**Something to look for:** the snippet doesn't check the scaler type or verify any
checksums. Neither matters for this workbook. A stricter parser would reject files whose
scaler type isn't `0x00010000` or `'true'` (an `'OTTO'` font stores CFF outlines instead of
`glyf`), and could check each table's sum of uint32 words against its `checkSum`.
