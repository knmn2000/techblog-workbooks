# 18 · Render a line of text

**Difficulty:** Hard · **Checkpoint** 18 of 18 · **Check:** `.\check 18`

**Tags**
- *Language:* UTF-8 decoding · organising a larger program · reusing your own code
- *Library:* `std::ifstream` (binary) · `std::unordered_map` · `std::vector`
- *Concepts:* the whole pipeline: table directory, cmap, loca, hmtx, simple and compound glyphs, non-zero filling, advance widths

## Read in the blog first

This page is complete on its own. This is where the blog ends up: its goal was to "load a Unicode
font, render an arbitrary string, and output it as a PNG file". Skim the
[Goal](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Goal) section and the final
pictures in the [Non-zero Rule](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Non-zero%20Rule) section.

## Where this fits

Every earlier checkpoint built one piece. This one puts them together: from the bytes of a font file
and a string of text to a picture of that text. It's the last piece of your project: `TextRenderer`
includes the files of checkpoints 02 to 17, and `main.cpp` turns the project into a program you
can run.

## The problem

Write a program that draws lines of text with a TrueType font and writes the picture as a PNG.

Only the picture is checked, so you can structure the code however you like. This checkpoint's
code goes in your project, in `utils/Unicode.h`, `TextRenderer.h`, `TextRenderer.cpp` and
`main.cpp` under `src/`. It can build on `font/FontParser.h`, `font/Cmap.h`, `font/Loca.h`,
`font/Metrics.h`, `font/CompoundGlyph.h` and `render/NonZero.h`.
`checkpoints/p18_render_text.cpp` is the program the checker runs: it reads the test input,
calls your code and writes the answer.

Each new file starts blank, with a comment saying what belongs in it, and the program with an
empty `main`, so the includes, reading the input and writing the output are yours. To start from
working input/output code instead, pick Boilerplate in the book's editor (or copy this
checkpoint's files from `starters/boilerplate/`): the declarations use the author's names where
the post has them, and what's left to write is `utf8ToCodepoints` and the `TextRenderer`
functions. `main.cpp` is the program you'll run when you're done: `tiny_ttf <font.ttf> "<text>"
<out.png>`. The boilerplate has it written; it uses your `TextRenderer`.

### Input

The checker runs `<program> <input-file> <output-png>` from the workbook folder.

| Line | Meaning |
|---|---|
| `font <path>` | The TrueType font to use (relative to the workbook folder) |
| `canvas <width> <height>` | The picture size in pixels; it starts black |
| `pen <x> <baseline> <scale>` | Where the next text starts: the first glyph's origin is at pixel position (x, baseline). `scale` is pixels per font unit. |
| `color <r> <g> <b>` | The colour of the next text |
| `text <...>` | Text to draw, in UTF-8, from after the space following `text` to the end of the line (spaces included) |

`pen`, `color` and `text` can repeat. A `text` line starts where the pen is: at the most recent `pen`
line, moved right by any text drawn since (the provided code passes the pen x on). Later text is
drawn on top of earlier text.

### Output

A PNG (or binary PPM) of exactly `width` x `height` pixels. For each character, in order:

1. **Decode UTF-8** into Unicode code points. A code point takes 1 to 4 bytes: `0xxxxxxx`,
   `110xxxxx 10xxxxxx`, `1110xxxx 10xxxxxx 10xxxxxx` or `11110xxx 10xxxxxx 10xxxxxx 10xxxxxx`.
2. **Find the glyph** with the font's cmap: the format 12 subtable with platform 0, encoding 4
   (checkpoint 03). A code point the font doesn't map uses **glyph 0** (`.notdef`), usually a box.
