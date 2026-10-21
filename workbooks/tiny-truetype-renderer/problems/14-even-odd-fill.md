# 14 · Fill a glyph: even-odd rule

**Difficulty:** Hard · **Assignment** 14 of 18 · **Check:** `.\check 14`

**Tags**
- *Language:* sorting · floating-point comparisons · solving a quadratic equation
- *Library:* `std::vector` · `std::sort` · `std::sqrt`
- *Concepts:* scanline filling · the even-odd rule · quadratic Bézier curves · implied on-curve points · half-open intervals

## Read in the blog first

This page is complete on its own; the blog tells the story behind it. Read the blog's
[Renderer: Filling Glyph](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Renderer%3A%20Filling%20Glyph)
section through [Removal of fill errors](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Removal%20of%20fill%20errors),
skipping the code blocks if you want to work it out yourself. The blog builds this in two steps
(a first version, then a fix for errors at vertices); here they are one assignment.

## Where this fits

A glyph is only an outline until it's filled. This assignment takes the outlines you decoded in
assignments 07 and 09 (your `GlyphComponent`) and paints their inside by the even-odd rule. The
row-by-row scanning goes in `render/Scanline`, which assignments 16 and 17 reuse for the non-zero
rule; assignment 18 then renders whole lines of text.

## The problem

Write a program that fills glyph outlines on a black canvas by the even-odd rule and saves the
picture as a PNG.

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

### Output

A PNG (or binary PPM) of exactly `width` x `height` pixels. Every pixel starts black (0, 0, 0). A
pixel is painted in the fill colour when its **centre** is inside an outline by the even-odd rule.
Pixel (px, py), with py counted down from the top, has its centre at screen position
(px + 0.5, py + 0.5), which is glyph point ((px + 0.5 − x0) / scale, (baseline − py − 0.5) / scale).

**The checker forgives edges that move by one pixel.** If you sample at the top of each row instead
of the centre, or round x differently, you still pass. Missing or extra shapes, holes in the wrong
place, and stray lines don't pass.

**Writing the picture.** Write it to the output path you're given. The name ends in `.png`, but
the checker looks at the contents, so either of these works:

- **A PNG.** Your `FrameBufferCanvas` from assignment 06 already does this in `writePng`, and the
  boilerplate calls it. Underneath, `third_party/stb_image_write.h` is on your project's include
  path: `#define STB_IMAGE_WRITE_IMPLEMENTATION` before including it in one file, then call
  `stbi_write_png(path, width, height, 3, pixels, width * 3)`.
- **A binary PPM**, the easiest to write by hand. The header is `P6`, the width, the height and
  `255`, separated by spaces or newlines and ended by one newline (for example
  `P6\n205 195\n255\n`). Then come 3 bytes per pixel (red, green, blue), row by row from the
  top-left. Open the file in binary mode (`std::ios::binary`), or Windows writes every pixel
  byte 10 as two bytes.

### From points to edges

Each contour is closed: after its last point it continues to its first. Walk the points in order,
as your `render/Outline` did when it drew curves in assignment 11:

- Two on-curve points in a row are joined by a straight line.
- An off-curve point is the control point of a quadratic Bézier curve from the previous on-curve
  point to the next on-curve point: B(t) = (1−t)²·P0 + 2(1−t)t·P1 + t²·P2 for t from 0 to 1.
- When two off-curve points are next to each other, there is an **implied on-curve point** exactly
  halfway between them. Each off-curve point then has on-curve points on both sides.
- A contour can start with an off-curve point, and can even consist only of off-curve points (then
  every on-curve point is implied).

### The even-odd rule

Draw a ray from the point to the right and count how many times it crosses the outline. An odd count
means inside, an even count means outside.

A **scanline** is a horizontal line through a row of pixel centres. With scanlines the rule
becomes, for each row:

1. Find every x where the scanline crosses an edge.
2. Sort them.
3. Fill between the 1st and 2nd, the 3rd and 4th, and so on.

