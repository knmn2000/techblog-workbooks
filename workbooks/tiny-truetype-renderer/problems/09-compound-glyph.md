# 09 · Resolve compound glyphs

**Difficulty:** Hard · **Assignment** 9 of 18 · **Check:** `.\check 09`

**Tags**
- *Language:* [recursion](#primer/recursion) · [affine transforms](#primer/affine-transform) as six numbers · [signed bytes](#primer/integer-types) (`int8`) · [fixed-point numbers](#primer/f2dot14)
- *Library:* [`std::ifstream`](#primer/fstream) (binary) · [`std::map`](#primer/map) · [`std::vector`](#primer/vector)
- *Concepts:* [compound glyphs](#primer/compound-glyph) · [component records](#primer/component-flags) · [F2Dot14](#primer/f2dot14) · [composing transforms](#primer/component-transform) · [depth-first traversal](#primer/recursion)

## Read in the blog first

For background, the blog's
[Compound glyph](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Compound%20glyph) section
goes up to the transformation matrix. Stop at the paragraph that starts "Implementation. As compound
glyphs are nested"; the author's code comes after it.

## Learning material

- [Compound glyphs](#primer/compound-glyph): a glyph with no points of its own, made of other
  glyphs. `resolveGlyph` returns the outlines of the simple glyphs inside one, depth first,
  without the empty ones.
- [Component records and their flags](#primer/component-flags): what follows the header.
  `CompoundGlyph.cpp` reads `flags`, `glyphIndex` and two arguments per record, and the record
  with MORE_COMPONENTS clear is the last.
- [Component transforms](#primer/component-transform): the scale flags give a, b, c and d, the
  arguments give the offset, and with SCALED_COMPONENT_OFFSET set, the offset goes through a, b, c, d.
- [Affine transforms and 2 x 2 matrices](#primer/affine-transform): six numbers, and what
  happens when one transform follows another. A nested component goes through its own transform
  and then its parent's.
- [Recursion](#primer/recursion): a component can be compound too, so the resolver calls itself
  for each component. Simple and empty glyphs are the base cases.
- [Fixed-point numbers and F2Dot14](#primer/f2dot14): the font stores the scales as F2Dot14. Your
  `readF2Dot14` from assignment 01 turns one into a `double` (`40 00` is 1.0).
- [Integer types](#primer/integer-types): 1-byte arguments are signed, so they go through
  `readInt8`, and the byte `e2` gives -30.
- [`<cstdio>`](#primer/cstdio): the program's `number()` writes a fractional coordinate with
  `std::snprintf` and `"%.4f"`, then drops the trailing zeros.

## Source material

- Apple, *TrueType Reference Manual*, ['glyf' table](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6glyf.html): compound glyph flags and the transformation
- Microsoft, *OpenType specification*, [glyf: composite glyph description](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf#composite-glyph-description)
- The blog: [Compound glyph](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Compound%20glyph)

## Where this fits

Your `GlyphParser` from assignment 07 spots a compound glyph and moves on. This one opens it up.
A compound glyph has no points of its own. It lists other glyphs, its components, and where each
goes: `é`, for example, is `e` plus an acute accent shifted above it. The job is to flatten any
glyph into the simple outlines that make it up, each already in its final position. Those are what
the fill assignments (14, 16, 17) and the text renderer (18) draw.

## The problem

Write a program that takes a glyph, simple or compound, and prints the outlines of the simple
glyphs inside it, each moved to its final position.

### Input

From the workbook folder, the checker starts your program as `<program> <input-file> <output-file>`.
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

- An empty glyph (length 0) gives `components 0`. A simple glyph gives `components 1` and its
  own outline.
- Components come out depth first: in the order of the component records, and for a nested
  compound glyph, all of its components before the next record. A component that is an empty
  glyph adds nothing and isn't counted.
- `ends` and `on|off` are the simple glyph's own values, as in assignment 07.
- Print coordinates after every transform that applies, so they can be fractional: one of the
  random tests expects `points 338.5 -275.25 on 324.4375 -266.8125 off ...`.
- Each number may be off by up to 0.01, so the exact value or anything rounded to two or more
  decimals passes. The boilerplate's `number()` handles the format: whole numbers print bare,
  anything else prints rounded to 4 decimals without trailing zeros (`47.5`, `374.9062`).

### The compound glyph record

The 10-byte header matches the simple-glyph one: `numberOfContours` (int16, negative for a
compound glyph) and the bounding box (4 x int16, which you can ignore).

Component records follow, one per component, back to back, until one has MORE_COMPONENTS clear:

| Field | Type | Meaning |
|---|---|---|
| `flags` | uint16 | See the table below |
| `glyphIndex` | uint16 | The component glyph |
| `argument1`, `argument2` | int16 each if ARG_1_AND_2_ARE_WORDS is set, otherwise int8 each | The offset (e, f) |
| transform | F2Dot14 x 0, 1, 2 or 4 | Depends on the scale flags |

All numbers are big-endian. F2Dot14 is a signed 16-bit number divided by 16384 (your
`ByteReader` from assignment 01 reads it), so `40 00` is 1.0 and `c0 00` is -1.0. The arguments
are signed as well: the byte `e2` is -30, not 226.

The bits of `flags` are below; bits not listed don't affect the output:

| Bit | Mask | Name | Meaning |
|---|---|---|---|
| 0 | `0x0001` | ARG_1_AND_2_ARE_WORDS | The two arguments are int16; otherwise int8 |
| 1 | `0x0002` | ARGS_ARE_XY_VALUES | The arguments are an x/y offset. Every test sets it |
| 3 | `0x0008` | WE_HAVE_A_SCALE | One F2Dot14 follows: a = d = scale |
| 5 | `0x0020` | MORE_COMPONENTS | Another component record follows this one |
| 6 | `0x0040` | WE_HAVE_AN_X_AND_Y_SCALE | Two F2Dot14 follow: a, then d |
| 7 | `0x0080` | WE_HAVE_A_TWO_BY_TWO | Four F2Dot14 follow: a, b, c, d |
| 8 | `0x0100` | WE_HAVE_INSTRUCTIONS | Hinting instructions follow the last component; ignore them |
| 11 | `0x0800` | SCALED_COMPONENT_OFFSET | The transform applies to the offset too; this workbook uses fontTools' rule (see below) |

A record sets at most one of bits 3, 6 and 7. With none of them, a = d = 1 and b = c = 0.

### Placing a component

Every point (x, y) of the component becomes

```
x' = a*x + c*y + e
y' = b*x + d*y + f
```

Here a, b, c, d are the 2 x 2 part the scale flags set (it can scale, flip or rotate), and
(e, f) is the offset, (argument1, argument2).

If the flags include SCALED_COMPONENT_OFFSET, the offset goes through the 2 x 2 part first:

```
e = a*argument1 + c*argument2
f = b*argument1 + d*argument2
```

That is fontTools' reading of the flag, and fontTools produces this workbook's expected outputs.
The OpenType specification says only that the offset is then in the component's coordinate
system and that the transformation applies to it. Other implementations scale the offset
without rotating it, so a rotated or flipped component lands somewhere else. Test
`09-R5-scaled-offset-rot` (offset (50, 10), a = 0, b = 1, c = -1, d = 0) shows the split:

| Implementation | e | f | Offset in that test |
|---|---|---|---|
| fontTools (the tests) | a*argument1 + c*argument2 | b*argument1 + d*argument2 | (-10, 50) |
| FreeType | hypot(a, c) * argument1 | hypot(b, d) * argument2 | (50, 10) |
| Apple's *TrueType Reference Manual* | m * argument1 | n * argument2 | (50, 10) |

Apple's m is max(|a|, |b|), doubled when |(|a| - |c|)| is at most 33/65536, and n is
max(|c|, |d|), doubled when |(|b| - |d|)| is at most 33/65536. Apple's manual applies this to
every component's offset and doesn't mention the flag. All three agree when b = c = 0 and a and d
are positive, as in Example 1. Follow the fontTools row to pass.

A component can itself be a compound glyph. Place its own components with their own transforms
first, then place the result with the outer transform: transforms compose from the inside out.

## Requirements

Each test belongs to one requirement. The report shows a pass count for each, plus a `likely cause` line
when a failure points at one.

- **R1** An empty glyph gives `components 0`; a simple glyph gives `components 1` and its
  outline. A simple glyph with no contours (`numberOfContours` 0) has no outline, so it gives
  `components 0` too.
- **R2** The component records are read: flags, glyph index, signed 1-byte or 2-byte arguments,
  and the loop over MORE_COMPONENTS.
- **R3** The three scale forms work: one scale, separate x and y scales, and the full 2 x 2
  matrix.
- **R4** Every point goes through x' = a*x + c*y + e and y' = b*x + d*y + f.
- **R5** With SCALED_COMPONENT_OFFSET, a, b, c, d transform the offset too (fontTools' rule).
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

The scale of 0.5 halves the square, and because the flags include SCALED_COMPONENT_OFFSET it halves the
offset (40, 40) to (20, 20):

```
output:  glyph 14 components 1
         ends 3
         points 20 20 on 20 70 on 70 70 on 70 20 on
```

### Example 2: a rotation (test `09-R3-rotate`)

Glyph 11's component record is `00 82 | 00 02 | 64 00 | 00 00 40 00 c0 00 00 00`: flags 0x0082
(WE_HAVE_A_TWO_BY_TWO plus ARGS_ARE_XY_VALUES; bit 0 is clear, so the arguments are bytes),
glyph 2, offset (100, 0), and a = 0, b = 1, c = -1, d = 0. That gives x' = -y + 100 and y' = x, a
quarter turn:

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
- The time limit is 10 seconds per case.
- The suite has 36 tests: hand-made glyphs for each rule in a small test font, accented letters
  from JetBrains Mono Bold such as `é` and `Ü`, and 6 random compound glyphs (new ones with
  `-Fresh`).

## Hints

<details><summary>Hint 1: where to start</summary>

Sort out three cases at the top: no outline (length 0), a simple glyph (numberOfContours ≥ 0),
and a compound glyph. Only the last needs new code, and it calls the same function again for
each component.
</details>

<details><summary>Hint 2: the approach</summary>

Keep a transform as six numbers a, b, c, d, e, f. For a compound glyph, read all of its
component records first (reading a component moves the file position elsewhere), then recurse
for each one. The boilerplate's `resolveGlyph(reader, locations, id)` takes no transform, so
there are two ways to go:
- Recurse, then transform: resolve the component with `resolveGlyph` and apply the component's
  transform to every point it returns.
- Pass the transform down: write a private helper that takes a glyph id and the transform to
  apply and appends outlines to a list, and let `resolveGlyph` call it with the identity
  transform. The pseudocode in Hint 4 does this.

Both give the same points.
</details>

<details><summary>Hint 3: the traps</summary>

- Read int8 arguments as `int8_t`, not `uint8_t`, or `e2` won't come out as -30.
- After WE_HAVE_A_TWO_BY_TWO the file stores a, b, c, d in that order. Since x' = a*x + c*y + e,
  the y term in x' takes c, not b (b multiplies x in y').
- Inner transforms apply first. Outer (A) after inner (B) combines as
  a = A.a*B.a + A.c*B.b, b = A.b*B.a + A.d*B.b, c = A.a*B.c + A.c*B.d, d = A.b*B.c + A.d*B.d,
  e = A.a*B.e + A.c*B.f + A.e, f = A.b*B.e + A.d*B.f + A.f.
- SCALED_COMPONENT_OFFSET changes only the offset, not the 2 x 2 part, and it rotates the offset
  too (fontTools' rule, in "Placing a component").
- Skip a component that is an empty glyph; don't write out an empty outline for it.
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

Here x' used b in place of c, and the test fails like this:

```
  R4  x' = a*x + c*y + e and y' = b*x + d*y + f for every point ............    1 / 2   FAILED
      x 09-R4-shear  shear: 2x2 with c = 0.5: x' = x + 0.5*y (a shear)
          points[2]: expected (x=70, y=80, curve=on), got (x=30, y=80, curve=on) - differs in x  (in `glyph 12 components 1`)
          likely cause: R4 - x' = a*x + c*y + e and y' = b*x + d*y + f for every point
          expected values from: fontTools 4.67.0
          reproduce: build/solutions/assignment_09 build/cases/09/09-R4-shear.in build/cases/09/09-R4-shear.out
```

## After you pass: compare with the author's code

[The blog's compound-glyph parser](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Parser%20for%20compound%20glyphs)
has two functions. `getCompoundGlyph` loops over the component records while MORE_COMPONENTS is
set, and `getCompoundSubComponents` decodes one component and recurses into nested compound
glyphs. Each component gets a `glm::mat3`. The code saves the stream position before recursing
and jumps back afterwards, and it takes the glyph's metrics from a component with
USE_MY_METRICS.

The snippet departs from the current specifications in several places:
- It reads 1-byte arguments as unsigned, so a small negative offset like -30 becomes 226.
  JetBrains Mono has 48 such components: 28 in ligature glyphs, the rest in numerator forms and
  in characters such as `"` (U+0022, test `09-E2E-U+0022`), ŀ (U+0140) and ‼ (U+203C).
- It scales the offset with Apple's older `m`/`n` rule for every component. The current
  specifications scale the offset only with SCALED_COMPONENT_OFFSET, and fontTools, which
  this workbook follows, rotates it as well. JetBrains Mono marks its components
  UNSCALED_COMPONENT_OFFSET and uses no scales, and the rule as Apple states it gives m = n = 1
  there.
- Its version of that rule drops the outer absolute value in |(|b| − |d|)|. For an unscaled
  component |b| − |d| is −1, which passes the test, so n becomes 2 and every y offset doubles: in
  `·` (U+00B7) the period lands at y = 530 instead of 265. JetBrains Mono has 92 components with
  a nonzero y offset; test `09-E2E-U+01D8` has one. (In the post, the line that declares `eps`
  as 33/65536 ended up inside the comment above it, so the comparison uses the tiny `eps` from
  `Geometry.h`; the repository declares it on its own line. The doubling happens either way.)
- For a nested compound glyph, `getCompoundSubComponents` doesn't pass its own matrix down to the
  inner components, so an outer offset or scale is lost. JetBrains Mono has no nested compound
  glyphs, but the tests do.
- A component that is an empty glyph isn't skipped. `readGlyphHeader` returns 0 contours without
  moving the stream, and `getCompoundSubComponents` hands every count that isn't positive to
  `getCompoundGlyph`, which then reads the parent's next component record as the empty glyph's
  own. Test `09-R7-with-empty` covers this case.
- With no USE_MY_METRICS component, it returns a zero `Metric`, and `getGlyphByCode` doesn't
  fall back to the compound glyph's own `hmtx` entry. In JetBrains Mono 22 compound characters
  have no such component, among them `"` and the grave accent (U+0060), so the author's text
  renderer would give them an advance width of 0. The spec takes every glyph's advance width
  from `hmtx`, as assignment 18 does.