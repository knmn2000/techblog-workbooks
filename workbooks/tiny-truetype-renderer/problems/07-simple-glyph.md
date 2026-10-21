# 07 · Decode simple glyphs

**Difficulty:** Medium · **Assignment** 7 of 18 · **Check:** `.\check 07`

**Tags**
- *Language:* bit flags and masks · signed vs unsigned integers (`int16`, `uint8`) · running sums · binary file I/O (`seekg`, `get`)
- *Library:* `std::ifstream` in binary mode · `std::vector`
- *Concepts:* glyph outlines · contours · on-curve and off-curve points · delta encoding · run-length encoding · big-endian byte order

## Read in the blog first

You can pass using this page alone. For the background, read the blog's
**"Glyph Parsing & Outline Rendering"** section, from
[Parsing glyf tables](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Parsing%20glyf%20tables)
through the list of flag rules under **Simple glyph**. Stop at the paragraph that starts
"Implementation.", before the author's code.

## Source material

- Apple, *TrueType Reference Manual*, ['glyf' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6glyf.html)
- Microsoft, *OpenType specification*, [glyf: Glyph Data](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf). Its simple-glyph flags table is the clearest.
- Apple, [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html), on on-curve and off-curve points
- The blog: [Simple glyph](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Simple%20glyph)

## Where this fits

Your `Cmap` (assignment 03) and `Loca` (assignment 04) take you from a character to a byte
offset inside the font file. Here you decode the record at that offset into the points of the
glyph's outline. Assignment 08 draws those points with straight lines and assignment 11 with
curves. Assignment 09 handles **compound glyphs**, glyphs built out of other glyphs; in this
assignment you only recognise them.

## The problem

Write a program that decodes glyph records in font files and prints each glyph's outline: where
its contours end and where every point is.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains two kinds of lines:

| Line | Meaning |
|---|---|
| `font <path>` | The file that the following `glyph` lines refer to. The path is relative to the workbook folder and contains no spaces. This line may appear more than once. |
| `glyph <id> <offset> <length>` | A glyph record `length` bytes long, starting at byte `offset` of the current file. `id` is a non-negative whole number used as a label: print it back unchanged. |

Your `Loca` from assignment 04 works out these offsets and lengths, so you need no other table
here.

- You only need `length` to tell whether there is a record at all (0 means none). Records are
  well-formed, so you don't have to bounds-check against it.
- Some test files are real fonts. Others are hand-made files that contain one glyph record at
  offset 0.

### Output

For each `glyph` line, in input order, write one of three things:

- **Length 0** (the glyph has no outline, e.g. the space character): `glyph <id> empty`
- **`numberOfContours` < 0** (a compound glyph): `glyph <id> compound`, without decoding the
  rest of the record.
- **Otherwise** (a simple glyph), three lines:

```
glyph <id> contours <numberOfContours> bbox <xMin> <yMin> <xMax> <yMax>
ends <endPtsOfContours[0]> <endPtsOfContours[1]> ...
points <x0> <y0> <on|off> <x1> <y1> <on|off> ...
```

- `ends` lists the `endPtsOfContours` values in the order they appear in the file.
- `points` gives every point in order as **absolute** coordinates in font units. Each is
  followed by `on` if it is an **on-curve point** (the outline passes through it) or `off` if
  it is an **off-curve point**, also called a control point (it bends a curve without lying on
  it).
- If `numberOfContours` is 0 (no test has one), print the header line, then `ends` and
  `points` with nothing after them.
- Separate words with spaces; the checker ignores extra whitespace.

