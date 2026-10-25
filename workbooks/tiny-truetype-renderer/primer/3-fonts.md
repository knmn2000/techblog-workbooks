# Fonts and TrueType

How a TrueType font file is laid out, and the terms the problem pages use for its parts.

## Big-endian byte order
<!--
id: big-endian
also: byte order; endianness; network byte order; most significant byte first
-->
A number wider than one byte is stored as several bytes in a row, and a format has to say which
comes first. Big-endian puts the most significant byte first, the way you write digits: the 16-bit
number 0x1234 (4660) is stored as the byte 0x12, then 0x34. Little-endian stores the same number
as 0x34, then 0x12.

TrueType fonts are big-endian throughout. Most computers you'd run the workbook on (x86 and ARM)
are little-endian, so copying two bytes from the file straight into a `uint16_t` gives the wrong
number. Build the number from its bytes instead, with [shifts and OR](#primer/bit-operations),
which works on any machine:

```cpp
uint16_t value = (uint16_t(b0) << 8) | b1;   // b0 is the byte that came first in the file
```

Assignment 01 writes these readers for 8, 16 and 32 bits, and every later assignment reads the
font through them.

Learn more:
- [Endianness](https://en.wikipedia.org/wiki/Endianness) on Wikipedia, with diagrams of both orders
- [Data types](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#data-types) in the
  OpenType specification, which says all its numbers are big-endian

## TrueType and OpenType fonts
<!--
id: truetype
also: font file; .ttf; .otf; OpenType; outline font; CFF; scaler type; sfntVersion; OTTO
-->
A typeface is the design of a set of characters, such as JetBrains Mono or Noto Sans JP. A font
is one style of a typeface, such as JetBrains Mono Bold, in a file a program can use. The file
stores the shapes of the characters as outlines: straight lines and curves described by points,
which a program can scale to any size and then fill with pixels. Next to the outlines it keeps
tables that say which shape belongs to which character and how far apart to space them.

TrueType is the outline format Apple released in 1991. OpenType, from Microsoft and Adobe, kept
TrueType's file layout and its tables and added more. An OpenType font stores its outlines in one
of two ways: in a `glyf` table, TrueType's format, built from quadratic curves, or in a `CFF `
table, built from cubic curves. CFF (Compact Font Format) is Adobe's format for the outlines of
its PostScript fonts; PostScript is the language for describing printed pages that Adobe
released in 1984. The first four bytes of the file tell the two apart: `00 01 00 00` (or `true`
in some Apple fonts) for TrueType outlines, and `OTTO` for CFF. The file extension is a weaker
clue. Fonts with TrueType outlines usually end in .ttf, but the specification allows .otf and
.ttf for both kinds, so a reader checks the bytes.

The workbook's `fonts/` folder holds two fonts. `JetBrainsMonoNerdFont-Bold.ttf` is a Nerd Font
build: the Nerd Fonts project takes a programming font, here JetBrains Mono, and patches in
thousands of icons for terminals and code editors, from sets such as Font Awesome, Material
Design Icons and Powerline. This build (Nerd Fonts 3.3.0) has 12125 glyphs and maps about 10,400
icon code points in [private-use areas](#primer/code-point), 6896 of them above U+FFFF.
`NotoSansJP-Variable.ttf` is a [variable font](#primer/variable-font) for Japanese. Both start
with `00 01 00 00` and keep their outlines in `glyf`, so the parser you build reads TrueType
outlines and nothing else. Assignment 02 reads those four bytes as the scaler type and skips them
(see [the table directory](#primer/table-directory)). A stricter parser would stop there when it
finds `OTTO`.

Learn more:
- [TrueType](https://en.wikipedia.org/wiki/TrueType) on Wikipedia, with the format's history and
  how its outlines are built
- [OpenType](https://en.wikipedia.org/wiki/OpenType) on Wikipedia, on how OpenType grew out of
  TrueType
- [Organization of an OpenType font](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#organization-of-an-opentype-font)
  in the OpenType specification, which lists the `sfntVersion` values
- [Nerd Fonts](https://www.nerdfonts.com/), with the icon sets it patches in and a cheat sheet
  of their code points

## File offsets
<!--
id: file-offset
also: offset; byte offset; position in a file; relative offset; absolute offset
-->
An offset is a position counted in bytes from a starting point, with the first byte at offset 0.
A font file is full of them. Its tables don't come in a fixed order: the file stores where each
table starts, and tables store where their own parts start. To read a part, you move to its
offset and read from there.

The part to watch is the starting point, because each kind of offset counts from a different
place, and the specification says which:

- the [table directory](#primer/table-directory)'s offsets count from the start of the file
  (assignment 02)
- a [`cmap`](#primer/cmap) encoding record's offset counts from the start of the `cmap` table
  (assignment 03)
- a [`loca`](#primer/loca) entry counts from the start of the `glyf` table (assignment 04)

To find a part in the file, add the table's offset to the offset inside the table. If `glyf`
starts at byte 484 and a glyph's `loca` entry says 26, the glyph's record starts at byte 510.

Your `ByteReader` from assignment 01 keeps a current position, with `jumpTo` for an offset from
the start of the file and `skipBytes` to move forward from where it is (a stream does the same
with `seekg`, see [`<fstream>`](#primer/fstream)). The later font assignments jump to a table,
then skip over fields they don't need.

Learn more:
- [Offset (computer science)](https://en.wikipedia.org/wiki/Offset_%28computer_science%29) on
  Wikipedia, the general idea
- [Data types](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#data-types) in the
  OpenType specification, which defines `Offset16` and `Offset32` and says where table offsets
  count from

## The table directory
<!--
id: table-directory
also: sfnt; sfnt wrapper; offset table; offset subtable; table record; numTables; checksum; checkSum
-->
A TrueType font is a set of tables packed into one file, and the table directory at byte 0 is its
list of contents. The format is called sfnt, and OpenType uses the same wrapper.

The directory starts with a 12-byte header: the scaler type (4 bytes, see
[TrueType and OpenType fonts](#primer/truetype)), `numTables` (uint16), and three uint16 fields
meant to speed up a binary search, `searchRange`, `entrySelector` and `rangeShift`. Those three
can be worked out from `numTables`, and the OpenType specification advises readers not to rely
on them. Then come `numTables` table records of 16 bytes each:

| Field | Type | Meaning |
|---|---|---|
| tag | 4 bytes | the table's name, such as `cmap` (see [Table tags](#primer/table-tag)) |
| checkSum | uint32 | the sum of the table's bytes read as uint32 numbers, wrapping around |
| offset | uint32 | where the table starts, in bytes from the start of the file |
| length | uint32 | the table's length in bytes |

Record k starts at byte 12 + 16k. The checksum lets a tool detect a damaged table; a renderer can
ignore it, and the workbook never checks it.

Assignment 02 reads this directory into `TableRecord` values in `src/font/FontParser.h` and
`.cpp`, and `FontParser` keeps them in `Tables`, a [`std::map`](#primer/map) from tag to
record. Assignments 03 to 05 find `cmap`, `head`, `loca`, `maxp`, `hhea` and `hmtx` by tag in
that map.

Learn more:
- [Table directory](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#table-directory)
  in the OpenType specification, with the TableRecord layout
- [The font directory](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html)
  in Apple's TrueType Reference Manual, which calls the header the offset subtable
- [Calculating checksums](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#calculating-checksums)
  in the OpenType specification, if you want to verify them

## Table tags
<!--
id: table-tag
also: tag; four-character code; 4CC; table name; 'cvt '
-->
A tag is a table's name, stored as 4 bytes that read as 4 ASCII characters: `cmap`, `glyf`,
`head`, `OS/2`. A shorter name is padded with spaces at the end, so the control value table's tag
is `cvt ` with a trailing space, and Adobe's outline table is `CFF `. Tags are case-sensitive:
`head` and `HEAD` would be different tables. Apple reserves the all-lowercase names for its own
tables.

Because a tag is 4 bytes, you can treat it as text or as a 32-bit number. Each byte is the
ASCII code of one character:

```
bytes in the file   as text   as a big-endian uint32
63 6d 61 70         "cmap"    0x636D6170
63 76 74 20         "cvt "    0x63767420   (0x20 is a space)
```

Keeping a tag as a 4-character [`std::string`](#primer/string), one [`char`](#primer/char) per
byte, makes it easy to look up in a [map](#primer/map) and to print. Don't trim the spaces:
`"cvt "` and `"cvt"` are different keys, and assignment 02's output writes the tag in quotes
with its spaces. A well-made font sorts its records by tag, byte by byte, which puts uppercase
tags such as `GDEF` before lowercase ones such as `cmap`.

Assignment 02 reads each tag from its table record. Assignments 03 to 05 look tables up by tag,
and their inputs name each table with a `table "<tag>" ...` line.

Learn more:
- [Data types](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#data-types) in the
  OpenType specification, the rules for the Tag type
- [The font directory](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6.html)
  in Apple's TrueType Reference Manual, with the list of required and optional tables

## Fixed-point numbers and F2Dot14
<!--
id: f2dot14
also: fixed point; F2DOT14; 2.14; Fixed; 16.16; readF2Dot14
code: \breadF2Dot14\b
-->
The binary point is the binary version of the decimal point. Digits after a decimal point count
tenths, hundredths and so on; bits after a binary point count halves, quarters, eighths and so
on. So binary 1.11 is 1 + 1/2 + 1/4 = 1.75.

A fixed-point number is an integer with an agreed scale: you store an integer and divide it by a
fixed power of 2 to get the value. The binary point sits at the same place in every value,
which is where the name comes from. Fonts use fixed point where they need fractions, because
it is compact and exact.

F2Dot14 is a signed 16-bit integer ([two's complement](#primer/twos-complement)) with 2 bits
before the binary point and 14 after. Its value is the integer divided by 16384 (2^14), so its
range is −2 to 1.99993896484375, in steps of 1/16384. Outside fonts, the usual name for such a
format is Q notation: Qm.n has m bits before the point and n after, so F2Dot14 is Q2.14 (some
authors don't count the sign bit and write Q1.14). The OpenType specification's examples, with
two more:

| Bytes | As an int16 | Value |
|---|---|---|
| `7f ff` | 32767 | 1.999939 |
| `70 00` | 28672 | 1.75 |
| `40 00` | 16384 | 1 |
| `00 01` | 1 | 0.000061 |
| `ff ff` | −1 | −0.000061 |
| `c0 00` | −16384 | −1 |
| `80 00` | −32768 | −2 |

The font format also has a `Fixed` type: a signed 32-bit number with 16 bits before the point and
16 after, written 16.16 (Q16.16), so `00 01 80 00` is 1.5. `head` stores the font revision this
way, and `fvar` the axis ranges of [variable fonts](#primer/variable-font).

Assignment 01 adds `readF2Dot14` to your `ByteReader`, which returns a
[`double`](#primer/floating-point) (see [integer division](#primer/integer-division) for why the
divisor is 16384.0). Assignment 09 reads the scale factors of compound glyphs as F2Dot14, so a
component can be scaled by 0.5 (`20 00`) or flipped by −1 (`c0 00`) (see
[component records](#primer/component-flags)).

Learn more:
- [Fixed-point arithmetic](https://en.wikipedia.org/wiki/Fixed-point_arithmetic) on Wikipedia,
  the general idea
- [Q (number format)](https://en.wikipedia.org/wiki/Q_%28number_format%29) on Wikipedia, the
  Qm.n names and the two ways of counting the sign bit
- [Data types](https://learn.microsoft.com/en-us/typography/opentype/spec/otff#data-types) in the
  OpenType specification, with the F2DOT14 example table

## Unicode code points
<!--
id: code-point
also: Unicode; U+; code point; BMP; Basic Multilingual Plane; supplementary planes; character code
-->
Unicode gives every character a number, its code point, written `U+` followed by at least 4
[hexadecimal](#primer/hex-literals) digits: `A` is U+0041, `é` is U+00E9, `あ` is U+3042, and the
grinning-face emoji is U+1F600. Code points run from U+0000 to U+10FFFF, about 1.1 million
values, split into 17 planes of 65536. Plane 0, U+0000 to U+FFFF, is the Basic Multilingual
Plane (BMP) with most living scripts, including the common CJK characters: the Han characters
that Chinese, Japanese and Korean writing share. The planes above it hold emoji, rare CJK
characters and two more private-use areas.

A private-use area is a range of code points that Unicode gives no meaning, so that a font can
put its own symbols there: U+E000 to U+F8FF in the BMP, and nearly all of planes 15 and 16. Two
fonts can put different symbols at the same private-use code point. The Nerd Font build of
JetBrains Mono in `fonts/` (see [TrueType and OpenType fonts](#primer/truetype)) maps 3487 icons
in the BMP's area and 6896 in plane 15.

A code point is a number. How that number is stored as bytes in a file or a `std::string` is a
separate choice, the encoding (see [UTF-8](#primer/utf-8)). Fonts look characters up by code
point, so a renderer decodes the text into code points first.

The BMP fits in 16 bits and the full range doesn't, which matters in two places. A
[`cmap`](#primer/cmap) subtable in format 4 stores 16-bit codes and can reach the BMP only, while
format 12 stores 32-bit codes. And code points above U+FFFF need a 32-bit variable (see
[`<cstdint>`](#primer/cstdint)): a `uint16_t` turns U+1F600 into U+F600.

Assignment 03 reads input lines such as `lookup U+1F600` and maps code points to glyph ids.
Assignment 18 decodes its text into code points and looks each one up.

Learn more:
- [Code point](https://en.wikipedia.org/wiki/Code_point) on Wikipedia
- [Plane (Unicode)](https://en.wikipedia.org/wiki/Plane_%28Unicode%29) on Wikipedia, with what each
  plane holds
- [Private Use Areas](https://en.wikipedia.org/wiki/Private_Use_Areas) on Wikipedia
- [The Absolute Minimum Every Software Developer Must Know About Unicode](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)
  by Joel Spolsky, on code points versus encodings

## Glyphs and glyph ids
<!--
id: glyph-id
also: glyph; glyph index; glyph ID; GlyphCode; numGlyphs; character vs glyph
-->
A glyph is one shape the font can draw, and its glyph id is its number in the font, counting
from 0. Glyphs and characters aren't the same thing. A font can draw one character with several
glyphs, draw a ligature such as `fi` with one glyph for two characters, or hold glyphs that no
character maps to (accents meant only as parts of other glyphs, for example). The blog calls
the glyph id the GlyphCode; the specifications say glyph ID or glyph index.

Every per-glyph table is indexed by glyph id: [`loca`](#primer/loca) gives the position of glyph
i's outline, and [`hmtx`](#primer/hmtx) its advance width. The number of glyphs, `numGlyphs`,
comes from the [`maxp` table](#primer/maxp), so valid ids run from 0 to `numGlyphs` − 1.
JetBrains Mono Bold has 12125 glyphs and Noto Sans JP 17936. Glyph 0 has a special job, see
[Glyph 0 and `.notdef`](#primer/notdef).

The path from a character to its pixels goes through the glyph id at every step:

```
code point --cmap--> glyph id --loca--> outline in glyf
                              --hmtx--> advance width
```

Assignment 03 maps [code points](#primer/code-point) to glyph ids with [`cmap`](#primer/cmap).
Assignments 04 to 09 take glyph ids as input, and assignment 18 runs the whole path for every
character.

Learn more:
- [Glyph](https://en.wikipedia.org/wiki/Glyph) on Wikipedia, on glyphs and characters
- [glyf: Table organization](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#table-organization)
  in the OpenType specification, on how glyph ids index the glyph data

## The `cmap` table
<!--
id: cmap
also: character map; character to glyph mapping; encoding record; platform ID; encoding ID; format 12; format 4; segmented coverage; startCharCode; startGlyphID
-->
`cmap` maps [code points](#primer/code-point) to [glyph ids](#primer/glyph-id). It can hold
several maps, called subtables, for different platforms and encodings, so it starts with a list
of encoding records. Each record has a `platformID` (0 Unicode, 1 Macintosh, 3 Windows), an
`encodingID` whose meaning depends on the platform, and the [offset](#primer/file-offset) of its
subtable from the start of `cmap`. Platform 0 with encoding 4 means "Unicode, full repertoire",
and platform 0 with encoding 3 means "Unicode, BMP only".

Every subtable starts with a uint16 `format`. Most fonts use one of two formats:

- Format 4 stores 16-bit codes in segments, with a delta per segment and an extra array for
  the codes the delta doesn't cover. It reaches the BMP only, U+0000 to U+FFFF.
- Format 12 stores groups of 32-bit codes. Each group maps a run of consecutive code points
  to consecutive glyph ids:

```
glyph = startGlyphID + (c - startCharCode)    for startCharCode <= c <= endCharCode
```

A code point no group covers maps to glyph 0 (see [Glyph 0 and `.notdef`](#primer/notdef)).
The groups are sorted and don't overlap, so you can expand them into a map (see
[`<unordered_map>`](#primer/unordered-map)) or search them with a binary search.

Assignment 03 finds the (0, 4) record, checks that its subtable is format 12, and reads the
groups into a map in `src/font/Cmap.cpp`; any other case is `unsupported`. Both workbook fonts
have that subtable. Assignment 18 looks up every character through this map.

Learn more:
- [Format 12: Segmented coverage](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap#format-12-segmented-coverage)
  in the OpenType specification
- [Format 4: Segment mapping to delta values](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap#format-4-segment-mapping-to-delta-values)
  in the OpenType specification, the BMP-only format a fuller renderer would read as a fallback
- ['cmap' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html)
  in Apple's TrueType Reference Manual

## The `maxp` table
<!--
id: maxp
also: maximum profile; numGlyphs; maxComponentDepth
-->
`maxp`, the maximum profile, tells a renderer how much memory the font's glyphs can need. It
starts with a 4-byte version, then `numGlyphs`, a uint16 at offset 4: the number of glyphs in
the font. Fonts with TrueType outlines use version 1.0 (`00 01 00 00`), which goes on with limits
such as the most points in one glyph, the most contours, and `maxComponentDepth`, how deeply
compound glyphs nest. Fonts with CFF outlines use version 0.5, which stops after `numGlyphs`.

You need `numGlyphs` for two jobs. It tells you how many entries to read from other tables:
[`loca`](#primer/loca) has `numGlyphs` + 1 of them, and [`hmtx`](#primer/hmtx) describes
`numGlyphs` glyphs, some with a full record and the rest with a side bearing only. It also
bounds glyph ids: an id of `numGlyphs` or more is invalid (see [glyph ids](#primer/glyph-id)).

```
the first 6 bytes of maxp in JetBrains Mono Bold:
00 01 00 00   2f 5d
version 1.0   numGlyphs = 0x2f5d = 12125
```

Assignment 04 reads `numGlyphs` to size its `loca` read, and assignment 05 reads it to know how
long the `leftSideBearings` array in `hmtx` is. Both find `maxp` through the
[table directory](#primer/table-directory) from assignment 02.

Learn more:
- [maxp: Maximum Profile](https://learn.microsoft.com/en-us/typography/opentype/spec/maxp) in the
  OpenType specification, with both versions
- ['maxp' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6maxp.html)
  in Apple's TrueType Reference Manual

## The `head` table
<!--
id: head
also: font header; unitsPerEm; indexToLocFormat; magicNumber; checksumAdjustment
-->
`head`, the font header, holds facts about the whole font. Among its fields:

| Offset | Field | Type | Meaning |
|---|---|---|---|
| 12 | `magicNumber` | uint32 | always 0x5F0F3CF5, a check that this is a font header |
| 18 | `unitsPerEm` | uint16 | how many font units make one em (see [Font units](#primer/font-units)) |
| 36 to 42 | `xMin`, `yMin`, `xMax`, `yMax` | int16 each | a box that holds every glyph |
| 50 | `indexToLocFormat` | int16 | 0: `loca` holds short offsets, 1: long offsets |

The field the workbook needs is `indexToLocFormat`. It decides how to read
[`loca`](#primer/loca), and reading `loca` with the wrong format gives nonsense offsets for
every glyph. Both workbook fonts use the long format; the hand-made test fonts in assignment 04
use both.

`head` also holds `checksumAdjustment`, which makes the checksum of the whole file come out to
a fixed value, and the creation and modification dates as seconds since 1904.

Assignment 04 reads `indexToLocFormat` at `head` + 50 in `src/font/Loca.cpp`. Assignment 01's
second example reads `unitsPerEm` from JetBrains Mono, where it is 1000.

Learn more:
- [head: Font Header Table](https://learn.microsoft.com/en-us/typography/opentype/spec/head) in
  the OpenType specification
- ['head' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6head.html)
  in Apple's TrueType Reference Manual

## The `loca` table
<!--
id: loca
also: index to location; glyph offsets; short offsets; long offsets; empty glyph; glyph record length
-->
`loca`, index to location, says where each glyph's record starts inside the `glyf` table. It is
an array of `numGlyphs` + 1 offsets, counted from the start of `glyf`, in one of two formats that
the [`head` table](#primer/head) chooses:

| `indexToLocFormat` | Entry | Offset |
|---|---|---|
| 0, short | uint16 | the entry × 2 |
| 1, long | uint32 | the entry |

The short format halves every offset so it fits in 16 bits, which reaches 131070 bytes; glyph
records in such fonts have even lengths. Keep the doubled value in a 32-bit variable: C++ computes
`2 * entry` as an `int`, so the product is right, but storing it back in a `uint16_t` drops the
top bit (see [integer promotion](#primer/integer-promotion)).

Glyph i's record runs from offset(i) up to offset(i + 1), so its length is the difference. The
extra entry at the end gives the last glyph's end. A glyph with no outline, such as the space,
has length 0: its offset equals the next one.

```
loca, long format:   0     120   120   304
glyph 0:   from 0 to 120     length 120
glyph 1:   from 120 to 120   length 0, an empty glyph such as the space
glyph 2:   from 120 to 304   length 184
```

These offsets count from the start of `glyf`. If `glyf` starts at byte 484 of the file, glyph 2's
record starts at byte 604 (see [file offsets](#primer/file-offset)).

Assignment 04 builds a `GlyphLocations` list of offset and length per glyph in
`src/font/Loca.cpp`. Assignment 07 decodes the [`glyf`](#primer/glyf) record at a location.

Learn more:
- [loca: Index to Location](https://learn.microsoft.com/en-us/typography/opentype/spec/loca) in
  the OpenType specification
- ['loca' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6loca.html)
  in Apple's TrueType Reference Manual, with an example of each format

## Font units and the em
<!--
id: font-units
also: FUnits; font design units; units per em; upem; em square; unitsPerEm; FWORD
-->
A type designer draws glyphs on a grid of whole numbers, and its unit is the font unit (FUnit).
Every coordinate in [`glyf`](#primer/glyf) and every metric in [`hhea`](#primer/hhea) and
[`hmtx`](#primer/hmtx) is in font units. The em is the font's nominal size: when you set text at
20 pixels, one em becomes 20 pixels. The [`head`](#primer/head) table's `unitsPerEm` says how
many font units make one em. The OpenType specification allows 16 to 16384; 2048 is common in
TrueType fonts, and both workbook fonts use 1000.

To draw at a size, multiply font units by a scale:

```
scale = pixels per em / unitsPerEm       20 px text, 1000 units per em: scale = 0.02
```

At that scale, an `A` 730 units tall (JetBrains Mono Bold) is 14.6 pixels tall. Glyphs may reach
outside the em: accents, descenders and the line's ascent and descent often do.

Font y grows upwards from the baseline, the opposite of screen pixels; see
[Font coordinates and screen coordinates](#primer/screen-coordinates) for the transform.

Assignment 05's metrics come out in font units. From assignment 08 on, the workbook gives you
the scale directly: each `place` or `pen` line carries one in pixels per font unit, and
assignment 18's `main.cpp` works one out from a pixel height and the font's ascent and descent.

Learn more:
- [FUnits and the em square](https://learn.microsoft.com/en-us/typography/opentype/spec/ttch01#funits-and-the-em-square)
  in the OpenType specification's TrueType fundamentals, with the conversion to pixels
- [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html)
  in Apple's TrueType Reference Manual, on the em square and the grid

## The baseline and the pen
<!--
id: baseline
also: pen position; origin; glyph origin; setting a line of text; advancing the pen
-->
Text in a Latin script sits on a horizontal line, the baseline. Most letters rest on it, and
descenders such as the tail of `g` hang below it. In font units the baseline is y = 0, so a
descender has negative y.

A renderer sets a line of text with a pen, a point on the baseline that moves from left to right.
For each character it draws the glyph with the glyph's origin, font point (0, 0), at the pen, then
moves the pen right by the glyph's advance width. The left side bearing is the gap from the pen to
the left edge of the outline. Both come from the [`hmtx` table](#primer/hmtx).

```
scale 0.02, pen starting at x = 10, advance width 600 font units = 12 pixels
first glyph: origin at x = 10    second: x = 22    third: x = 34
```

Keep the pen's x as a [`double`](#primer/floating-point). Rounding it after every glyph adds up
to half a pixel of error per character, and a long line drifts.

Assignment 05 reads the numbers the pen needs. Assignment 08 introduces the placement, three
numbers that put font (0, 0) at a pixel column and a baseline row (see
[Font coordinates and screen coordinates](#primer/screen-coordinates)). Assignment 18 moves the
pen through a whole line, including spaces, which have an advance width but no outline.

Learn more:
- [Glyph metrics](https://freetype.org/freetype2/docs/glyphs/glyphs-3.html) in the FreeType
  glyph conventions, with pictures of the pen, the origin and the advance
- [Baseline (typography)](https://en.wikipedia.org/wiki/Baseline_%28typography%29) on Wikipedia

## The `hhea` table
<!--
id: hhea
also: horizontal header; ascent; ascender; descent; descender; lineGap; numberOfHMetrics
-->
`hhea`, the horizontal header, holds the font-wide numbers for setting text in horizontal lines.
It is 36 bytes long. The workbook reads three fields:

| Offset | Field | Type | Meaning |
|---|---|---|---|
| 4 | ascent | int16 | how far the line reaches above the baseline |
| 6 | descent | int16 | how far it reaches below, negative in most fonts |
| 34 | `numberOfHMetrics` | uint16 | how many full records the `hmtx` table starts with |

The OpenType specification names the first two `ascender` and `descender`, Apple's manual
`ascent` and `descent`. The designer chooses them as the line's height, and some glyphs reach
past them (see [The baseline and the pen](#primer/baseline)). Ascent minus descent is the height
of one line without extra spacing: JetBrains Mono Bold has 1020 and −300, so 1320 font units.
Windows reads its line metrics from the `OS/2` table instead, which the workbook doesn't use.

`numberOfHMetrics` belongs to the [`hmtx` table](#primer/hmtx), which has no count of its own.

Assignment 05 reads these fields in `src/font/Metrics.cpp`. Assignment 18's `main.cpp` sets the
scale to the requested pixel height divided by ascent − descent, so one line of text fills that
height, and puts the baseline the ascent below the top margin.

Learn more:
- [hhea: Horizontal Header Table](https://learn.microsoft.com/en-us/typography/opentype/spec/hhea)
  in the OpenType specification
- ['hhea' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6hhea.html)
  in Apple's TrueType Reference Manual

## The `hmtx` table
<!--
id: hmtx
also: horizontal metrics; advance width; advanceWidth; left side bearing; lsb; longHorMetric; leftSideBearings
-->
`hmtx`, horizontal metrics, gives two numbers per glyph, both in font units:

- the advance width, how far the [pen](#primer/baseline) moves after the glyph (an unsigned
  uint16)
- the left side bearing (lsb), the distance from the pen to the glyph's leftmost point (an
  int16, negative when the glyph reaches left of the pen)

The table starts with `numberOfHMetrics` records (from [`hhea`](#primer/hhea)) of 4 bytes, an
advance width and then an lsb. Glyphs with ids from `numberOfHMetrics` up to `numGlyphs` − 1
(from [`maxp`](#primer/maxp)) get 2 bytes each, an lsb alone, and they all take the advance
width of the last full record. This saves space in fonts where the last glyphs share one width,
such as a monospaced font or a run of CJK glyphs.

```
numberOfHMetrics = 3, numGlyphs = 6
glyphs 0, 1, 2:  4 bytes each, advance width and lsb
glyphs 3, 4, 5:  2 bytes each, lsb only; their advance width is glyph 2's
```

The glyph's outline doesn't hold its advance width, so every glyph, simple, compound or empty,
takes it from here.

Assignment 05 reads the table in `src/font/Metrics.cpp`, both the full records and the
lsb-only ones. Assignment 18 moves the pen by each glyph's advance width, compound glyphs
included (see [component records](#primer/component-flags)).

Learn more:
- [hmtx: Horizontal Metrics Table](https://learn.microsoft.com/en-us/typography/opentype/spec/hmtx)
  in the OpenType specification
- ['hmtx' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6hmtx.html)
  in Apple's TrueType Reference Manual
- [Glyph metrics](https://freetype.org/freetype2/docs/glyphs/glyphs-3.html) in the FreeType
  glyph conventions, with pictures of advance width and bearing

## The `glyf` table and the glyph header
<!--
id: glyf
also: glyph data; glyph record; glyph description; numberOfContours; bounding box; bbox; xMin; simple glyph
-->
`glyf` holds the outlines: one record per glyph, one after another, with no index of its own.
The [`loca` table](#primer/loca) says where each record starts and how long it is.

Every record starts with the same 10-byte header:

| Field | Type | Meaning |
|---|---|---|
| `numberOfContours` | int16 | 0 or more: a simple glyph with that many contours. Negative (normally −1): a compound glyph |
| `xMin`, `yMin`, `xMax`, `yMax` | int16 each | the bounding box, in font units |

The bounding box is the smallest rectangle that holds all the glyph's points, on-curve and
off-curve. Because off-curve points can lie outside the curve, it contains the outline without
always touching it.

After the header, a simple glyph describes its points (see [Contours](#primer/contour) and
[Simple glyph flags](#primer/glyph-flags)), and a compound glyph lists other glyphs to reuse (see
[Compound glyphs](#primer/compound-glyph)). A record of length 0 has no header at all: the glyph
is empty.

Assignment 07 reads the header and decodes simple glyphs in `src/font/GlyphParser.cpp`, and
`src/Glyph.h` keeps the three kinds apart (`Empty`, `Simple`, `Compound`, an
[`enum class`](#primer/enum-class)). Assignment 09 decodes compound records.

Learn more:
- [glyf: Glyph Data](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#glyph-headers)
  in the OpenType specification, the glyph header
- ['glyf' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6glyf.html)
  in Apple's TrueType Reference Manual

## Contours and `endPtsOfContours`
<!--
id: contour
also: contour; outline; endPtsOfContours; closed path; point numbers; contour direction
code: \bendPtsOfContours\b
-->
A contour is one closed loop of the outline. An `o` has two, the outside and the hole, `i` has
two (stem and dot), and `B` has three. A simple glyph stores all its points in one list,
numbered from 0, and `endPtsOfContours` says where each contour ends: entry k is the index of
contour k's last point. The point count is the last entry + 1.

```
endPtsOfContours = 3 7     contour 0: points 0..3   contour 1: points 4..7
```

Each contour is closed: after its last point the outline goes back to its first point, and no
line joins one contour to the next. The order of the points gives each contour a direction,
which the fill uses: TrueType fills by the [non-zero rule](#primer/nonzero), and outer contours
run so that the inside lies to the right, clockwise as you look at the glyph, while holes run the
other way.

`GlyphComponent` in `src/GlyphComponent.h` holds an outline as `endPtsOfContours` and `points`.
Assignment 07 reads `endPtsOfContours` from the record, and from assignment 08 on the drawing
code splits the points into contours with it.

Learn more:
- [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html)
  in Apple's TrueType Reference Manual, on contours and their direction
- [Simple glyph description](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#simple-glyph-description)
  in the OpenType specification

## On-curve and off-curve points
<!--
id: on-off-curve
also: on-curve point; off-curve point; control point; ON_CURVE_POINT; quadratic outline
-->
Each point of a TrueType outline is either on the curve or off it. The outline passes through an
on-curve point. An off-curve point, also called a control point, bends the outline toward itself
without lying on it.

How the points combine:

- two on-curve points in a row: a straight line between them
- on, off, on: a quadratic Bézier curve that starts and ends at the on-curve points and is
  pulled toward the off-curve one (see [Quadratic Bézier curves](#primer/bezier))
- two off-curve points in a row: an on-curve point is implied halfway between them (see
  [Implied on-curve points](#primer/implied-point))

Bit 0 of each point's [flag](#primer/glyph-flags) says which kind it is: 1 for on-curve, 0 for
off-curve.

TrueType uses quadratic curves, one control point per curve. CFF fonts use cubic curves with two
control points each, which is one reason the two outline formats can't share a reader.

Assignment 07 prints `on` or `off` after every point. Assignment 08 draws every point the same
way, joined with straight lines, so you can see where the control points sit, and assignment 11
turns the off-curve points into curves.

Learn more:
- [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html)
  in Apple's TrueType Reference Manual, with figures of on-curve and off-curve points
- [Glyph Conventions: outlines](https://freetype.org/freetype2/docs/glyphs/glyphs-6.html) in the
  FreeType documentation, the same rules with pictures

## Simple glyph flags
<!--
id: glyph-flags
also: flags; ON_CURVE_POINT; X_SHORT_VECTOR; Y_SHORT_VECTOR; REPEAT_FLAG; X_IS_SAME_OR_POSITIVE_X_SHORT_VECTOR; run-length encoding; bit flags
-->
A simple glyph stores one flag byte per point, and the bits of the flag say how to read the
point. The bits that matter:

| Mask | Name | Meaning |
|---|---|---|
| 0x01 | ON_CURVE_POINT | the point is on the curve |
| 0x02 | X_SHORT_VECTOR | the x delta is 1 byte |
| 0x04 | Y_SHORT_VECTOR | the y delta is 1 byte |
| 0x08 | REPEAT_FLAG | the next byte says how many more points use this flag |
| 0x10 | X_IS_SAME_OR_POSITIVE_X_SHORT_VECTOR | with 0x02: the byte is positive; without: x is unchanged |
| 0x20 | Y_IS_SAME_OR_POSITIVE_Y_SHORT_VECTOR | the same for y |

Test a bit with `&` (see [bit operations](#primer/bit-operations)): `flag & 0x01` is non-zero when
the point is on the curve.

The flags are packed with run-length encoding, which stores a repeated value once with a count.
When REPEAT_FLAG is set, the byte after the flag is a count, and the flag applies to that many
more points. So the bytes `3f 03` give four points that all have flag 0x3f. Expand the run
before you read any coordinates, so that every point has its own flag.

Bits 0x02 and 0x10 together decide the x delta (0x04 and 0x20 the y delta): 1 byte added, 1 byte
subtracted, nothing (same as before), or 2 bytes signed. See
[Delta-encoded coordinates](#primer/delta-encoding).

Assignment 07 decodes these flags in `src/font/GlyphParser.cpp` (see
[on-curve and off-curve points](#primer/on-off-curve) for bit 0).

Learn more:
- [Simple glyph description](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#simple-glyph-description)
  in the OpenType specification, whose flag table is the clearest
- [Run-length encoding](https://en.wikipedia.org/wiki/Run-length_encoding) on Wikipedia

## Delta-encoded coordinates
<!--
id: delta-encoding
also: delta encoding; deltas; relative coordinates; running sum; xCoordinates; yCoordinates
-->
Delta encoding stores the change from one value to the next in place of the values. A glyph's
points are often close together, so the changes are small and many fit in 1 byte where the
coordinates need 2.

In a simple glyph, the first point's delta is relative to (0, 0) and each later point's delta
is relative to the point before it. To get the coordinates back, keep a running sum:

```
x deltas:        +100   +50   −30    0
x coordinates:    100   150   120   120
```

All the x deltas come first, one per point, then all the y deltas. Each one takes 0, 1 or 2
bytes, as its point's [flag](#primer/glyph-flags) says:

| short bit | same-or-positive bit | Bytes | Delta |
|---|---|---|---|
| 1 | 1 | 1, uint8 | + the byte |
| 1 | 0 | 1, uint8 | − the byte |
| 0 | 1 | 0 | 0, the same as the point before |
| 0 | 0 | 2, int16 | the value |

The running sum carries on from one contour to the next: the first point of contour 1 is
relative to the last point of contour 0, not to (0, 0).

Assignment 07 decodes the deltas into absolute coordinates in font units in
`src/font/GlyphParser.cpp`.

Learn more:
- [Delta encoding](https://en.wikipedia.org/wiki/Delta_encoding) on Wikipedia
- [Simple glyph description](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#simple-glyph-description)
  in the OpenType specification, the X_SHORT_VECTOR and X_IS_SAME_OR_POSITIVE_X_SHORT_VECTOR rows

## Hinting instructions
<!--
id: hinting
also: hinting; instructions; instructionLength; bytecode; grid-fitting; fpgm; prep; cvt
-->
At small sizes a glyph covers few pixels, and an outline scaled straight onto the pixel grid can
come out blotchy: one stem two pixels wide, the next one pixel, a stroke that vanishes. Hinting
moves outline points slightly at each size so that they line up with the pixel grid. TrueType
does it with a small program per glyph, written in a stack-based bytecode, and font-wide programs
in the `fpgm` and `prep` tables, with shared values in `cvt `.

A simple glyph record holds its program after `endPtsOfContours`: a uint16 `instructionLength`,
then that many bytes of instructions. A compound glyph can have instructions after its last
component, when WE_HAVE_INSTRUCTIONS is set.

The workbook draws outlines without hinting, so a parser passes over these bytes. In a simple
glyph record they sit between the contour ends and the flags:

```
endPtsOfContours     instructionLength   instructions             flags ...
2 bytes per contour  uint16, say 37      37 bytes, not needed
```

JetBrains Mono is hinted and its glyphs carry instructions, so a parser that forgets to skip them
reads the instructions as flags. Assignment 07's tests include long instruction blocks.

Learn more:
- [Font hinting](https://en.wikipedia.org/wiki/Font_hinting) on Wikipedia
- [Grid-fitting a glyph outline](https://learn.microsoft.com/en-us/typography/opentype/spec/ttch01#grid-fitting-a-glyph-outline)
  in the OpenType specification's TrueType fundamentals

## Compound glyphs
<!--
id: compound-glyph
also: composite glyph; component; components; nested compound glyph; depth-first; maxComponentDepth
-->
A compound glyph (the OpenType specification says composite) has no points of its own (see
[the glyph header](#primer/glyf)). It lists other glyphs, its components, and says where to put
each one. `é` can be the glyph for `e` plus the glyph for an acute accent moved up, so the font
stores each shape once and reuses it. `numberOfContours` is negative in a compound glyph's
header.

Each component can be moved, scaled, flipped or rotated (see
[Component transforms](#primer/component-transform)). A component can itself be compound, so
glyphs can nest: to resolve one, you recurse into each component, and a nested component gets
its own transform first and then its parent's. The order this produces is depth-first: the first
component and everything inside it, then the second, and so on. The [`maxp`](#primer/maxp)
table's `maxComponentDepth` says how deep a font nests, and the specification asks that the
nesting never loops.

A component that is an empty glyph adds nothing. A simple glyph with 0 contours adds nothing
either.

```
glyph 300, compound:  glyph 200 at offset (0, 0), then glyph 150 at offset (40, 500)
glyph 200, compound:  glyph 80 at offset (10, 0)
glyph 300's outlines, in order:  glyph 80 moved by (10, 0), then glyph 150 moved by (40, 500)
```

Code that follows components inside components is usually written with
[recursion](#primer/recursion). Assignment 09 resolves any glyph into the outlines of its simple
glyphs in `src/font/CompoundGlyph.cpp`. JetBrains Mono has no nested compound glyphs, but the
hand-made test fonts do.

Learn more:
- [Composite glyph description](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#composite-glyph-description)
  in the OpenType specification
- [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html)
  in Apple's TrueType Reference Manual, its "Compound glyphs" section

## Component records and their flags
<!--
id: component-flags
also: component record; ARG_1_AND_2_ARE_WORDS; ARGS_ARE_XY_VALUES; MORE_COMPONENTS; WE_HAVE_A_SCALE; WE_HAVE_AN_X_AND_Y_SCALE; WE_HAVE_A_TWO_BY_TWO; WE_HAVE_INSTRUCTIONS; USE_MY_METRICS; SCALED_COMPONENT_OFFSET; UNSCALED_COMPONENT_OFFSET
code: \b(ARG_1_AND_2_ARE_WORDS|MORE_COMPONENTS|WE_HAVE_A_TWO_BY_TWO)\b
-->
After its 10-byte [header](#primer/glyf), a compound glyph holds one record per component: a
uint16 `flags`, a uint16 `glyphIndex`, two arguments, then 0 to 4 [F2Dot14](#primer/f2dot14)
numbers for the [transform](#primer/component-transform). The records follow each other until
one has MORE_COMPONENTS clear. The flags:

| Mask | Name | Meaning |
|---|---|---|
| 0x0001 | ARG_1_AND_2_ARE_WORDS | the arguments are 2 bytes each; otherwise 1 byte each |
| 0x0002 | ARGS_ARE_XY_VALUES | the arguments are a signed x and y offset; otherwise point numbers to line up |
| 0x0008 | WE_HAVE_A_SCALE | one F2Dot14 follows, a scale for x and y |
| 0x0020 | MORE_COMPONENTS | another component record follows |
| 0x0040 | WE_HAVE_AN_X_AND_Y_SCALE | two F2Dot14 follow, x scale then y scale |
| 0x0080 | WE_HAVE_A_TWO_BY_TWO | four F2Dot14 follow, a full 2 x 2 matrix |
| 0x0100 | WE_HAVE_INSTRUCTIONS | hinting instructions follow the last component |
| 0x0200 | USE_MY_METRICS | the compound glyph takes this component's metrics |
| 0x0800 | SCALED_COMPONENT_OFFSET | the transform applies to the offset too |
| 0x1000 | UNSCALED_COMPONENT_OFFSET | the offset is used as stored |

At most one of the three scale flags is set. Test each flag with `&` (see
[bit operations](#primer/bit-operations)). With x/y values, 1-byte arguments are signed:
`e2` is −30, not 226. If neither offset flag is set, the OpenType specification says
Microsoft's and Apple's rasterizers use the offset unscaled.

USE_MY_METRICS gives the compound glyph this component's advance width and side bearings, as
with the dotless i inside `î`. The compound glyph still has its own entry in
[`hmtx`](#primer/hmtx), and the workbook takes every advance width from there, so assignment 18
doesn't need the flag.

Assignment 09 reads these records in `src/font/CompoundGlyph.cpp`. Its tests set
ARGS_ARE_XY_VALUES in every record.

Learn more:
- [Composite glyph description](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#composite-glyph-description)
  in the OpenType specification, with the full flag table
- ['glyf' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6glyf.html)
  in Apple's TrueType Reference Manual, its component flags table

## Component transforms
<!--
id: component-transform
also: xscale; scale01; scale10; yscale; 2x2 matrix; component offset; composing transforms; transformation matrix
-->
Each component of a [compound glyph](#primer/compound-glyph) is placed with six numbers: a 2 x 2
part a, b, c, d that scales, flips or rotates it, and an offset (e, f) that moves it. Every point
(x, y) of the component becomes:

```
x' = a*x + c*y + e
y' = b*x + d*y + f
```

The OpenType specification calls a, b, c, d `xscale`, `scale01`, `scale10` and `yscale`. The
flags say which are stored: none (a = d = 1, b = c = 0), one scale (a = d), an x and a y scale,
or all four. The offset is (argument1, argument2).

When SCALED_COMPONENT_OFFSET is set, the offset goes through the 2 x 2 part as well. The workbook
follows fontTools, which applies the whole 2 x 2 part:

```
e = a*argument1 + c*argument2
f = b*argument1 + d*argument2
```

For a nested component, apply its own transform first, then its parent's. Two transforms
combine into one by multiplying them (see [Affine transforms](#primer/affine-transform)), so
you can pass one combined transform down the recursion.

Example: a component with scale 0.5 and offset (40, 40), with SCALED_COMPONENT_OFFSET set, moves
the corner (100, 100) of a square to (0.5·100 + 20, 0.5·100 + 20) = (70, 70).

Assignment 09 applies these transforms in `src/font/CompoundGlyph.cpp`, including rotations,
flips and nested glyphs, and prints the fractional coordinates they produce (see
[`<cstdio>`](#primer/cstdio)).

Learn more:
- [Composite glyph description](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#composite-glyph-description)
  in the OpenType specification, on the transform and the offset flags
- ['glyf' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6glyf.html)
  in Apple's TrueType Reference Manual, with Apple's older rule for scaling offsets

## Implied on-curve points
<!--
id: implied-point
also: implied point; implied on-curve point; midpoint; consecutive off-curve points; all off-curve contour
-->
When two off-curve points follow each other in a contour, the outline passes through the point
halfway between them. The font doesn't store that point. It is implied, and it ends one quadratic
curve and starts the next:

```
implied = (offA + offB) / 2     for each coordinate
```

<svg viewBox="0 0 400 200" role="img" aria-label="Two off-curve points with the implied on-curve point halfway between them, joining two quadratic curves" style="width:100%;max-width:420px;height:auto">
<polyline points="40,160 120,40 280,40 360,160" fill="none" stroke="var(--rule)" stroke-width="2" stroke-dasharray="6 5"/>
<path d="M40 160 Q120 40 200 40 Q280 40 360 160" fill="none" stroke="var(--ink)" stroke-width="3"/>
<circle cx="40" cy="160" r="7" fill="var(--fig-a)"/>
<circle cx="360" cy="160" r="7" fill="var(--fig-a)"/>
<circle cx="120" cy="40" r="7" fill="none" stroke="var(--fig-b)" stroke-width="3"/>
<circle cx="280" cy="40" r="7" fill="none" stroke="var(--fig-b)" stroke-width="3"/>
<circle cx="200" cy="40" r="6" fill="var(--muted)"/>
<text x="40" y="186" text-anchor="middle" font-size="14" fill="var(--ink)">on</text>
<text x="360" y="186" text-anchor="middle" font-size="14" fill="var(--ink)">on</text>
<text x="120" y="24" text-anchor="middle" font-size="14" fill="var(--ink)">off</text>
<text x="280" y="24" text-anchor="middle" font-size="14" fill="var(--ink)">off</text>
<text x="200" y="72" text-anchor="middle" font-size="14" fill="var(--muted)">implied on-curve point</text>
</svg>

TrueType fonts leave these points out to save space, and smooth shapes such as `o` or `s` use
many of them. The rule also covers the ends of a contour, because the last and first points are
neighbours. A contour can start with an off-curve point, and a circle can be made of off-curve
points alone, a ring of curves joined at implied points. When you walk such a contour, start from
an on-curve point, real or implied, never from (0, 0).

Assignment 08 draws only the stored points. Assignment 11 draws the curves (see
[Quadratic Bézier curves](#primer/bezier)) and marks the implied points in blue.

Learn more:
- [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html)
  in Apple's TrueType Reference Manual, on points that can be left out
- [Glyph Conventions: outlines](https://freetype.org/freetype2/docs/glyphs/glyphs-6.html) in the
  FreeType documentation, which draws two off points with the virtual on point between them

## Glyph 0 and `.notdef`
<!--
id: notdef
also: .notdef; missing glyph; glyph 0; tofu; unmapped character
-->
Glyph 0 is the missing-character glyph, named `.notdef`. A renderer draws it for any character the
font has no glyph for. Most fonts draw it as a box, sometimes with a cross or a slash through it;
people call these boxes tofu. In JetBrains Mono Bold it is a box with a slash.

The [`cmap`](#primer/cmap) table can't list every code point the font lacks, so the rule is the
other way round: a code point that no `cmap` entry covers maps to glyph 0. The OpenType
specification requires the glyph at index 0 to be this missing-character glyph. Like any glyph,
it has an outline in `glyf` and an advance width in [`hmtx`](#primer/hmtx), so the pen still
moves past it.

Dropping unmapped characters would hide the problem from whoever reads the output, and throwing
an error would stop the whole line for one character, which is why renderers draw glyph 0.

Assignment 03 answers `none` for an unmapped code point. Assignment 18 draws glyph 0 in its
place, for example for U+0378, which JetBrains Mono doesn't have.

Learn more:
- [cmap: Table overview](https://learn.microsoft.com/en-us/typography/opentype/spec/cmap#table-overview)
  in the OpenType specification, on mapping missing characters to glyph index 0
- [loca](https://learn.microsoft.com/en-us/typography/opentype/spec/loca) in the OpenType
  specification, which says glyph index 0 is the missing-character glyph

## UTF-8
<!--
id: utf-8
also: UTF8; UTF-8 decoding; encoding; continuation byte; multi-byte character; utf8ToCodepoints; U+FFFD; replacement character
code: \butf8ToCodepoints\b
-->
UTF-8 stores each [code point](#primer/code-point) as 1 to 4 bytes. ASCII characters keep their
single byte, so plain English text is the same in ASCII and UTF-8. The first byte's high bits say
how many bytes the character takes, and every following byte starts with the bits `10`:

| Code points | Bytes |
|---|---|
| U+0000 to U+007F | `0xxxxxxx` |
| U+0080 to U+07FF | `110xxxxx 10xxxxxx` |
| U+0800 to U+FFFF | `1110xxxx 10xxxxxx 10xxxxxx` |
| U+10000 to U+10FFFF | `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx` |

To decode, take the x bits of the first byte, then for each continuation byte shift left by 6
and add its low 6 bits. `é` is `c3 a9`: (0x03 << 6) | 0x29 = 0xE9, so U+00E9.

A C++ [`std::string`](#primer/string) holds bytes: a string holding `あ` has a `size()` of 3.
Read each byte as `unsigned char` before you test its [bits](#primer/bit-operations): `char` is
signed with GCC and MSVC on x86, so bytes from 0x80 up come out negative (see
[`char` and `unsigned char`](#primer/char)). A decoder also has to handle broken input, such as
a missing continuation byte; replacing each bad byte with U+FFFD, the replacement character, is
the usual choice.

Assignment 18's text lines are UTF-8, and `utf8ToCodepoints` in `src/utils/Unicode.h` decodes
them before your `TextRenderer` looks up each code point.

Learn more:
- [UTF-8](https://en.wikipedia.org/wiki/UTF-8) on Wikipedia, with the byte patterns and the
  invalid sequences
- [The Absolute Minimum Every Software Developer Must Know About Unicode](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)
  by Joel Spolsky

## Variable fonts
<!--
id: variable-font
also: variable font; font variations; fvar; gvar; HVAR; axis; wght; default instance
-->
A variable font holds a whole range of styles in one file. It defines one or more axes, such as
weight (`wght`), and a program can pick any position on them: weight 400 for regular, 700 for
bold, or anything between. OpenType added variable fonts in version 1.8 (2016).

The file still has ordinary tables. `glyf` stores the outlines of one style, the default instance,
and extra tables say how to move each point for other positions: `fvar` lists the axes, `gvar`
holds the point movements (deltas) for TrueType outlines, and `HVAR` adjusts advance widths. A
reader that ignores those tables gets a complete font, the default instance. Inside these tables
an axis position is normalized to a number from −1 to 1 and stored as an
[F2Dot14](#primer/f2dot14). The optional `avar` table bends that scale: it maps each normalized
position to another through a list of pairs, so that the weights in between the ends can be
spaced as the designer wants. Noto Sans JP's `avar` maps 0.5 (weight 500) to 0.56.

`NotoSansJP-Variable.ttf` in `fonts/` is a variable build. Its one axis is weight, from 100 to
900, and its default is 100, so the outlines in `glyf` are the thin end of the range. It also
uses overlapping contours, as many variable fonts do, which the [non-zero](#primer/nonzero)
fill handles.

Assignment 01's tests read F2Dot14 values from its `avar`. Assignment 18 draws its `glyf`
outlines and ignores the variation tables, as its page says.

Learn more:
- [Variable font](https://en.wikipedia.org/wiki/Variable_font) on Wikipedia
- [OpenType Font Variations overview](https://learn.microsoft.com/en-us/typography/opentype/spec/otvaroverview)
  in the OpenType specification, on axes, the default instance and deltas
- [avar: Axis Variations Table](https://learn.microsoft.com/en-us/typography/opentype/spec/avar)
  in the OpenType specification
