# 03 · Map characters to glyphs (cmap format 12)

**Difficulty:** Medium · **Checkpoint** 3 of 18 · **Check:** `.\check 03`

**Tags**
- *Language:* 32-bit unsigned integers · hexadecimal · nested loops · exceptions
- *Library:* `std::ifstream` in binary mode (`seekg`) · `std::unordered_map` (or `std::map`, or a sorted `std::vector` with binary search)
- *Concepts:* Unicode code points (U+XXXX) beyond the BMP · glyph ids · the `cmap` table · encoding records · format 12 range groups · big-endian byte order

## Read in the blog first

This page is complete on its own; the blog tells the story behind it. Read the blog's
[cmap table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=cmap%20table)
section up to the paragraph that starts "In the implementation, simply loop". The author's
code comes right after it.

## Where this fits

Text arrives as characters, but a font stores glyphs, numbered 0, 1, 2, ... The `cmap`
table turns a character's code point into a glyph id. Checkpoint 4 then turns the glyph id
into the byte offset of the glyph's outline, and checkpoint 7 decodes the outline there.

## The problem

Write a program that reads a font's Unicode character map (the platform 0 / encoding 4
subtable, in format 12) and answers questions about it: how many characters it maps, and
which glyph a given character maps to.

Only the program's output is checked, so you can structure the code however you like. This
checkpoint's code goes in your project, in `font/Cmap.h` and `font/Cmap.cpp` under `src/`. It
can build on `font/ByteReader.h` and `font/FontParser.h`. `checkpoints/p03_cmap.cpp` is the
program the checker runs: it reads the test input, calls your code and writes the answer.

Each new file starts blank, with a comment saying what belongs in it, and the program with an
empty `main`, so the includes, reading the input and writing the output are yours. To start from
working input/output code instead, pick Boilerplate in the book's editor (or copy this
checkpoint's files from `starters/boilerplate/`): the declarations use the author's names where
the post has them, and what's left to write is `loadUnicodeToGlyphCodeMap`.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains these lines, in this order:

| Line | Meaning |
|---|---|
| `font <path>` | The font file. The path is relative to the workbook folder and contains no spaces. |
| `table "cmap" <checkSum> <offset> <length>` | The `cmap` table's record from the table directory, written as checkpoint 2 writes it. You only need `offset`: where `cmap` starts, in bytes from the start of the file. |
| `count` | A question: how many code points does the subtable map? |
| `lookup U+<hex>` | A question: which glyph does this code point map to? The code point is in hexadecimal, uppercase, with 4 to 6 digits (`U+0041`, `U+1F600`, `U+10FFFD`). |

There are one or more `count` and `lookup` lines, in any mix.

### Output

If the font has no platform 0 / encoding 4 subtable in format 12 (see below), write the
single line `unsupported` and nothing else.

Otherwise write one line per question, in input order:

- `count` → `count <n>`, the number of code points the subtable maps
- `lookup U+<hex>` → `lookup U+<hex> <glyphId>`, or `lookup U+<hex> none` if no group covers
  the code point. Write the code point exactly as it appears in the input.

### The `cmap` table

All numbers are **big-endian**. Every offset in `cmap` is counted from the start of the
`cmap` table, not from the start of the file.

**Header**, 4 bytes, at the table's offset:

| Field | Type | Meaning |
|---|---|---|
| `version` | uint16 | 0. Skip it. |
| `numberSubtables` | uint16 | How many encoding records follow |

**Encoding records**: `numberSubtables` of them, 8 bytes each, right after the header:

| Field | Type | Meaning |
|---|---|---|
| `platformID` | uint16 | 0 = Unicode, 1 = Macintosh, 3 = Windows |
| `encodingID` | uint16 | Meaning depends on the platform. For platform 0: 3 = Unicode, BMP only; 4 = Unicode, full repertoire; 5 = variation sequences |
| `offset` | uint32 | Where this record's subtable starts, from the start of `cmap` |

**Which subtable.** Use the subtable of the record with `platformID` 0 and `encodingID` 4,
wherever it is in the list. Ignore every other record, even one that points to a format 12
subtable. If there is no such record, the answer is `unsupported`.

Every subtable starts with a uint16 `format`. If the (0, 4) subtable's format isn't 12, the
answer is also `unsupported`. (Fonts also use format 4 for BMP-only maps, format 13 for
"many codes, one glyph" maps, and format 14 for variation sequences. This checkpoint reads
only format 12.)

**Format 12 subtable** ("segmented coverage"):

| Field | Type | Meaning |
|---|---|---|
| `format` | uint16 | 12 |
| `reserved` | uint16 | 0. Skip it. |
| `length` | uint32 | Length of the subtable in bytes, header included. Skip it. |
| `language` | uint32 | 0 for Unicode subtables. Skip it. |
| `numGroups` | uint32 | How many groups follow |
| `groups[numGroups]` | 12 bytes each | See below |

