# 04 · Locate glyph records (loca)

**Difficulty:** Medium · **Assignment** 4 of 18 · **Check:** `.\check 04`

**Tags**
- *Language:* unsigned arithmetic (`uint16_t`, `uint32_t`) · signed `int16_t` · off-by-one reasoning · `std::vector`
- *Library:* `std::ifstream` in binary mode (`seekg`)
- *Concepts:* glyph ids · the `maxp`, `head`, `loca` and `glyf` tables · short and long offset formats · empty glyphs · big-endian byte order

## Read in the blog first

You can pass using this page alone. For the background, read the blog's
[loca table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=loca%20table)
section through the paragraph that starts "Additionally, a minor point is". The author's
code follows that paragraph.

## Where this fits

Assignment 03 turns a character into a glyph id. Here you turn the glyph id into the location
of the glyph's outline: a byte offset and a length inside the `glyf` table. The `glyph` lines
you write use assignment 07's input format, and assignment 07 decodes the outline at that
location. Assignments 09 and 18 also find glyphs through your `Loca`.

## The problem

Write a program that finds where each requested glyph's record is in the font file, and how
many bytes long it is.

A glyph's **record** is the block of bytes in the `glyf` table that holds its outline. The
`loca` table (index to location) gives the start of each record, and two fields in `maxp` and
`head` tell you how to read `loca`.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains these lines, in this order:

| Line | Meaning |
|---|---|
| `font <path>` | The font file. The path is relative to the workbook folder and contains no spaces. |
| `table "<tag>" <checkSum> <offset> <length>` | Four lines, for `glyf`, `head`, `loca` and `maxp`: their records from the table directory, written as assignment 02 writes them. `offset` is where the table starts in the file. |
| `glyph <id>` | A glyph id, from 0 to `numGlyphs` − 1. An input can have none of these lines, or many. |

Your program can parse the `table` lines into the table records your `FontParser` from
assignment 02 declares, and read the font with your `ByteReader` from assignment 01.

### Output

The first line is

```
glyphs <numGlyphs> loca <short|long>
```

Then, for each `glyph` line, in input order:

```
glyph <id> <offset> <length>
```

- `offset` is where the glyph's record starts, in bytes from the start of the **file**.
- `length` is the record's size in bytes. A length of 0 means the glyph has no outline (the
  space character, for example).

The `glyph` lines match assignment 07's input lines: put the `font` line in front of them,
and your assignment 07 program can decode the glyphs.

### The tables you need

All numbers are **big-endian**.

**`maxp`**: you need one field.

| Offset in `maxp` | Field | Type | Meaning |
|---|---|---|---|
| 0 | `version` | 4 bytes | Skip it |
| 4 | `numGlyphs` | uint16 | How many glyphs the font has. Glyph ids go from 0 to `numGlyphs` − 1. |

**`head`**: you need one field, 50 bytes in.

| Offset in `head` | Field | Type | Meaning |
|---|---|---|---|
| 0 to 49 | version, revision, checksum adjustment, magic number, flags, `unitsPerEm`, dates, bounding box, ... | | Not needed here |
| 50 | `indexToLocFormat` | int16 | 0: `loca` holds short offsets. 1: `loca` holds long offsets. |
| 52 | `glyphDataFormat` | int16 | 0 (not needed) |

**`loca`**: `numGlyphs` + 1 entries, one after another from the start of the table.

| `indexToLocFormat` | Entry type | The offset it stands for |
|---|---|---|
| 0 (short) | uint16 | the entry × 2 |
| 1 (long) | uint32 | the entry itself |

Short entries store half the offset, so a font whose `glyf` table is under 128 KB can use 2
bytes per entry. (That only works if every offset is even, which is why short-format fonts
pad their glyph records to even lengths.)

The offsets count from the start of the **`glyf` table**. Glyph i's record runs from
offset(i) up to, but not including, offset(i + 1):

- absolute offset = `glyf` table offset + offset(i)
- length = offset(i + 1) − offset(i)

`loca` has one more entry than there are glyphs: entry `numGlyphs` marks where the last glyph
ends. A glyph with no outline has length 0 and shares its offset with the next glyph. The
length may include a few bytes of padding at the end of the record, and assignment 07 ignores
those bytes.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** `numGlyphs` is the uint16 at `maxp` + 4.
- **R2** The format is the int16 `indexToLocFormat` at `head` + 50: 0 is `short`, 1 is
  `long`.
- **R3** In the short format, each entry is a uint16 holding half the offset, and your program
  multiplies it by 2. The results can be larger than 65535, so do the multiplication in 32
  bits: a uint16 doubled in 16-bit arithmetic overflows.
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

`maxp` + 4 (byte 268) holds `00 08`: 8 glyphs. `head` + 50 (byte 222) holds `00 00`: short
format, and `loca` has 9 uint16 entries:

```
00 00  00 0d  00 21  00 2d  00 3b  00 4f  00 5c  00 6a  00 76
  0      13     33     45     59     79     92    106    118     entries
  0      26     66     90    118    158    184    212    236     offsets (x 2)
```

