# 03 · Map characters to glyphs (cmap format 12)

**Difficulty:** Medium · **Assignment** 3 of 18 · **Check:** `.\check 03`

**Tags**
- *Language:* [32-bit unsigned integers](#primer/cstdint) · [hexadecimal](#primer/hex-literals) · [nested loops](#primer/loops) · [exceptions](#primer/exceptions)
- *Library:* [`std::ifstream`](#primer/fstream) in binary mode (`seekg`) · [`std::unordered_map`](#primer/unordered-map) (or [`std::map`](#primer/map), or a sorted [`std::vector`](#primer/vector) with binary search)
- *Concepts:* [Unicode code points](#primer/code-point) (U+XXXX) beyond the BMP · [glyph ids](#primer/glyph-id) · [the `cmap` table](#primer/cmap) · [encoding records](#primer/cmap) · [format 12 range groups](#primer/cmap) · [big-endian byte order](#primer/big-endian)

## Read in the blog first

This page is enough on its own. The blog's
[cmap table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=cmap%20table) section is the
background, through the paragraph that starts "In the implementation, simply loop"; the author's
code follows it.

## Learning material

- [Unicode code points](#primer/code-point): each `lookup` line names one, like `U+1F600`, and
  the ones above U+FFFF are why the map's keys are `uint32_t`.
- [Hexadecimal](#primer/hex-literals): the digits after `U+` are base 16, which the program
  parses with `std::stoul(..., nullptr, 16)`.
- [Glyphs and glyph ids](#primer/glyph-id): the number a code point maps to. Assignment 04 turns
  it into the position of the glyph's outline.
- [The `cmap` table](#primer/cmap): `src/font/Cmap.cpp` does the lookup this assignment asks for, through the
  encoding records, a subtable and its format 12 groups.
- [`<unordered_map>`](#primer/unordered-map): `loadUnicodeToGlyphCodeMap` returns a
  `std::unordered_map<uint32_t, uint32_t>` from code point to glyph id, and the program answers
  `count` with its `size()`.
- [Iterators](#primer/iterators): to answer a `lookup`, the program calls `glyphFor.find(...)`
  and writes `none` if the result equals `glyphFor.end()`.
- [`<optional>`](#primer/optional): one way to track whether a (0, 4) record has turned up yet,
  with no invented offset standing in.
- [Deriving from a class](#primer/inheritance): `UnsupportedCmap` in `Cmap.h` derives from
  `std::runtime_error`, borrows its constructors with a `using` line, and the program catches
  it by name to write `unsupported`.
- [`std::size_t`](#primer/size-t): in a `table "<tag>" ...` line the program locates the quotes
  with `line.find('"')`, which returns a `std::size_t`, or `std::string::npos` if there are none.

## Source material

- Apple, *TrueType Reference Manual*, ['cmap' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html)
  (the header, the subtable list and "Format 12")
- Microsoft, *OpenType specification*, [cmap: Character to Glyph Index Mapping Table](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap)
  (platform and encoding IDs, "Format 12: Segmented coverage", "Format 13: Many-to-one range mappings")
- The blog: [cmap table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=cmap%20table)

## Where this fits

A font numbers its glyphs 0, 1, 2, ... and `cmap` is how a character finds its number.
Assignment 04 then turns that number into the byte offset of the glyph's outline and 07 decodes the outline; 18 looks up
every character of its text in the map you read here.

## The problem

Read a font's character map and answer two kinds of question: how many characters it maps, and
which glyph a given character maps to.

A code point is a character's number in Unicode, written `U+` and hex digits: `A` is U+0041. A
glyph is a shape the font can draw, and its glyph id is its position in the font, counting from
0. The blog calls that number the GlyphCode, and the specifications say glyph index. The `cmap`
table gives the glyph id for each code point. Your program reads one slice of it, the platform
0 / encoding 4 subtable in format 12, described below.

### Input

The checker starts your program from the workbook folder with `<program> <input-file> <output-file>`.
The input holds these lines, in order:

| Line | Meaning |
|---|---|
| `font <path>` | The font file. The path is relative to the workbook folder and contains no spaces. |
| `table "cmap" <checkSum> <offset> <length>` | The `cmap` table's record from the table directory, written as assignment 02 writes it. Your program needs only `offset`: where `cmap` starts, in bytes from the start of the file. |
| `count` | Asks for the number of code points the subtable maps. |
| `lookup U+<hex>` | Asks which glyph this code point maps to. The code point is in hexadecimal, uppercase, with 4 to 6 digits (`U+0041`, `U+1F600`, `U+10FFFD`). |

There are one or more `count` and `lookup` lines, in any mix.

You can parse the `table` line into the record type your `FontParser` declares (assignment 02)
and read the font with `ByteReader` (assignment 01).

### Output

If the font has no platform 0 / encoding 4 subtable in format 12 (see below), write the
single line `unsupported` and nothing else.

Otherwise write one line per question, in input order:

- `count` → `count <n>`, the number of code points the subtable maps
- `lookup U+<hex>` → `lookup U+<hex> <glyphId>`, or `lookup U+<hex> none` if no group covers
  the code point. Write the code point as it appears in the input.

### The `cmap` table

All numbers are big-endian, and every offset inside `cmap` is relative to the start of the
`cmap` table.

The table starts with a 4-byte header:

| Field | Type | Meaning |
|---|---|---|
| `version` | uint16 | 0 (skip it) |
| `numberSubtables` | uint16 | How many encoding records follow |

Right after the header come `numberSubtables` encoding records, 8 bytes each:

| Field | Type | Meaning |
|---|---|---|
| `platformID` | uint16 | 0 = Unicode, 1 = Macintosh, 3 = Windows |
| `encodingID` | uint16 | Meaning depends on the platform. For platform 0: 3 = Unicode, BMP only (code points up to U+FFFF); 4 = Unicode, full repertoire; 5 = variation sequences |
| `offset` | uint32 | Where this record's subtable starts, from the start of `cmap` |

Every subtable starts with a uint16 `format`. To choose a subtable, find the (0, 4) record,
the one with `platformID` 0 and `encodingID` 4:

- If it exists and its subtable is format 12, use that subtable, wherever the record is in
  the list.
- If there is no such record, the answer is `unsupported`.
- If its subtable's format isn't 12, the answer is also `unsupported`.
- Ignore every other record, even one that points to a format 12 subtable.

Fonts use other formats too: 4 for BMP-only maps, 13 for "many codes, one glyph" maps, 14 for
variation sequences. Only format 12 is in play here.

A format 12 subtable ("segmented coverage") has these fields:

| Field | Type | Meaning |
|---|---|---|
| `format` | uint16 | 12 |
| `reserved` | uint16 | 0 |
| `length` | uint32 | Length of the subtable in bytes, header included |
| `language` | uint32 | 0 for Unicode subtables |
| `numGroups` | uint32 | How many groups follow |
| `groups[numGroups]` | 12 bytes each | See below |

Skip `reserved`, `length` and `language`: 10 bytes in all.

Each group is 12 bytes:

| Field | Type | Meaning |
|---|---|---|
| `startCharCode` | uint32 | First code point in the group |
| `endCharCode` | uint32 | Last code point in the group, included |
| `startGlyphID` | uint32 | Glyph id of `startCharCode` |

A code point c with `startCharCode` ≤ c ≤ `endCharCode` maps to glyph
`startGlyphID` + (c − `startCharCode`). A group of one code point has
`startCharCode` = `endCharCode`. Groups come in increasing order and don't overlap, so the
subtable maps Σ (`endCharCode` − `startCharCode` + 1) code points in total.

Code points go up to U+10FFFF, which needs 32 bits. Format 4 stores 16-bit codes and can't
reach emoji, rare CJK characters or the Nerd Font icons in JetBrains Mono; format 12 exists
to cover them.

## Requirements

A test checks one requirement, and the report groups results that way. For some failures it adds a
`likely cause` line with the requirement the output hints at.

- **R1** Your program reads the subtable whose record has platform 0 and encoding 4, wherever
  that record is in the list, and ignores the others, including format 12 subtables with
  different mappings.
- **R2** Each group maps every code point from `startCharCode` to `endCharCode`, both
  included, to consecutive glyph ids starting at `startGlyphID`.
- **R3** Code points above U+FFFF follow the same rules as the rest, as 32-bit numbers.
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

U+0039 ends the first group, so it maps to 1 + (0x39 − 0x30) = 10. U+003A, one past the end,
belongs to no group.

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
`cmap` + 8728, (1, 0), (3, 1) and (3, 10). The first one points to a format 4 subtable, so the
search has to go on past it. The (0, 4) subtable at byte 49020 + 8728 = 57748 has 226 groups.
Its second group is `00 00 00 20 00 00 00 7e 00 00 00 04`: U+0020..U+007E → glyphs 4..98,
which puts U+0041 at glyph 4 + (0x41 − 0x20) = 4 + 33 = 37.

### Example 3: a format 13 subtable (test `03-R6-format13`)

```
input:   font tests/03/data/03-R6-format13.ttf
         table "cmap" 1442434 412 104
         count
         lookup U+0041
         lookup U+0042

output:  unsupported
```

This font's (0, 4) record points to a format 13 subtable. Format 13 has the same layout as
format 12, but every code in a group maps to the *same* glyph. Read as format 12 it gives wrong
answers, so check the format number.

## Constraints

- The tests' subtables map up to about 17,000 code points, in up to about 5,500 groups.
  Every group has `startCharCode` ≤ `endCharCode` ≤ U+10FFFF.
- The groups come in increasing `startCharCode` order and don't overlap. There is at most one
  (0, 4) record.
- Each input has at most 100 questions.
- The limit per case is 10 seconds, though a correct solution finishes in under a second.
- 24 tests in all: both real fonts (ASCII, Latin-1, Nerd Font icons above U+F0000, kanji and kana,
  CJK characters above U+FFFF, unmapped code points, counts), fonts assembled with fontTools (decoy
  subtables, (0, 4) listed last, long runs, one-code groups, emoji-range codes, gaps, and four kinds
  of unsupported `cmap`: no (0, 4) record at all, a (0, 4) record pointing to a format 4 or a format
  13 subtable, and a format 12 subtable listed only under (3, 10)), and random character maps.

## Hints

<details><summary>Hint 1: where to start</summary>

Three hops: the `cmap` header, the right encoding record, then the subtable and its groups. An
encoding record's offset counts from the start of `cmap`, so the subtable sits at
(`cmap` offset + record offset) in the file.
</details>

<details><summary>Hint 2: the approach</summary>

Read every encoding record and keep the offset of the one with platform 0 and encoding 4. Jump
to it and read the format. If there's no such record or the format isn't 12, report an
unsupported font (the Boilerplate throws `UnsupportedCmap`). Otherwise skip the 10 bytes of
`reserved`, `length` and `language`, read `numGroups`, and for each group put every code point
from start to end into a hash map with its glyph id. `count` is then the size of the map.
</details>

<details><summary>Hint 3: the traps</summary>

- The (0, 4) record may not come first. JetBrains Mono lists (0, 3) first, and that one is
  format 4.
- Don't take the first format 12 subtable you meet. The (3, 10) subtable often has the same
  mappings, but the spec doesn't require it, and two tests contain decoys with different
  mappings. This assignment reads (0, 4) only. A complete renderer would also accept a format 12
  subtable under (3, 10), Windows' record for the full Unicode range.
- The range includes `endCharCode`: loop with `<=`, not `<`.
- Keep code points in 32-bit (or wider) variables throughout. A `uint16_t` key turns U+1F600
  into U+F600. And if the loop counter has the same type as `endCharCode`, `c <= end` can't
  become false when `end` is the largest value of that type; a 64-bit counter avoids that.
- Format 13 has the same layout as format 12, so check the format number.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
cmap = tables.at("cmap").offset           # tables is const: at() or find(), not []
seek(cmap); skip(2)                        # version
n = read_u16()
subtable = none
repeat n times:
    platform = read_u16(); encoding = read_u16(); offset = read_u32()
    if platform == 0 and encoding == 4 and subtable is none: subtable = offset
if subtable is none: report unsupported
seek(cmap + subtable)
if read_u16() != 12: report unsupported
skip(10)                                   # reserved, length, language
map = {}
repeat read_u32() times:                   # numGroups
    start = read_u32(); end = read_u32(); glyph = read_u32()
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

On failure the checker prints:

```
  R2  Every group maps startCharCode..endCharCode (both included) ..........    1 / 4   FAILED
      x 03-R2-long-runs  two long groups: U+0100-U+04FF (1024 codes) and U+3041-U+3096
          line 5: expected `lookup U+04FF 1024`, got `lookup U+04FF none`
          likely cause: R2 - Every group maps startCharCode..endCharCode (both included)
          expected values from: fontTools 4.67.0 cmap.getcmap(0, 4) and getGlyphID, cross-checked against a struct parse
          reproduce: build/solutions/assignment_03.exe build/cases/03/03-R2-long-runs.in build/cases/03/03-R2-long-runs.out
```

## After you pass: compare with the author's code

[The blog's character map loader](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Unicode%E2%86%92GlyphCode%20mapping),
`loadUnicodeToGlyphCodeMap`, jumps to `cmap`, skips the version and loops over every encoding
record, keeping the offset of a platform 0 / encoding 4 record. If there is none, or the
subtable's format isn't 12, it throws "Not supported format". Otherwise it skips the 10 header
bytes, reads the group count and expands every group into an `unordered_map` from code point
to glyph id, `unicodeToGlyphCode`, which later steps use to look characters up.

The loop doesn't stop at the first match, so a font with two (0, 4) records would end up with
the last one. The spec forbids duplicate records (fontTools won't write them), so it makes no difference
in practice. Expanding every group buys simple code with memory: a font that maps most
of Unicode would need over a million map entries, where the sorted groups plus a binary search
stay small. Many fonts that cover only the BMP have a format 4 subtable and no format 12 one
(like test `03-R6-format4-only`). A complete renderer would read format 4 as a fallback, as the
comment in the author's code says, and would also accept a format 12 subtable under (3, 10)
when the font has no (0, 4) record.

The author marks "not found yet" with `u_int32_t subtableOffset = -1`. The -1 becomes 4294967295 and
the later `== -1` converts the same way, so the check works. `u_int32_t` comes from the BSD and
glibc headers and isn't standard C++ (MSVC doesn't have it); `uint32_t` is the standard name.
The group loop counts with an `int` up to `endCharCode - startCharCode`, an unsigned
difference, so a malformed group whose start is above its end would wrap to about 4 billion
steps. The spec rules such groups out, and so do this page's constraints. The repository's code
matches the post, and its header declares the map as `std::unordered_map<uint32_t, uint16_t>`:
a glyph id fits in 16 bits, since `numGlyphs` is a uint16.
