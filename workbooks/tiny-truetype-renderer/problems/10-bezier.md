# 10 · Lerp and quadratic Bezier curves

**Difficulty:** Easy · **Assignment** 10 of 18 · **Check:** `.\check 10`

**Tags**
- *Language:* [floating-point arithmetic](#primer/floating-point) (`double`) · small structs with [`+`, `-` and `*` operators](#primer/operator-overloading)
- *Library:* none for the maths itself · the boilerplate's input and output code uses [`std::istringstream`](#primer/sstream), [`std::snprintf`](#primer/cstdio) and [`std::isnan`/`std::isinf`](#primer/cmath)
- *Concepts:* [linear interpolation (lerp)](#primer/lerp) · [quadratic Bezier curves](#primer/bezier) · [control points](#primer/on-off-curve) · [de Casteljau's algorithm](#primer/bezier) · [curve parameter t](#primer/bezier)

## Read in the blog first

The page doesn't depend on the blog. If you want the background, it is at the start of the blog's
"Renderer: Curve Rendering" section:
[Definition of Bézier Curves](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Definition%20of%20B%C3%A9zier%20Curves)
and
[De Casteljau's algorithm](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=De%20Casteljau,algorithm).
Read up to the sentence that introduces the code. The author's listing, "Lerp for a segment and a
quadratic Bézier curve", comes right after; save it for the comparison at the end. The next heading,
"TrueType Bézier curves", belongs to assignment 11.

## Learning material

- [2D vectors and the dot product](#primer/vector-2d): `Vec2` in `utils/Geometry.h` stores a
  point as `double` x and y, and the program reads each pair of numbers on a line into one.
- [Operator overloading](#primer/operator-overloading): `Geometry.h` already declares `+`, `-`
  and `*` for `Vec2`, so point arithmetic reads like the maths on this page.
- [`inline` functions](#primer/inline): there is no `Geometry.cpp`, so `lerp` and `bezierLerp`
  sit in the header, marked `inline`.
- [Linear interpolation (lerp)](#primer/lerp): a `lerp` line asks for the point a fraction t of
  the way from a to b.
- [Quadratic Bézier curves](#primer/bezier): a `bezier` line gives the start, the control point
  and the end, and `bezierLerp` returns the point at t.
- [`<cmath>`](#primer/cmath): the program's `number()` checks each result with `std::isnan` and
  `std::isinf` and prints `nan` or `inf` instead of a number.

## Source material

- Apple, *TrueType Reference Manual*, [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html), on quadratic curves in TrueType outlines
- Microsoft, *OpenType specification*, [glyf: Glyph Data](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf), which defines on-curve and off-curve points
- Pomax, *A Primer on Bézier Curves*, [de Casteljau's algorithm](https://pomax.github.io/bezierinfo/#decasteljau), with interactive drawings
- The blog: [De Casteljau's algorithm](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=De%20Casteljau,algorithm)

## Where this fits

Assignment 08 drew glyph outlines with straight lines only. TrueType outlines also carry
quadratic curves: an on-curve start, an off-curve control point that pulls the curve toward
itself, and an on-curve end. This assignment finds points along one. Assignment 11 draws the
curve by joining a lot of them with short lines.

## The problem

Each input line asks for one point: either part of the way along a straight segment, or a spot
on a quadratic Bezier curve. Print it.

### Input

Command line, run from the workbook folder: `<program> <input-file> <output-file>`. Two kinds of
lines make up the input:

| Line | Meaning |
|---|---|
| `lerp ax ay bx by t` | The point a fraction `t` of the way along the straight segment from a = (ax, ay) to b = (bx, by). |
| `bezier ax ay bx by cx cy t` | The point at parameter `t` on the quadratic Bezier curve that starts at a = (ax, ay), ends at c = (cx, cy), and bends toward the control point b = (bx, by). |

- Numbers are decimals such as `12`, `-3.25` or `0.0625`.
- `t` is between 0 and 1, inclusive.
- Watch the order on a `bezier` line: start, control point, end. The control point is the
  middle pair.

### Output

One output line per input line, in input order, with the point written as `x y` (a space between the
coordinates).

The checker takes anything within 0.001 of the expected value, so `25`, `25.0` and `25.0000`
all match `25`. For fractional values, 4 decimals are enough. The boilerplate's `number()` does
the formatting for you: whole numbers print without a decimal point, the rest print rounded to 4
decimals with trailing zeros dropped (`37.5`, `0.0625`).

### Linear interpolation

Lerp, short for linear interpolation, gives the point a fraction t of the way from a to b:

```
lerp(a, b, t) = a + (b − a) · t
```

- Apply the formula to x, then to y.
- t = 0 gives a, t = 1 gives b, t = 0.5 gives the midpoint.
- t counts from a. `lerp(a, b, 0.25)` lands near a; `lerp(b, a, 0.25)` lands near b.

### A point on a quadratic Bezier curve

Three points define the curve: the start a, the control point b and the end c. The curve
leaves a heading toward b and arrives at c coming from the direction of b. It bends toward b
without passing through it, except when all three points lie on one line with b between a and c.

Each value of the curve parameter t picks one point on the curve. De Casteljau's construction
finds it with three lerps, all using the same t:

1. p = lerp(a, b, t), a point on the leg from a to the control point
2. q = lerp(b, c, t), a point on the leg from the control point to c
3. The curve point is lerp(p, q, t).

Multiply that out and you get a single formula for the same point. Use it instead if you like:

```
B(t) = (1 − t)² · a  +  2 (1 − t) t · b  +  t² · c
```

The three weights (1 − t)², 2(1 − t)t and t² add up to 1 for any t. At t = 0 the curve is at
a, and at t = 1 it is at c.

| t | (1 − t)² | 2(1 − t)t | t² |
|---|---|---|---|
| 0 | 1 | 0 | 0 |
| 0.25 | 0.5625 | 0.375 | 0.0625 |
| 0.5 | 0.25 | 0.5 | 0.25 |
| 1 | 0 | 0 | 1 |

## Requirements

Each test sits under one of these requirements. Failures get a count per requirement, plus a
`likely cause` line when the difference points at one in particular.

- **R1** A `lerp` line gives the point a fraction t of the way from a to b.
- **R2** A `bezier` line gives the point at t on the curve that starts at a, ends at c and is
  pulled toward the control point b (the middle point on the line).
- **R3** The ends are exact: t = 0 gives the first point and t = 1 the last. For a curve, the
  last is c, not the control point b.
- **R4** Negative coordinates, fractional coordinates and fractional t all work.

## Examples

### Example 1: lerp in both directions (test `10-R1-direction`)

```
input:   lerp 10 20 50 100 0.25
         lerp 50 100 10 20 0.25
         lerp 10 20 50 100 0.9
         lerp 50 100 10 20 0.9

output:  20 40
         40 80
         46 92
         14 28
```

First line: b − a = (40, 80), a quarter of that is (10, 20), and a + (10, 20) = (20, 40). The
second line swaps a and b, which moves the starting point to (50, 100).

### Example 2: the middle of an arch (test `10-R2-midpoint`)

```
input:   bezier 0 0 50 100 100 0 0.5
output:  50 50
```

| Step | Computation | Result |
|---|---|---|
| p = lerp(a, b, 0.5) | halfway from (0, 0) to (50, 100) | (25, 50) |
| q = lerp(b, c, 0.5) | halfway from (50, 100) to (100, 0) | (75, 50) |
| lerp(p, q, 0.5) | halfway from (25, 50) to (75, 50) | (50, 50) |

The control point sits at height 100 and the curve peaks at 50. The formula agrees:
0.25 · (0, 0) + 0.5 · (50, 100) + 0.25 · (100, 0) = (50, 50).

### Example 3: the end of a curve is c, not b (test `10-R3-control-not-on-curve`)

```
input:   bezier 0 0 0 100 100 100 1
         bezier 0 0 0 100 100 100 0.5

output:  100 100
         25 75
```

At t = 1 every weight except t² is 0: the curve ends at c = (100, 100). The control point
(0, 100) only bends the path. At t = 0.5, p = (0, 50), q = (50, 100) and the point is (25, 75).

## Constraints

- Coordinates are between −1000 and 1000, with at most 4 digits after the decimal point. `t` is
  between 0 and 1, inclusive.
- The input is well-formed: each line has its keyword and the right count of numbers.
- Tests run from 1 to about 80 lines.
- 24 tests, covering hand-made lines for each rule, random lines, every line and curve of
  'S' and 'o' (JetBrains Mono Bold) and 'あ' (Noto Sans JP), and one curve of '3' cut into 16
  steps.
- 10 seconds is the limit per case; a correct solution runs in milliseconds.
- 32-bit `float` is accurate enough for these tests. `Geometry.h` uses `double` for its point
  type anyway.

## Hints

<details><summary>Hint 1: where to start</summary>

Write `lerp` first and run it against Example 1. Once it works, the curve function is three
calls to it.
</details>

<details><summary>Hint 2: the approach</summary>

A point is a pair, and the same arithmetic applies to x and y. For a curve, lerp along the leg
a → b and along the leg b → c with the same t, then lerp between those two results, again with
that t. Example 2 is the one to check against: every step lands on a round number.
</details>

<details><summary>Hint 3: the traps</summary>

- It is (b − a) · t, not (a − b) · t. At t = 0.25 the point should be closer to a.
- On a `bezier` line the middle point is the control point and the last is the end. At t = 1
  the answer is c.
- All three lerps take the same t. The last one goes from the first leg's point to the second
  leg's point, in that order.
- With the expanded formula, don't drop the 2 on the middle term. The weights have to add up
  to 1.
- Read numbers as floating point. Inputs like `46.5` and `0.0625` are common.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
lerp(a, b, t):
    return (a.x + (b.x - a.x) * t,  a.y + (b.y - a.y) * t)

bezier(a, b, c, t):
    p = lerp(a, b, t)
    q = lerp(b, c, t)
    return lerp(p, q, t)
```
</details>

## Checking your solution

```
.\check 10                         run every test
.\check 10 -Case 10-R2-midpoint    one test, showing its full input, expected output and your output
.\check 10 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 10 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failed test shows:

```
  R2  bezier: the point at t on the curve from a to c, which bends toward b .....    0 / 7   FAILED
      x 10-R2-midpoint  an arch from (0,0) to (100,0) pulled toward (50,100): t = 0.5
          line 1: expected `50 50`, got `37.5 25`
          expected values from: exact arithmetic with Python fractions.Fraction
          reproduce: build/solutions/assignment_10.exe build/cases/10/10-R2-midpoint.in build/cases/10/10-R2-midpoint.out
```

## After you pass: compare with the author's code

[The blog's listing](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Lerp%20for%20a%20segment)
is two short functions on `glm::vec2`. `lerp` asserts that t is between 0 and 1 and returns
a + (b − a) · t. `bezierLerp` nests three `lerp` calls in de Casteljau's order, as in Example 2.
The expanded formula shows up in the blog's prose but not in its code.

One naming wrinkle: the next section's drawing code ("TrueType Bézier curves") calls the curve
function `quadBezierLerp`, where this listing says `bezierLerp`. Same function. The author's
repository uses `quadBezierLerp` in both places, and this project keeps the listing's name.

The prose also describes subdividing the curve at the ratio t : t − 1. De Casteljau splits each
leg at t : 1 − t, which is what `lerp` computes.