Glyph 1 starts at 484 + 26 = 510 and is 66 − 26 = 40 bytes long. The last entry, 236, is
the size of the whole `glyf` table.

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

JetBrains Mono uses long offsets. Entry 17 (at byte 64980 + 4 × 17) is `00 00 07 74` = 1908,
and entry 18 is 1964, so glyph 17, the hyphen, starts at 113484 + 1908 = 115392 and is
1964 − 1908 = 56 bytes long. Entries 4 and 5 are both 100, so glyph 4 (the space) is empty.
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

The 5 entries are 0, 13, 25, 45, 45, so the offsets are 0, 26, 50, 90, 90. Glyph 3, the
last one, runs from 90 to 90, so it is empty. This font's `glyf` table is 94 bytes long, 4
more than the last entry, so taking the end of `glyf` as the end of the last glyph gives the
wrong length here (4). Use `loca`'s extra entry for the end of the last glyph.

## Constraints

- `numGlyphs` is at most 17,936 in the tests. Every `glyph` id is below it.
- `indexToLocFormat` is 0 or 1 in every test, and each `loca` entry is at least as large as
  the one before it.
- Each input has at most 30 `glyph` lines.
- Each case has a 10-second limit. A correct solution finishes in milliseconds.
- There are 18 tests: both real fonts (long format, empty glyphs, first and last glyphs,
  random glyphs) and small fonts built with fontTools (short and long formats, a short
  `loca` whose offsets pass 65535, empty glyphs at the start, middle and end, and spare
  bytes after the last glyph).

## Source material

- Apple, *TrueType Reference Manual*, ['loca' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6loca.html),
  ['head' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6head.html),
  ['maxp' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6maxp.html)
- Microsoft, *OpenType specification*, [loca: Index to Location](https://learn.microsoft.com/en-us/typography/opentype/spec/loca),
  [head: Font Header Table](https://learn.microsoft.com/en-us/typography/opentype/spec/head),
  [maxp: Maximum Profile](https://learn.microsoft.com/en-us/typography/opentype/spec/maxp)
- The blog: [loca table](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=loca%20table)

## Hints

<details><summary>Hint 1: where to start</summary>

Read the two numbers that tell you how to read `loca`: how many glyphs there are (`maxp`)
and how big each entry is (`head`). Then read the whole `loca` table into a list of offsets,
and get each length by subtracting neighbouring offsets.
</details>

<details><summary>Hint 2: the approach</summary>

Read `numGlyphs` + 1 entries into a vector, doubling them in the short format. Then, for
each glyph i from 0 to `numGlyphs` − 1, its location is (`glyf` offset + entry[i],
entry[i + 1] − entry[i]).
</details>

<details><summary>Hint 3: the traps</summary>

- Read `numGlyphs` + 1 entries, not `numGlyphs`. Without the extra one you can't tell how
  long the last glyph is. The `glyf` table's length can't stand in for it: a font may have
  spare bytes after the last glyph.
- In the short format, multiply by 2. Do it in a 32-bit variable: twice a uint16 can be more
  than 65535.
- `indexToLocFormat` is at `head` + 50. The field right after it (+52) is `glyphDataFormat`,
  whose value is 0, so reading it by mistake makes every font look short.
- `loca` offsets count from the start of `glyf`, not from the start of the file.
- An empty glyph has the same offset as the next glyph. Write both lines with that offset.
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

A failing test looks like this:

```
  R3  Short format: each uint16 entry is the offset / 2 ....................    0 / 2   FAILED
      x 04-R3-short-x2  8 glyphs in a short loca: every offset is twice the stored value
          glyph[0]: expected (id=0, offset=484, length=26), got (id=0, offset=484, length=13) - differs in length  (in `glyphs 8 loca short`)
          likely cause: R5 - Length = next entry - this one (x2 if short); numGlyphs + 1 entries
          expected values from: fontTools 4.67.0 maxp, head, loca and the glyf offset, cross-checked against a struct parse of loca
          reproduce: build/solutions/assignment_04.exe build/cases/04/04-R3-short-x2.in build/cases/04/04-R3-short-x2.out
```

## After you pass: compare with the author's code

[The blog's loca reader](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=GlyphCode%E2%86%92GlyphOffset%20mapping),
`loadGlyphOffsetsMap`, reads `numGlyphs` from `maxp` and `indexToLocFormat` from `head`, then
reads one `loca` entry per glyph (doubling short ones) and stores `glyf` offset + entry in a
map from glyph id to file offset, `glyphCodeToOffset`. It doesn't store lengths. Instead, when
glyph i − 1 has the same offset as glyph i, it marks glyph i − 1 as empty, and later steps
skip empty glyphs.

**Something to look for:** the snippet reads `numGlyphs` entries, where the spec has
`numGlyphs` + 1. With no entry after the last glyph to compare against, the loader can't mark
the last glyph as empty, and later steps would read its record even when it has no outline.
In JetBrains Mono the last glyph (12124) is empty. The spec's extra entry covers this case,
and R5 tests it.