<figure class="split-figure">
<svg viewBox="-30 -30 660 800" role="img" aria-label="The outline of A in JetBrains Mono Bold, drawn from its 17 decoded points"><rect x="35" y="0" width="530" height="730" fill="none" stroke="var(--rule)" stroke-width="4" stroke-dasharray="14 10"/><line x1="-30" y1="730" x2="630" y2="730" stroke="var(--muted)" stroke-width="3"/><polygon points="35,730 219,0 380,0 565,730 437,730 397,553 203,553 163,730" fill="none" stroke="var(--ink)" stroke-width="5" stroke-linejoin="round"/><polygon points="226,451 374,451 330,255 319,206 303,127 300,109 297,127 281,206 270,254" fill="none" stroke="var(--ink)" stroke-width="5" stroke-linejoin="round"/><g fill="var(--fig-a)"><circle cx="35" cy="730" r="13"/><circle cx="219" cy="0" r="13"/><circle cx="380" cy="0" r="13"/><circle cx="565" cy="730" r="13"/><circle cx="437" cy="730" r="13"/><circle cx="397" cy="553" r="13"/><circle cx="203" cy="553" r="13"/><circle cx="163" cy="730" r="13"/><circle cx="226" cy="451" r="13"/><circle cx="374" cy="451" r="13"/><circle cx="330" cy="255" r="13"/><circle cx="300" cy="109" r="13"/><circle cx="270" cy="254" r="13"/></g><g fill="var(--surface)" stroke="var(--fig-b)" stroke-width="6"><circle cx="319" cy="206" r="11"/><circle cx="303" cy="127" r="11"/><circle cx="297" cy="127" r="11"/><circle cx="281" cy="206" r="11"/></g></svg>
<figcaption><p>What the output describes: <code>A</code> is glyph 37, with two contours (<code>ends 7 16</code>) and 17 points, joined here with straight lines as assignment 08 will draw them. The four off-curve points at the top of the inner triangle are what assignment 11 turns into a curve.</p><div class="legend"><span><span class="dot a"></span>on-curve point</span><span><span class="dot b"></span>off-curve (control) point</span><span>dashed: bbox 35 0 565 730</span></div></figcaption>
</figure>

### The glyph record you are decoding

All numbers are **big-endian**: the most significant byte comes first.

**Header**, 10 bytes:

| Field | Type | Meaning |
|---|---|---|
| `numberOfContours` | int16 | ≥ 0: a simple glyph (this assignment). < 0: a compound glyph |
| `xMin`, `yMin`, `xMax`, `yMax` | int16 each | Bounding box in font units |

**Simple-glyph description**, starting at byte 10 of the record:

| Field | Type | Meaning |
|---|---|---|
| `endPtsOfContours[numberOfContours]` | uint16 each | Index of the last point of each contour, in increasing order |
| `instructionLength` | uint16 | Number of hinting-instruction bytes that follow |
| `instructions[instructionLength]` | uint8 each | Hinting bytecode, which you skip |
| `flags[]` | uint8 each | One flag per point, compressed (see below) |
| `xCoordinates[]` | 0, 1 or 2 bytes per point | Every point's x, delta-encoded |
| `yCoordinates[]` | 0, 1 or 2 bytes per point | Every point's y, delta-encoded |

The record has no point count: work it out as `endPtsOfContours[last] + 1`. A record may end
with up to 3 padding bytes, which you can ignore.

**Flag bits:**

| Bit | Mask | Name | Meaning |
|---|---|---|---|
| 0 | `0x01` | ON_CURVE_POINT | The point is on the curve; otherwise it is a control point |
| 1 | `0x02` | X_SHORT_VECTOR | The x delta is 1 byte (unsigned) |
| 2 | `0x04` | Y_SHORT_VECTOR | The y delta is 1 byte (unsigned) |
| 3 | `0x08` | REPEAT_FLAG | The next byte says how many **more** points use this same flag |
| 4 | `0x10` | X_IS_SAME_OR_POSITIVE_X_SHORT_VECTOR | Meaning depends on bit 1 (table below) |
| 5 | `0x20` | Y_IS_SAME_OR_POSITIVE_Y_SHORT_VECTOR | Meaning depends on bit 2 (table below) |
| 6, 7 | | | Ignore |

**Reading one coordinate.** The table shows x; y works the same way with bits 2 and 5.

| Bit 1 (short) | Bit 4 | Bytes read | Delta |
|---|---|---|---|
| 1 | 1 | 1, uint8 | +value |
| 1 | 0 | 1, uint8 | −value |
| 0 | 1 | none | 0, meaning "same as the previous point" |
| 0 | 0 | 2, int16 | value (already signed) |

