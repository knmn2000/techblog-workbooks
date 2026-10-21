# 17 · Fill a glyph: non-zero rule

**Difficulty:** Hard · **Checkpoint** 17 of 18 · **Check:** `.\check 17`

**Tags**
- *Language:* sorting · solving a quadratic equation · floating-point care
- *Library:* `std::vector` · `std::sort` · `std::sqrt`
- *Concepts:* the non-zero winding rule · quadratic Bézier curves · implied on-curve points · curve direction · splitting curves at their y extremes

## Read in the blog first

This page is complete on its own; the blog tells the story behind it. Read the blog's
[Non-zero Rule](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Non-zero%20Rule)
section to the end, including the two cases where a scanline crosses one curve twice. Skip the
code blocks if you want to work it out yourself.

## Where this fits

Checkpoint 16 filled straight-line outlines with the non-zero rule. Real glyphs have curves, and a
curve can cross one scanline twice, going up at one crossing and down at the other. This checkpoint
fills full glyph outlines, curves included, which is what the text renderer in checkpoint 18 needs.

## The problem

Write a program that fills glyph outlines on a black canvas with the non-zero rule and writes the
picture as a PNG.

Only the picture is checked, so you can structure the code however you like. This checkpoint
adds to `render/NonZero.h` and `render/NonZero.cpp` (under `src/`), which you started in
checkpoint 16. It can build on `render/Scanline.h` and `utils/Geometry.h`.
`checkpoints/p17_nonzero_curves.cpp` is the program the checker runs: it reads the test input,
calls your code and writes the answer.

The program starts blank, with a comment and an empty `main`, so the includes, reading the input
and writing the output are yours. To start from working input/output code instead, pick
Boilerplate in the book's editor (or copy this checkpoint's files from `starters/boilerplate/`):
the declarations use the author's names where the post has them, and what's left to write is
`renderGlyphByNonZero`, now with curves.

### Input

The checker runs `<program> <input-file> <output-png>` from the workbook folder.

| Line | Meaning |
|---|---|
| `canvas <width> <height>` | The picture size in pixels |
| `place <x0> <baseline> <scale>` | Glyph point (x, y) goes to pixel position (x0 + scale·x, baseline − scale·y). y grows up in the glyph and down on the screen. |
| `color <r> <g> <b>` | The fill colour |
| `outline` | Starts an outline; its `ends` and `points` lines follow |
| `ends <e0> <e1> ...` | Index of the last point of each contour, counting from 0: contour k runs from the point after the previous end up to and including `e_k` |
| `points <x> <y> <on\|off> ...` | The outline's points; coordinates may be fractional |