**One group**, 12 bytes:

| Field | Type | Meaning |
|---|---|---|
| `startCharCode` | uint32 | First code point in the group |
| `endCharCode` | uint32 | Last code point in the group, **included** |
| `startGlyphID` | uint32 | Glyph id of `startCharCode` |

A code point c with `startCharCode` ≤ c ≤ `endCharCode` maps to glyph
`startGlyphID` + (c − `startCharCode`). A group of one code point has
`startCharCode` = `endCharCode`. Groups are sorted and never overlap, so the subtable maps
Σ (`endCharCode` − `startCharCode` + 1) code points in total.

Code points go up to U+10FFFF, so they need 32 bits. Format 12 exists for exactly that
reason: format 4 stores 16-bit codes and can't reach emoji, rare CJK characters or the Nerd
Font icons in JetBrains Mono.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement
the difference most likely comes from.

- **R1** The subtable is the one whose record has platform 0 and encoding 4, wherever that
  record is in the list. Other subtables, even format 12 ones with different mappings, are
  ignored.
- **R2** Each group maps every code point from `startCharCode` to `endCharCode`, both
  included, to consecutive glyph ids starting at `startGlyphID`.
- **R3** Code points above U+FFFF work like any other: they are 32-bit numbers.
- **R4** A code point that no group covers gives `none`.
- **R5** `count` is the number of code points the subtable maps.
- **R6** If there is no (0, 4) record, or its subtable isn't format 12, the whole output is
  the single line `unsupported`.

## Examples

### Example 1: two groups (test `03-R4-gaps`)

```
input:   font tests/03/data/03-R4-gaps.ttf
         table "cmap" 786752 476 52
         lookup U+002F
         lookup U+0030
         lookup U+0039
         lookup U+003A
         lookup U+0040
         lookup U+0041
         lookup U+0046
         lookup U+0047
         lookup U+0061
```

The 52 bytes at offset 476:

```
00 00 00 01                  version 0, numberSubtables 1
00 00 00 04 00 00 00 0c      platform 0, encoding 4, subtable at cmap + 12
00 0c 00 00                  format 12, reserved
00 00 00 28 00 00 00 00      length 40, language 0
00 00 00 02                  numGroups 2
00 00 00 30 00 00 00 39 00 00 00 01     U+0030..U+0039 ('0'..'9') -> glyphs 1..10
00 00 00 41 00 00 00 46 00 00 00 14     U+0041..U+0046 ('A'..'F') -> glyphs 20..25
```

```
output:  lookup U+002F none
         lookup U+0030 1
         lookup U+0039 10
         lookup U+003A none
         lookup U+0040 none
         lookup U+0041 20
         lookup U+0046 25
         lookup U+0047 none
         lookup U+0061 none
```

U+0039 is the last code of the first group, so it maps to 1 + (0x39 − 0x30) = 10. U+003A,
one past the end, is in no group.

### Example 2: a real font (test `03-R1-jetbrains`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf
         table "cmap" 2612855665 49020 11978
         lookup U+0041
         lookup U+0061
         lookup U+0030
         lookup U+20AC
         count

output:  lookup U+0041 37
         lookup U+0061 69
         lookup U+0030 20
         lookup U+20AC 744
         count 11743
```

JetBrains Mono's `cmap` has 5 encoding records: (0, 3) at `cmap` + 44, (0, 4) at
`cmap` + 8728, (1, 0), (3, 1) and (3, 10). The first one is a format 4 subtable, so the
program has to keep looking. The (0, 4) subtable at byte 49020 + 8728 = 57748 has 226 groups.
The second group is `00 00 00 20 00 00 00 7e 00 00 00 04`: U+0020..U+007E → glyphs 4..98. So
U+0041 maps to 4 + (0x41 − 0x20) = 4 + 33 = 37.

### Example 3: a format 13 subtable (test `03-R6-format13`)

```
input:   font tests/03/data/03-R6-format13.ttf
         table "cmap" 1442434 412 104
         count
         lookup U+0041
         lookup U+0042

