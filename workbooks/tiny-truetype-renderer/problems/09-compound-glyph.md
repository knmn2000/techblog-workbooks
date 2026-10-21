# 09 · Resolve compound glyphs

**Difficulty:** Hard · **Assignment** 9 of 18 · **Check:** `.\check 09`

**Tags**
- *Language:* recursion · affine transforms as six numbers · signed bytes (`int8`) · fixed-point numbers
- *Library:* `std::ifstream` (binary) · `std::map` · `std::vector`
- *Concepts:* compound glyphs · component records · F2Dot14 · composing transforms · depth-first traversal

## Read in the blog first

You can pass using this page alone. For the background, read the blog's
[Compound glyph](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Compound%20glyph)
section up to the transformation matrix. Stop at the paragraph that starts "Implementation.
As compound glyphs are nested", before the author's code.

## Source material

- Apple, *TrueType Reference Manual*, ['glyf' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6glyf.html): compound glyph flags and the transformation
- Microsoft, *OpenType specification*, [glyf: composite glyph description](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#composite-glyph-description)
- The blog: [Compound glyph](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Compound%20glyph)

## Where this fits

Your `GlyphParser` from assignment 07 decodes simple glyphs and only reports compound ones. A
**compound glyph** has no points of its own: it lists other glyphs, its **components**, and where
to put each one. For example, `é` is `e` plus an acute accent moved above it. Here you turn any
glyph into the outlines of the simple glyphs that make it up, each in its final position. The
fill assignments (14, 16, 17) and the text renderer (18) draw those outlines.

## The problem

Write a program that takes a glyph, simple or compound, and prints the outlines of the simple
glyphs that make it up, each moved to its final position.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains three kinds of lines:

| Line | Meaning |
|---|---|
| `font <path>` | The font file the following lines refer to (relative to the workbook folder). Starts a new font: forget earlier `glyph` lines. |
| `glyph <id> <offset> <length>` | Where glyph `id`'s record is in the file and how long it is (0 = no outline), as your `Loca` from assignment 04 works out. The input lists every glyph you will need. |
| `decode <id>` | Resolve glyph `id` and write it out. |

### Output

For each `decode` line, write a header line and then one `ends` / `points` pair per simple glyph
inside the glyph:

```
glyph <id> components <k>
ends <...>
points <x0> <y0> <on|off> <x1> <y1> <on|off> ...
... (k pairs)
```

- An empty glyph (length 0) gives `components 0`. A simple glyph gives `components 1` with its own
  outline.
- Components appear in **depth-first order**: the order of the component records, and inside a
  nested compound glyph, its components in their order before moving on. A component that is an
  empty glyph adds nothing and isn't counted.
- `ends` and `on|off` are the simple glyph's own values, as in assignment 07.
- Print coordinates after every transform that applies, so they can be fractional: one of the
  random tests expects `points 338.5 -275.25 on 324.4375 -266.8125 off ...`.
- The checker accepts a difference of up to 0.01 per number, so the exact value or anything
  rounded to two or more decimals passes. The boilerplate's `number()` prints whole numbers
  without a decimal point and others rounded to 4 decimals with trailing zeros dropped (`47.5`,
  `374.9062`).

### The compound glyph record

The 10-byte header is the same as for simple glyphs: `numberOfContours` (int16, negative for a
compound glyph) and the bounding box (4 x int16, you can ignore it).

**Component records** follow, one per component, one after another, until one has
MORE_COMPONENTS clear:

| Field | Type | Meaning |
|---|---|---|
| `flags` | uint16 | See the table below |
| `glyphIndex` | uint16 | The component glyph |
| `argument1`, `argument2` | int16 each if ARG_1_AND_2_ARE_WORDS is set, otherwise int8 each | The offset (e, f) |
| transform | F2Dot14 x 0, 1, 2 or 4 | Depends on the scale flags |

All numbers are big-endian. **F2Dot14** is a signed 16-bit number divided by 16384 (your
`ByteReader` from assignment 01 reads it), so `40 00` is 1.0 and `c0 00` is -1.0.

**The arguments are signed**: the byte `e2` is -30, not 226.

**Component flags** (bits not listed don't affect the output):

| Bit | Mask | Name | Meaning |
|---|---|---|---|
| 0 | `0x0001` | ARG_1_AND_2_ARE_WORDS | The two arguments are int16; otherwise int8 |
| 1 | `0x0002` | ARGS_ARE_XY_VALUES | The arguments are an x/y offset. Every test sets it |
| 3 | `0x0008` | WE_HAVE_A_SCALE | One F2Dot14 follows: a = d = scale |
| 5 | `0x0020` | MORE_COMPONENTS | Another component record follows this one |
| 6 | `0x0040` | WE_HAVE_AN_X_AND_Y_SCALE | Two F2Dot14 follow: a, then d |
| 7 | `0x0080` | WE_HAVE_A_TWO_BY_TWO | Four F2Dot14 follow: a, b, c, d |
| 8 | `0x0100` | WE_HAVE_INSTRUCTIONS | Hinting instructions follow the last component; ignore them |
| 11 | `0x0800` | SCALED_COMPONENT_OFFSET | a, b, c, d transform the offset too (see below) |

At most one of bits 3, 6 and 7 is set. With none of them, a = d = 1 and b = c = 0.

### Placing a component

Every point (x, y) of the component becomes

```
x' = a*x + c*y + e
y' = b*x + d*y + f
```

where a, b, c, d are the **2 x 2 part** set by the scale flags (it scales, flips or rotates)
and (e, f) is the **offset**, (argument1, argument2). If SCALED_COMPONENT_OFFSET is set, the
offset goes through the 2 x 2 part first: e = a*argument1 + c*argument2 and
f = b*argument1 + d*argument2.

A component can itself be a compound glyph. In that case you place its own components with
their own transforms first, then place the result with the outer transform, so transforms
compose **from the inside out**.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** An empty glyph gives `components 0`; a simple glyph gives `components 1` and its outline.
- **R2** Your program reads the component records: flags, glyph index, signed 1-byte or 2-byte
  arguments, and the loop over MORE_COMPONENTS.
- **R3** The three scale forms: one scale, separate x and y scales, and the full 2 x 2 matrix.
- **R4** Every point goes through x' = a*x + c*y + e and y' = b*x + d*y + f.
- **R5** With SCALED_COMPONENT_OFFSET, a, b, c, d transform the offset too.
- **R6** Nested compound glyphs: inner transforms apply first, then outer ones.
- **R7** Components come out depth first, in record order, and empty components add nothing.

## Examples

### Example 1: a scaled component with a scaled offset (test `09-R5-scaled-offset`)

```
input:   font tests/09/data/compound-test.ttf
         glyph 14 800 18
         glyph 2 536 22
         decode 14
```

Glyph 2 is a square from (0, 0) to (100, 100). Glyph 14's 18 bytes:

```
ff ff                       numberOfContours = -1: compound
00 14 00 14 00 46 00 46     bounding box (ignore)
08 0a                       flags 0x080a: ARGS_ARE_XY_VALUES, WE_HAVE_A_SCALE, SCALED_COMPONENT_OFFSET
00 02                       glyphIndex 2
28 28                       arguments as int8: 40, 40
20 00                       scale 0x2000 / 16384 = 0.5
```

The scale of 0.5 halves the square, and because SCALED_COMPONENT_OFFSET is set, it also halves
the offset (40, 40) to (20, 20):

```
output:  glyph 14 components 1
         ends 3
         points 20 20 on 20 70 on 70 70 on 70 20 on
```

### Example 2: a rotation (test `09-R3-rotate`)

Glyph 11's component record is `00 82 | 00 02 | 64 00 | 00 00 40 00 c0 00 00 00`: flags
WE_HAVE_A_TWO_BY_TWO with byte arguments, glyph 2, offset (100, 0), and a = 0, b = 1, c = -1,
d = 0. That gives x' = -y + 100 and y' = x, a quarter turn:

```
input:   font tests/09/data/compound-test.ttf
         glyph 11 730 24
         glyph 2 536 22
         decode 11

output:  glyph 11 components 1
         ends 3
         points 100 0 on 0 0 on 0 100 on 100 100 on
```

### Example 3: three components (test `09-R2-three-parts`)

Glyph 8 places glyph 2 (a square) at (0, 0), glyph 3 (a triangle) at (120, 0) and glyph 4
(two contours, with off-curve points) at (0, 150):

```
input:   font tests/09/data/compound-test.ttf
         glyph 8 662 30
         glyph 2 536 22
         glyph 3 558 20
         glyph 4 578 34
         decode 8

output:  glyph 8 components 3
         ends 3
         points 0 0 on 0 100 on 100 100 on 100 0 on
         ends 2
         points 120 0 on 180 0 on 150 80 on
         ends 3 6
         points 0 150 on 20 210 off 60 210 off 80 150 on 30 160 on 50 160 on 40 180 on
```

## Constraints

- Records are well-formed, every glyph you need has a `glyph` line, and compound glyphs nest at
  most 3 levels deep. Point-matched components (ARGS_ARE_XY_VALUES clear) don't occur.
- Scales are within the F2Dot14 range, from -2 up to 32767/16384 (a little under 2).
- Each case has a 10-second limit.
- There are 36 tests: hand-made glyphs for each rule in a small test font, accented letters from
  JetBrains Mono Bold such as `é` and `Ü`, and 6 random compound glyphs (new ones with
  `-Fresh`).

## Hints

<details><summary>Hint 1: where to start</summary>

Handle the three cases at the top: no outline (length 0), a simple glyph (numberOfContours ≥ 0),
and a compound glyph. Only the last one needs new code, and it calls the same function again for
each component.
</details>

<details><summary>Hint 2: the approach</summary>

Write one recursive function that takes a glyph id and the transform to apply, and appends
outlines to a list. For a compound glyph, read **all** of its component records first (reading a
component moves the file position elsewhere), then call the function again for each one with the
combined transform. Keep a transform as six numbers a, b, c, d, e, f.
</details>

<details><summary>Hint 3: the traps</summary>

- Read int8 arguments as `int8_t`, not `uint8_t`, so that `e2` comes out as -30.
- After WE_HAVE_A_TWO_BY_TWO the order is a, b, c, d, and x' uses c (not b) for y.
- Inner transforms apply first. Combining outer (A) after inner (B) gives
  a = A.a*B.a + A.c*B.b, b = A.b*B.a + A.d*B.b, c = A.a*B.c + A.c*B.d, d = A.b*B.c + A.d*B.d,
  e = A.a*B.e + A.c*B.f + A.e, f = A.b*B.e + A.d*B.f + A.f.
- SCALED_COMPONENT_OFFSET changes only the offset, not the 2 x 2 part.
- Skip components that are empty glyphs instead of writing an empty outline.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
resolve(id, T, out):
    if length(id) == 0: return
    seek(offset(id)); n = readInt16()
    if n >= 0: out.append(transform(decodeSimple(id), T)); return
    skip(8)
    records = []
    do:
        flags = readUint16(); gid = readUint16()
        e, f = (readInt16(), readInt16()) if flags & 0x1 else (readInt8(), readInt8())
        a, b, c, d = 1, 0, 0, 1
        if flags & 0x08: a = d = readF2Dot14()
        elif flags & 0x40: a = readF2Dot14(); d = readF2Dot14()
        elif flags & 0x80: a, b, c, d = 4 x readF2Dot14()
        if flags & 0x800: e, f = a*e + c*f, b*e + d*f
        records.append((gid, (a, b, c, d, e, f)))
    while flags & 0x20
    for gid, L in records:
        resolve(gid, T after L, out)
```
</details>

## Checking your solution

```
.\check 09                         run every test
.\check 09 -Case 09-R6-nested      one test, showing its input, the expected output and yours
.\check 09 -Fresh                  new random compound glyphs (new seed)
.\check 09 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R2  Component records: flags, glyph id, signed 1- or 2-byte arguments... .    3 / 4   FAILED
      x 09-R2-neg-bytes  neg_bytes: offset (-30, -5) stored as two signed bytes
          points[0]: expected (x=-30, y=-5, curve=on), got (x=226, y=251, curve=on) - differs in x, y
          likely cause: R4 - x' = a*x + c*y + e and y' = b*x + d*y + f for every point
          expected values from: fontTools 4.67.0
          reproduce: build/solutions/assignment_09.exe build/cases/09/09-R2-neg-bytes.in build/cases/09/09-R2-neg-bytes.out
```

## After you pass: compare with the author's code

[The blog's compound-glyph parser](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Parser%20for%20compound%20glyphs)
splits the work into `getCompoundGlyph`, which loops over the component records while
MORE_COMPONENTS is set, and `getCompoundSubComponents`, which decodes a component and recurses for
nested compound glyphs. It builds a `glm::mat3` for each component, saves the stream position
before recursing and jumps back afterwards, and takes the glyph's metrics from a component with
USE_MY_METRICS.

**Things to look for:**
- The snippet reads 1-byte arguments as unsigned, so a small negative offset like -30 becomes 226.
  JetBrains Mono has 48 such components, all in its ligature glyphs.
- It scales the offset with Apple's older `m`/`n` rule for every component. The current
  specifications only scale the offset when SCALED_COMPONENT_OFFSET is set. JetBrains Mono marks
  its components UNSCALED_COMPONENT_OFFSET and uses no scales, so the two agree there.
- For a nested compound glyph, `getCompoundSubComponents` doesn't pass its own matrix down to the
  inner components, so an outer offset or scale is lost. JetBrains Mono has no nested compound
  glyphs, but the tests do.