There can be several outlines. Fill each one on its own, one after another, in the same colour.
Compound glyphs arrive already resolved into one outline (checkpoint 09's job).

### Output

A PNG (or binary PPM) of exactly `width` x `height` pixels, black to begin with. A pixel is painted
in the fill colour when its **centre** (px + 0.5, py + 0.5) is inside an outline by the non-zero rule.
The checker forgives edges that move by one pixel; missing or extra shapes and stray lines fail.

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

### From points to edges

Each contour is closed: after its last point it continues to its first.

- Two on-curve points in a row are joined by a straight line.
- An off-curve point is the control point of a quadratic Bézier curve from the previous on-curve
  point to the next one: B(t) = (1−t)²·P0 + 2(1−t)t·P1 + t²·P2 for t from 0 to 1.
- Between two off-curve points next to each other there is an **implied on-curve point** halfway
  between them.
- A contour can start with an off-curve point, or consist only of off-curve points.

### The non-zero rule with curves

Every edge has a direction, from a point to the next one. For each place a scanline crosses the
outline, note the x and whether the outline is going down or up the screen there (+1 or −1). Sort by
x, keep a running count from left to right, and fill wherever the count isn't zero.

**Where a piece crosses the scanline.** For a line, interpolate. For a curve piece, solve
y(t) = scanline y, a quadratic in t: a·t² + b·t + c = 0 with a = y0 − 2·y1 + y2, b = 2·(y1 − y0) and
c = y0 − scanline y (linear when a = 0). After the split below exactly one root lies in [0, 1]; its
x is (1−t)²·x0 + 2(1−t)t·x1 + t²·x2. Bisection on t also works, since each piece is monotone.

**A curve can cross one scanline twice.** At the bottom of a `U`, the curve goes down then up, so its
two crossings have opposite directions. Split each curve at the point where its y turns around:
for y(t) = (1−t)²·y0 + 2(1−t)t·y1 + t²·y2 that is t = (y0 − y1) / (y0 − 2·y1 + y2), when the
denominator isn't 0 and t is strictly between 0 and 1. Each piece then goes only up or only down,
crosses a scanline at most once, and its direction is simply whether its end is below its start.

**Vertices and touching scanlines.** Treat every piece as half-open in y: it counts at scanline y when
min(y_start, y_end) ≤ y < max(y_start, y_end). A scanline that just touches a curve's extreme then
counts it twice with opposite directions (the extreme is the smaller y of both pieces) or not at all
(the extreme is the larger y of both), which doesn't change the result either way.

**Clipping.** Crossings can lie far outside the canvas, especially at large scales. Clamp x to the
canvas before converting it to an integer pixel index: converting a huge double to `int` is
undefined behaviour in C++.

## Requirements

- **R1** Curved outlines fill exactly the pixels whose centre is inside.
- **R2** Implied on-curve points, and contours that start with or consist only of off-curve points.
- **R3** Where curved contours going the same way overlap, the overlap is filled.
- **R4** A contour going the opposite way inside another cuts a hole.
- **R5** A scanline that crosses one curve twice, or just touches it, is counted correctly.
- **R6** Several outlines are filled one after another; compound glyphs arrive as one outline.
- **R7** Placement and scale are applied; anything outside the canvas is clipped.

## Examples

### Example 1: a contour with no on-curve points (test `17-R2-all-off`)

```
input:   canvas 133 133
         place 6 126 1
         color 255 255 255
         outline
         ends 7
         points 119.53 60 off 102.1 17.9 off 60 0.47 off 17.9 17.9 off 0.47 60 off 17.9 102.1 off
                60 119.53 off 102.1 102.1 off
```

(The `points` line is one line in the real input.) Eight off-curve points, so all eight on-curve
points are implied midpoints. The curves between them make a circle:

![expected picture for 17-R2-all-off](tests/17/expected/17-R2-all-off.png)

### Example 2: two overlapping round shapes (test `17-R3-two-circles`)

```
input:   canvas 223 148
         place -1 149 1.5
         color 255 255 255
         outline
         ends 7 15
         points 95 50 on 95 5 off 50 5 on 5 5 off 5 50 on 5 95 off 50 95 on 95 95 off
                145 50 on 145 5 off 100 5 on 55 5 off 55 50 on 55 95 off 100 95 on 145 95 off
```

(One `points` line in the real input.) Two contours of four curves each, both going the same way,
overlap in the middle. The overlap has a
count of 2, so it is filled. With the even-odd rule it would be a hole.

![expected picture for 17-R3-two-circles](tests/17/expected/17-R3-two-circles.png)

### Example 3: overlapping strokes in a real glyph (test `17-R3-a-hiragana`)

U+3042 (あ) from Noto Sans JP is drawn as overlapping curved strokes, which is common in variable
fonts. Its outline has 106 points; `.\check 17 -Case 17-R3-a-hiragana` prints the full input.

![expected picture for 17-R3-a-hiragana](tests/17/expected/17-R3-a-hiragana.png)

## Constraints

- Canvases are at most about 560 x 560 pixels; outlines have at most a few hundred points.
- Every contour has at least 2 points.
- There are 24 tests: hand-made curved shapes for each rule, letters from JetBrains Mono Bold,
  characters from Noto Sans JP, and 7 random glyphs (new ones with `-Fresh`). Each case has 10
  seconds.

## Source material

- Wikipedia, [Nonzero-rule](https://en.wikipedia.org/wiki/Nonzero-rule)
- Pomax, [A Primer on Bézier Curves](https://pomax.github.io/bezierinfo/): extremities and splitting curves
- Apple, *TrueType Reference Manual*, [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html)
- The blog: [Non-zero Rule](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Non-zero%20Rule)

## Hints

<details><summary>Hint 1: where to start</summary>

Combine your checkpoint 14 (curves into edges, crossings per row) and checkpoint 16 (counting with
directions). The new part is giving each curve crossing the right direction.
</details>

<details><summary>Hint 2: the approach</summary>

Turn each contour into lines and curves in pixel coordinates. Split every curve at its y turning
point so each piece is monotone in y. Now every piece, line or curve, crosses a row at most once,
with a direction you can read from its endpoints. Then fill exactly as in checkpoint 16.
</details>

<details><summary>Hint 3: the traps</summary>

- After splitting, solve the piece's quadratic for the scanline y and keep the root in [0, 1]; if the
  quadratic coefficient is 0, the equation is linear.
- The direction of a curve piece is its end's y compared with its start's y, not the control point.
- Implied midpoints, and contours that start off-curve, as in checkpoint 14.
- Fill where the count is not zero, of either sign.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
pieces = []
for each contour (pixel coordinates, implied points inserted, starting on-curve):
    on->on:      pieces.append(line(a, b))
    on->off->on: split curve(a, c, b) at t = (a.y - c.y) / (a.y - 2c.y + b.y) if 0 < t < 1
                 pieces.extend(the one or two monotone curves)

for row in 0 .. height-1:
    y = row + 0.5
    crossings = []
    for p in pieces:
        if min(p.start.y, p.end.y) <= y < max(p.start.y, p.end.y):
            x = crossing x (line: interpolate; curve: solve for t in [0, 1], then B(t).x)
            crossings.append((x, +1 if p.end.y > p.start.y else -1))
    sort by x; walk with a running count; fill where count != 0
```
</details>

## Checking your solution

```
.\check 17                         run every test
.\check 17 -Case 17-R5-U           one test: its input, and where the expected and your pictures are
.\check 17 -Fresh                  new random glyphs (new seed)
.\check 17 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

## After you pass: compare with the author's code

The blog's [non-zero renderer](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Fixing%20the%20counting%20error%20of%20B%C3%A9zier%20curve)
doesn't split curves. When a scanline meets a curve twice, it decides the two directions from the
curve's convexity: the crossing nearer the curve's start gets one direction and the other crossing
gets the opposite. It scans only the rows inside the glyph's bounding box, and fills each component
of a compound glyph separately.

**Something to look for:** like the line-only version, it fills only where the count is positive,
so a contour wound the other way on its own would stay empty (checkpoint 16, test `16-R4-reversed`).