output:  unsupported
```

This font's (0, 4) record points to a format 13 subtable. Format 13 has exactly the same
layout as format 12, but every code in a group maps to the *same* glyph. Reading it as
format 12 would give wrong answers, so the program must check the format.

## Constraints

- The tests' subtables map up to about 17,000 code points, in up to about 5,500 groups.
  Every group has `startCharCode` ≤ `endCharCode` ≤ U+10FFFF.
- Groups are sorted by `startCharCode` and don't overlap. There is at most one (0, 4) record.
- Each input has at most 100 questions.
- Each case has a 10-second limit. A correct solution takes well under a second.
- There are 24 tests: both real fonts (ASCII, Latin-1, Nerd Font icons above U+F0000, kanji
  and kana, CJK characters above U+FFFF, unmapped code points, counts), small fonts built
  with fontTools (decoy subtables, (0, 4) listed last, long runs, one-code groups, emoji-range
  codes, gaps, and four kinds of unsupported `cmap`: no (0, 4) record at all, a (0, 4) record
  pointing to a format 4 or a format 13 subtable, and a format 12 subtable listed only under
  (3, 10)), and random character maps.

## Source material

- Apple, *TrueType Reference Manual*, ['cmap' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html)
  (the header, the subtable list and "Format 12")
- Microsoft, *OpenType specification*, [cmap: Character to Glyph Index Mapping Table](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap)
  (platform and encoding IDs, "Format 12: Segmented coverage", "Format 13: Many-to-one range mappings")
- The blog: [cmap table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=cmap%20table)

## Hints

<details><summary>Hint 1: where to start</summary>

It's three hops: the `cmap` header, the right encoding record, then the subtable and its
groups. Remember that the offset in an encoding record is counted from the start of `cmap`,
so the subtable is at (`cmap` offset + record offset) in the file.
</details>

<details><summary>Hint 2: the approach</summary>

Read every encoding record and remember the offset of the one with platform 0 and encoding
4. Jump to it and read the format; if there is no such record or the format isn't 12, throw
`UnsupportedCmap`. Otherwise skip the 10 bytes of `reserved`, `length` and `language`, read
`numGroups`, and for each group put every code point from start to end into a hash map with
its glyph id. `count` is then the size of the map.
</details>

<details><summary>Hint 3: the traps</summary>

- The (0, 4) record is usually not the first. JetBrains Mono lists (0, 3) first, and that
  one is format 4.
- Don't take "any format 12 subtable". The (3, 10) subtable often holds the same mappings,
  but nothing guarantees it, and two tests contain decoys with different mappings.
- `endCharCode` is included: loop with `<=`, not `<`.
- Keep code points in 32-bit (or wider) variables everywhere. A `uint16_t` key turns U+1F600
  into U+F600. If your loop counter has the same type as `endCharCode`, `c <= end` can never
  become false when end is the largest value of that type; a 64-bit counter avoids that.
- Format 13 looks exactly like format 12. Check the format number.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
cmap = tables["cmap"].offset
seek(cmap); skip(2)                        # version
n = readUint16()
subtable = none
repeat n times:
    platform = readUint16(); encoding = readUint16(); offset = readUint32()
    if platform == 0 and encoding == 4 and subtable is none: subtable = offset
if subtable is none: throw Unsupported
seek(cmap + subtable)
if readUint16() != 12: throw Unsupported
skip(10)                                   # reserved, length, language
map = {}
repeat readUint32() times:                 # numGroups
    start = readUint32(); end = readUint32(); glyph = readUint32()
    for c from start to end, both included:
        map[c] = glyph + (c - start)
return map
```
</details>

## Checking your solution

```
.\check 03                         run every test
.\check 03 -Case 03-R4-gaps        one test, showing its full input, expected output and your output
.\check 03 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 03 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R2  Every group maps startCharCode..endCharCode (both included) ..........    1 / 4   FAILED
      x 03-R2-long-runs  two long groups: U+0100-U+04FF (1024 codes) and U+3041-U+3096
          line 5: expected `lookup U+04FF 1024`, got `lookup U+04FF none`
          likely cause: R2 - Every group maps startCharCode..endCharCode (both included)
          expected values from: fontTools 4.67.0 cmap.getcmap(0, 4) and getGlyphID, cross-checked against a struct parse
          reproduce: build/solutions/p03.exe build/cases/03/03-R2-long-runs.in build/cases/03/03-R2-long-runs.out
```

## After you pass: compare with the author's code

[The blog's character map loader](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Unicode%E2%86%92GlyphCode%20mapping),
`loadUnicodeToGlyphCodeMap`, jumps to `cmap`, skips the version, and loops over every
encoding record, keeping the offset of a platform 0 / encoding 4 record. It throws "Not
supported format" if there is none, or if the subtable's format isn't 12. Then it skips the
10 header bytes, reads the group count, and expands every group into an `unordered_map`
from code point to glyph id, `unicodeToGlyphCode`, which later steps look characters up in.

**Something to look for:** the loop doesn't stop at the first match, so if a font had two
(0, 4) records the last one would win. The spec doesn't allow duplicate records (fontTools
refuses to write them), so it makes no difference in practice. Expanding every group trades
memory for simplicity: a font that maps most of Unicode would need over a million map
entries, while keeping the sorted groups and binary-searching them stays small. Finally,
many fonts that cover only the BMP have no format 12 subtable at all, just format 4 (like
test `03-R6-format4-only`). A complete renderer would read format 4 as a fallback.
