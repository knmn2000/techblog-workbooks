# 16 · Fill a polygon: non-zero rule

**Difficulty:** Medium · **Checkpoint** 16 of 18 · **Check:** `.\check 16`

**Tags**
- *Language:* sorting pairs · signed counters
- *Library:* `std::vector` · `std::sort`
- *Concepts:* the non-zero winding rule · edge direction · scanline filling · half-open intervals

## Read in the blog first

This page is complete on its own; the blog tells the story behind it. Read the blog's
[Non-zero Rule](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Non-zero%20Rule)
section up to the sentence about considering only line segments for now. The author's code comes
right after it.

## Where this fits

Checkpoint 14 filled glyphs with the even-odd rule, which leaves a hole wherever two contours
overlap. Fonts are designed for the non-zero rule, which doesn't. This checkpoint fills outlines
made only of straight lines with the non-zero rule; checkpoint 17 adds curves.

## The problem

Write a program that fills polygon outlines on a black canvas with the non-zero rule and writes the
picture as a PNG.

Only the picture is checked, so you can structure the code however you like. This checkpoint's
code goes in your project, in `render/NonZero.h` and `render/NonZero.cpp` under `src/`. It can
build on `render/Scanline.h`. `checkpoints/p16_nonzero_lines.cpp` is the program the checker
runs: it reads the test input, calls your code and writes the answer.

Each new file starts blank, with a comment saying what belongs in it, and the program with an
empty `main`, so the includes, reading the input and writing the output are yours. To start from
working input/output code instead, pick Boilerplate in the book's editor (or copy this
checkpoint's files from `starters/boilerplate/`): the declarations use the author's names where
the post has them, and what's left to write is `renderGlyphByNonZero`.

### Input

The checker runs `<program> <input-file> <output-png>` from the workbook folder.

| Line | Meaning |
|---|---|
| `canvas <width> <height>` | The picture size in pixels |
| `place <x0> <baseline> <scale>` | Outline point (x, y) goes to pixel position (x0 + scale·x, baseline − scale·y). y grows up in the outline and down on the screen. |
| `color <r> <g> <b>` | The fill colour |
| `outline` | Starts an outline; its `ends` and `points` lines follow |
| `ends <e0> <e1> ...` | Index of the last point of each contour, counting from 0: contour k runs from the point after the previous end up to and including `e_k` |
| `points <x> <y> on ...` | The outline's points. **In this checkpoint every point is on-curve**, so every edge is a straight line. |

There can be several outlines. Fill each one on its own, one after another, in the same colour: the winding count is per outline, and a pixel ends up painted if any outline fills it.

### Output

A PNG (or binary PPM) of exactly `width` x `height` pixels, black to begin with. A pixel is painted
in the fill colour when its **centre** is inside an outline by the non-zero rule. Pixel (px, py),
with py counted down from the top, has its centre at screen position (px + 0.5, py + 0.5).

The checker forgives edges that move by one pixel, so sampling at the top of each row instead of
the centre, or rounding x differently, still passes. Missing or extra shapes and stray lines don't.

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

### The non-zero rule

