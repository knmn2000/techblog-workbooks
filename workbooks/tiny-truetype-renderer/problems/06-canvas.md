# 06 · Draw on a framebuffer

**Difficulty:** Medium · **Assignment** 6 of 18 · **Check:** `.\check 06`

**Tags**
- *Language:* [structs](#primer/struct-class) · [`std::vector`](#primer/vector) as a 2D grid · [integer division](#primer/integer-division) · [`std::swap`](#primer/utility) · [converting a float to an int](#primer/float-to-int) (rounding vs truncating)
- *Library:* [`stbi_write_png`](#primer/stb-image-write) from stb_image_write (the Boilerplate already calls it)
- *Concepts:* [framebuffer](#primer/framebuffer) · [row-major pixel layout](#primer/framebuffer) · [clipping](#primer/clipping) · [line rasterization along the longer axis](#primer/line-drawing) · [drawing order](#primer/framebuffer)

## Read in the blog first

You don't need the blog for this. If you do read it, take the blog's
[Preparation of a renderer](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Preparation%20of%20a%20renderer)
section up to and including the paragraph that starts "The line drawing algorithm", and stop before
the author's code that follows.

## Learning material

- [Pixels and RGB colour](#primer/pixel): `RGB` in `src/FrameBufferCanvas.h` is one `uint8_t`
  per channel, and the `point`, `rect` and `line` commands all end in a colour as `r g b`.
- [Framebuffer](#primer/framebuffer): `FrameBufferCanvas` stores its pixels row by row in
  `pixels_`, a `std::vector<RGB>`, so pixel (x, y) is at index `y * width + x`.
- [Clipping](#primer/clipping): `set` ignores coordinates outside the canvas, and `drawRect`
  starts and stops its loops at the canvas edges.
- [Drawing a line](#primer/line-drawing): the idea behind `drawLine`: walk the longer axis,
  work out the other coordinate from a `double` slope, stamp a square at each step.
- [PNG files](#primer/png): `writePng` saves the canvas as a PNG, the format of the expected
  pictures and of the diff pictures the checker writes.
- [Binary PPM files](#primer/ppm): the library-free alternative to PNG, written with an
  `std::ofstream` in binary mode.
- [`stb_image_write.h`](#primer/stb-image-write): `writePng` hands `pixels_.data()` to
  `stbi_write_png` with 3 channels and `width * 3` bytes per row.
- [`#define` and `#pragma`](#primer/preprocessor): `src/FrameBufferCanvas.cpp` defines
  `STB_IMAGE_WRITE_IMPLEMENTATION` before the stb include and quiets that header's warnings
  with `#pragma GCC diagnostic`.
- [Operator overloading](#primer/operator-overloading): `RGB` has a defaulted `operator==`, so
  two colours compare channel by channel.
- [`<cmath>`](#primer/cmath): `std::lround` rounds to the nearest whole number, which is how a
  point on your line becomes a pixel.
- [Converting a float to an int](#primer/float-to-int): rounding with `std::lround` and
  truncating with `static_cast<int>` both pass here, since the checker forgives an edge that
  moves by one pixel.
- [`<algorithm>`](#primer/algorithm): `std::min` and `std::max` are handy for keeping a square
  that hangs over the edge inside the canvas.
- [`<utility>`](#primer/utility): `std::swap` exchanges two values, and a line routine that
  wants a single stepping direction will reach for it.
- [`<cstdlib>`](#primer/cstdlib): `std::abs` gives the size of a difference, which is how to
  tell a steep line from a flat one.
- [`<optional>`](#primer/optional): the program declares `std::optional<FrameBufferCanvas> canvas`
  and calls `canvas.emplace(w, h)` once it has read the `canvas` line.
- [Integer division](#primer/integer-division): rounding down is what you want for `cx - w / 2` in
  `drawRect` and wrong for the line's slope, which needs a `double` division.
- [`static_assert`](#primer/static-assert): `FrameBufferCanvas.cpp` checks `sizeof(RGB) == 3` at
  compile time, matching the 3 bytes per pixel that `stbi_write_png` reads.
- [Debug builds](#primer/debug-build): the checker builds in Debug with GCC's bounds checks, so
  a write outside the canvas's vector stops the program instead of corrupting memory.
- [`static_cast`](#primer/static-cast): the program narrows each colour's `int` to a `uint8_t`
  with `static_cast`, and the canvas widens `width` to `std::size_t` before it multiplies.
- [Brace initialization](#primer/brace-init): the program builds a colour as `RGB{r, g, b}`,
  one value per member in order.

## Source material

- Wikipedia, [Digital differential analyzer (graphics algorithm)](https://en.wikipedia.org/wiki/Digital_differential_analyzer_(graphics_algorithm)): the line method used here
- Wikipedia, [Bresenham's line algorithm](https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm): the same idea with integers only
- stb, [stb_image_write.h](https://github.com/nothings/stb/blob/master/stb_image_write.h): the PNG writer (`third_party/stb`)
- The blog: [Preparation of a renderer](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Preparation%20of%20a%20renderer)

## Where this fits

Assignments 01 to 05 only read numbers. The six that draw (outlines in 08 and 11, filled
glyphs in 14, 16 and 17, the line of text in 18) all paint onto the framebuffer you build
here, in `src/FrameBufferCanvas.h` and `.cpp`: a grid of pixels in memory with three
operations (paint one pixel, fill a rectangle, draw a thick line) and a way to save it as a
PNG.

## The problem

Turn a list of drawing commands into a picture and save it as a PNG.

### Input

The checker runs `<program> <input-file> <output-file>` from the workbook folder, and the output
file name ends in `.png`. The input has one command per line, all values whole numbers.

| Line | Meaning |
|---|---|
| `canvas <w> <h>` | Always the first line: the picture is `w` pixels wide and `h` pixels tall, all black. |
| `point <x> <y> <r> <g> <b>` | Paint pixel (x, y) in colour (r, g, b). |
| `rect <cx> <cy> <w> <h> <r> <g> <b>` | A filled `w` x `h` rectangle centred on (cx, cy). |
| `line <ax> <ay> <bx> <by> <thickness> <r> <g> <b>` | A line from (ax, ay) to (bx, by), `thickness` pixels thick. |

Colours are 0 to 255 per channel. Coordinates can be negative or beyond the picture.

### Output

A PNG (or binary PPM) file of `w` x `h` pixels, 8 bits per channel, RGB (RGBA works too; the
checker ignores alpha). Pixel (0, 0) is the top-left corner, x grows to the right and y grows
downwards. A pixel that no command paints stays black (0, 0, 0).

Write the picture to the output path the checker passes you. It ends in `.png`, but the checker looks
at what is inside, so you have two options:

- A binary PPM, which needs no library: the header `P6`, the width, the height and
  `255`, separated by spaces or newlines and ended by one newline (for example
  `P6\n205 195\n255\n`), then 3 bytes per pixel (red, green, blue), row by row from the
  top-left. Open the file in binary mode (`std::ios::binary`), or Windows writes every pixel
  byte 10 as two bytes.
- A real PNG: `third_party/stb_image_write.h` in your project is on the include path.
  `#define STB_IMAGE_WRITE_IMPLEMENTATION` before including it in one file, then call
  `stbi_write_png(path, width, height, 3, pixels, width * 3)`.

### The commands, in order

Run the commands in file order. If two overlap, the later one paints over the earlier.

### Painting one pixel

`point x y ...` paints one pixel. If (x, y) is outside the picture (x < 0, y < 0, x ≥ w or
y ≥ h), nothing happens.

The rectangle and the line both paint through this operation, so its bounds check clips every
shape: one that crosses the edge of the picture keeps only the part inside.

### Drawing a rectangle

`rect cx cy w h ...` paints every pixel (x, y) with

| | from | to (included) |
|---|---|---|
| x | `cx - w/2` | `cx - w/2 + w - 1` |
| y | `cy - h/2` | `cy - h/2 + h - 1` |

where `w/2` and `h/2` round down. An odd size has a centre pixel in the middle. An even size
gives the left (or top) side one pixel more than the right (or bottom):

| w | columns, for cx = 100 |
|---|---|
| 1 | 100 |
| 4 | 98 ... 101 |
| 5 | 98 ... 102 |
| 50 | 75 ... 124 |

### Drawing a line

`line ax ay bx by t ...` stamps a `t` x `t` square (centred like a rectangle) at each step
along the line's longer direction:

1. If the line is steep, meaning |by - ay| > |bx - ax|, swap the roles of x and y for
   the steps below (step along y instead of x).
2. Step from the end with the smaller x to the end with the larger x, both ends included.
   With x = the step and (x1, y1), (x2, y2) the two ends in that order, the other coordinate
   is `y1 + (y2 - y1) / (x2 - x1) * (x - x1)`, worked out in floating point and rounded to
   the nearest whole number.
3. At each step, draw a `t` x `t` rectangle centred on (x, y) (on (y, x) for a steep line,
   swapping back).
4. If both ends are the same pixel, the line is a single square.

Truncating toward zero instead of rounding passes too, and a tie at .5 can go either way: the
checker forgives an edge that moves by one pixel. A missing piece, a gap or a shape in the
wrong place gets no such pass.

Do the slope in floating point. `(by - ay) / (bx - ax)` on ints is integer division and drops
the fraction.

### How the picture is compared

The checker loads your PNG and compares it with the expected picture pixel by pixel. A
differing pixel is forgiven only if it sits on an edge that moved by at most 1 pixel: extra ink
next to the same ink in the expected picture, or missing ink with the same ink next to it in
yours. Any other difference counts, and every test allows 0 of them.

A failing test gets a diff picture:

- red where you have extra ink;
- blue where ink is missing;
- magenta for the wrong colour;
- yellow for forgiven pixels.

## Requirements

One requirement per test. After a failing run the report counts passes for each requirement, and a
`likely cause` line can single out the one your difference looks like.

- **R1** The picture is `w` x `h` pixels, black wherever no command paints, with (0, 0) at
  the top-left and y growing downwards.
- **R2** `point` paints one pixel, in its colour.
- **R3** `rect` covers columns `cx - w/2` to `cx - w/2 + w - 1` and rows likewise, for even and
  odd sizes.
- **R4** `line` works in every direction (shallow, steep, horizontal, vertical, either end
  first), with both ends included and no gaps, and a zero-length line is one square.
- **R5** `line` stamps a `thickness` x `thickness` square at every step.
- **R6** A shape that crosses the edge of the picture keeps its inside part, and a shape with
  no pixel inside the picture draws nothing and doesn't crash your program.
- **R7** Later commands paint over earlier ones.

## Examples

### Example 1: the blog's demo scene (test `06-E2E-blog-demo`)

```
input:   canvas 500 500
         line 100 100 300 400 5 255 255 255
         line 400 200 50 300 2 200 0 0
         rect 200 400 50 50 0 200 0

output:  a 500 x 500 PNG
```

![The blog's demo: a thick white line, a thin red line crossing it, and a green square](../tests/06/expected/06-E2E-blog-demo.png)

The white line is steep (300 down, 200 across), so it steps along y. The red one runs right
to left, so your program swaps its ends before stepping along x. At the crossing, red wins
because it comes later.

### Example 2: even-sized rectangles (test `06-R3-even`)

```
input:   canvas 220 140
         rect 60 70 50 50 0 200 0
         rect 160 40 20 8 255 120 170
         rect 160 100 2 2 255 255 255
         point 60 70 255 255 255
         point 160 40 60 120 255

output:  a 220 x 140 PNG
```

The green square covers columns 60 - 25 = 35 to 35 + 49 = 84 and rows 45 to 94: 25 pixels
left of the centre column, 24 to the right. The pink bar takes columns 150 to 169 and rows 36
to 43, and the 2 x 2 square takes columns 159 to 160 and rows 99 to 100. Both points come
last, so they show on top of the rectangles' centres.

### Example 3: lines 1 to 3 pixels long (test `06-R4-short`)

```
input:   canvas 120 80
         line 10 10 11 10 1 255 255 255
         line 30 10 30 12 1 200 0 0
         line 50 10 52 13 1 0 200 0
         line 80 13 77 10 1 255 220 0
         line 10 50 13 49 1 0 220 220
         line 60 60 59 57 1 255 120 170

output:  a 120 x 80 PNG
```

Take the green line from (50, 10) to (52, 13). It goes 3 down and 2 across, so it is steep:
step y from 10 to 13 and work out x = 50 + 2/3 * (y - 10).

| y | x before rounding | x rounded | pixel |
|---|---|---|---|
| 10 | 50 | 50 | (50, 10) |
| 11 | 50.67 | 51 | (51, 11) |
| 12 | 51.33 | 51 | (51, 12) |
| 13 | 52 | 52 | (52, 13) |

Skip the swap and you step x from 50 to 52, paint 3 pixels and leave a gap.

## Constraints

- `w` and `h` run from 1 to 600, and so do rectangle sizes and line thicknesses (Hint 3 covers
  what that means for speed).
- Coordinates run from -1000 to 1000, so a line has at most a few thousand steps.
- A picture uses at most 15 colours, each far from the others and from black.
- Each case gets 10 seconds, and a correct solution needs milliseconds.
- 30 tests: the blog's demo, hand-made scenes for each requirement, and 5 random scenes.

## Hints

<details><summary>Hint 1: where to start</summary>

Get `set()` right first. It is the only function that touches the pixel array, so if it checks
the bounds, no shape can write outside the picture. After that `drawRect()` is two loops
calling `set()`, and `drawLine()` is one loop calling `drawRect()`.
</details>

<details><summary>Hint 2: the approach</summary>

Pixel (x, y) lives at index `y * width + x` of the vector. For the line, decide once whether
it is steep and, if so, swap x and y in both ends. Then swap the ends if the first has the
larger x. One case remains: x goes up by 1 per step, y changes by `slope` per step, and
`|slope| <= 1`. Swap x and y back when you stamp the square.
</details>

<details><summary>Hint 3: the traps</summary>

- The bounds check needs `x >= width`, not `x > width`. Index `y * width + width` is the first
  pixel of the next row, or past the end of the vector on the last row.
- Without the steep swap, a line close to vertical turns into a few dots.
- `(by - ay) / (bx - ax)` on ints is integer division. Convert to `double` first.
- A zero-length line has `bx - ax == 0`. Don't divide by it; draw one square.
- `w / 2` in the rectangle rounds down on purpose: it is integer division.
- Loop `x <= bx`, not `x < bx`, or the far end goes missing.
- A thick line stamps one rectangle per step, up to 600 x 600 pixels each, and most of a stamp
  can hang outside the canvas. Start and stop the rectangle's loops at the canvas edges so
  those pixels cost nothing. `set()` would drop them anyway, but one call at a time.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
set(x, y, c):
    if 0 <= x < width and 0 <= y < height: pixels[y * width + x] = c

drawRect(cx, cy, w, h, c):
    left = cx - w / 2;  top = cy - h / 2          # integer division
    for y in max(top, 0) .. min(top + h, height) - 1:          # only the rows inside the canvas
        for x in max(left, 0) .. min(left + w, width) - 1: set(x, y, c)

drawLine(ax, ay, bx, by, t, c):
    steep = |by - ay| > |bx - ax|
    if steep: swap(ax, ay); swap(bx, by)
    if ax > bx: swap(ax, bx); swap(ay, by)
    slope = (bx == ax) ? 0 : (by - ay) / double(bx - ax)
    for x in ax .. bx:
        y = round(ay + slope * (x - ax))
        if steep: drawRect(y, x, t, t, c) else: drawRect(x, y, t, t, c)
```
</details>

## Checking your solution

```
.\check 06                         run every test
.\check 06 -Case 06-R4-short       one test, showing its full input and where your picture is
.\check 06 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 06 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

Open your picture (`build/cases/06/<id>.out.png`), the expected one
(`tests/06/expected/<id>.png`) and the diff side by side. A failing run:

```
  R4  line in every direction (shallow, steep, axis-aligned), both ends... .    2 / 6   FAILED
      x 06-R4-steep  steep lines (|slope| > 1) going up and down: no gaps allowed
          570 pixels missing, e.g. (20, 12) should be white (beyond the 1-pixel edge tolerance). Diff: build/cases/06/06-R4-steep.diff.png - red extra, blue missing, magenta wrong colour, yellow forgiven
          likely cause: R4 - line in every direction (shallow, steep, axis-aligned), both ends included
          expected values from: reference drawing, checked against the ideal shapes (exact pixels for point/rect, true segment for line)
          reproduce: build/solutions/assignment_06.exe build/cases/06/06-R4-steep.in build/cases/06/06-R4-steep.out.png
```

## After you pass: compare with the author's code

[The blog's first `FrameBufferCanvas`](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Preparation%20of%20a%20renderer)
owns a one-dimensional array of `RGB` pixels (a `std::unique_ptr<RGB[]>`, filled with
`BLACK`). `set` writes a pixel and ignores coordinates outside the picture, `drawRect` takes
a centre and a size and clips its loops to the canvas, and `drawLine` does the steep swap,
orders the ends and stamps a `drawRect` at every step. `writePngFile` hands the buffer to
`stbi_write_png` with 3 channels, and the post's `main` draws the scene from Example 1. Your
Boilerplate keeps those names, except `writePng` for `writePngFile`, and adds `get`, which
reads a pixel back. The post's text also suggests overloads that take 2D vectors; the
author's repository has them for `drawLine` and `drawRect`, rounding the vector to the nearest
pixel with `std::lround`. They keep the glyph code in later sections short.

The post credits its line method to a Bresenham tutorial, but the snippet steps with a
floating-point slope: the DDA method from this page's sources. It adds the slope to `y` at
each step and turns `y` into a pixel with a plain cast. A cast truncates toward zero instead
of rounding, and the repeated additions pile up `float` error (on a line from (0, 0) to
(9, 3), nine additions of 3/9 end at y = 2.9999998, which truncates to 2, one row short of the
end point), so its lines can sit up to a pixel to one side. The tests accept both. If a
line's ends are the same pixel, the loop draws its one square and then divides 0 by 0 in
floating point. Nothing reads the result, so the line comes out as one square, as this page
asks.

In the post's snippet `RGB` holds three `unsigned` values of 4 bytes each, so a pixel takes 12
bytes, while `stbi_write_png` with 3 channels reads 3 bytes per pixel. The PNG would come out
scrambled. The author's repository declares the channels as `unsigned char`, which gives the 3
bytes the writer expects, and the Boilerplate's `uint8_t` channels and its
`static_assert(sizeof(RGB) == 3)` do the same.
