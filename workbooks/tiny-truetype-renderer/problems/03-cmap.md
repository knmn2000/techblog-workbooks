# 03 · Map characters to glyphs (cmap format 12)

**Difficulty:** Medium · **Assignment** 3 of 18 · **Check:** `.\check 03`

**Tags**
- *Language:* 32-bit unsigned integers · hexadecimal · nested loops · exceptions
- *Library:* `std::ifstream` in binary mode (`seekg`) · `std::unordered_map` (or `std::map`, or a sorted `std::vector` with binary search)
- *Concepts:* Unicode code points (U+XXXX) beyond the BMP · glyph ids · the `cmap` table · encoding records · format 12 range groups · big-endian byte order

## Read in the blog first

You can pass using this page alone. For the background, read the blog's
[cmap table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=cmap%20table)
section through the paragraph that starts "In the implementation, simply loop". The author's
code follows that paragraph.

## Source material

- Apple, *TrueType Reference Manual*, ['cmap' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html)
  (the header, the subtable list and "Format 12")
- Microsoft, *OpenType specification*, [cmap: Character to Glyph Index Mapping Table](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap)
  (platform and encoding IDs, "Format 12: Segmented coverage", "Format 13: Many-to-one range mappings")
- The blog: [cmap table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=cmap%20table)

## Where this fits

A font stores glyphs, numbered 0, 1, 2, ..., and its `cmap` table maps each character's code
point to a glyph id. Assignment 04 then turns the glyph id into the byte offset of the glyph's
outline, and assignment 07 decodes the outline there. Assignment 18 looks up every character
of its text in the map you read here.

## The problem

Write a program that reads a font's character map and answers two kinds of question: how many
characters it maps, and which glyph a given character maps to.

A code point is a character's number in Unicode, written `U+` and hexadecimal digits: `A`
is U+0041. A glyph is a shape the font can draw, and its glyph id is its number in the
font, from 0 up. The blog calls this number the GlyphCode (the specifications also say glyph
index). The character map (the `cmap` table) lists the glyph id for each code
point. Your program reads one part of it: the platform 0 / encoding 4 subtable in format 12,
described below.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains these lines, in this order:

| Line | Meaning |
|---|---|
| `font <path>` | The font file. The path is relative to the workbook folder and contains no spaces. |
| `table "cmap" <checkSum> <offset> <length>` | The `cmap` table's record from the table directory, written as assignment 02 writes it. Your program needs only `offset`: where `cmap` starts, in bytes from the start of the file. |
| `count` | Asks for the number of code points the subtable maps. |
| `lookup U+<hex>` | Asks which glyph this code point maps to. The code point is in hexadecimal, uppercase, with 4 to 6 digits (`U+0041`, `U+1F600`, `U+10FFFD`). |

There are one or more `count` and `lookup` lines, in any mix.

Your program can parse the `table` line into the table record your `FontParser` from
assignment 02 declares, and read the font with your `ByteReader` from assignment 01.

### Output

If the font has no platform 0 / encoding 4 subtable in format 12 (see below), write the
single line `unsupported` and nothing else.

Otherwise write one line per question, in input order:

- `count` → `count <n>`, the number of code points the subtable maps
- `lookup U+<hex>` → `lookup U+<hex> <glyphId>`, or `lookup U+<hex> none` if no group covers
  the code point. Write the code point as it appears in the input.

### The `cmap` table

All numbers are big-endian. Every offset inside `cmap` counts from the start of the
`cmap` table, not from the start of the file.

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

Fonts also use format 4 for BMP-only maps, format 13 for "many codes, one glyph" maps, and
format 14 for variation sequences. Your program reads only format 12.

A format 12 subtable ("segmented coverage") has these fields:

| Field | Type | Meaning |
|---|---|---|
| `format` | uint16 | 12 |
| `reserved` | uint16 | 0 |
| `length` | uint32 | Length of the subtable in bytes, header included |
| `language` | uint32 | 0 for Unicode subtables |
| `numGroups` | uint32 | How many groups follow |
| `groups[numGroups]` | 12 bytes each | See below |

Your program skips `reserved`, `length` and `language`, 10 bytes in all.

Each group is 12 bytes:

| Field | Type | Meaning |
|---|---|---|
| `startCharCode` | uint32 | First code point in the group |
| `endCharCode` | uint32 | Last code point in the group, included |
| `startGlyphID` | uint32 | Glyph id of `startCharCode` |

A code point c with `startCharCode` ≤ c ≤ `endCharCode` maps to glyph
`startGlyphID` + (c − `startCharCode`). A group of one code point has
`startCharCode` = `endCharCode`. The groups come in increasing order and don't overlap, so the
subtable maps Σ (`endCharCode` − `startCharCode` + 1) code points in total.

