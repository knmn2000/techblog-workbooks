# Drawing and geometry

How a picture is held in memory and saved, and the geometry the renderer uses to draw lines and
curves and to fill glyphs: interpolation, Bézier curves, intersections and fill rules.

## Pixels and RGB colour
<!--
id: pixel
also: pixel; RGB; colour; color; 8 bits per channel; 24-bit colour; channel; RGB struct
-->
A digital picture is a grid of pixels, small squares that each have one colour. A colour is
three numbers, the amounts of red, green and blue light (RGB), each stored in 8 bits, so each
channel runs from 0 to 255:

| Colour | r, g, b |
|---|---|
| black | 0, 0, 0 |
| white | 255, 255, 255 |
| red | 255, 0, 0 |
| yellow | 255, 255, 0 |

Three channels of 8 bits give 24 bits per pixel and about 16.7 million colours. An image file
or a PNG writer often wants the pixels as one run of bytes, red, green, blue, red, green, blue,
and so on, so the pixel type should be those 3 bytes and nothing more (see
[structs](#primer/struct-class), [`static_assert`](#primer/static-assert) and
[`sizeof`](#primer/sizeof)):

```cpp
struct RGB { uint8_t r = 0, g = 0, b = 0; };
static_assert(sizeof(RGB) == 3);   // no padding: a vector of RGB is the byte run the writer wants
```

A channel type wider than a byte, such as `unsigned`, makes each pixel 12 bytes, and a writer
that expects 3 bytes per pixel reads garbage.

Assignment 06 defines `RGB` in `src/FrameBufferCanvas.h` with [`uint8_t`](#primer/cstdint)
channels, and `FrameBufferCanvas.cpp` checks its size with that `static_assert`. Every drawing
assignment's input gives colours as `r g b` from 0 to 255.

Learn more:
- [Pixel](https://en.wikipedia.org/wiki/Pixel) on Wikipedia
- [RGB color model](https://en.wikipedia.org/wiki/RGB_color_model) on Wikipedia, with the 24-bit
  representation

## Framebuffer
<!--
id: framebuffer
also: frame buffer; canvas; pixel buffer; row-major; row-major order; pixel index; drawing order; FrameBufferCanvas
-->
A framebuffer is a block of memory that holds one picture, one colour per pixel. Drawing means
writing colours into it, and saving the picture means writing the block to a file.

Memory is one long line of bytes, so the pixels go in row-major order: the whole top row
from left to right, then the next row, and so on. Pixel (x, y) of a picture `width` pixels wide
sits at index `y * width + x`:

```
a picture 4 pixels wide and 3 high, index = y * 4 + x
row 0:   0   1   2   3
row 1:   4   5   6   7
row 2:   8   9  10  11      pixel (1, 2) is at index 2 * 4 + 1 = 9
```

In C++ the block is a [`std::vector<RGB>`](#primer/vector) of `width * height` elements.

Picture coordinates put (0, 0) at the top-left corner, with x growing to the right and y growing
downwards (see [Font coordinates and screen coordinates](#primer/screen-coordinates)).

Drawing order matters. A later write replaces an earlier one, so when shapes overlap, the one
drawn last shows. The workbook draws in input order: in assignment 06 a later command paints
over an earlier one, and in assignment 11 the markers go on top of the lines.

Assignment 06 builds the framebuffer, `FrameBufferCanvas` in `src/FrameBufferCanvas.h` and
`.cpp`, with a `std::vector<RGB>` stored top row first. Every later picture is drawn on it, from
the outlines of assignment 08 to the text of 18.

Learn more:
- [Framebuffer](https://en.wikipedia.org/wiki/Framebuffer) on Wikipedia
- [Row- and column-major order](https://en.wikipedia.org/wiki/Row-_and_column-major_order) on
  Wikipedia, with the address formula

## Clipping
<!--
id: clipping
also: clip; bounds check; out of bounds; off-canvas; clamping to the canvas
-->
Clipping keeps drawing inside the picture. A shape can reach past the edge, a line from
(−50, 10) to (300, 10) on a 200-pixel-wide canvas for example, and only its inside part should
appear. Without clipping, a pixel outside the picture doesn't disappear: `pixels[y * width + x]`
with x past the right edge lands on the next row, and an index past the end of the vector is
undefined behaviour.

```
canvas 200 pixels wide, pixel (200, 10), one past the right edge:
index = 10 * 200 + 200 = 2200, which is pixel (0, 11), the first pixel of the next row
```

The simplest clipping lives in the function that paints one pixel: it ignores coordinates
outside the picture. If every shape paints through that function, every shape is clipped.

For a fill there's a second trap. A crossing point can lie far outside the canvas, and
converting a `double` too large for `int` is undefined behaviour in C++ (see
[converting a float to an int](#primer/float-to-int)). Clamp the value to the canvas first,
with `std::clamp` from [`<algorithm>`](#primer/algorithm), then convert it.

Assignment 06's `FrameBufferCanvas::set` ignores pixels outside the canvas (requirement R6 tests
shapes that cross the edge or lie outside). The fills from assignment 14 on turn crossing x
values into pixel columns, so they meet the second trap.

Learn more:
- [Clipping (computer graphics)](https://en.wikipedia.org/wiki/Clipping_%28computer_graphics%29) on
  Wikipedia
- [Floating-integral conversions](https://en.cppreference.com/w/cpp/language/implicit_conversion#Floating%E2%80%93integral_conversions)
  on cppreference, on converting a `double` that doesn't fit

## PNG files
<!--
id: png
also: PNG; Portable Network Graphics; image file; stb_image_write; writePng
-->
PNG is a common image file format. It stores a picture without losing detail (lossless) and
compresses it with DEFLATE, the method behind zip files. A PNG file starts with an 8-byte
signature, then a series of chunks: a header with the size and colour type, compressed pixel
data, and an end marker, each with a CRC checksum. Writing that by hand means writing a
compressor and a CRC, so programs use a library.

The workbook ships one: [`stb_image_write.h`](#primer/stb-image-write), a single-file library
by Sean Barrett. One `.cpp` file defines `STB_IMAGE_WRITE_IMPLEMENTATION` before it includes the
header, which puts the code in that file; other files include it without the define.

```cpp
// 3 channels (RGB), and each row is width * 3 bytes long in memory; returns 0 on failure
stbi_write_png(path, width, height, 3, pixels, width * 3);
```

The [checker](#primer/checker) reads your picture's contents, not its name, so a
[binary PPM](#primer/ppm) passes as well. When a test fails, it writes a diff picture as a PNG:
red for extra ink, blue for missing ink, magenta for the wrong colour, yellow for pixels it
forgave.

Assignment 06's `FrameBufferCanvas::writePng` calls `stbi_write_png` (the Boilerplate already
does), and every later drawing assignment saves its picture through it.

Learn more:
- [PNG](https://en.wikipedia.org/wiki/PNG) on Wikipedia, with the file structure
- [stb_image_write.h](https://github.com/nothings/stb/blob/master/stb_image_write.h) on GitHub,
  whose comments document `stbi_write_png`

## Binary PPM files
<!--
id: ppm
also: PPM; P6; Netpbm; portable pixmap
-->
PPM is about the simplest image format there is, which makes it handy when you don't want a
library. A binary PPM file is a short text header followed by the raw pixel bytes:

- the two characters `P6`
- the width and the height, in decimal
- the largest channel value, `255`
- one whitespace character (usually a newline), then 3 bytes per pixel, red, green, blue, row by
  row from the top-left

The header fields are separated by spaces or newlines, so `P6\n205 195\n255\n` starts a
205 x 195 picture.

```cpp
std::ofstream out(path, std::ios::binary);
out << "P6\n" << width << ' ' << height << "\n255\n";
out.write(reinterpret_cast<const char*>(pixels.data()), pixels.size() * 3);
```

Open the file in binary mode (see [`<fstream>`](#primer/fstream)). In text mode Windows turns
every byte 10 (a newline) into the two bytes 13 10, and every pixel after it shifts.

Every drawing assignment, from 06 on, accepts a binary PPM in place of a [PNG](#primer/png),
since the checker reads the contents and ignores the `.png` name. Fewer image viewers open PPM
files than PNG files, so a PNG is easier to look at.

Learn more:
- [PPM format specification](https://netpbm.sourceforge.net/doc/ppm.html) from the Netpbm project
- [Netpbm](https://en.wikipedia.org/wiki/Netpbm) on Wikipedia, on the family of formats

## Drawing a line: DDA and Bresenham
<!--
id: line-drawing
also: line rasterization; DDA; digital differential analyzer; Bresenham; steep line; thick line; drawLine; one-pixel tolerance
code: \bdrawLine\b
-->
A line on a pixel grid is a run of pixels, one per step along the line's longer direction. If
the line is shallow (it changes more in x than in y), step through every x from one end to the
other and work out y; if it is steep, swap the roles of x and y. Stepping along the shorter
direction would leave gaps.

The DDA (digital differential analyzer) works out the other coordinate in
[floating point](#primer/floating-point) and rounds it to the nearest pixel (see
[`<cmath>`](#primer/cmath)). For a line from (0, 0) to (5, 2), y grows by 2 / 5 = 0.4 per
column. With `int` operands, 2 / 5 is 0 (see [integer division](#primer/integer-division)), so
compute it in `double`:

```
x:           0     1     2     3     4     5
exact y:     0   0.4   0.8   1.2   1.6     2
rounded y:   0     0     1     1     2     2
```

Bresenham's algorithm draws the same pixels with integers only: it keeps an error term and adds
whole numbers to it at each step. It was faster on old hardware; on a modern machine either is
fine.

The workbook draws a thick line by stamping a square of `thickness` x `thickness` pixels at each
step. Rounding y to the nearest pixel or truncating it can move a line by one pixel, and the
checker allows for that: it forgives a differing pixel when it sits on an edge that moved by at
most 1 pixel, and counts gaps and missing pieces.

Assignment 06 writes `drawLine` in `src/FrameBufferCanvas.cpp`. Assignment 08 draws outlines
with it, and assignment 11 draws each [flattened](#primer/flattening) curve as a chain of short
lines.

Learn more:
- [Digital differential analyzer (graphics algorithm)](https://en.wikipedia.org/wiki/Digital_differential_analyzer_%28graphics_algorithm%29)
  on Wikipedia
- [Bresenham's line algorithm](https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm) on
  Wikipedia
- [Line drawing on a grid](https://www.redblobgames.com/grids/line-drawing/) by Red Blob Games,
  an interactive explanation

## Font coordinates and screen coordinates
<!--
id: screen-coordinates
also: screen coordinates; pixel coordinates; image coordinates; y axis flip; y down; y up; placement; Placement; font units to pixels; pixel centre
code: \bPlacement\b
-->
Font coordinates and picture coordinates point y in opposite directions. In a font, (0, 0) is
the glyph's origin on the baseline and y grows upwards. In a picture, (0, 0) is the top-left
corner and y grows downwards, row by row.

To place a glyph, pick the pixel column where font x = 0 lands (x0), the pixel row of the
baseline, and a scale in pixels per font unit. A font point (x, y) then lands at

```
px = x0 + scale * x
py = baseline - scale * y
```

The minus sign flips y: a point above the baseline (y > 0) gets a smaller row number, higher up
the picture, and a descender (y < 0) ends up below the baseline row.

<svg viewBox="0 0 420 230" role="img" aria-label="A canvas with pixel (0, 0) at the top-left and y growing down; the font origin sits at (x0, baseline) with y growing up" style="width:100%;max-width:420px;height:auto">
<rect x="20" y="20" width="380" height="190" fill="none" stroke="var(--rule)" stroke-width="2"/>
<line x1="20" y1="20" x2="100" y2="20" stroke="var(--muted)" stroke-width="3"/>
<polygon points="100,14 112,20 100,26" fill="var(--muted)"/>
<line x1="20" y1="20" x2="20" y2="90" stroke="var(--muted)" stroke-width="3"/>
<polygon points="14,90 20,102 26,90" fill="var(--muted)"/>
<text x="120" y="25" font-size="13" fill="var(--muted)">pixel x</text>
<text x="28" y="100" font-size="13" fill="var(--muted)">pixel y</text>
<text x="8" y="14" font-size="13" fill="var(--muted)">(0, 0)</text>
<line x1="20" y1="160" x2="400" y2="160" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="6 5"/>
<text x="395" y="152" text-anchor="end" font-size="13" fill="var(--muted)">baseline row</text>
<line x1="150" y1="160" x2="150" y2="62" stroke="var(--fig-a)" stroke-width="3"/>
<polygon points="144,62 150,50 156,62" fill="var(--fig-a)"/>
<line x1="150" y1="160" x2="262" y2="160" stroke="var(--fig-a)" stroke-width="3"/>
<polygon points="262,154 274,160 262,166" fill="var(--fig-a)"/>
<text x="158" y="58" font-size="13" fill="var(--fig-a)">font y</text>
<text x="278" y="176" font-size="13" fill="var(--fig-a)">font x</text>
<line x1="230" y1="95" x2="230" y2="160" stroke="var(--fig-b)" stroke-width="1.5" stroke-dasharray="4 4"/>
<line x1="230" y1="95" x2="150" y2="95" stroke="var(--fig-b)" stroke-width="1.5" stroke-dasharray="4 4"/>
<circle cx="230" cy="95" r="6" fill="var(--fig-b)"/>
<text x="240" y="92" font-size="13" fill="var(--ink)">(x, y) in font units</text>
<text x="190" y="178" text-anchor="middle" font-size="13" fill="var(--ink)">scale·x</text>
<text x="145" y="132" text-anchor="end" font-size="13" fill="var(--ink)">scale·y</text>
<text x="145" y="198" text-anchor="end" font-size="13" fill="var(--ink)">(x0, baseline)</text>
<circle cx="150" cy="160" r="4" fill="var(--ink)"/>
</svg>

The fills test pixels at their centres: pixel (px, py) covers the square from (px, py) to
(px + 1, py + 1), and its centre is (px + 0.5, py + 0.5).

`Placement` in `src/render/Placement.h` holds x0, baseline and scale, with the scale in pixels
per [font unit](#primer/font-units). Assignment 08 introduces it, and assignment 18 moves its x0
along the line as the [pen](#primer/baseline) advances. This placement is a small
[affine transform](#primer/affine-transform).

Learn more:
- [Converting FUnits to pixels](https://learn.microsoft.com/en-us/typography/opentype/spec/ttch01#converting-funits-to-pixels)
  in the OpenType specification's TrueType fundamentals
- [Glyph metrics](https://freetype.org/freetype2/docs/glyphs/glyphs-3.html) in the FreeType
  glyph conventions, with the font's y axis pointing up

## Affine transforms and 2 x 2 matrices
<!--
id: affine-transform
also: affine transformation; transformation matrix; 2x2 matrix; linear map; translation; composing transforms; rotation; scaling; shear
-->
An affine transform moves every point of a shape by the same rule: a 2 x 2 matrix part that can
scale, flip, rotate or shear, plus an offset that slides the result. With six numbers a, b, c,
d, e, f:

```
x' = a*x + c*y + e
y' = b*x + d*y + f
```

Some 2 x 2 parts: a = d = 2 doubles the size; a = −1, d = 1 mirrors left to right; a = d = 0,
b = 1, c = −1 turns a quarter turn counter-clockwise (in y-up coordinates). Straight lines stay
straight and midpoints stay midpoints, so you can transform a Bézier curve by transforming its
three points.

Two transforms in a row make one transform. Applying an inner transform T1 and then an outer T2
gives a new 2 x 2 part, the matrix product of the outer and the inner, and a new offset, the
inner offset put through the outer 2 x 2 part plus the outer offset. Order matters: scaling by 2
and then moving by 10 differs from moving by 10 and then scaling by 2.

```
p' = M2 (M1 p + t1) + t2 = (M2 M1) p + (M2 t1 + t2)
```

The workbook uses affine transforms twice. A [component transform](#primer/component-transform)
in assignment 09 places each part of a compound glyph, and nested compound glyphs compose them
from the inside out. The font-to-pixel [placement](#primer/screen-coordinates) from assignment
08 is affine as well: a = scale, d = −scale, b = c = 0, e = x0, f = baseline.

Learn more:
- [Affine transformation](https://en.wikipedia.org/wiki/Affine_transformation) on Wikipedia
- [Transformation matrix](https://en.wikipedia.org/wiki/Transformation_matrix) on Wikipedia, with
  the 2D rotation, scaling, shearing and reflection matrices

## 2D vectors and the dot product
<!--
id: vector-2d
also: vector; Vec2; point; 2D vector; dot product; normal vector; perpendicular
-->
A 2D vector is a pair of numbers (x, y). The same pair can mean a position (a point) or a step
from one point to another (a direction with a length). Subtracting two points gives the step
between them, and adding a step to a point gives another point. A small struct with `+`, `-` and
multiplication by a number ([operator overloading](#primer/operator-overloading)) makes geometry
code read like the formulas:

```cpp
struct Vec2 { double x = 0, y = 0; };
Vec2 operator+(Vec2 a, Vec2 b) { return {a.x + b.x, a.y + b.y}; }
Vec2 operator-(Vec2 a, Vec2 b) { return {a.x - b.x, a.y - b.y}; }
Vec2 operator*(Vec2 v, double s) { return {v.x * s, v.y * s}; }
```

The length of v is `std::hypot(v.x, v.y)` (see [`<cmath>`](#primer/cmath)).

The dot product of u and v is `u.x * v.x + u.y * v.y`. It is 0 when the two are perpendicular.
That gives a test for "is X on this line": take the line's direction d = l2 − l1 and the
perpendicular K = (d.y, −d.x), a normal vector of the line. X is on the line if and only if
K · (X − l1) = 0.

The workbook's `Vec2` lives in `src/utils/Geometry.h` from assignment 10, where
[lerp](#primer/lerp) and the [Bézier curve](#primer/bezier) use it. Assignment 12 adds the
[cross product](#primer/cross-product), and assignment 13 uses the normal vector and the dot
product to turn a line and a curve into one equation.

Learn more:
- [Basic geometry](https://cp-algorithms.com/geometry/basic-geometry.html) on cp-algorithms, on
  points, vectors and the dot product in code
- [Dot product](https://en.wikipedia.org/wiki/Dot_product) on Wikipedia

## Linear interpolation (lerp)
<!--
id: lerp
also: lerp; linear interpolation; interpolate; mix; parameter t
-->
Linear interpolation finds the point a fraction t of the way from a to b:

```
lerp(a, b, t) = a + (b - a) * t
```

t = 0 gives a, t = 1 gives b, t = 0.5 the midpoint, and values in between move along the
straight segment at a steady rate. For points, apply it to x and to y. It counts from a:
`lerp(a, b, 0.25)` lands near a, `lerp(b, a, 0.25)` near b.

The same formula answers the opposite question. To find where a straight edge from p to q
crosses the row y, solve for t, then interpolate x:

```
edge from p = (2, 0) to q = (6, 8), row y = 2
t = (2 - 0) / (8 - 0) = 0.25
x = 2 + (6 - 2) * 0.25 = 3
```

The division needs an edge that isn't horizontal; a horizontal edge never counts as crossing a
row (see [Half-open edges](#primer/half-open)).

In [floating point](#primer/floating-point), `a + (b - a) * t` at t = 1 can miss b by a
rounding error; the form `(1 - t) * a + t * b` returns b. The workbook's checkers allow 0.001, so
either passes.

Assignment 10 writes `lerp` in `src/utils/Geometry.h`. The [Bézier curve](#primer/bezier) in the
same assignment is three lerps, and the fills from assignment 14 on interpolate to find where a
straight edge crosses each row.

Learn more:
- [Linear interpolation](https://en.wikipedia.org/wiki/Linear_interpolation) on Wikipedia,
  including the two floating-point forms
- [Line drawing on a grid](https://www.redblobgames.com/grids/line-drawing/) by Red Blob Games,
  which builds line drawing from lerp

## Quadratic Bézier curves
<!--
id: bezier
also: Bezier; Bézier curve; quadratic curve; control point; de Casteljau; curve parameter t; B(t)
-->
A quadratic Bézier curve is defined by three points: a start P0, a control point P1 and an end
P2. The curve leaves P0 heading toward P1, arrives at P2 coming from P1's direction, and bends
toward P1 without passing through it. TrueType outlines are made of these curves and straight
lines, with P1 an [off-curve point](#primer/on-off-curve).

Each value of the parameter t from 0 to 1 picks one point on the curve. De Casteljau's
construction finds it with three [lerps](#primer/lerp), all with the same t: p = lerp(P0, P1, t),
q = lerp(P1, P2, t), and the curve point is lerp(p, q, t). Multiplied out, that is

```
B(t) = (1 - t)² P0 + 2 (1 - t) t P1 + t² P2
```

<svg viewBox="0 0 420 220" role="img" aria-label="De Casteljau's construction at t = 0.4: points p and q on the two legs, and the curve point on the segment between them" style="width:100%;max-width:420px;height:auto">
<polyline points="40,190 200,30 380,190" fill="none" stroke="var(--rule)" stroke-width="2" stroke-dasharray="6 5"/>
<path d="M40 190 Q200 30 380 190" fill="none" stroke="var(--ink)" stroke-width="3"/>
<line x1="104" y1="126" x2="272" y2="94" stroke="var(--fig-a)" stroke-width="2"/>
<circle cx="40" cy="190" r="6" fill="var(--ink)"/>
<circle cx="380" cy="190" r="6" fill="var(--ink)"/>
<circle cx="200" cy="30" r="6" fill="none" stroke="var(--muted)" stroke-width="2.5"/>
<circle cx="104" cy="126" r="5" fill="var(--fig-a)"/>
<circle cx="272" cy="94" r="5" fill="var(--fig-a)"/>
<circle cx="171.2" cy="113.2" r="6" fill="var(--fig-b)"/>
<text x="40" y="212" text-anchor="middle" font-size="14" fill="var(--ink)">P0</text>
<text x="380" y="212" text-anchor="middle" font-size="14" fill="var(--ink)">P2</text>
<text x="212" y="24" font-size="14" fill="var(--muted)">P1 (control)</text>
<text x="94" y="122" text-anchor="end" font-size="14" fill="var(--fig-a)">p</text>
<text x="282" y="90" font-size="14" fill="var(--fig-a)">q</text>
<text x="171" y="140" text-anchor="middle" font-size="14" fill="var(--fig-b)">B(0.4)</text>
</svg>

Written as a polynomial in t, the same curve is A t² + B t + C with A = P0 − 2 P1 + P2,
B = 2 (P1 − P0) and C = P0. Assignments 13, 14, 15 and 17 work with that form.

Assignment 10 writes the curve as `bezierLerp` in `src/utils/Geometry.h`. Assignment 11 draws
curves with it, and assignment 13 intersects one with a line.

Learn more:
- [De Casteljau's algorithm](https://pomax.github.io/bezierinfo/#decasteljau) in Pomax's A Primer
  on Bézier Curves, with interactive drawings
- [Bézier curve: quadratic curves](https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B%C3%A9zier_curves)
  on Wikipedia

## Flattening a curve
<!--
id: flattening
also: flatten; curve subdivision; polyline; line segments; approximating a curve
-->
A [line-drawing](#primer/line-drawing) routine can't draw a curve, but it can draw many short
straight lines. Flattening picks points along the curve and joins neighbours with lines. With n
pieces, line i runs from B((i − 1) / n) to B(i / n).

The question is how many pieces. Too few and the corners show; a fixed 8 looks fine on a small
glyph and angular on a large one. A rule that grows with the curve's size works better. The
curve is never longer than its control polygon, the path P0 to P1 to P2, so this n makes each
piece about a pixel long at most:

```
n = max(1, ceil(|P1 - P0| + |P2 - P1|))       lengths in pixels
```

`std::hypot` measures each length and `std::ceil` rounds the sum up (see
[`<cmath>`](#primer/cmath)).

Compute the points in pixel coordinates, as `double`, and round only when you call the line
routine. Rounding each point first moves it by up to half a pixel, which still passes but bends
the curve.

The fills don't flatten. They find where each row crosses a curve by solving the curve's
equation (see [Solving a quadratic equation](#primer/quadratic-equation)), which is exact.

Assignment 11 flattens every curve of an outline in `src/render/Outline.cpp` and draws the pieces
with your `drawLine` from assignment 06.

Learn more:
- [Flattening a curve](https://pomax.github.io/bezierinfo/#flattening) in Pomax's A Primer on
  Bézier Curves
- [Flattening quadratic Béziers](https://raphlinus.github.io/graphics/curves/2019/12/23/flatten-quadbez.html)
  by Raph Levien, on choosing the number of pieces for a given error

## The 2D cross product and the side test
<!--
id: cross-product
also: cross product; 2D cross product; perp dot product; orientation; side of a line; side test; cross
-->
For two [2D vectors](#primer/vector-2d) u and v, the cross product is one number:

```
cross(u, v) = u.x * v.y - u.y * v.x
```

It is 0 when u and v are parallel (or one of them is zero), and only then. Its sign says which
way you turn going from the direction of u to the direction of v: positive for
counter-clockwise, negative for clockwise, in coordinates with y up. On a screen, where y points
down, the same sign means the opposite visual turn (see
[Font coordinates and screen coordinates](#primer/screen-coordinates)).

That gives the side test. For a line through s and e and a point p, `cross(e - s, p - s)` is
positive on one side of the line, negative on the other and 0 when p lies on the line. Two
points are on opposite sides when the product of their side values is negative, and a product of
0 means one of them lies on the line:

```
line through s = (0, 0) and e = (4, 0), so e - s = (4, 0)
p = (1, 2):    cross((4, 0), (1, 2))  = 4 * 2 - 0 * 1    =  8    one side
p = (3, -1):   cross((4, 0), (3, -1)) = 4 * (-1) - 0 * 3 = -4    the other side
product 8 * (-4) = -32 < 0: the two points are on opposite sides
```

Assignment 12 builds its segment intersection on this test in `src/utils/Geometry.h`: first the
side test on both segments, then a cross product to find the meeting point (see
[Intersecting two segments](#primer/segment-intersection)).

Learn more:
- [Basic geometry](https://cp-algorithms.com/geometry/basic-geometry.html) on cp-algorithms, which
  calls it the pseudo-scalar product and explains its sign
- [Check if two segments intersect](https://cp-algorithms.com/geometry/check-segments-intersection.html)
  on cp-algorithms, the side test with all its cases

## Intersecting two segments
<!--
id: segment-intersection
also: segment intersection; line intersection; parametric form; parallel lines; collinear; segmentsIntersect
-->
A segment from a1 to a2 can be written in parametric form, as the points a1 + t·v1 with
v1 = a2 − a1 and t from 0 to 1. t = 0 is a1, t = 1 is a2. With a second segment b1 + s·v2, the
meeting point is where the two expressions are equal. Taking the
[cross product](#primer/cross-product) of both sides with v2 removes s, because
cross(v2, v2) = 0, and leaves

```
t = cross(b1 - a1, v2) / cross(v1, v2)        point = a1 + t * v1
s = cross(b1 - a1, v1) / cross(v1, v2)
```

The segments meet when 0 ≤ t ≤ 1 and 0 ≤ s ≤ 1, ends included. Outside that range the lines
cross, but beyond the end of a segment.

When cross(v1, v2) is 0 the segments are parallel and the division fails. That includes
collinear segments, which lie on one line and may overlap; they have no single meeting point,
and the workbook answers `none` for them.

Assignment 12 writes `segmentsIntersect` in `src/utils/Geometry.h`, returning
[`std::optional`](#primer/optional) for "no point". Whether a cross product counts as 0 is a
[tolerance](#primer/epsilon) question. The blog's even-odd fill finds where each row meets each
straight edge with this function. Your fills from assignment 14 on work out the crossing from
the edge directly, because this function reports a shared vertex for both of its edges.

Learn more:
- [Line–line intersection: given two points on each line segment](https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line_segment)
  on Wikipedia, with t and u in closed form
- [Finding intersection of two segments](https://cp-algorithms.com/geometry/segments-intersection.html)
  on cp-algorithms

## Floating-point tolerances
<!--
id: epsilon
also: epsilon; eps; tolerance; floating-point comparison; rounding error; exact zero
-->
A [`double`](#primer/floating-point) holds a binary fraction, so most decimals can't be stored
without error: 0.1 is stored as a number a little above 0.1, and `0.1 + 0.2 == 0.3` is false.
After a few operations, a value that should be 0 can come out as 1e-17. Code that tests `== 0`
then takes the wrong branch, or divides by a tiny number and gets a huge one.

The usual fix is a tolerance, often called epsilon: treat a value as 0 when its size is below a
small bound, such as `std::abs(d) < 1e-9` (see [`<cmath>`](#primer/cmath)). Pick the bound from
the size of your numbers; `1e-9` suits values around 1 to 1000.

Some numbers are exact. Whole numbers up to 2^53 are stored without error, and so are fractions
whose denominator is a power of 2, such as 0.25 or 0.0625. Adding, subtracting and multiplying
them stays exact while the results fit in a `double`'s 53 binary digits. The test data for
assignments 12 and 13 use multiples of 0.25 for that reason, so `== 0` works there, and so does
a tolerance.

Assignment 12's page accepts `== 0` or a tolerance such as `1e-9` for the
[parallel test](#primer/segment-intersection). Assignment 13's data make a and the discriminant
come out as 0, with no rounding error, in the linear and tangent cases (see
[Solving a quadratic equation](#primer/quadratic-equation)).

Learn more:
- [Comparison](https://floating-point-gui.de/errors/comparison/) in The Floating-Point Guide
- [Catastrophic cancellation](https://en.wikipedia.org/wiki/Catastrophic_cancellation) on
  Wikipedia, on the error from subtracting nearly equal numbers

## Solving a quadratic equation
<!--
id: quadratic-equation
also: quadratic formula; discriminant; roots; a t² + b t + c = 0; linear case; cancellation; numerically stable quadratic; solveQuadratic
-->
A quadratic equation is a·t² + b·t + c = 0. Where a line meets a curve, or a row crosses a curve,
the curve's polynomial form turns the question into one, and its solutions (roots) are the
values of t at the crossings. The cases:

| Case | Roots |
|---|---|
| a = 0, b ≠ 0 | one, t = −c / b: the equation is linear |
| a = 0, b = 0 | none (or every t, if c = 0 too) |
| D = b² − 4ac < 0 | none |
| D = 0 | one, t = −b / (2a): the line touches the curve |
| D > 0 | two, (−b − √D) / (2a) and (−b + √D) / (2a) |

D is the discriminant. Check a = 0 first (see [Floating-point tolerances](#primer/epsilon)): it
is common in fonts (a curve whose control point sits halfway between its ends in y has a = 0 for
a horizontal row), and the formula would divide by zero.

The textbook formula loses precision when b² is much larger than 4ac: √D is then close to |b|,
and one of −b ± √D subtracts two nearly equal numbers (cancellation). A safer form computes
one root with an addition and gets the other from the product of the roots, c / a:

```
q = −(b + sign(b) · √D) / 2        roots: q / a and c / q
```

Giving √D the sign of b makes the two terms add up instead of cancel. In C++, `std::sqrt` and
`std::copysign` from [`<cmath>`](#primer/cmath) give √D and a value with b's sign.

Assignment 13 solves for t where a line meets a [Bézier curve](#primer/bezier), keeping roots in
[0, 1], and the fills from assignment 14 on solve y(t) = row for each curve piece.

Learn more:
- [Quadratic formula](https://en.wikipedia.org/wiki/Quadratic_formula) on Wikipedia, with the
  discriminant and the cancellation problem
- [Intersections](https://pomax.github.io/bezierinfo/#intersections) in Pomax's A Primer on
  Bézier Curves, line and curve intersection

## Scanline filling
<!--
id: scanline
also: scanline; scan line; scan conversion; rasterization; filling a polygon; span; crossings; active edges; pixel centres
-->
Scanline filling paints the inside of an outline one row of pixels at a time. For each row:

1. Lay a horizontal line, the scanline, through the centres of the row's pixels, at
   y = row + 0.5.
2. Find every x where it crosses an edge of the outline (see [lerp](#primer/lerp) for a
   straight edge and [Solving a quadratic equation](#primer/quadratic-equation) for a curve).
3. Sort the crossings by x (see [`<algorithm>`](#primer/algorithm)).
4. Walk left to right and fill the stretches the fill rule calls inside: between the 1st and
   2nd crossing, the 3rd and 4th, and so on, for the [even-odd rule](#primer/even-odd), or
   wherever a running count isn't zero for the [non-zero rule](#primer/nonzero).

A pixel is painted when its centre lies inside, which is the TrueType rule too. A stretch from
x = 10.3 to x = 14.6 covers the pixels whose centres x + 0.5 fall in [10.3, 14.6): columns 10 to
14.

Before scanning, turn the outline into edges in pixel coordinates: straight lines, and curves
split where their y turns (see [Splitting a curve where y turns](#primer/curve-turning-point)).
Then each edge crosses a row at most once, and edges that don't reach a row can be skipped.

Two details decide whether the result has stray lines: how a row through a vertex counts (see
[Half-open edges](#primer/half-open)), and clamping crossings to the canvas (see
[Clipping](#primer/clipping)).

Assignment 14 writes the shared machinery in `src/render/Scanline.cpp`: `edgePieces` builds the
edges, `forEachRow` hands each row's crossings, sorted by x, to a
[`std::function`](#primer/functional), and `fillSpan` paints a stretch. Assignment 16 reuses it
for the non-zero rule.

Learn more:
- [Scanline rendering](https://en.wikipedia.org/wiki/Scanline_rendering) on Wikipedia
- [How the stb_truetype anti-aliased software rasterizer v2 works](https://nothings.org/gamedev/rasterize/)
  by Sean Barrett, a scanline rasterizer for font outlines

## Half-open edges
<!--
id: half-open
also: half-open interval; half-open rule; vertex on a scanline; horizontal edge; [a, b)
-->
A half-open interval includes one end and leaves out the other: [a, b) is every y with
a ≤ y < b. [Scanline fills](#primer/scanline) use it to count each vertex the right number of times.

Where two edges meet at a vertex and a scanline passes through it, both edges touch the row at
that point. Counting both gives two crossings at one x, where the outline crosses the row once,
and the rest of the row fills inverted: a stray line. Counting neither leaves a gap. The fix is
to count an edge from y0 to y1 at row y only when

```
min(y0, y1) <= y < max(y0, y1)        y in screen pixels
```

At a vertex where the outline passes through, one edge ends there and the other starts, so the
rule counts it once. At a pointed tip, with both edges above or both below, it counts two or
none, and either leaves the parity right. A horizontal edge never counts: min and max are equal,
so no y passes.

The rule works for curve pieces too, once each curve is split into pieces that only rise or only
fall.

Assignment 14 introduces it (requirement R4, with tests such as a diamond whose vertex sits on a
pixel centre), and the `forEachRow` comment in `src/render/Scanline.h` states the same rule.

Learn more:
- [Interval (mathematics)](https://en.wikipedia.org/wiki/Interval_%28mathematics%29) on Wikipedia,
  with the notation for half-open intervals
- [The scan converter](https://learn.microsoft.com/en-us/typography/opentype/spec/ttch01#the-scan-converter)
  in the OpenType specification's TrueType fundamentals, the rules TrueType itself uses

## The even-odd rule
<!--
id: even-odd
also: even-odd; odd-even rule; parity rule; ray casting; evenodd
-->
The even-odd rule decides whether a point is inside a shape by counting. Draw a ray from the
point in any direction, to the right for instance, and count how many times it crosses the
outline. An odd count means inside, an even count outside.

Holes come out right without any extra information: a ray from inside the hole of an `o` crosses
the inner contour and the outer one, 2 crossings, so the hole stays empty. The rule ignores which
way the [contours](#primer/contour) run.

With scanlines the rule becomes "fill between crossings 1 and 2, 3 and 4, ...", one row at a time.

Where two contours overlap, every point of the overlap is inside both, so the count there is even
and the overlap stays empty. A five-pointed star drawn as one self-crossing contour gets an empty
pentagon in the middle for the same reason. Fonts that build a glyph from overlapping strokes,
as variable fonts often do, need the [non-zero rule](#primer/nonzero) instead.

Assignment 14 fills glyphs with the even-odd rule in `src/render/EvenOdd.cpp`, on top of the
[scanline](#primer/scanline) code. Its requirement R5 checks that overlaps stay empty, with that
star among its tests.

Learn more:
- [Even–odd rule](https://en.wikipedia.org/wiki/Even%E2%80%93odd_rule) on Wikipedia
- [Nonzero-rule](https://en.wikipedia.org/wiki/Nonzero-rule) on Wikipedia, which compares the two

## Splitting a curve where y turns
<!--
id: curve-turning-point
also: turning point; y extreme; monotone curve; splitting a curve; curve crosses a scanline twice; monotone piece
-->
A quadratic curve can cross one scanline twice. At the bottom of a `U` the curve goes down, turns
and comes back up, so a row a little above the turn meets it twice, once going down and once going
up. The fill has to see both crossings, and the [half-open rule](#primer/half-open) works per
piece of outline that only rises or only falls. Splitting each curve where its y turns gives such
pieces.

The [curve](#primer/bezier)'s y is a quadratic in t, y(t) = (1 − t)² y0 + 2 (1 − t) t y1 + t²
y2, and it turns where its slope is 0:

```
t = (y0 - y1) / (y0 - 2*y1 + y2)
```

Split only when the denominator isn't 0 and 0 < t < 1; otherwise the curve already rises or
falls the whole way. De Casteljau's construction (three [lerps](#primer/lerp)) gives the two
halves as curves of their own: (P0, lerp(P0, P1, t), B(t)) and (B(t), lerp(P1, P2, t), P2). Both
halves share the point B(t), so use the same value for both.

Each piece then crosses a row at most once. Solve y(t) = row for the piece (see
[Solving a quadratic equation](#primer/quadratic-equation)), keep the one root closest to
[0, 1] and clamp it. Keeping every root in [0, 1] would count a crossing twice on a
row through the split point.

Assignment 14 splits curves in `edgePieces` in `src/render/Scanline.cpp`, and assignment 17
gives each piece a direction for the [non-zero rule](#primer/nonzero).

Learn more:
- [Finding extremities: root finding](https://pomax.github.io/bezierinfo/#extremities) in Pomax's
  A Primer on Bézier Curves
- [Splitting curves](https://pomax.github.io/bezierinfo/#splitting) in Pomax's A Primer on Bézier
  Curves, with de Casteljau's halves

## Lowest point of a quadratic curve
<!--
id: curve-min-y
also: minimum y; lowest point; vertex of a parabola; getBezierMinY; topmost point on screen; bounding box of a curve
-->
The smallest y on a quadratic curve between t = 0 and t = 1 is at one of the ends, or at the
turning point if the curve dips below both ends. Write y as a polynomial in t:

```
y(t) = a t² + b t + y0     with a = y0 - 2*y1 + y2,  b = 2*(y1 - y0)
```

The slope 2at + b is 0 at t* = −b / (2a). When a > 0 the curve is a valley and t* is its lowest
point; when a < 0 it is a hill and t* is its highest; when a = 0 y changes at a steady rate and
there is no turning point. So the answer is min(y0, y2), lowered to y(t*) when a > 0 and
0 < t* < 1. Testing a > 0 before you divide also avoids dividing by zero (see
[Floating-point tolerances](#primer/epsilon)).

On a screen, where y points down, the smallest y is the curve's highest point.

The blog's [even-odd](#primer/even-odd) fill needs this number. Its fix for rows through
vertices counts an edge only when the edge's top on screen is above the row, and for a curve
that top is its smallest y. A curve that bulges up and crosses a row twice needs its own branch
there, which is why the blog also tests a > 0. Your fills split curves instead (see
[Splitting a curve where y turns](#primer/curve-turning-point)), so they don't call this
function.

Assignment 15 adds `getBezierMinY` to `src/utils/Geometry.h`. It returns the exact value as a
`double`, where the blog's version truncates it to an `int`.

Learn more:
- [Quadratic function: vertex](https://en.wikipedia.org/wiki/Quadratic_function#Vertex) on
  Wikipedia
- [Component functions](https://pomax.github.io/bezierinfo/#components) in Pomax's A Primer on
  Bézier Curves, on treating x and y as separate functions of t

## The non-zero winding rule
<!--
id: nonzero
also: non-zero rule; nonzero; winding number; winding count; edge direction; contour direction
-->
The non-zero rule counts crossings with a sign. Draw a ray from the point to the right and keep a
winding count from 0. Each edge the ray crosses adds 1 if the edge goes down the screen and
subtracts 1 if it goes up (the opposite signs work too, if every edge uses them). The point is
inside when the count isn't 0.

Direction comes from the [contour](#primer/contour)'s point order: an edge runs from a point to
the next one. Two overlapping contours that run the same way give a count of 2 in the overlap,
inside, where the [even-odd rule](#primer/even-odd) leaves a hole. A contour inside another that
runs the opposite way cancels it, 1 − 1 = 0, and makes a hole: that is how a font draws the
inside of an `o`.

<svg viewBox="0 0 420 200" role="img" aria-label="Two overlapping squares that both run clockwise: the even-odd rule leaves the overlap empty, the non-zero rule fills it" style="width:100%;max-width:420px;height:auto">
<path d="M20 30H120V110H20Z M70 70H170V150H70Z" fill="var(--fig-a)" fill-opacity="0.45" fill-rule="evenodd" stroke="var(--ink)" stroke-width="2"/>
<path d="M240 30H340V110H240Z M290 70H390V150H290Z" fill="var(--fig-a)" fill-opacity="0.45" fill-rule="nonzero" stroke="var(--ink)" stroke-width="2"/>
<line x1="95" y1="90" x2="190" y2="90" stroke="var(--fig-b)" stroke-width="2"/>
<polygon points="190,85 200,90 190,95" fill="var(--fig-b)"/>
<circle cx="95" cy="90" r="4" fill="var(--fig-b)"/>
<line x1="315" y1="90" x2="408" y2="90" stroke="var(--fig-b)" stroke-width="2"/>
<polygon points="406,85 416,90 406,95" fill="var(--fig-b)"/>
<circle cx="315" cy="90" r="4" fill="var(--fig-b)"/>
<text x="95" y="178" text-anchor="middle" font-size="13" fill="var(--ink)">even-odd: 2, outside</text>
<text x="315" y="178" text-anchor="middle" font-size="13" fill="var(--ink)">non-zero: +2, inside</text>
</svg>

TrueType fills by this rule, and its outer contours run clockwise as you look at the glyph, holes
counter-clockwise. A contour that runs the other way on its own gives −1, still inside, so test
"not zero", not "greater than zero".

With [scanlines](#primer/scanline), each crossing carries an x and a direction, and the count
runs from left to right along the row.

Assignment 16 writes the rule for straight edges in `src/render/NonZero.cpp` (the `Crossing`
type in `src/render/Scanline.h` carries the direction), and assignment 17 adds curves.
Assignment 18 fills every glyph with it, including the overlapping strokes of the
[variable font](#primer/variable-font) Noto Sans JP.

Learn more:
- [Nonzero-rule](https://en.wikipedia.org/wiki/Nonzero-rule) on Wikipedia
- [The scan converter](https://learn.microsoft.com/en-us/typography/opentype/spec/ttch01#the-scan-converter)
  in the OpenType specification's TrueType fundamentals, the winding number TrueType uses
- [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html)
  in Apple's TrueType Reference Manual, on contour direction