**The trap: vertices on the scanline.** When a scanline passes exactly through a point where two
edges meet, a naive count sees that point twice and the rest of the row flips (a stray line), or it
misses a crossing it should count. A clean fix is to treat each edge as **half-open in y**:

- An edge from y0 to y1 counts at scanline y when min(y0, y1) ≤ y < max(y0, y1), with y measured
  on the screen (pixels, growing downward).
- Horizontal edges never count.

Then a vertex the outline passes through counts once. A pointed tip (both edges above, or both
below) counts twice or not at all, which leaves the parity right either way.

**Curves.** A quadratic curve can cross one scanline twice. Split each curve where its y turns
around: each piece then crosses a scanline at most once, and the half-open rule works for curves
too.

- For a curve P0, P1, P2 the turning point is at t = (P0.y − P1.y) / (P0.y − 2·P1.y + P2.y).
  Split there only when the denominator isn't 0 and t is strictly between 0 and 1. Otherwise the
  curve is already **monotone**: it only rises or only falls.
- Use the same split point, with the same y, for both halves.
- To find where a piece crosses scanline y, solve y(t) = y as a quadratic in t (linear when
  P0.y − 2·P1.y + P2.y = 0) and keep the root in [0, 1].

**Clipping.** Crossings can lie far outside the canvas. Clamp x to the canvas before converting it
to an integer, since converting a huge double to `int` is undefined behaviour in C++. Whatever fills
a stretch of a row (the boilerplate's `fillSpan`) should skip columns outside the canvas and do
nothing when the stretch is empty.

## Requirements

- **R1** Pixels whose centre is inside are filled; every other pixel stays black.
- **R2** A contour inside another is a hole and stays empty.
- **R3** Curves are followed exactly, with implied on-curve points and contours that start or stay
  off-curve.
- **R4** Vertices that sit exactly on a scanline are counted correctly (no stray lines).
- **R5** Where contours cross or overlap, the even-odd rule leaves the overlap empty.
- **R6** Several outlines are filled one after another (their union).
- **R7** Placement and scale are applied; anything outside the canvas is clipped.

## Examples

### Example 1: a pentagram (test `14-R5-star`)

```
input:   canvas 205 195
         place 2 206 2
         color 255 255 255
         outline
         ends 4
         points 50 100 on 79 9 on 2 65 on 98 65 on 21 9 on
```

One contour that crosses itself. Under even-odd the pentagon in the middle is covered twice, so it
stays black:

![expected picture for 14-R5-star](tests/14/expected/14-R5-star.png)

### Example 2: a vertex on a pixel centre (test `14-R4-diamond-half`)

```
input:   canvas 133 133
         place 5 128 1.5
         color 255 255 255
         outline
         ends 3
         points 41 1 on 1 41 on 41 81 on 81 41 on
```

A diamond with corners at (41, 1), (1, 41), (41, 81) and (81, 41), placed at scale 1.5. Every
corner lands exactly on a pixel centre, so the scanlines through those rows pass right through a
vertex. With the half-open rule the side corners count once (one edge above, one below) and the
top and bottom tips count twice or zero times. The result is a clean diamond with no stray
horizontal line:

![expected picture for 14-R4-diamond-half](tests/14/expected/14-R4-diamond-half.png)

### Example 3: crossing strokes (test `14-R5-ten`)

```
input:   canvas 234 238
         place -9 214 0.25
         color 255 255 255
         outline
         ends 3 7
         points 62 443 on 945 443 on 945 414 on 62 414 on 486 829 on 516 829 on 516 -70 on 486 -70 on
```

U+5341 (十) from Noto Sans JP is two overlapping rectangles. Even-odd leaves the small square where
they cross empty. Assignment 16 fills it with the non-zero rule.

![expected picture for 14-R5-ten](tests/14/expected/14-R5-ten.png)

## Constraints

- Canvases are at most about 560 x 560 pixels; outlines have at most a few hundred points.
- Outlines are well-formed: every contour has at least 2 points.
- There are 28 tests: hand-made shapes for each rule, letters from JetBrains Mono Bold at several
  scales, U+5341 from Noto Sans JP, and 6 random letters (new ones with `-Fresh`). Each case has 10
  seconds.

## Source material

- Wikipedia, [Even–odd rule](https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule)
- Apple, *TrueType Reference Manual*, [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html): on-curve and off-curve points
- Pomax, [A Primer on Bézier Curves](https://pomax.github.io/bezierinfo/): finding extremities and intersections
- The blog: [Even-odd Rule](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Even-odd%20Rule) and [Removal of fill errors](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Removal%20of%20fill%20errors)

## Hints

<details><summary>Hint 1: where to start</summary>

Turn the outline into a list of edges first (lines and quadratic curves, in pixel coordinates),
then fill row by row. Getting the edges right is half the job, and your `render/Outline` from
assignment 11 (drawing curves) already does most of it.
</details>

<details><summary>Hint 2: the approach</summary>

For each pixel row, take the horizontal line through the pixel centres (y = row + 0.5). Collect
the x of every place an edge crosses it, sort the list, and fill from the 1st crossing to the 2nd,
the 3rd to the 4th, and so on. A pixel is filled when its centre x (px + 0.5) is in one of those
ranges.
</details>

<details><summary>Hint 3: the traps</summary>

- Use half-open intervals in y (min ≤ y < max) so a shared vertex counts once; skip horizontal edges.
- Split each quadratic curve where its y turns around (t = (y0 − yc) / (y0 − 2·yc + y2), with yc
  the control point's y, when that t is strictly between 0 and 1), so each piece crosses a row at
  most once.
- Implied on-curve points: between two off-curve points, add their midpoint.
- A contour may start off-curve: start walking from an on-curve point (or an implied one).
- Remember y flips: pixel y = baseline − scale·glyph y.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
edges = []
for each contour:
    pts = points mapped to pixels, with midpoints inserted between consecutive off-curve points
    rotate pts so it starts at an on-curve point
    walk around: on->on adds a line; on->off->on adds a curve (split at its y turning point)

for row in 0 .. height-1:
    y = row + 0.5
    xs = []
    for e in edges:
        if min(e.y0, e.y1) <= y < max(e.y0, e.y1):
            xs.append(x where e crosses y)      # line: interpolate; curve: solve the quadratic in t
    sort xs
    for i in 0, 2, 4, ...:
        fill pixels px with xs[i] <= px + 0.5 < xs[i+1]
```
</details>

## Checking your solution

```
.\check 14                         run every test
.\check 14 -Case 14-R5-star        one test: its input, and where the expected and your pictures are
.\check 14 -Fresh                  new random letters (new seed)
.\check 14 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing picture comes with a diff image:

```
  R4  Vertices exactly on a scanline are counted correctly .................    4 / 5   FAILED
      x 14-R4-W  'W' at scale 0.5: vertices sharing a row
          26 extra pixels, e.g. (145, 115) should be black (beyond the 1-pixel edge tolerance).
          Diff: build/cases/14/14-R4-W.diff.png - red extra, blue missing, magenta wrong colour, yellow forgiven
```

## After you pass: compare with the author's code

The blog's [even-odd renderer](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Glyph%20rendering%20with%20Even-odd%20rule)
loops over every pixel row of the canvas and every point of the outline. It uses two helper
functions from assignments 12 and 13 to intersect the row with each line or curve, truncates the
crossing x to an integer, and draws horizontal lines between pairs. The scanline is the row's top
edge (integer y), not its centre. Its fix for vertices counts an edge only when the edge's lowest y
(on screen) is above the scanline, and handles curves that cross twice with a convexity check
(assignment 15 finds the curve's lowest point).

**Something to look for:** in the fixed version, the check for a curve's endpoint on the scanline
compares the row y with the endpoints' **x** coordinates, so that branch rarely does what it
intends.
