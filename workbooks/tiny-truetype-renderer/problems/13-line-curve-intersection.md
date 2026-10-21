# 13 · Intersect a line and a quadratic curve

**Difficulty:** Medium · **Assignment** 13 of 18 · **Check:** `.\check 13`

**Tags**
- *Language:* floating-point arithmetic (`double`) · returning a list of results (`std::vector`) · sorting
- *Library:* `std::sqrt`, `std::sort`
- *Concepts:* quadratic Bezier curve as a polynomial · normal vector and dot product · quadratic equations and the discriminant · the degenerate (linear) case · tangent lines · curve parameter t

## Read in the blog first

This page is complete on its own; the blog tells the story behind it. In the blog's
**"Renderer: Filling Glyph"** section, read
[Intersection detection for Bézier curves](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Intersection%20detection%20for%20B%C3%A9zier%20curves)
up to the quadratic equation in t. The author's code (the listing "Function to find a
intersections of a segment and a quadratic Bezier curve") comes right after it. Assignment 10
covers the curve itself.

## Where this fits

Assignment 14 fills a glyph row by row. For every row of pixels it lays a horizontal line
across the glyph and finds where that line crosses the outline. Assignment 12 found the
crossing with a straight edge.

This assignment finds the crossings with a curved edge. There can be zero, one or two of them.

## The problem

The program reads pairs of a quadratic Bezier curve and a straight line. For each pair it
prints the points where the line meets the curve, or `none`.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Every line of the input file has the same form:

| Line | Meaning |
|---|---|
| `curve p1x p1y p2x p2y p3x p3y line l1x l1y l2x l2y` | The curve starts at p1, is pulled toward the control point p2, and ends at p3. The line is the **infinite** straight line through l1 and l2. |

- The curve is the one from assignment 10: the point at parameter t is
  P(t) = (1 − t)² p1 + 2(1 − t)t p2 + t² p3, for t from 0 to 1.
- The line doesn't stop at l1 or l2: those two points only fix its position and direction.

### Output

One line per input line, in the same order:

- `none` when the line doesn't meet the curve, or
- the meeting points on one line: `x1 y1`, or `x1 y1 x2 y2`.

Points come in increasing order of t (the order you meet them travelling along the curve from
p1 to p3), not by x or y. A line that touches the curve without crossing it (a **tangent**)
gives its one point once.

The checker accepts any number within 0.001 of the expected value. When a value isn't whole,
print enough decimals to be within 0.001 (4 is plenty). The boilerplate's `number()` does
this: whole numbers plainly, others rounded to 4 decimals with trailing zeros dropped (`37.5`,
`0.0625`).

### The curve as a polynomial

Multiplying out the curve's formula gives

```
P(t) = A t² + B t + C,    where A = p1 − 2 p2 + p3,   B = 2 (p2 − p1),   C = p1
```

A, B and C are vectors; work out x and y separately.

### The line as an equation

Let d = l2 − l1 be the line's direction, and K = (d.y, −d.x). K is perpendicular to the line:
it is a **normal vector** of the line. A point X lies on the line exactly when

```
K · (X − l1) = 0           (· is the dot product: u · v = u.x v.x + u.y v.y)
```

Moving along the line changes X by a multiple of d, and K · d = 0, so the left side stays 0.

### From a line and a curve to a quadratic

Put P(t) in place of X:

```
K · (A t² + B t + C − l1) = 0
a t² + b t + c = 0,    where a = K · A,   b = K · B,   c = K · (C − l1)
```

a, b and c are plain numbers. Every solution t is a place where the curve's polynomial meets
the line.

### Solving for t

Which case you are in depends on whether a is 0, and on D = b² − 4ac, the **discriminant**:

| Case | Roots |
|---|---|
| a ≠ 0 and D = b² − 4ac < 0 | none |
| a ≠ 0 and D = 0 | one: t = −b / (2a). The line is tangent to the curve. |
| a ≠ 0 and D > 0 | two: t = (−b − √D) / (2a) and t = (−b + √D) / (2a) |
| a = 0 and b ≠ 0 | one: t = −c / b. The equation is linear. |
| a = 0 and b = 0 | none. The "curve" is a straight segment parallel to the line. (If c were also 0, it would lie on the line; the tests don't have that.) |

The case a = 0 is common in real fonts: for a horizontal line, a is 0 whenever the control
point's y is halfway between the end points' y. The quadratic formula would divide by 0 there.

When a < 0, the second formula in the table gives the smaller t, so sort the roots.

### Which roots count

Keep only the roots with 0 ≤ t ≤ 1, including t = 0 and t = 1 exactly (the line passes
through p1 or p3). Roots outside that range belong to the curve's polynomial beyond its ends.
For each root you keep, the point is P(t) = A t² + B t + C.

### Precision

Every coordinate is a multiple of 0.25 between −1000 and 1000, so a, b, c and D are exact in
`double`.

- In tangent cases D is exactly 0, and in linear cases a is exactly 0, so comparing with 0
  works.
- A tiny tolerance also works: every root that isn't exactly 0 or 1 is at least 0.01 away from
  0 and 1, and two different roots are at least 0.01 apart. Accepting t within, say, 1e-9 of
  the ends gives the same answers.

## Requirements

Each test case is designed around one of these. A failing test may also print the requirement
the difference most likely comes from.

- **R1** A line that crosses the curve twice gives both points. The line is infinite: where l1
  and l2 sit along it makes no difference.
- **R2** Only roots with 0 ≤ t ≤ 1 count. When one root is on the curve and the other is beyond
  an end, the answer is the one point.
- **R3** When no root has 0 ≤ t ≤ 1 (or there are no real roots), the answer is `none`.
- **R4** A line that touches the curve without crossing it (D = 0) gives the touching point
  once.
- **R5** When a = K · A is 0, the equation is linear: t = −c / b, or no root when b is also 0.
- **R6** Points are in increasing order of t, whichever way the line points.
- **R7** Roots exactly at t = 0 or t = 1 count.

## Examples

### Example 1: two crossings (test `13-R1-arch`)

```
input:   curve 0 0 50 100 100 0 line 0 32 100 32
output:  20 32 80 32
```

| Step | Computation | Result |
|---|---|---|
| A, B, C | (0, 0) − 2·(50, 100) + (100, 0), 2·(50, 100), (0, 0) | (0, −200), (100, 200), (0, 0) |
| d, K | (100, 0), (0, −100) | |
| a, b, c | K·A, K·B, K·((0, 0) − (0, 32)) | 20000, −20000, 3200 |
| D | 20000² − 4 · 20000 · 3200 | 144,000,000, so √D = 12000 |
| t | (20000 ∓ 12000) / 40000 | 0.2 and 0.8 |
| P(0.2), P(0.8) | A t² + B t + C | **(20, 32)** and **(80, 32)** |

### Example 2: the linear case (test `13-R5-scanline`)

```
input:   curve 0 0 10 5 0 10 line -10 5 10 5
         curve 100 0 160 50 100 100 line 0 30 1 30

output:  5 5
         125.2 30
```

On the first line, A = (−20, 0) and K = (0, −20), so a = 0. Then b = K · (20, 10) = −200 and
c = K · ((0, 0) − (−10, 5)) = 100, so t = −c / b = 0.5 and P(0.5) = (5, 5). Both curves
bulge sideways, so a horizontal line crosses each of them once.

### Example 3: a tangent (test `13-R4-arch-top`)

```
input:   curve 0 0 5 10 10 0 line 0 5 10 5
output:  5 5
```

Here a = 200, b = −200 and c = 50, so D = 40000 − 40000 = 0. The single root t = 0.5 is the
top of the arch, where the line touches it. Print it once.

## Constraints

- Every coordinate is between −1000 and 1000 and is a multiple of 0.25. l1 ≠ l2. The curve
  never lies along the line.
- Every root that isn't exactly 0 or 1 is at least 0.01 away from 0 and from 1. Two different
  roots are at least 0.01 apart.
- A test has from 1 to 74 lines.
- There are 35 tests: hand-made lines for each rule, random curves and lines, and one
  horizontal line against every curve of 'o' and 'S' (JetBrains Mono Bold) and 'あ' (Noto
  Sans JP).
- Each case has a 10-second limit. A correct solution takes milliseconds.

## Source material

- Pomax, *A Primer on Bézier Curves*, [Intersections](https://pomax.github.io/bezierinfo/#intersections) (line-curve intersection) and [Bézier curvatures as matrix operations](https://pomax.github.io/bezierinfo/#matrix) (the polynomial form)
- Wikipedia, [Quadratic formula](https://en.wikipedia.org/wiki/Quadratic_formula), including the discriminant and a version that avoids cancellation
- Microsoft, *OpenType specification*, [glyf: Glyph Data](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf), on the quadratic curves in TrueType outlines
- The blog: [Intersection detection for Bézier curves](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Intersection%20detection%20for%20B%C3%A9zier%20curves)

## Hints

<details><summary>Hint 1: where to start</summary>

Write `solveQuadratic(a, b, c)` on its own first and test it by hand: (1, −3, 2) gives 1 and 2;
(1, 2, 1) gives −1 once; (1, 0, 1) gives nothing; (0, 2, −1) gives 0.5. Then the rest is a
few dot products.
</details>

<details><summary>Hint 2: the approach</summary>

Compute A, B and C from the curve, and K from the line. Turn them into the three numbers
a, b, c. Solve, keep the roots between 0 and 1, sort them, and turn each one back into a point
with A t² + B t + C. Check each step against Example 1.
</details>

<details><summary>Hint 3: the traps</summary>

- a = 0 happens, and often with horizontal lines. Dividing by 2a then gives `inf` or `nan`, and
  the crossing silently disappears.
- When D = 0, return the root once, not twice.
- Sort the roots. Which formula gives the smaller one depends on the sign of a, and that sign
  flips when the line's direction is reversed.
- Don't check the points against l1 and l2. The line goes on forever.
- Keep t = 0 and t = 1: use ≤ at both ends. A half-open range like 0 ≤ t < 1 loses crossings at
  p3.
- Check D before taking its square root. The square root of a negative number is `nan`.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
solveQuadratic(a, b, c):
    if a == 0:
        return [] if b == 0 else [-c / b]
    D = b*b - 4*a*c
    if D < 0:  return []
    if D == 0: return [-b / (2*a)]
    return sorted([(-b - sqrt(D)) / (2*a), (-b + sqrt(D)) / (2*a)])

intersect(p1, p2, p3, l1, l2):
    A = p1 - 2*p2 + p3;  B = 2*(p2 - p1);  C = p1
    d = l2 - l1;  K = (d.y, -d.x)
    roots = solveQuadratic(dot(K, A), dot(K, B), dot(K, C - l1))
    return [A*t*t + B*t + C for t in roots if 0 <= t <= 1]
```
</details>

## Checking your solution

```
.\check 13                          run every test
.\check 13 -Case 13-R1-arch         one test, showing its full input, expected output and your output
.\check 13 -Fresh                   a new set of tests (new random seed), to confirm on data you haven't seen
.\check 13 -Dispute <id> "why"      set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  A tangent line gives its touching point once .........................    1 / 4   FAILED
      x 13-R4-arch-top  a horizontal line touching the top of an arch at t = 0.5
          line 1: expected `5 5`, got `5 5 5 5`
          expected values from: exact arithmetic (fractions.Fraction, 60-digit decimal square roots), root count cross-checked
          reproduce: build/solutions/assignment_13.exe build/cases/13/13-R4-arch-top.in build/cases/13/13-R4-arch-top.out
```

## After you pass: compare with the author's code

[The blog's listing](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=intersections%20of%20a%20segment%20and%20a%20quadratic)
is one function, `segmentQuadBezierIntersect`, that returns `std::vector<glm::vec2>`. It
builds K, A, B and C as on this page, calls `solveQuadratic(dot(k, a), dot(k, b),
dot(k, c - l1))`, and keeps the roots with −eps ≤ t ≤ 1 + eps.

**Something to look for:**

- Despite its name, the function treats l1 and l2 as an infinite line. It never checks that a
  point lies between them. That suits the blog's fill, whose scanline spans the whole image.
- `solveQuadratic` isn't shown. A version that always uses the quadratic formula loses every
  crossing where a = 0 (R5), and in real glyphs that is a common case for horizontal lines.
- The points come out in whatever order `solveQuadratic` returns the roots. This assignment
  asks for increasing t so that every answer has one correct form.