3. **Get its outline** (checkpoints 04, 07, 09): find the glyph's record with `loca`; a simple glyph
   gives one outline, a compound glyph the outlines of its components placed with their full
   transforms (offsets, scales, 2 x 2 matrices, nested compound glyphs: checkpoint 09's rules), and
   an empty glyph (such as space) nothing. Fill every component outline; filling them one by one
   or merged gives the same picture for these fonts. Noto Sans JP is a variable font: use the
   outlines stored in `glyf` and ignore its variation tables.
4. **Fill it** with the non-zero rule (checkpoint 17), placed with glyph point (x, y) at pixel
   position (penX + scale·x, baseline − scale·y). A pixel is painted when its centre is inside.
5. **Move the pen**: penX += advanceWidth × scale, using the glyph's advance width from `hmtx`
   (checkpoint 05; glyphs past numberOfHMetrics use the last advance). Don't round the pen
   position: keep it fractional.

The checker forgives edges that move by one pixel. Missing glyphs, glyphs in the wrong place or
colour, and holes in the wrong places fail.

**Writing the picture.** Write it to the output path you're given. The name ends in `.png`, but
the checker looks at the contents, so a PNG and a binary PPM both work. A binary PPM is the
easiest to write by hand: the header `P6`, the width, the height and `255`, separated by spaces
or newlines and ended by one newline (for example `P6\n205 195\n255\n`), then 3 bytes per pixel
(red, green, blue), row by row from the top-left. Open the file in binary mode
(`std::ios::binary`), or Windows writes every pixel byte 10 as two bytes. For a real PNG,
`third_party/stb_image_write.h` in your project is on the include path: `#define
STB_IMAGE_WRITE_IMPLEMENTATION` before including it in one file, then call `stbi_write_png(path,
width, height, 3, pixels, width * 3)`. Your `FrameBufferCanvas` from checkpoint 06 does all of this in
`writePng`; the boilerplate calls it.

### Where each piece is explained

| Step | Checkpoint | Key facts |
|---|---|---|
| Table directory | 02 | numTables: uint16 at byte 4; 16-byte records from byte 12: tag, checkSum, offset, length |
| cmap | 03 | encoding records (platform, encoding, offset from cmap) after a 4-byte header; format 12 groups: start, end, startGlyphID (uint32 each) |
| loca | 04 | numGlyphs: uint16 at `maxp` + 4; `head` + 50: 0 = short (uint16 × 2), 1 = long (uint32); numGlyphs + 1 entries, offsets from the start of `glyf` |
| Advance widths | 05 | numberOfHMetrics: uint16 at `hhea` + 34; `hmtx`: (uint16 advance, int16 lsb) per glyph, later glyphs reuse the last advance |
| Simple glyphs | 07 | header, contour ends, instructions, flags with REPEAT, delta-coded x then y |
| Compound glyphs | 09 | component records: flags, glyph index, arguments, optional scale / x-y scale / 2 × 2 |
| Filling | 17 | non-zero rule, curves split at their y turning point, pixel centres |

Load the font once and reuse it for every `text` line: `drawText` is called once per line.

## Requirements

- **R1** UTF-8 is decoded into code points, including 2-, 3- and 4-byte characters.
- **R2** Characters are mapped to glyphs with cmap; characters the font doesn't have draw glyph 0.
- **R3** Each glyph moves the pen right by its advance width times the scale.
- **R4** Compound glyphs are drawn with their components in place.
- **R5** Glyphs are filled with the non-zero rule, curves and overlapping strokes included.
- **R6** Several pen positions, colours and text lines; later text is drawn on top.
- **R7** The scale is applied; text that runs off the canvas is clipped.

## Examples

### Example 1: Hello, World! (test `18-E2E-hello`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf
         canvas 562 113
         pen 8 80 0.07
         color 255 255 255
         text Hello, World!
```

JetBrains Mono is monospaced: every advance width is 600 font units, so each character moves the
pen 600 × 0.07 = 42 pixels.

![expected picture for 18-E2E-hello](tests/18/expected/18-E2E-hello.png)

### Example 2: two lines, two colours (test `18-R6-two-lines`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf
         canvas 412 184
         pen 8 70 0.06
         color 255 255 255
         text first line
         pen 8 154 0.06
         color 255 170 40
         text second line
```

![expected picture for 18-R6-two-lines](tests/18/expected/18-R6-two-lines.png)

### Example 3: a character the font doesn't have (test `18-R2-unmapped`)

```
input:   font fonts/JetBrainsMonoNerdFont-Bold.ttf
         canvas 196 152
         pen 8 110 0.1
         color 255 255 255
         text A͸B
```

The middle character, U+0378 (bytes `cd b8` in UTF-8), isn't in JetBrains Mono's cmap, so glyph 0 is drawn in its place: a
box with a slash. The pen still moves on by glyph 0's advance width.

![expected picture for 18-R2-unmapped](tests/18/expected/18-R2-unmapped.png)

## Constraints

- Both fonts in the tests have a platform 0 / encoding 4 format 12 cmap subtable. Canvases are at
  most 600 pixels wide.
- The text contains no control characters, and no character needs more than one glyph.
- There are 18 tests: one or more per requirement with JetBrains Mono Bold and Noto Sans JP, plus
  phrases and random words (new ones with `-Fresh`). Each case has 10 seconds.

## Source material

- Wikipedia, [UTF-8](https://en.wikipedia.org/wiki/UTF-8): the byte patterns
- Apple, *TrueType Reference Manual*: ['cmap'](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6cmap.html), ['loca'](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6loca.html), ['hmtx'](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6hmtx.html), ['glyf'](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM06/Chap6glyf.html)
- The blog: [Goal](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Goal)

## Hints

<details><summary>Hint 1: where to start</summary>

Make a small font class that loads everything once: the table directory, the cmap mapping, the
`loca` offsets and lengths, and the advance widths. Then drawing a string is a loop over code points.
</details>

<details><summary>Hint 2: the approach</summary>

Copy in your solutions to checkpoints 02-05 (tables), 07 and 09 (glyph outlines) and 17 (filling),
adapting their inputs: each one already turns a font file into exactly what the next step needs.
Decode the UTF-8 into code points first, then for each: glyph id, outlines, fill, advance.
</details>

<details><summary>Hint 3: the traps</summary>

- A character the font doesn't map draws glyph 0, not nothing.
- Keep the pen x as a double. Rounding it each step drifts by up to half a pixel per character.
- The space character has no outline but does have an advance width.
- Fill every outline of a compound glyph.
- Text runs off the canvas in one test: skip pixels outside it.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
font = load(path)          # directory, cmap (0/4 format 12), loca, hmtx
for cp in utf8_decode(text):
    gid = font.cmap.get(cp, 0)
    for outline in font.outlines(gid):          # simple: 1, compound: its components
        fill_nonzero(canvas, outline, place=(penX, baseline, scale), color)
    penX += font.advance(gid) * scale
return penX
```
</details>

## Checking your solution

```
.\check 18                         run every test
.\check 18 -Case 18-E2E-hello      one test: its input, and where the expected and your pictures are
.\check 18 -Fresh                  new random words (new seed)
.\check 18 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

## After you pass: compare with the author's code

The blog's final program loads the font once in a `FontParser`, converts the string to code points
with a small `utf8ToCodepoints` helper, asks the parser for each glyph and renders it with the
non-zero renderer, moving a start x by each glyph's metrics. The pictures at the end of the blog are
made that way.
