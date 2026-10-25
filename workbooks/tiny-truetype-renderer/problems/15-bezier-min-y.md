# 15 · Lowest point of a quadratic curve

**Difficulty:** Easy · **Assignment** 15 of 18 · **Check:** `.\check 15`

**Tags**
- *Language:* [floating-point arithmetic](#primer/floating-point) (`double`) · [avoiding a division by zero](#primer/floating-point) · [`nan`](#primer/floating-point)
- *Library:* [`std::min`](#primer/algorithm) (`<algorithm>`)
- *Concepts:* [quadratic Bezier curve as a polynomial in t](#primer/bezier) · [turning point of a parabola](#primer/curve-min-y) · [minimum over a closed interval](#primer/curve-min-y) · [straight and flat curves](#primer/curve-min-y) · [screen coordinates](#primer/screen-coordinates) with y pointing down

## Read in the blog first

You can pass using this page alone. For the background, in the blog's
"Renderer: Filling Glyph" section, read
[Removal of fill errors](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Removal%20of%20fill%20errors)
up to the formula for the t where the curve turns. The author's code (the listing "Find a
minimum curve of a quad Bézier curve") comes right after it. Assignment 10 covers the curve
itself.

## Learning material

- [Lowest point of a quadratic curve](#primer/curve-min-y): `getBezierMinY` in
  `utils/Geometry.h` returns min(y1, y3), lowered to y(t*) when a > 0 and 0 < t* < 1.
- [Floating-point tolerances](#primer/epsilon): decimal inputs such as 0.1 can leave a at 1e-17
  where it should be 0, and testing a > 0 and 0 < t* < 1 before you use t* makes an `a == 0`
  comparison unnecessary.
- [Font coordinates and screen coordinates](#primer/screen-coordinates): test `15-E2E-screen-S`
  gives 'S' flipped into screen coordinates, where the smallest y is the curve's highest point
  on screen and the rule stays the same.

## Source material

- Pomax, *A Primer on Bézier Curves*, [Component functions](https://pomax.github.io/bezierinfo/#components) and [Finding extremities: root finding](https://pomax.github.io/bezierinfo/#extremities), on treating x and y as separate functions of t and finding where the derivative is 0
- Wikipedia, [Quadratic function: vertex](https://en.wikipedia.org/wiki/Quadratic_function#Vertex)
- Microsoft, *OpenType specification*, [glyf: Glyph Data](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf), on the quadratic curves in TrueType outlines
- The blog: [Removal of fill errors](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Removal%20of%20fill%20errors)

## Where this fits

The blog's even-odd fill can count a row's crossings twice, or miss them, where an edge touches
the row without crossing it or two edges meet on the row. The blog's repair checks how far each
edge reaches above the row, and for a curved edge it needs the curve's smallest y. Your fill from
assignment 14 splits curves instead and doesn't need this function. It is the last of the blog's
geometry helpers, and you add it to your `utils/Geometry.h` from assignment 10.

## The problem

Write a program that reads quadratic Bezier curves and prints, for each one, the smallest y
that the curve reaches.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Every line of the input file has the same form:

| Line | Meaning |
|---|---|
| `curve p1x p1y p2x p2y p3x p3y` | The curve starts at p1, bends toward the control point p2, and ends at p3. |

Your `utils/Geometry.h` has evaluated this curve since assignment 10: the point at parameter t
is (1 − t)² p1 + 2(1 − t)t p2 + t² p3, for t from 0 to 1.

### Output

One line per input line, in the same order: the smallest y of any point on the curve, for t
from 0 to 1 inclusive.

The checker accepts any number within 0.001 of the expected value. If a value isn't whole, print
enough decimals to be within 0.001 (4 is plenty), and don't round it to a whole number. The
boilerplate's `number()` does this: it prints whole numbers without a decimal point, and rounds
others to 4 decimals with trailing zeros dropped (`37.5`, `0.0625`).

### The curve's height as a polynomial

You only need y. Multiplying out the curve's formula for y gives

```
y(t) = a t² + b t + y1,    where a = y1 − 2 y2 + y3   and   b = 2 (y2 − y1)
```

with y1, y2, y3 the y coordinates of p1, p2, p3.

### Candidates for the lowest point

On 0 ≤ t ≤ 1, the lowest point is at one of the ends, y(0) = y1 or y(1) = y3, or at the
turning point, where y stops falling and starts rising. There the slope 2at + b is 0:

```
t* = −b / (2a),     y(t*) = a t*² + b t* + y1
```

| a | Shape | Smallest y |
|---|---|---|
| a > 0 | a valley: the turning point is the lowest point of the whole parabola | y(t*) if 0 < t* < 1; otherwise min(y1, y3) |
| a < 0 | a hill: the turning point is the highest point | min(y1, y3) |
| a = 0, b ≠ 0 | straight: y changes at a steady rate | min(y1, y3) |
| a = 0, b = 0 | flat: y1 = y2 = y3 | y1 |

The answer is the smallest of y1, y3 and, when a > 0 and 0 < t* < 1, y(t*). Don't compute t*
when a = 0, because the formula divides by zero.

Decimal coordinates like 0.1 aren't exact in binary, so a can come out as a
tiny non-zero number such as 1e-17 when it should be 0. That does no harm if you use t* only when
a > 0 and 0 < t* < 1: on a curve whose a should be 0, t* lands far outside [0, 1], or y(t*) is
within rounding of an endpoint. You don't need an `a == 0` comparison.

### Screen coordinates

The blog calls this function after it has scaled the outline to pixels and flipped it so that y
points down (row 0 at the top of the image). There, the smallest y is the curve's highest point on
screen.

The blog returns it as a whole number (`static_cast<int>`, which drops the fraction) because it
compares it with integer row numbers. Your program prints the exact minimum instead.

The tests use both font units (y up) and screen coordinates (y down); the rule is the same.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A curve that only rises or only falls has its minimum at an end.
- **R2** A valley whose turning point lies inside the curve (0 < t* < 1) has its minimum there.
- **R3** A turning point outside 0 ≤ t ≤ 1 doesn't count. The minimum is then at an end.
- **R4** Straight curves (a = 0) and flat ones (a = b = 0) work, with no division by zero.
- **R5** For a curve that bulges upward (a < 0), the turning point is the highest point, so the
  minimum is at an end.

## Examples

### Example 1: a valley (test `15-R2-asymmetric`)

```
input:   curve 0 30 40 -20 100 10
output:  -1.25
```

a = 30 − 2·(−20) + 10 = 80 and b = 2·(−20 − 30) = −100, so t* = 100 / 160 = 0.625, which is
inside the curve. y(0.625) = 80 · 0.390625 − 100 · 0.625 + 30 = −1.25. Both ends are higher
(30 and 10).

### Example 2: the turning point is past the end (test `15-R3-after-end`)

```
input:   curve 0 40 50 10 100 0
output:  0
```

a = 40 − 20 + 0 = 20 and b = 2·(10 − 40) = −60, so t* = 1.5. The curve is still going down
when it stops at t = 1, so the answer is min(40, 0) = 0. Evaluating y at t* would give −5, a
point on the parabola beyond the curve's end.

### Example 3: hills (test `15-R5-hill`)

```
input:   curve 0 0 5 10 10 4
         curve 0 6 5 20 10 2

output:  0
         2
```

On the first line a = 0 − 20 + 4 = −16, a hill. Its turning point, t* = 0.625 with y = 6.25,
is the top of the curve. The lowest point is the lower end: min(0, 4) = 0.

## Constraints

- Every coordinate is between −1000 and 1000 and has at most 4 digits after the decimal point.
- A test has from 1 to 74 lines.
- There are 22 tests: hand-made curves for each rule, random curves, and every curve of 'o'
  and 'S' (JetBrains Mono Bold) and 'あ' (Noto Sans JP), plus 'S' scaled and flipped into
  screen coordinates.
- Each case has a 10-second limit. A correct solution takes milliseconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Ignore x and write y(t) as a t² + b t + y1. Sketch the three shapes it can have on 0 ≤ t ≤ 1, a
valley, a hill and a straight line, and mark on each sketch the places its lowest point can be.
</details>

<details><summary>Hint 2: the approach</summary>

Both ends are candidates on every curve. The turning point is a candidate only when a > 0 and it
lies between t = 0 and t = 1. Take the smallest candidate, and test your reasoning on Examples 1
and 2.
</details>

<details><summary>Hint 3: the traps</summary>

- A turning point outside 0 ≤ t ≤ 1 is not on the curve (R3).
- If a < 0, the turning point is the top of a hill (R5). If you return y(t*) whenever t* is in
  range, you return the highest point.
- With a = 0, −b / (2a) is ±infinity, or `nan` (0 / 0) if b is also 0. A `nan` that reaches
  `std::min` can come out as the answer, depending on the argument order. Handle a = 0 before
  dividing (R4).
- A straight curve can fall, so with a = 0 the answer is min(y1, y3), which can be y3.
- Keep the fraction: the blog's whole-number result would turn −1.25 into −1.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
minY(p1, p2, p3):
    a = p1.y - 2*p2.y + p3.y
    b = 2*(p2.y - p1.y)
    lowest = min(p1.y, p3.y)
    if a > 0:
        t = -b / (2*a)
        if 0 < t < 1:
            lowest = min(lowest, a*t*t + b*t + p1.y)
    return lowest
```
</details>

## Checking your solution

```
.\check 15                          run every test
.\check 15 -Case 15-R3-after-end    one test, showing its full input, expected output and your output
.\check 15 -Fresh                   a new set of tests (new random seed), to confirm on data you haven't seen
.\check 15 -Dispute <id> "why"      set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R3  A turning point outside 0 <= t <= 1 doesn't count ....................    0 / 4   FAILED
      x 15-R3-before-start  turning point at t = -0.5 (y = -0.5 there, off the curve)
          line 1: expected `0`, got `-0.5`
          expected values from: exact arithmetic with Python fractions.Fraction, checked against 2001 samples of the curve
          reproduce: build/solutions/assignment_15.exe build/cases/15/15-R3-before-start.in build/cases/15/15-R3-before-start.out
```

## After you pass: compare with the author's code

[The blog's listing](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=minimum%20curve%20of%20a%20quad)
is one function, `getBezierMinY`, that takes the three points and returns an `int`. It computes
a and b as on this page. If |a| is below a small eps it returns p1.y when |b| is also tiny, and
min(p1.y, p3.y) otherwise. Else it computes t*, and returns y(t*) when t* lies in
[−eps, 1 + eps] and a > 0, and min(p1.y, p3.y) in every other case. Its branches match the rows
of the table above. The blog doesn't define `eps`; the author's repository sets it to
`std::numeric_limits<float>::epsilon()`, about 1.2e-7.

The blog's fill listings also call `isBezierConvexUpwards`, which the blog doesn't show. In the
repository it sits next to `getBezierMinY` and returns whether a > 0: the valley row of the table,
"convex upwards" on a screen where y points down.

The result goes through `static_cast<int>`, which drops the fraction
by rounding toward zero. On screen, where y is positive, that is the same as rounding down, so
61.875 becomes 61 and the comparison with the integer row still works. For a negative y it
rounds up instead (−1.25 becomes −1). This assignment asks for the exact value, so a solution
that copies the cast fails R2.