Code points go up to U+10FFFF, so they need 32 bits. Format 4 stores 16-bit codes and can't
reach emoji, rare CJK characters or the Nerd Font icons in JetBrains Mono, and format 12
exists to cover them.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

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
`cmap` + 8728, (1, 0), (3, 1) and (3, 10). The first record points to a format 4 subtable, so
your program has to keep looking. The (0, 4) subtable at byte 49020 + 8728 = 57748 has 226
groups. The second group is `00 00 00 20 00 00 00 7e 00 00 00 04`: U+0020..U+007E → glyphs
4..98, which puts U+0041 at glyph 4 + (0x41 − 0x20) = 4 + 33 = 37.

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
format 12, but every code in a group maps to the *same* glyph. Reading it as format 12 would
give wrong answers, so your program has to check the format.

## Constraints

- The tests' subtables map up to about 17,000 code points, in up to about 5,500 groups.
  Every group has `startCharCode` ≤ `endCharCode` ≤ U+10FFFF.
- The groups come in increasing `startCharCode` order and don't overlap. There is at most one
  (0, 4) record.
- Each input has at most 100 questions.
- Each case has a 10-second limit. A correct solution finishes in under a second.
- There are 24 tests: both real fonts (ASCII, Latin-1, Nerd Font icons above U+F0000, kanji
  and kana, CJK characters above U+FFFF, unmapped code points, counts), small fonts built
  with fontTools (decoy subtables, (0, 4) listed last, long runs, one-code groups, emoji-range
  codes, gaps, and four kinds of unsupported `cmap`: no (0, 4) record at all, a (0, 4) record
  pointing to a format 4 or a format 13 subtable, and a format 12 subtable listed only under
  (3, 10)), and random character maps.

## Hints

<details><summary>Hint 1: where to start</summary>

Your program makes three hops: the `cmap` header, the right encoding record, then the
subtable and its groups. The offset in an encoding record counts from the start of `cmap`, so
the subtable is at (`cmap` offset + record offset) in the file.
</details>

<details><summary>Hint 2: the approach</summary>

Read every encoding record and remember the offset of the one with platform 0 and encoding
4. Jump to it and read the format; if there is no such record or the format isn't 12, report
an unsupported font (the Boilerplate throws `UnsupportedCmap`). Otherwise skip the 10 bytes of `reserved`, `length` and `language`, read
`numGroups`, and for each group put every code point from start to end into a hash map with
its glyph id. `count` is then the size of the map.
</details>

<details><summary>Hint 3: the traps</summary>

- The (0, 4) record may not come first. JetBrains Mono lists (0, 3) first, and that one is
  format 4.
- Don't take the first format 12 subtable you find. The (3, 10) subtable often holds the same
  mappings, but the spec doesn't require it, and two tests contain decoys with different
  mappings. This assignment reads only (0, 4); a complete renderer would also accept a format 12
  subtable under (3, 10), Windows' record for the full Unicode range.
- The range includes `endCharCode`: loop with `<=`, not `<`.
- Keep code points in 32-bit (or wider) variables everywhere. A `uint16_t` key turns U+1F600
  into U+F600. If your loop counter has the same type as `endCharCode`, `c <= end` can never
  become false when end is the largest value of that type; a 64-bit counter avoids that.
- Format 13 has the same layout as format 12. Check the format number.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
cmap = tables["cmap"].offset
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

A failing test looks like this:

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
`loadUnicodeToGlyphCodeMap`, jumps to `cmap`, skips the version, and loops over every
encoding record, keeping the offset of a platform 0 / encoding 4 record. It throws "Not
supported format" if there is none, or if the subtable's format isn't 12. Then it skips the
10 header bytes, reads the group count, and expands every group into an `unordered_map`
from code point to glyph id, `unicodeToGlyphCode`, which later steps look characters up in.

The loop doesn't stop at the first match, so if a font had two
(0, 4) records, the loader would keep the last one. The spec doesn't allow duplicate records
(fontTools won't write them), so this makes no difference in practice. Expanding every group
trades memory for simpler code: a font that maps most of Unicode would need over a million
map entries, while the sorted groups with a binary search stay small. Many fonts that cover
only the BMP have a format 4 subtable and no format 12 one (like test `03-R6-format4-only`).
A complete renderer would read format 4 as a fallback, as the comment in the author's code
says, and would also accept a format 12 subtable under (3, 10) when the font has no (0, 4)
record.

The loader marks "not found yet" with `u_int32_t subtableOffset = -1`. The -1 becomes
4294967295, and the later `== -1` converts the same way, so the check works. `u_int32_t` comes
from the BSD and glibc headers and isn't standard C++ (MSVC doesn't have it); `uint32_t` is the
standard name. The group loop counts with an `int` up to `endCharCode - startCharCode`, an
unsigned difference, so a malformed group whose start is above its end would wrap to about
4 billion steps. The spec rules such groups out, and so do this page's constraints. The
repository's code matches the post, and its header declares the map as
`std::unordered_map<uint32_t, uint16_t>`: a glyph id fits in 16 bits, since `numGlyphs` is a
uint16.
