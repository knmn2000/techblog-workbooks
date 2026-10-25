# 11 · Draw an outline with curves

**Difficulty:** Medium · **Assignment** 11 of 18 · **Check:** `.\check 11`

**Tags**
- *Language:* walking a circular list with an [index modulo its length](#primer/integer-division) · a small [2D vector](#primer/vector-2d) struct · floating-point arithmetic, [rounding only at the end](#primer/float-to-int)
- *Library:* your [`FrameBufferCanvas`](#primer/framebuffer) from assignment 06 (`drawLine`, `drawRect`, `writePng`)
- *Concepts:* [quadratic Bézier curves](#primer/bezier) · [on-curve and off-curve points](#primer/on-off-curve) · [implied on-curve points](#primer/implied-point) · [flattening a curve](#primer/flattening) into short lines

## Read in the blog first

The blog covers this in its "Renderer: Curve Rendering" section, through [TrueType Bézier
curves](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=TrueType%20B%C3%A9zier%20curves),
up to the sentence that introduces the code. Reading it is optional. The author's code is what
follows that sentence.

## Learning material

- [On-curve and off-curve points](#primer/on-off-curve): a contour mixes the two kinds. Assignment
  08 joined every point with a line whatever its kind; here an on-curve point ends a straight
  line and an off-curve point is a curve's control point.
- [Implied on-curve points](#primer/implied-point): the midpoint of two off-curve points in a
  row. `renderGlyphCurves` gives each one a blue marker.
- [Flattening a curve](#primer/flattening): a curve goes onto the canvas as short straight lines,
  and `bezierLerp` from assignment 10 supplies the points between them.
- [Integer division and `%`](#primer/integer-division): contours are circular, and `%` is how an
  index past the last point wraps back to the first.
- [`<cmath>`](#primer/cmath): `std::hypot` for lengths and `std::ceil` for rounding up, which
  the piece count needs.

## Source material

- Apple, *TrueType Reference Manual*, [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html): quadratic curves, on-curve and off-curve points, and the implied point between two off-curve points
- FreeType, [Glyph Conventions: outlines](https://freetype.org/freetype2/docs/glyphs/glyphs-6.html): the same rules, with pictures
- Wikipedia, [Bézier curve: quadratic curves](https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B%C3%A9zier_curves)
- The blog: [TrueType Bézier curves](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=TrueType%20B%C3%A9zier%20curves)

## Where this fits

Assignment 08 drew every outline point-to-point with straight lines. Real TrueType contours also
have off-curve points, which pull the outline toward themselves without lying on it. You now
draw those as curves, with the curve function from assignment 10 in `utils/Geometry.h`.
Assignments 13, 14 and 17 fill glyphs from the same lines and curves.

## The problem

Read one or more glyph outlines and draw each with straight lines and quadratic curves. Every
point gets a coloured square, and the picture goes out as a PNG.

### Input

The checker runs `<program> <input-file> <output-file>` from the workbook folder and writes to a
name ending in `.png`. The input format is the one from assignment 08, except that `style` takes a
single number (no marker size):

| Line | Meaning |
|---|---|
| `canvas <w> <h>` | The first line of the file: the picture is `w` x `h` pixels, all black. |
| `place <x0> <baseline> <scale>` | Where the following outlines go (see below). |
| `style <lineThickness>` | Thickness of lines and curves, in pixels, for the following outlines. |
| `color <r> <g> <b>` | Colour of the lines and curves of the following outlines. |
| `outline` | Starts an outline. An `ends` line and a `points` line follow. |
| `ends <e0> <e1> ...` | Index of the last point of each contour, in increasing order. |
| `points <x> <y> <on\|off> ...` | Every point of the outline, in order, in font units. |

`place`, `style` and `color` come before the first `outline` and can change between outlines;
an outline uses the most recent ones. Coordinates may have a fractional part.

### Output

Same kind of file as in assignment 08: `w` x `h` pixels, RGB, PNG or binary PPM, with (0, 0) at the
top-left and y growing downwards.

Write it to the output path the checker gives you. Despite the `.png` name, the file can be a PNG or
a binary PPM, since the checker reads the contents.

- The PNG route: the boilerplate already calls `writePng`, a method of the `FrameBufferCanvas` you
  built in assignment 06.
- By hand, use the PPM layout from assignment 06: `P6`, the width and height, then `255`, separated
  by spaces or newlines, with one newline closing the header (for example `P6\n205 195\n255\n`).
  After it come the pixels as red, green and blue bytes, a row at a time from the top-left. Leave
  out `std::ios::binary` and Windows turns each byte 10 in the pixel data into two bytes.
- For a PNG without the canvas, `third_party/stb_image_write.h` is on your project's include path.
  Put `#define STB_IMAGE_WRITE_IMPLEMENTATION` before including it in one file, then call
  `stbi_write_png(path, width, height, 3, pixels, width * 3)`.

### From font units to pixels

A point (x, y) in font units sits at

```
px = x0 + scale * x
py = baseline - scale * y
```

Keep these as floating-point numbers. Work out curves and implied points from them, and round
to whole pixels only at the moment you draw. `FrameBufferCanvas::drawLine` from assignment 06
takes whole pixels, so round each end to the nearest pixel (`std::lround`) as you call it. A
cast to `int` cuts off the fraction instead of rounding.

Rounding every point first, as assignment 08 did, shifts a curve by less than a pixel, and that
passes too.

### Walking a contour

`ends` splits the points into contours as in assignment 08: contour 0 is points 0 to `e0`,
contour 1 is points `e0 + 1` to `e1`, and so on. A contour closes on itself, so its first point
follows its last.

Go round a contour with a current position, the point where the next piece starts. It is always
an on-curve point, real or implied. Each point you reach adds one piece that starts there:

| Point reached | The point after it | Piece | Current position becomes |
|---|---|---|---|
| on-curve | (doesn't matter) | a straight line to it | this point |
| off-curve | on-curve | a curve with this point as control point, ending at the point after it, which the walk then skips | the point after it |
| off-curve | off-curve | a curve with this point as control point, ending at the implied on-curve point halfway between the two | the implied point |

If two off-curve points follow each other, the outline passes through the point halfway
between them. The font doesn't store that point. It is an implied on-curve point, where one
curve ends and the next begins. The last and first points of a contour count as neighbours.

Every piece starts at an on-curve point, so start the walk at the contour's first on-curve
point and go round until you reach it again:

- if the contour's last point is on-curve, the final piece is a line back to the start;
- if it is off-curve, the final piece is a curve that ends at the start.

A contour with k off-curve control points gives k curves. If it has no on-curve point at all,
start at the implied point halfway between its last and first points.

The start rule matters for two kinds of contour:

- one whose first point is off-curve: its first curve starts at the contour's last on-curve
  point (or at the implied point between its last and first points), and never at (0, 0);
- one made only of off-curve points, such as a circle of 4 or 8 control points: a ring of curves
  joined at implied points.

### Drawing a curve

The quadratic Bézier curve from P0 to P2 with control point P1 is

```
B(t) = (1 - t)² P0 + 2 (1 - t) t P1 + t² P2,     t from 0 to 1
```

Draw it as `n` short straight lines from B((i - 1) / n) to B(i / n) for i = 1 to n, where

```
n = max(1, ceil(|P1 - P0| + |P2 - P1|))       lengths in pixels
```

A curve is never longer than its control polygon (P0 to P1 to P2), so each short line comes
out about a pixel long at most. More pieces are fine. Far fewer, such as a fixed 8, leave
visible corners on long curves.

Lines and curves share the thickness `lineThickness` and the outline's colour.

### Markers

Draw the markers after all the lines and curves of an outline: a square of size
`2 * lineThickness` on each point, rounded to the nearest pixel. The size is even, so the
square covers columns x − lineThickness up to x + lineThickness − 1 (and rows likewise), as
`FrameBufferCanvas::drawRect` from assignment 06 does: a 6 x 6 marker at x = 50 covers columns
47 to 52. The colour depends on the point:

| Point | Colour |
|---|---|
| every on-curve point of the input | red (255, 0, 0) |
| every off-curve point of the input | green (0, 255, 0) |
| every implied on-curve point | blue (0, 0, 255) |

Markers sit on top of the lines, so each square shows its full colour. Markers of different
colours don't overlap in the tests, so the order among them is free.

### How the picture is compared

The checker compares your PNG with the expected picture, pixel by pixel. The one allowance is for edges:
one that sits at most 1 pixel from where it should is forgiven, so small rounding differences pass.
A straight line where a curve belongs, a missing marker or a marker of the wrong colour fails.

A failing test's diff picture uses the colours from before: red for ink you added, blue for ink you left
out, magenta where the colour is wrong, yellow for pixels the tolerance forgave.

## Requirements

Each test exercises one of the requirements below. The failure report lists how many tests pass
under each, and a `likely cause` line may blame one of them.

- **R1** A straight line joins two on-curve points in a row, including the last and first
  point of a contour.
- **R2** An off-curve point between two on-curve points makes one quadratic curve between
  them, drawn as short lines.
- **R3** Two off-curve points in a row have an implied on-curve point halfway between them.
  One curve ends there and the next starts there, and the point gets a blue marker.
- **R4** Your program draws every piece of a contour that starts with an off-curve point or
  has no on-curve point, the closing curve included.
- **R5** Markers are `2 * lineThickness` squares on top of the lines: red on-curve, green
  off-curve, blue implied.
- **R6** `place` positions the points (x0 + scale * x, baseline - scale * y), and several
  outlines on one canvas each use their own `place`, `style` and `color`.

## Examples

### Example 1: two off-curve points in a row (test `11-R3-two-offs`)

```
input:   canvas 344 344
         place 12 332 0.8
         style 3
         color 255 255 255
         outline
         ends 3
         points 0 0 on 0 400 off 400 400 off 400 0 on

output:  a 344 x 344 PNG
```

![A white arch: two curves meeting at a blue marker at the top, closed by a straight line at the bottom](../tests/11/expected/11-R3-two-offs.png)

In pixels the points are A (12, 332) on, B (12, 12) off, C (332, 12) off and D (332, 332) on.
B and C are both off-curve, so the outline passes through the implied point halfway between
them, M = (172, 12). The pieces:

| Piece | From | Control | To | n |
|---|---|---|---|---|
| curve | A (12, 332) | B (12, 12) | M (172, 12) | 320 + 160 = 480 |
| curve | M (172, 12) | C (332, 12) | D (332, 332) | 160 + 320 = 480 |
| line | D (332, 332) | | A (12, 332) | |

Then the 6 x 6 markers: red on A and D, green on B and C, blue on M.

### Example 2: a contour that starts off-curve (test `11-R4-off-first`)

```
input:   canvas 384 294
         place 12 282 0.9
         style 3
         color 255 220 0
         outline
         ends 3
         points 300 0 off 400 200 on 200 300 on 0 100 off

output:  a 384 x 294 PNG
```

![expected picture for 11-R4-off-first](../tests/11/expected/11-R4-off-first.png)

In pixels: P0 (282, 282) off, P1 (372, 102) on, P2 (192, 12) on, P3 (12, 192) off. The first
on-curve point is P1, so start there and go round:

1. P2 is on-curve: a line P1 → P2.
2. P3 is off-curve and so is the next point, P0 (the walk has wrapped round): a curve from P2
   with control P3 to the implied point (147, 237).
3. P0 is off-curve and the next point, P1, is on-curve: a curve from (147, 237) with control
   P0 back to P1.

Start at P0 with a "previous point" of (0, 0) and you draw the first curve from (12, 282),
where font (0, 0) lands, and lose the curve from the implied point into P1.

### Example 3: only off-curve points (test `11-R4-circle4`)

```
input:   canvas 344 344
         place 12 332 0.8
         style 3
         color 255 255 255
         outline
         ends 3
         points 0 0 off 0 400 off 400 400 off 400 0 off

output:  a 344 x 344 PNG
```

![A white circle through four blue markers, with four green markers at the corners of a square around it](../tests/11/expected/11-R4-circle4.png)

No on-curve point, so the walk starts at the implied point between the last and first points:
halfway between (332, 332) and (12, 332), which is (172, 332). Each of the 4 points is the
control point of one curve, and the 4 curves meet at 4 implied points (blue).

## Constraints

- Canvas size `w` x `h` is at most 600 x 600, and every outline lies inside it.
- Contours have 3 points or more, and an outline has a few hundred points at most.
- Past 10 seconds a case fails, though a correct solution takes only milliseconds.
- 27 tests: glyphs from JetBrains Mono Bold (`-`, `A`, `B`, `D`, `S`, `a`, `g`,
  `o`), Nerd Font icons from the same file whose contours start off-curve or have no
  on-curve point (U+F111, U+F10C, U+E3A2, U+F00C, U+F042), `a` and U+5341 十 from Noto Sans JP,
  hand-made outlines and 3 random outlines.

## Hints

<details><summary>Hint 1: where to start</summary>

Open the expected pictures for Example 1 and Example 3 first. The blue markers show where
curves join. Then write `drawQuadratic()` and test it on Example 1's numbers. After that, copy
your loop from assignment 08 and change what happens at an off-curve point.
</details>

<details><summary>Hint 2: the approach</summary>

Convert the contour's points to pixels (as floats) and index them modulo the contour's length,
so the point after the last is the first. Keep a `current` position, where the next piece
starts. Find the first on-curve point and start there, or at the midpoint of the last and first
points if there is none. Then go round, one lap, and for each point after the start: an
on-curve point ends a straight line; an off-curve point ends a curve at the next point if that
one is on-curve (skip it, since the curve used it), or at the midpoint with the next point
otherwise. After each piece, `current` becomes the end of what you drew. Collect the markers as
you go and draw them after the loop.
</details>

<details><summary>Hint 3: the traps</summary>

- Don't start the walk at point 0 with `current = (0, 0)`. A contour whose first point is
  off-curve then starts its first curve in the wrong place and loses its closing curve.
- A contour can have no on-curve point at all (`fa-circle`, U+F111, is 8 off-curve points).
  Make sure your search for a starting on-curve point can't loop forever or run off the end.
- After a curve that ends at a real on-curve point, don't draw a line to that point again.
- The midpoint test applies across the wrap too: the last and first points of a contour are
  neighbours.
- Draw markers after all lines, or later lines cross earlier markers.
- Take the piece count from pixel positions. From font units, `n` would be far too big at a
  small scale (still correct, but slow) or too small at a large one.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
drawQuadratic(p0, p1, p2):
    n = max(1, ceil(|p1 - p0| + |p2 - p1|))
    prev = p0
    for i in 1 .. n:
        t = i / n
        next = (1-t)² p0 + 2(1-t)t p1 + t² p2
        drawLine(prev, next, lineThickness, color)
        prev = next

drawOutline(outline):
    markers = []
    for each contour (pixel points q[0..m-1], q[k] means q[k mod m]):
        s = index of the first on-curve point, or none
        if s exists: current = q[s]; k = s + 1; stop = s + m + 1
        else:        current = mid(q[m-1], q[0]); k = 0; stop = m
        while k < stop:
            if q[k] is on:        drawLine(current, q[k]); current = q[k]; k += 1
            elif q[k+1] is on:    drawQuadratic(current, q[k], q[k+1]); current = q[k+1]; k += 2
            else:                 mid = mid(q[k], q[k+1]); drawQuadratic(current, q[k], mid); current = mid; k += 1
        for i in 0 .. m-1:
            add marker (q[i], red if on else green)
            if q[i] and q[i+1] are both off: add marker (mid(q[i], q[i+1]), blue)
    for each marker: drawRect(round(x), round(y), 2 * lineThickness, 2 * lineThickness, colour)
```
</details>

## Checking your solution

```
.\check 11                         run every test
.\check 11 -Case 11-R4-off-first   one test, showing its full input and where your picture is
.\check 11 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 11 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

Open your output (`build/cases/11/<id>.out.png`), the expected image
(`tests/11/expected/<id>.png`) and the diff the checker writes. A failure report looks like this:

```
  R3  Two off-curve points in a row: implied on-curve point halfway (blue) .    0 / 4   FAILED
      x 11-R3-two-offs  hand-made: two off-curve points in a row, implied point between them
          2263 pixels missing, e.g. (169, 9) should be blue; 2353 extra pixels, e.g. (306, 11) should be black (beyond the 1-pixel edge tolerance). Diff: build/cases/11/11-R3-two-offs.diff.png - red extra, blue missing, magenta wrong colour, yellow forgiven
          likely cause: R3 - Two off-curve points in a row: implied on-curve point halfway (blue)
          expected values from: hand-made outline; reference drawing, checked against fontTools' pieces and implied points
          reproduce: build/solutions/assignment_11.exe build/cases/11/11-R3-two-offs.in build/cases/11/11-R3-two-offs.out.png
```

## After you pass: compare with the author's code

[The blog's curve renderer](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Glyph%20outline%20rendering%20with%20curves)
swaps the start position for a transform matrix: `setGlyphBaseline` moves the glyph to its
baseline and `transformVec2` maps a point to the picture. The new `renderGlyphOutline` walks
each contour once, and `drawBezier` flattens a curve with `quadBezierLerp`, taking the ceiling
of the control polygon's length as the number of pieces, as this page does. Its markers are
twice the line thickness and coloured red, green and blue, as here.

Its walk keeps a "previous point" that starts at (0, 0) and isn't reset between contours. A
contour whose first point is off-curve therefore starts its first curve from that stale point
and skips its real closing curve. The JetBrains Mono Nerd Font has over two thousand such
contours, most of them in icons, and R4's tests cover them. The snippet also draws each marker
inside the walk, so a line drawn later can cross an earlier marker. Here all markers go last.

Markers have a second quirk. After every off-curve point the snippet puts a blue marker on the
end of the curve, whether that end is an implied point or a real on-curve one. Most real points
get their red marker later in the walk, drawn over the blue. A contour's first point gets its
red one before the walk comes back round, so when the contour's last point is off-curve, that
first point stays blue. JetBrains Mono has about 16,500 such contours, both contours of `a` in
test `11-R5-big-markers` among them. R5 asks for red there, because the font says it's a real
on-curve point.

The blog's prose marks on-curve points in white, and its code uses red, as this page does. The
author's repository also multiplies the transform by a `scale` (`scale * transformMat`), which
scales the start position and baseline along with the glyph, so both count in font units there.
