# 05 · Read the horizontal metrics

**Difficulty:** Easy · **Assignment** 5 of 18 · **Check:** `.\check 05`

**Tags**
- *Language:* [signed vs unsigned integers](#primer/integer-types) (`int16_t`, `uint16_t`) · [structs](#primer/struct-class) · [`std::vector`](#primer/vector)
- *Library:* [`std::ifstream`](#primer/fstream) in binary mode (`seekg`)
- *Concepts:* [font units](#primer/font-units) · [ascent and descent](#primer/hhea) · [advance width](#primer/hmtx) · [left side bearing](#primer/hmtx) · the [`hhea`](#primer/hhea), [`hmtx`](#primer/hmtx) and [`maxp`](#primer/maxp) tables · [big-endian byte order](#primer/big-endian)

## Read in the blog first

You can pass using this page alone. For the background, read the blog's
[hhea, hmtx tables](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=hhea%2C%20hmtx%20tables)
section through the paragraph that starts "The hmtx table contains information for". The
author's code follows that paragraph.

## What you need

- [Font units and the em](#primer/font-units): the ascent, descent, advances and side
  bearings the program writes are in font units, and both real fonts have 1000 of them per em.
- [The `hhea` table](#primer/hhea): `src/font/Metrics.cpp` reads `ascent` and `descent` at
  `hhea` + 4 and + 6, and `numberOfHMetrics` at + 34.
- [The `hmtx` table](#primer/hmtx): `Metrics.cpp` reads `numberOfHMetrics` full records, then
  one lsb for each remaining glyph, which takes the last record's advance.
- [Integer types](#primer/integer-types): `ascent`, `descent` and each lsb are signed int16
  values and `advanceWidth` an unsigned uint16, and `GlyphMetric` holds both kinds in an `int`.

## Source material

- Apple, *TrueType Reference Manual*, ['hhea' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6hhea.html)
  and ['hmtx' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6hmtx.html)
- Microsoft, *OpenType specification*, [hhea: Horizontal Header Table](https://learn.microsoft.com/en-us/typography/opentype/spec/hhea)
  and [hmtx: Horizontal Metrics Table](https://learn.microsoft.com/en-us/typography/opentype/spec/hmtx)
- Apple, [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html),
  for pictures of advance width and left side bearing
- The blog: [hhea, hmtx tables](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=hhea%2C%20hmtx%20tables)

## Where this fits

Outlines give the shape of each glyph. To set a line of text, a renderer also needs the
height of the line and the distance from one glyph to the next. Assignment 18 moves the pen
by each glyph's advance width, and its `main.cpp` sizes the text from the ascent and descent
you read here.

## The problem

Write a program that reads a font's ascent and descent, and the advance width and left side
bearing of requested glyphs.

Text sits on a horizontal line, the baseline. A pen moves along it: the renderer draws
each glyph at the pen's position, then moves the pen right. The numbers your program reads
are:

- ascent and descent: how much room a line needs above and below the baseline.
- advance width: how far to move the pen after drawing a glyph.
- left side bearing (lsb): where the glyph's outline starts, measured from the pen.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains these lines, in this order:

| Line | Meaning |
|---|---|
| `font <path>` | The font file. The path is relative to the workbook folder and contains no spaces. |
| `table "<tag>" <checkSum> <offset> <length>` | Three lines, for `hhea`, `hmtx` and `maxp`: their records from the table directory, written as assignment 02 writes them. `offset` is where the table starts in the file. |
| `font-metrics` | Asks for the font's ascent and descent. |
| `glyph <id>` | Asks for this glyph's metrics. `id` is from 0 to `numGlyphs` − 1. |

Your program can parse the `table` lines into the table records your `FontParser` from
assignment 02 declares, and read the font with your `ByteReader` from assignment 01.

### Output

One line per question, in input order:

- `font-metrics` → `ascent <ascent> descent <descent>`
- `glyph <id>` → `glyph <id> advance <advanceWidth> lsb <leftSideBearing>`

All values are whole numbers in font units, the grid the type designer drew the glyphs on.
In both real fonts, 1000 font units make one em, the font's nominal size.

The Boilerplate writes `glyph <id> missing` if the list your function returns has no entry for
a glyph. Every glyph has metrics, so a `missing` line fails the test.

### The tables you need

All numbers are big-endian.

`hhea` (the horizontal header) is 36 bytes long, and you need three of its fields:

| Offset in `hhea` | Field | Type | Meaning |
|---|---|---|---|
| 0 | `version` | 4 bytes | Skip it |
| 4 | `ascent` | int16 | Distance from the baseline up to the top of the line |
| 6 | `descent` | int16 | Distance from the baseline down to the bottom of the line, negative in most fonts |
| 8 to 33 | `lineGap`, `advanceWidthMax`, ..., `metricDataFormat` | | Not needed here |
| 34 | `numberOfHMetrics` | uint16 | How many full records `hmtx` starts with |

From `maxp` you need `numGlyphs`, the uint16 at `maxp` + 4.

`hmtx` (horizontal metrics) has two parts, one after the other:

| Part | Count | Each entry |
|---|---|---|
| `hMetrics` | `numberOfHMetrics` | a `longHorMetric`, 4 bytes: `advanceWidth` (uint16), then `lsb` (int16) |
| `leftSideBearings` | `numGlyphs` − `numberOfHMetrics` | `lsb` only (int16), 2 bytes |

The `leftSideBearings` array starts at `hmtx` + 4 × `numberOfHMetrics`.

### A glyph's metrics

For glyph id i:

- If i < `numberOfHMetrics`: advance = `hMetrics[i].advanceWidth` and
  lsb = `hMetrics[i].lsb`.
- Otherwise: advance = the advance of the last `longHorMetric`,
  `hMetrics[numberOfHMetrics − 1].advanceWidth`, and lsb = `leftSideBearings[i − numberOfHMetrics]`.

The second rule saves space. If the last glyphs of a font all have the same advance (common in
monospaced fonts and in runs of CJK glyphs), the font stores that advance once and keeps a
2-byte side bearing for each of those glyphs.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** `ascent` and `descent` are the int16 values at `hhea` + 4 and `hhea` + 6. They can
  be negative.
- **R2** A glyph whose id is below `numberOfHMetrics` has its own `longHorMetric`: an
  unsigned advance and a signed lsb.
- **R3** A glyph whose id is `numberOfHMetrics` or more takes the last `longHorMetric`'s
  advance, and its lsb is entry (id − `numberOfHMetrics`) of the int16 array after the
  `longHorMetric` records.

## Examples

### Example 1: a real font's ascent and descent (test `05-R1-jetbrains`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf
         table "hhea" 34418196 356 36
         table "hmtx" 1631122185 520 48500
         table "maxp" 946608241 392 32
         font-metrics

output:  ascent 1020 descent -300
```

The 4 bytes at `hhea` + 4 (byte 360) are `03 fc fe d4`. `03 fc` is 1020. `fe d4` is 65236
as an unsigned number, and 65236 − 65536 = −300 as an int16.

### Example 2: glyphs past `numberOfHMetrics` (test `05-R3-negative-tail`)

```
input:   font tests/05/data/05-R3-negative-tail.ttf
         table "hhea" 60424786 228 36
         table "hmtx" 92143626 392 18
         table "maxp" 524293 264 32
         font-metrics
         glyph 0
         glyph 1
         glyph 2
         glyph 3
         glyph 4
         glyph 5
```

`hhea` + 4 holds `03 20 ff 38` (ascent 800, descent −200), and `hhea` + 34 holds `00 03`:
3 full records. `maxp` + 4 holds 6, the number of glyphs. The 18 bytes of `hmtx`:

```
01 f4 00 32      glyph 0: advance 500, lsb 50
02 80 00 14      glyph 1: advance 640, lsb 20
01 f4 ff c4      glyph 2: advance 500, lsb -60     (the last longHorMetric)
ff fb            glyph 3: lsb -5    advance 500, from glyph 2
00 00            glyph 4: lsb 0     advance 500
ff 1a            glyph 5: lsb -230  advance 500
```

```
output:  ascent 800 descent -200
         glyph 0 advance 500 lsb 50
         glyph 1 advance 640 lsb 20
         glyph 2 advance 500 lsb -60
         glyph 3 advance 500 lsb -5
         glyph 4 advance 500 lsb 0
         glyph 5 advance 500 lsb -230
```

### Example 3: a monospaced font (test `05-R2-jetbrains`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf
         table "hhea" 34418196 356 36
         table "hmtx" 1631122185 520 48500
         table "maxp" 946608241 392 32
         glyph 0
         glyph 1
         glyph 2
         glyph 3
         glyph 4
         glyph 5
         glyph 17
         glyph 37
         glyph 69
         glyph 77

output:  glyph 0 advance 600 lsb 90
         glyph 1 advance 0 lsb 0
         glyph 2 advance 333 lsb 0
         glyph 3 advance 600 lsb 0
         glyph 4 advance 600 lsb 0
         glyph 5 advance 600 lsb 216
         glyph 17 advance 600 lsb 140
         glyph 37 advance 600 lsb 35
         glyph 69 advance 600 lsb 58
         glyph 77 advance 600 lsb 76
```

JetBrains Mono stores a full record for all 12125 glyphs (`numberOfHMetrics` = `numGlyphs`),
so every glyph here follows the first rule. Most glyphs are 600 units wide, and glyph 1 has an
advance of 0.

## Constraints

- `numGlyphs` is at most 17,936 in the tests, and 1 ≤ `numberOfHMetrics` ≤ `numGlyphs`.
- Every `glyph` id is below `numGlyphs`.
- Each input has at most 31 questions.
- Each case has a 10-second limit. A correct solution finishes in milliseconds.
- There are 14 tests: both real fonts (ascent and descent, Latin, kana and kanji glyphs,
  random glyphs) and small fonts built with fontTools (the int16 limits, negative side
  bearings, trailing glyphs that share an advance, a font where `numberOfHMetrics` is 1, and
  random fonts).

## Hints

<details><summary>Hint 1: where to start</summary>

Read the two int16 values at `hhea` + 4, then `numberOfHMetrics` at `hhea` + 34 and
`numGlyphs` at `maxp` + 4. Those two counts give the layout of `hmtx`.
</details>

<details><summary>Hint 2: the approach</summary>

Walk through `hmtx` once from its start. First read `numberOfHMetrics` pairs of (uint16,
int16) and append each one to the result. Keep the last advance. Then read
`numGlyphs` − `numberOfHMetrics` more int16 values, appending (last advance, value) for
each. The result now has one entry per glyph id.
</details>

<details><summary>Hint 3: the traps</summary>

- `ascent`, `descent` and every `lsb` are signed. `advanceWidth` is unsigned.
- Glyphs past `numberOfHMetrics` still have metrics. Their advance is the last
  `longHorMetric`'s advance, but their lsb is their own, from the array that follows.
  Don't copy the last record's lsb.
- The lsb-only array starts right after the last 4-byte record, and its entries are 2 bytes
  each.
- `numberOfHMetrics` is at `hhea` + 34. The field before it (+32) is `metricDataFormat`,
  whose value is 0.
- Both real fonts store a full record for every glyph, so only the small test fonts check the
  second rule.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
seek(hhea + 4);  ascent = readInt16(); descent = readInt16()
seek(hhea + 34); n = readUint16()          # numberOfHMetrics
seek(maxp + 4);  numGlyphs = readUint16()
seek(hmtx)
glyphs = []
repeat n times:
    advance = readUint16(); lsb = readInt16()
    glyphs.append((advance, lsb))
last = glyphs[n - 1].advance
repeat numGlyphs - n times:
    glyphs.append((last, readInt16()))
```
</details>

## Checking your solution

```
.\check 05                         run every test
.\check 05 -Case 05-R3-negative-tail   one test, showing its full input, expected output and your output
.\check 05 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 05 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R3  Later glyphs: the last advance, lsb from the array after .............    0 / 3   FAILED
      x 05-R3-shared-advance  the last 3 glyphs share advance 600, so only 4 long metrics are stored
          line 5: expected `glyph 4 advance 600 lsb 5`, got `glyph 4 missing`
          likely cause: R3 - Later glyphs: the last advance, lsb from the array after
          expected values from: fontTools 4.67.0 hhea and hmtx, cross-checked against a struct parse of hmtx
          reproduce: build/solutions/assignment_05.exe build/cases/05/05-R3-shared-advance.in build/cases/05/05-R3-shared-advance.out
```

## After you pass: compare with the author's code

[The blog's metrics parser](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Parser%20for%20glyph%20metrics)
has two parts. `getFontMetric` returns a `FontMetric` holding the ascent and descent from
`hhea` + 4 and `hhea` + 6. `loadGlyphMetricsMap` reads `numberOfHMetrics` from `hhea` + 34,
then reads that many (advance width, left side bearing) pairs from `hmtx` into a map keyed by
glyph id, `glyphMetric`, whose values are `Metric` structs (`advanceWidth`,
`leftSideBearing`). In your project, `loadHorizontalMetrics` returns both parts at once in a
`HorizontalMetrics`, with one `GlyphMetric` per glyph id. The post calls the count field
"NumberOfMetrics" and the code names it `numOfMetrics`; the OpenType spec calls it
`numberOfHMetrics`, and Apple's manual `numOfLongHorMetrics`. The author's repository has the
same code.

The snippet stops after the `longHorMetric` records, so glyphs at
or past `numberOfHMetrics` get no entry. A later step that asks for one with
`glyphMetric[glyphCode]` gets a zeroed `Metric` from `operator[]`: advance 0 and lsb 0, so the
renderer draws the next glyph on top of it. The post skips the `leftSideBearing` array on
purpose, and its text says a monospaced font may store one record "or none at all"; the spec
requires at least one, since the later glyphs take their advance from the last one.
JetBrains Mono and Noto Sans JP store a full record
for every glyph, so the gap doesn't show with them. Many fonts, including those compiled by
fontTools, drop the trailing records when the last glyphs share an advance width, and a
monospaced font can end up with `numberOfHMetrics` = 1. R3 tests the spec's rule: the last
advance and the glyph's own lsb.