Each contour is closed (after its last point it continues to its first), and every edge has a
direction: from a point to the next one. Draw a ray from the point to the right. Start a count at 0;
for each edge the ray crosses, add 1 if the edge goes up the screen and subtract 1 if it goes down (either sign
convention works, as long as it's the same for all edges). The point is inside when the final count
is **not zero**.

- Two overlapping contours that go the same way give a count of 2 where they overlap: still
  inside, so there is no hole. (Even-odd would leave one.)
- A contour inside another that goes the opposite way gives 1 − 1 = 0: a hole. This is how fonts
  make the inside of an `o` or a `#`.
- A contour that goes counter-clockwise on its own gives −1: inside. Test "not zero", not "greater
  than zero".

With a scanline: collect each crossing as (x, direction), sort by x, walk left to right keeping a
running count, and fill the stretches where the count isn't zero.

**Vertices on the scanline.** As in checkpoint 14, treat each edge as half-open in y: it counts at
scanline y when min(y0, y1) ≤ y < max(y0, y1), with y measured on the screen (pixels, growing
downward), and horizontal edges never count. Clamp crossing x values to the canvas before converting
them to integers. The provided `drawSpan(row, x0, x1)` fills x0 ... x1 inclusive and does nothing
when x0 > x1. Then a vertex the
outline passes through counts once, with the right direction.

## Requirements

- **R1** Pixels whose centre is inside are filled; every other pixel stays black.
- **R2** Where contours going the same way overlap, the overlap is filled.
- **R3** A contour going the opposite way inside another cuts a hole.
- **R4** A contour going counter-clockwise on its own is still filled.
- **R5** Vertices exactly on a scanline are counted correctly.
- **R6** Several outlines are filled one after another (their union).
- **R7** Placement and scale are applied; anything outside the canvas is clipped.

## Examples

### Example 1: a pentagram (test `16-R2-star`)

```
input:   canvas 205 195
         place 2 206 2
         color 255 255 255
         outline
         ends 4
         points 50 100 on 79 9 on 2 65 on 98 65 on 21 9 on
```

The same star as checkpoint 14. The pentagon in the middle is wound twice (count 2), so under the
non-zero rule it is filled:

![expected picture for 16-R2-star](tests/16/expected/16-R2-star.png)

### Example 2: squares going opposite ways (test `16-R3-opposite-overlap`)

```
input:   canvas 133 133
         place 6 126 2
         color 255 255 255
         outline
         ends 3 7
         points 0 0 on 0 40 on 40 40 on 40 0 on 60 20 on 60 60 on 20 60 on 20 20 on
```

The first square goes clockwise, the second counter-clockwise, so their overlap has a count of 0:

![expected picture for 16-R3-opposite-overlap](tests/16/expected/16-R3-opposite-overlap.png)

### Example 3: crossing strokes (test `16-R2-ten`)

```
input:   canvas 234 238
         place -9 214 0.25
         color 255 255 255
         outline
         ends 3 7
         points 62 443 on 945 443 on 945 414 on 62 414 on 486 829 on 516 829 on 516 -70 on 486 -70 on
```

U+5341 (十) from Noto Sans JP: two rectangles going the same way. Checkpoint 14's even-odd rule
left the crossing empty; non-zero fills it.

![expected picture for 16-R2-ten](tests/16/expected/16-R2-ten.png)

## Constraints

- Every point is on-curve. Canvases are at most about 560 x 560 pixels.
- Every contour has at least 2 points.
- There are 24 tests: hand-made polygons for each rule, straight-line letters from JetBrains Mono
  Bold, and straight-line characters from Noto Sans JP (random picks change with `-Fresh`). Each
  case has 10 seconds.

## Source material

- Wikipedia, [Nonzero-rule](https://en.wikipedia.org/wiki/Nonzero-rule)
- Apple, *TrueType Reference Manual*, [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html): contour direction
- The blog: [Non-zero Rule](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Non-zero%20Rule)

## Hints

<details><summary>Hint 1: where to start</summary>

Start from your checkpoint 14 scanline fill, if you have one. The edges and crossings are the same;
only what you do with the sorted crossings changes.
</details>

<details><summary>Hint 2: the approach</summary>

For each crossing, record its x and whether the edge goes down or up the screen (+1 or −1). Sort by
x, walk left to right adding the directions, and fill each stretch between two crossings where the
running count isn't zero.
</details>

<details><summary>Hint 3: the traps</summary>

- "Inside" is count ≠ 0. A lone counter-clockwise contour gives −1 and must be filled.
- The direction comes from the edge's own order (point i to point i + 1), not from its endpoints
  sorted by y.
- Keep the half-open rule (min ≤ y < max) and skip horizontal edges.
- The last point connects back to the first point of its contour, not of the outline.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
edges = [(p[i], p[i+1]) for each contour, wrapping at its end], mapped to pixels
for row in 0 .. height-1:
    y = row + 0.5
    crossings = []
    for (a, b) in edges:
        if min(a.y, b.y) <= y < max(a.y, b.y):
            x = a.x + (y - a.y) * (b.x - a.x) / (b.y - a.y)
            crossings.append((x, +1 if b.y > a.y else -1))
    sort crossings by x
    count = 0
    for i in 0 .. len(crossings) - 2:
        count += crossings[i].direction
        if count != 0:
            fill pixels px with crossings[i].x <= px + 0.5 < crossings[i+1].x
```
</details>

## Checking your solution

```
.\check 16                         run every test
.\check 16 -Case 16-R4-reversed    one test: its input, and where the expected and your pictures are
.\check 16 -Fresh                  new random glyphs (new seed)
.\check 16 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

## After you pass: compare with the author's code

The blog's [line-only version](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Considering%20line%20direction%20at%20intersection%20counting)
stores each crossing as an x and an "is upward" flag and keeps a running count while it walks the
sorted crossings, as here.

**Something to look for:** it fills a stretch only when the count before it is greater than zero
(and the count after it isn't negative). That works for fonts whose outer contours are all
clockwise, but a contour wound the other way on its own (test `16-R4-reversed`) stays empty. The
non-zero rule fills whenever the count isn't zero.
