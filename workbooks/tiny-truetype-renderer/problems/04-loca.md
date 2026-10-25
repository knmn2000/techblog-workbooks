# 04 · Locate glyph records (loca)

**Difficulty:** Medium · **Assignment** 4 of 18 · **Check:** `.\check 04`

**Tags**
- *Language:* [unsigned arithmetic](#primer/integer-promotion) (`uint16_t`, `uint32_t`) · [signed `int16_t`](#primer/integer-types) · off-by-one reasoning · [`std::vector`](#primer/vector)
- *Library:* [`std::ifstream`](#primer/fstream) in binary mode (`seekg`)
- *Concepts:* [glyph ids](#primer/glyph-id) · the [`maxp`](#primer/maxp), [`head`](#primer/head), [`loca`](#primer/loca) and `glyf` tables · [short and long offset formats](#primer/loca) · [empty glyphs](#primer/loca) · [big-endian byte order](#primer/big-endian)

## Read in the blog first

The blog's [loca table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=loca%20table)
section is optional background, up to the paragraph that starts "Additionally, a minor point is".
The author's code starts straight after it.

## Learning material

- [The `maxp` table](#primer/maxp): where `numGlyphs` lives (`maxp` + 4). `src/font/Loca.cpp`
  needs it to know how many `loca` entries there are, and `loca` has one more than that.
- [The `head` table](#primer/head): the int16 `indexToLocFormat` at `head` + 50 decides
  whether `loca` stores short or long entries.
- [The `loca` table](#primer/loca): `Loca.cpp` turns each pair of neighbouring entries into a
  glyph's offset in the file and its length.
- [Integer promotion](#primer/integer-promotion): how C++ evaluates `2 * entry` (an `int`) when `entry` is a
  `uint16_t`, so a doubled offset above 65535 comes out right. The danger is
  storing the result back in a `uint16_t`, which cuts it to 16 bits; keep it in a `uint32_t`.
- [Variable fonts](#primer/variable-font): the workbook's Noto Sans JP is a variable build,
  so its space is glyph 1, unlike the static font in the blog's example.

## Source material

- Apple, *TrueType Reference Manual*, ['loca' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6loca.html),
  ['head' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6head.html),
  ['maxp' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6maxp.html)
- Microsoft, *OpenType specification*, [loca: Index to Location](https://learn.microsoft.com/en-us/typography/opentype/spec/loca),
  [head: Font Header Table](https://learn.microsoft.com/en-us/typography/opentype/spec/head),
  [maxp: Maximum Profile](https://learn.microsoft.com/en-us/typography/opentype/spec/maxp)
- The blog: [loca table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=loca%20table)

## Where this fits

Assignment 03 ended with a glyph id. This one finds the outline behind it, as a byte offset
and a length inside `glyf`. Assignment 07 decodes what sits there, and 09 and 18 also reach
glyphs through your `Loca`.

## The problem

Write a program that finds where each requested glyph's record sits in the font file and how
many bytes it takes.

A record is the block of bytes in the `glyf` table that holds one glyph's outline. The `loca`
table (index to location) lists where every record starts. Two fields, one in `maxp` and one
in `head`, tell you how to read `loca` itself.

### Input

The checker invokes `<program> <input-file> <output-file>` from inside the workbook folder. The
input file has these lines, in this order:

| Line | Meaning |
|---|---|
| `font <path>` | The font file. The path is relative to the workbook folder and contains no spaces. |
| `table "<tag>" <checkSum> <offset> <length>` | Four lines, for `glyf`, `head`, `loca` and `maxp`: their records from the table directory, written as assignment 02 writes them. `offset` is where the table starts in the file. |
| `glyph <id>` | A glyph id, from 0 to `numGlyphs` − 1. An input can have none of these lines, or many. |

The `table` lines fit the records your `FontParser` declares (assignment 02), and your
`ByteReader` from assignment 01 can read the font.

### Output

The first line is

```
glyphs <numGlyphs> loca <short|long>
```

Then, for each `glyph` line, in input order:

```
glyph <id> <offset> <length>
```

- `offset` is where the glyph's record starts, in bytes from the start of the file.
- `length` is the record's size in bytes. 0 means the glyph has no outline, as with the space.

These `glyph` lines are in assignment 07's input format. Put a `font` line above them and your
assignment 07 program decodes the glyphs.

### The tables you need

All numbers are big-endian.

From `maxp` you need one field:

| Offset in `maxp` | Field | Type | Meaning |
|---|---|---|---|
| 0 | `version` | 4 bytes | Skip it |
| 4 | `numGlyphs` | uint16 | How many glyphs the font has. Glyph ids go from 0 to `numGlyphs` − 1. |

From `head` you also need one field, 50 bytes in:

| Offset in `head` | Field | Type | Meaning |
|---|---|---|---|
| 0 to 49 | version, revision, checksum adjustment, magic number, flags, `unitsPerEm`, dates, bounding box, ... | | Not needed here |
| 50 | `indexToLocFormat` | int16 | 0: `loca` holds short offsets. 1: `loca` holds long offsets. |
| 52 | `glyphDataFormat` | int16 | 0 (not needed) |

`loca` holds `numGlyphs` + 1 entries, back to back from the start of the table:

| `indexToLocFormat` | Entry type | The offset it stands for |
|---|---|---|
| 0 (short) | uint16 | the entry × 2 |
| 1 (long) | uint32 | the entry itself |

Short entries store half the offset, which lets a font whose `glyf` table is under 128 KB get
by with 2 bytes per entry. It only works when every offset is even, so short-format fonts pad
their glyph records to even lengths.

Offsets count from the start of the `glyf` table. Glyph i's record runs from offset(i) up to,
but not including, offset(i + 1):

- absolute offset = `glyf` table offset + offset(i)
- length = offset(i + 1) − offset(i)

The extra entry, number `numGlyphs`, marks where the last glyph ends. A glyph with no outline
has length 0 and shares its offset with the next glyph. A record can end in a few bytes of
padding that count toward its length; assignment 07 skips them.

## Requirements

Each test targets one requirement. If any fail you get a tally under each requirement, and
sometimes a `likely cause` line pointing to the requirement the mismatch resembles.

- **R1** `numGlyphs` is the uint16 at `maxp` + 4.
- **R2** The format is the int16 `indexToLocFormat` at `head` + 50: 0 is `short`, 1 is
  `long`.
- **R3** In the short format, each entry is a uint16 holding half the offset, and your program
  multiplies it by 2. Results can be larger than 65535, so multiply in 32 bits: a uint16
  doubled in 16-bit arithmetic overflows.
- **R4** A glyph's offset is the `glyf` table's offset plus its `loca` offset.
- **R5** A glyph's length is the next `loca` offset minus its own. This includes the last
  glyph, whose end is the extra entry `numGlyphs`.

## Examples

### Example 1: a short `loca` (test `04-R3-short-x2`)

```
input:   font tests/04/data/04-R3-short-x2.ttf
         table "glyf" 932940381 484 236
         table "head" 603817628 172 54
         table "loca" 19792115 464 18
         table "maxp" 720906 264 32
         glyph 0
         glyph 1
         glyph 2
         glyph 3
         glyph 4
         glyph 5
         glyph 6
         glyph 7
```

`maxp` + 4 (byte 268) holds `00 08`, so 8 glyphs. `head` + 50 (byte 222) holds `00 00`, which
means the short format and 9 uint16 entries in `loca`:

```
00 00  00 0d  00 21  00 2d  00 3b  00 4f  00 5c  00 6a  00 76
  0      13     33     45     59     79     92    106    118     entries
  0      26     66     90    118    158    184    212    236     offsets (x 2)
```

Glyph 1 starts at 484 + 26 = 510 and is 66 − 26 = 40 bytes long. The last entry, 236, happens
to be the size of the whole `glyf` table.

```
output:  glyphs 8 loca short
         glyph 0 484 26
         glyph 1 510 40
         glyph 2 550 24
         glyph 3 574 28
         glyph 4 602 40
         glyph 5 642 26
         glyph 6 668 28
         glyph 7 696 24
```

### Example 2: assignment 07's glyphs (test `04-R4-jetbrains-07`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf
         table "glyf" 810950304 113484 2068620
         table "head" 546057157 300 54
         table "loca" 588705204 64980 48504
         table "maxp" 946608241 392 32
         glyph 17
         glyph 4
         glyph 77
         glyph 37

output:  glyphs 12125 loca long
         glyph 17 115392 56
         glyph 4 113584 0
         glyph 77 122844 24
         glyph 37 118060 112
```

JetBrains Mono uses long offsets. Entry 17 (at byte 64980 + 4 × 17) is `00 00 07 74` = 1908
and entry 18 is 1964, so glyph 17, the hyphen, starts at 113484 + 1908 = 115392 and is
1964 − 1908 = 56 bytes long. Entries 4 and 5 are both 100: glyph 4, the space, is empty.
These four lines are the input of assignment 07's example 3.

### Example 3: an empty last glyph (test `04-R5-empty-last-spare`)

```
input:   font tests/04/data/04-R5-empty-last-spare.ttf
         table "glyf" 1843900827 468 94
         table "head" 603817628 172 54
         table "loca" 4587578 456 10
         table "maxp" 458762 264 32
         glyph 0
         glyph 1
         glyph 2
         glyph 3

output:  glyphs 4 loca short
         glyph 0 468 26
         glyph 1 494 24
         glyph 2 518 40
         glyph 3 558 0
```

The 5 entries are 0, 13, 25, 45, 45, which doubles to offsets 0, 26, 50, 90, 90. Glyph 3, the
last, runs from 90 to 90 and is empty. This font's `glyf` table is 94 bytes long, 4 more than
the last entry, so using the end of `glyf` as the end of the last glyph gives a length of 4,
which is wrong. The end of the last glyph comes from `loca`'s extra entry.

## Constraints

- `numGlyphs` is at most 17,936 in the tests, and every `glyph` id is below it.
- `indexToLocFormat` is 0 or 1 in every test, and no `loca` entry is smaller than the one
  before it.
- At most 30 `glyph` lines per input.
- Time limit: 10 seconds per case. Correct solutions take milliseconds.
- 18 tests. Both real fonts (long format, empty glyphs, first and last glyphs, random glyphs), plus
  fonts generated with fontTools: short and long formats, a short `loca` whose offsets pass 65535,
  empty glyphs at the start, middle and end, and spare bytes after the last glyph.

## Hints

<details><summary>Hint 1: where to start</summary>

Two numbers tell you how to read `loca`: the glyph count (`maxp`) and the entry size (`head`).
Get those, read the whole `loca` table into a list of offsets, and take each length as the
difference between neighbours.
</details>

<details><summary>Hint 2: the approach</summary>

Read `numGlyphs` + 1 entries into a vector, doubling them if the format is short. Glyph i, for
i from 0 to `numGlyphs` − 1, then lives at (`glyf` offset + entry[i], entry[i + 1] − entry[i]).
</details>

<details><summary>Hint 3: the traps</summary>

- That is `numGlyphs` + 1 entries to read, one past the glyph count. Without the extra one the
  last glyph has no end. The `glyf` table's length can't stand in for it, since a font may
  have spare bytes after the last glyph.
- Multiply short entries by 2 in a 32-bit variable. Twice a uint16 can top 65535.
- `indexToLocFormat` is at `head` + 50. The field after it (+52) is `glyphDataFormat`, which
  is 0, so reading it by mistake makes every font look short.
- `loca` offsets count from the start of `glyf`, not from the start of the file.
- An empty glyph has the same offset as the glyph after it. Both lines get that offset.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
seek(maxp + 4);  numGlyphs = readUint16()
seek(head + 50); isLong = (readInt16() == 1)
seek(loca)
entries = []
repeat numGlyphs + 1 times:
    entries.append(readUint32() if isLong else 2 * readUint16())
for i in 0 .. numGlyphs - 1:
    glyph[i] = (glyf + entries[i], entries[i + 1] - entries[i])
```
</details>

## Checking your solution

```
.\check 04                         run every test
.\check 04 -Case 04-R3-short-x2    one test, showing its full input, expected output and your output
.\check 04 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 04 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing run, here with offsets that forget where `glyf` starts:

```
  R4  Offset = glyf table offset + loca entry (x2 when short) ..............    0 / 2   FAILED
      x 04-R4-jetbrains-07  JetBrains Mono: '-', ' ', 'i', 'A', the glyphs of checkpoint 7's example
          glyph[0]: expected (id=17, offset=115392, length=56), got (id=17, offset=1908, length=56) - differs in offset  (in `glyphs 12125 loca long`)
          likely cause: R4 - Offset = glyf table offset + loca entry (x2 when short)
          expected values from: fontTools 4.67.0 maxp, head, loca and the glyf offset, cross-checked against a struct parse of loca
          reproduce: build/solutions/assignment_04 build/cases/04/04-R4-jetbrains-07.in build/cases/04/04-R4-jetbrains-07.out
```

## After you pass: compare with the author's code

[The blog's loca reader](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=GlyphCode%E2%86%92GlyphOffset%20mapping),
`loadGlyphOffsetsMap`, takes `numGlyphs` from `maxp` and `indexToLocFormat` from `head`,
reads one `loca` entry per glyph (doubling short ones) and stores `glyf` offset + entry in a
map from glyph id to file offset, `glyphCodeToOffset`. It keeps no lengths. Instead, when
glyph i − 1 has the same offset as glyph i, it marks glyph i − 1 as empty by setting its
offset to 0, and later steps read offset 0 as a glyph with no outline. Your
`loadGlyphLocations` stores a length per glyph, and a length of 0 means the same thing. The
snippet doubles short entries with `* 2u`, in unsigned 32-bit arithmetic, which is what R3
asks for. The author's repository has the same code.

The post's example of the check, the space in Noto Sans JP taking the comma's outline, comes
from the static NotoSansJP-Regular font. The workbook's Noto Sans JP is the variable build,
where the space is glyph 1 and shares its offset with glyph 2, the `!`. Skip the check there
and the space draws as `!`.

The snippet reads `numGlyphs` entries where the spec has `numGlyphs` + 1. With nothing after
the last glyph to compare against, the loader can't mark that glyph as empty, and later steps
read its record even when it has no outline. In JetBrains Mono the last glyph (12124) is
empty. The spec's extra entry covers the case, and R5 tests it.