A **delta** is a change in position: the file stores each point's delta instead of its
coordinate. The first point's delta is relative to (0, 0), and each later point's delta is
relative to the point before it.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** One output record per `glyph` line, in input order, in the format above.
- **R2** A record of length 0 → `glyph <id> empty`.
- **R3** `numberOfContours` < 0 → `glyph <id> compound`, with nothing decoded.
- **R4** Your program prints the header's contour count and bounding box as the font stores
  them.
- **R5** `ends` lists `endPtsOfContours` in file order. The point count is the last value + 1.
- **R6** Your program skips the hinting instructions, however long they are.
- **R7** Your program expands REPEAT so that every point gets its own flag, and takes each
  point's on/off from that flag, **including points created by a repeat**.
- **R8** Your program adds up the 1-byte, 2-byte and "same" deltas into absolute coordinates.
  All x values come before all y values, and the running total carries on across contour
  boundaries without going back to 0.

## Examples

### Example 1: the hyphen in JetBrains Mono Bold (test `07-R8-hyphen`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf
         glyph 17 115392 56
```

These are the 56 bytes at offset 115392:

```
00 01                        numberOfContours = 1
00 8c 01 10 01 cc 01 84      bbox = (140, 272) - (460, 388)
00 03                        endPtsOfContours = [3], so there are 4 points
00 1e                        instructionLength = 30
.. 30 bytes ..               instructions: skip them
13 35 21 15                  flags, one per point (no REPEAT)
8c 01 40                     x data
01 10 74 74                  y data
00                           padding
```

| Point | Flag | x rule | x bytes | x | y rule | y bytes | y | on/off |
|---|---|---|---|---|---|---|---|---|
| 0 | `0x13` | short, + | `8c` | 0 + 140 = **140** | int16 | `01 10` | 0 + 272 = **272** | on |
| 1 | `0x35` | same | none | **140** | short, + | `74` | 272 + 116 = **388** | on |
| 2 | `0x21` | int16 | `01 40` | 140 + 320 = **460** | same | none | **388** | on |
| 3 | `0x15` | same | none | **460** | short, − | `74` | 388 − 116 = **272** | on |

```
output:  glyph 17 contours 1 bbox 140 272 460 388
         ends 3
         points 140 272 on 140 388 on 460 388 on 460 272 on
```

### Example 2: a repeated flag (test `07-R7-repeat`)

```
input:   font tests/07/data/07-R7-repeat.bin
         glyph 0 0 24
```

The 24 bytes:

```
00 01                        numberOfContours = 1
00 0a 00 00 00 28 00 32      bbox = (10, 0) - (40, 50)
00 05                        endPtsOfContours = [5], so 6 points
00 00                        instructionLength = 0
3b 03 35 22                  flags: 0x3b with REPEAT, count 3 (points 0-3); 0x35 (point 4); 0x22 (point 5)
0a 0a 0a 0a 1e               x data: +10 +10 +10 +10 (0x3b: short, +), none (0x35: same), -30 (0x22: short, -)
32                           y data: none for points 0-3 (same), +50 (0x35: short, +), none (0x22: same)
```

Point 5 is `off` because bit 0 of `0x22` is clear.

```
output:  glyph 0 contours 1 bbox 10 0 40 50
         ends 5
         points 10 0 on 20 0 on 30 0 on 40 0 on 40 50 on 10 50 off
```

### Example 3: one input with several glyphs (test `07-R1-four-glyphs`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf
         glyph 17 115392 56
         glyph 4 113584 0
         glyph 77 122844 24
         glyph 37 118060 112

output:  glyph 17 contours 1 bbox 140 272 460 388
         ends 3
         points 140 272 on 140 388 on 460 388 on 460 272 on
         glyph 4 empty
         glyph 77 compound
         glyph 37 contours 2 bbox 35 0 565 730
         ends 7 16
         points 35 0 on 219 730 on ... (17 points in total)
```

## Constraints

