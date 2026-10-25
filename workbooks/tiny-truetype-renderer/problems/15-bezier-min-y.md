# 15 · Lowest point of a quadratic curve

**Difficulty:** Easy · **Assignment** 15 of 18 · **Check:** `.\check 15`

**Tags**
- *Language:* [floating-point arithmetic](#primer/floating-point) (`double`) · [avoiding a division by zero](#primer/floating-point) · [`nan`](#primer/floating-point)
- *Library:* [`std::min`](#primer/algorithm) (`<algorithm>`)
- *Concepts:* [quadratic Bezier curve as a polynomial in t](#primer/bezier) · [turning point of a parabola](#primer/curve-min-y) · [minimum over a closed interval](#primer/curve-min-y) · [straight and flat curves](#primer/curve-min-y) · [screen coordinates](#primer/screen-coordinates) with y pointing down

## Read in the blog first

Passing doesn't need the blog. For the author's version, go to the "Renderer: Filling Glyph"
section and read
[Removal of fill errors](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Removal%20of%20fill%20errors)
as far as the formula for the t where the curve turns. The listing "Find a
minimum curve of a quad Bézier curve" follows right after. For the curve itself, see
assignment 10.

## Learning material

- [Lowest point of a quadratic curve](#primer/curve-min-y): `getBezierMinY` in
  `utils/Geometry.h` finds the smallest y on one curve. Both ends are candidates, and
  the turning point joins them when a > 0 and 0 < t* < 1.
- [Floating-point tolerances](#primer/epsilon): decimal inputs such as 0.1 aren't exact in
  binary, so a can come out near 1e-17 where it should be 0. Testing a > 0 and 0 < t* < 1 before
  you use t* makes an `a == 0` comparison unnecessary.
- [Font coordinates and screen coordinates](#primer/screen-coordinates): test `15-E2E-screen-S`
  gives 'S' flipped into screen coordinates. There the smallest y is the curve's highest point
  on screen, and the rule stays the same.

## Source material

- Pomax, *A Primer on Bézier Curves*, [Component functions](https://pomax.github.io/bezierinfo/#components) and [Finding extremities: root finding](https://pomax.github.io/bezierinfo/#extremities), on treating x and y as separate functions of t and finding where the derivative is 0
- Wikipedia, [Quadratic function: vertex](https://en.wikipedia.org/wiki/Quadratic_function#Vertex)
- Microsoft, *OpenType specification*, [glyf: Glyph Data](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf), on the quadratic curves in TrueType outlines
- The blog: [Removal of fill errors](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Removal%20of%20fill%20errors)

## Where this fits

The blog's even-odd fill miscounts a row when an edge brushes it without crossing, or when two
edges meet on it. Its repair asks how far each edge reaches above the row, and for a curved
edge that means the curve's smallest y. This function is the last of the blog's geometry
helpers and goes into the `utils/Geometry.h` you started in assignment 10. Your own fill in
assignment 14 splits curves instead and has no use for it.

## The problem

Read quadratic Bezier curves and print, for each, the smallest y the curve reaches.

### Input

`<program> <input-file> <output-file>` is the command line, issued from the workbook folder. Each
line of the input has the same form:

| Line | Meaning |
|---|---|
| `curve p1x p1y p2x p2y p3x p3y` | The curve starts at p1, bends toward the control point p2, and ends at p3. |

`utils/Geometry.h` has evaluated this curve since assignment 10: the point at parameter t
is (1 − t)² p1 + 2(1 − t)t p2 + t² p3, for t from 0 to 1.

### Output

One line per input line, in the same order: the smallest y of any point on the curve, for t
from 0 to 1 inclusive.

The checker allows 0.001 either way, so a fractional minimum needs enough decimals (4 is plenty)
and you must not round it to a whole number. The boilerplate's `number()` formats it: bare integers
for whole numbers, 4 decimals minus trailing zeros for other values (`37.5`, `0.0625`).

### The curve's height as a polynomial

Only y matters, so multiply out the curve's formula for y and you get

```
y(t) = a t² + b t + y1,    where a = y1 − 2 y2 + y3   and   b = 2 (y2 − y1)
```

with y1, y2, y3 the y coordinates of p1, p2, p3.

### Candidates for the lowest point

On 0 ≤ t ≤ 1 the lowest point sits at one of the ends, y(0) = y1 or y(1) = y3, or at the
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

The answer is the smallest of y1, y3 and, when a > 0 and 0 < t* < 1, y(t*). Leave t* alone
when a = 0: the formula divides by zero.

Decimal coordinates like 0.1 aren't exact in binary, so a can land on a tiny non-zero number
such as 1e-17 when it should be 0. That's harmless if you use t* only when a > 0 and
0 < t* < 1. On a curve whose a should be 0, t* then falls far outside [0, 1], or y(t*) is
within rounding of an endpoint. No `a == 0` comparison needed.

### Screen coordinates

The blog calls this function after scaling the outline to pixels and flipping it so y points
down (row 0 at the top of the image). In that frame the smallest y is the curve's highest point
on screen.

The blog returns the result as a whole number (`static_cast<int>`, which drops the fraction)
because it compares the result with integer row numbers. Your program prints the exact minimum.

The tests use both font units (y up) and screen coordinates (y down). The rule is the same.

## Requirements

Each test checks one requirement. The checker's failure report gives pass totals for each one, and a
`likely cause` line appears when the difference hints at a particular requirement.

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

a = 30 − 2·(−20) + 10 = 80 and b = 2·(−20 − 30) = −100, so t* = 100 / 160 = 0.625, inside the
curve. y(0.625) = 80 · 0.390625 − 100 · 0.625 + 30 = −1.25. Both ends are higher (30 and 10).

### Example 2: the turning point is past the end (test `15-R3-after-end`)

```
input:   curve 0 40 50 10 100 0
output:  0
```

a = 40 − 20 + 0 = 20 and b = 2·(10 − 40) = −60, so t* = 1.5. At t = 1, where the curve stops,
it is still heading down, so the answer is min(40, 0) = 0. Evaluating y at t* would give −5,
which is a point on the parabola beyond the curve's end.

### Example 3: hills (test `15-R5-hill`)

```
input:   curve 0 0 5 10 10 4
         curve 0 6 5 20 10 2

output:  0
         2
```

First line: a = 0 − 20 + 4 = −16, a hill. Its turning point, t* = 0.625 with y = 6.25, is the
top of the curve, and the lowest point is the lower end: min(0, 4) = 0.

## Constraints

- Every coordinate is between −1000 and 1000 and has at most 4 digits after the decimal point.
- Inputs are 1 to 74 lines long.
- 22 tests: hand-made curves for each rule, random curves, and every curve of 'o' and 'S'
  (JetBrains Mono Bold) and 'あ' (Noto Sans JP), plus 'S' scaled and flipped into screen
  coordinates.
- Time limit 10 seconds per case; milliseconds is typical for a correct solution.

## Hints

<details><summary>Hint 1: where to start</summary>

Forget x and write y(t) as a t² + b t + y1. Sketch the three shapes it can take on 0 ≤ t ≤ 1, a
valley, a hill and a straight line, and mark where the lowest point can be on each.
</details>

<details><summary>Hint 2: the approach</summary>

Both ends are candidates on every curve. The turning point is a candidate only when a > 0 and
it lies between t = 0 and t = 1. Take the smallest candidate, and run your reasoning through
Examples 1 and 2.
</details>

<details><summary>Hint 3: the traps</summary>

- A turning point outside 0 ≤ t ≤ 1 isn't on the curve (R3).
- If a < 0 the turning point is the top of a hill (R5). Returning y(t*) whenever t* is in range
  gives the highest point.
- With a = 0, −b / (2a) is ±infinity, or `nan` (0 / 0) if b is also 0. A `nan` that reaches
  `std::min` may come out as the answer, depending on the argument order. Deal with
  a = 0 before dividing (R4).
- A straight curve can fall, so with a = 0 the answer is min(y1, y3), which can be y3.
- Keep the fraction. The blog's whole-number result would turn −1.25 into −1.
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

A failed test, as printed:

```
  R3  A turning point outside 0 <= t <= 1 doesn't count ....................    0 / 4   FAILED
      x 15-R3-before-start  turning point at t = -0.5 (y = -0.5 there, off the curve)
          line 1: expected `0`, got `-0.5`
          expected values from: exact arithmetic with Python fractions.Fraction, checked against 2001 samples of the curve
          reproduce: build/solutions/assignment_15.exe build/cases/15/15-R3-before-start.in build/cases/15/15-R3-before-start.out
```

## After you pass: compare with the author's code

[The blog's
listing](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=minimum%20curve%20of%20a%20quad)
is `getBezierMinY`, a single function that takes the three points and returns an `int`. It computes
a and b the way this page does. If |a| is below a small eps it returns p1.y when |b| is also tiny,
and min(p1.y, p3.y) otherwise. Past that it computes t* and returns y(t*) when t* lies in [−eps, 1 +
eps] and a > 0, and min(p1.y, p3.y) in every other case. Its branches line up with the rows of the
table above. The blog leaves `eps` undefined; the author's repository sets it to
`std::numeric_limits<float>::epsilon()`, about 1.2e-7.

The blog's fill listings also call `isBezierConvexUpwards`, which the blog doesn't show. In the
repository it sits next to `getBezierMinY` and returns whether a > 0: the valley row of the
table, "convex upwards" on a screen where y points down.

The result goes through `static_cast<int>`, which drops the fraction by rounding toward zero.
On screen, where y is positive, that is the same as rounding down: 61.875 becomes 61, and the
comparison with the integer row still works. For a negative y it rounds up (−1.25 becomes −1).
This assignment asks for the exact value, so a solution that copies the cast fails R2.