- The test records are well-formed: `endPtsOfContours` increases, no REPEAT run goes past the
  last point, and the flags and coordinates fit inside the record.
- The largest glyph in the tests has a few hundred points. Every coordinate fits in an int16,
  and so does every running total.
- Each case has a 10-second limit. A correct solution takes milliseconds.
- There are 151 tests: the examples above, hand-made records for each rule, every simple ASCII
  glyph in the font, and 40 other glyphs (Nerd Font icons with hundreds of points, glyphs that
  repeat on-curve flags, and random picks).

## Hints

<details><summary>Hint 1: where to start</summary>

Read the fields in the order the record lays them out: header, contour ends, instructions,
flags, every x, every y. You can't read any coordinate until you have expanded all the flags,
because the flags decide how many bytes each coordinate takes.
</details>

<details><summary>Hint 2: the approach</summary>

Work in two passes. First expand the compressed flags into a list with one flag for each
point. Then walk that list twice, once for x and once for y. Each time, keep a running total
and read 0, 1 or 2 bytes per point depending on two bits. Write the coordinate reader once
and give it the bit numbers for the axis (1 and 4 for x, 2 and 5 for y).
</details>

<details><summary>Hint 3: the traps</summary>

- A REPEAT count of 3 means 3 **more** copies, so that one flag covers 4 points.
- A repeated point gets every bit of the flag, including ON_CURVE. If you keep the on-curve
  points in a list of their own, add the repeated points to it too.
- "Same as previous" (short bit clear, bit 4/5 set) reads **no** bytes.
- A short delta is an unsigned size from 0 to 255, and its sign comes from bit 4/5. A long
  delta is already a signed int16.
- The running total doesn't reset at a contour boundary.
- Compound glyphs: check `numberOfContours` before reading anything past the header.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
if length == 0: return EMPTY
seek(offset)
numberOfContours = readInt16()
if numberOfContours < 0: return COMPOUND
bbox = readInt16() x 4
ends = readUint16() x numberOfContours
n = ends[last] + 1
skip(readUint16())                       # instructions
flags = []
while len(flags) < n:
    f = readUint8()
    copies = 1 + readUint8() if f & 0x08 else 1
    append f to flags, copies times
xs = readAxis(flags, shortBit=0x02, sameOrPositiveBit=0x10)
ys = readAxis(flags, shortBit=0x04, sameOrPositiveBit=0x20)
point i = (xs[i], ys[i], flags[i] & 0x01)

readAxis(flags, shortBit, sameOrPositiveBit):
    value = 0
    for f in flags:
        if f & shortBit:                   value += readUint8() if f & sameOrPositiveBit else -readUint8()
        elif not (f & sameOrPositiveBit):  value += readInt16()
        output value
```
</details>

## Checking your solution

```
.\check 07                         run every test
.\check 07 -Case 07-R7-repeat      one test, showing its full input, expected output and your output
.\check 07 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 07 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  Header: number of contours and bounding box ...............    0 / 2   FAILED
      x 07-R4-B  'B': three contours
          points[26]: expected (x=199, y=626, curve=on), got (x=199, y=626, curve=off) - differs in curve
          likely cause: R7 - REPEAT expanded; on/off for every point, repeats included
          expected values from: fontTools 4.67.0
          reproduce: build/solutions/assignment_07.exe build/cases/07/07-R4-B.in build/cases/07/07-R4-B.out
```

## After you pass: compare with the author's code

[The blog's simple-glyph parser](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Parser%20for%20simple%20glyphs)
splits the work into `readGlyphHeader` (the header), `getGlyphComponent` (contour ends,
instructions and flags) and `getGlyphCoordinates`, which it calls once for x and once for y.
It stores the contour ends and on-curve indices in `unordered_set`s and multiplies every
point by an affine matrix. The matrix is the identity for simple glyphs; it matters for
compound glyphs in assignment 09.

**Something to look for:** in the snippet as published, the flag loop records ON_CURVE only
for the first point of a repeated run. In JetBrains Mono Bold, 42 of the 90 simple ASCII
glyphs repeat an on-curve flag, which is why R7 has its own tests.
