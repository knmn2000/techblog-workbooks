# 13 · Intersect a line and a quadratic curve

**Difficulty:** Medium · **Assignment** 13 of 18 · **Check:** `.\check 13`

**Tags**
- *Language:* [floating-point arithmetic](#primer/floating-point) (`double`) · returning a list of results ([`std::vector`](#primer/vector)) · [sorting](#primer/algorithm)
- *Library:* [`std::sqrt`](#primer/cmath), [`std::sort`](#primer/algorithm)
- *Concepts:* [quadratic Bezier curve](#primer/bezier) as a polynomial · [normal vector and dot product](#primer/vector-2d) · [quadratic equations and the discriminant](#primer/quadratic-equation) · [the degenerate (linear) case](#primer/quadratic-equation) · [tangent lines](#primer/quadratic-equation) · [curve parameter t](#primer/bezier)

## Read in the blog first

You need nothing outside this page to pass. For the author's take, open the "Renderer: Filling Glyph"
section of the blog and read
[Intersection detection for Bézier curves](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Intersection%20detection%20for%20B%C3%A9zier%20curves)
as far as the quadratic equation in t. The listing "Function to find a
intersections of a segment and a quadratic Bezier curve" comes straight after. The curve
itself was assignment 10.

## Learning material

- [Solving a quadratic equation](#primer/quadratic-equation): `segmentQuadBezierIntersect` in
  `utils/Geometry.h` boils down to a t² + b t + c = 0, which needs a solver that copes
  with a = 0. A horizontal line produces that whenever the control point's y sits halfway
  between the end points' y.
- [Quadratic Bézier curves](#primer/bezier): you multiply out the curve from assignment 10
  into a polynomial in t, with one set of coefficients for x and one for y.
- [2D vectors and the dot product](#primer/vector-2d): the line becomes K · (X − l1) = 0, with K
  the line's normal vector, and you add a dot product helper to `utils/Geometry.h` to compute
  a, b and c.
- [Floating-point tolerances](#primer/epsilon): the test coordinates are multiples of 0.25, so
  a and D come out as 0 with no rounding error in the linear and tangent cases. `== 0` passes, and so does a
  tolerance such as 1e-9.

## Source material

- Pomax, *A Primer on Bézier Curves*, [Intersections](https://pomax.github.io/bezierinfo/#intersections) (line-curve intersection) and [Bézier curvatures as matrix operations](https://pomax.github.io/bezierinfo/#matrix) (the polynomial form)
- Wikipedia, [Quadratic formula](https://en.wikipedia.org/wiki/Quadratic_formula), including the discriminant and a version that avoids cancellation
- Microsoft, *OpenType specification*, [glyf: Glyph Data](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf), on the quadratic curves in TrueType outlines
- The blog: [Intersection detection for Bézier curves](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Intersection%20detection%20for%20B%C3%A9zier%20curves)

## Where this fits

The blog's even-odd fill sweeps a horizontal line across the glyph, one pixel row at a time,
and asks where it meets each edge. Assignment 12 answered that for straight edges. A curve can meet
the line in zero, one or two points. You add the function to your `utils/Geometry.h`.

Your fill in assignment 14 won't call that function. Here the roots at t = 0 and t = 1 stay, so a scanline
through the joint between a curve and the next edge finds that point on both, and the fill's
half-open rule wants it counted once. The fill splits each curve where y turns and solves each
piece's own quadratic.

## The problem

Each input line gives a quadratic Bezier curve and a straight line. For each one, print the
points where the line meets the curve, or `none`.

### Input

The workbook folder is where the checker executes `<program> <input-file> <output-file>`. Every
input line has the same form:

| Line | Meaning |
|---|---|
| `curve p1x p1y p2x p2y p3x p3y line l1x l1y l2x l2y` | The curve starts at p1, bends toward the control point p2, and ends at p3. The line is the infinite straight line through l1 and l2. |

- The curve is the one from assignment 10: the point at parameter t is
  P(t) = (1 − t)² p1 + 2(1 − t)t p2 + t² p3, for t from 0 to 1.
- The line doesn't stop at l1 or l2. Those two points only fix its position and direction.

### Output

One line of output per input line, in the same order:

- `none` when the line misses the curve, or
- the meeting points on one line: `x1 y1`, or `x1 y1 x2 y2`.

Order the points by increasing t, meaning the order you meet them walking along the curve from
p1 to p3. Not by x, not by y. A line that touches the curve without crossing it (a tangent)
gives its one point once.

A tolerance of 0.001 applies. Print as many decimals as you need to stay inside it; 4 do the job.
`number()` from the boilerplate is the easy route: whole numbers without a decimal point, other
values rounded to 4 decimals, trailing zeros removed (`37.5`, `0.0625`).

### The curve as a polynomial

Multiply out the curve's formula and you get

```
P(t) = A t² + B t + C,    where A = p1 − 2 p2 + p3,   B = 2 (p2 − p1),   C = p1
```

A, B and C are vectors, so work each one out for x and for y.

### The line as an equation

Let d = l2 − l1 be the line's direction, and K = (d.y, −d.x). K is perpendicular to the line,
a normal vector. A point X lies on the line if and only if

```
K · (X − l1) = 0           (· is the dot product: u · v = u.x v.x + u.y v.y)
```

Sliding along the line changes X by a multiple of d, and K · d = 0, which leaves the left side at 0.

### From a line and a curve to a quadratic

Put P(t) in place of X:

```
K · (A t² + B t + C − l1) = 0
a t² + b t + c = 0,    where a = K · A,   b = K · B,   c = K · (C − l1)
```

a, b and c come out as ordinary numbers, and every solution t is a place where the curve's
polynomial meets the line.

### Solving for t

The case depends on a and on the discriminant D = b² − 4ac:

| Case | Roots |
|---|---|
| a ≠ 0 and D = b² − 4ac < 0 | none |
| a ≠ 0 and D = 0 | one: t = −b / (2a). The line is tangent to the curve. |
| a ≠ 0 and D > 0 | two: t = (−b − √D) / (2a) and t = (−b + √D) / (2a) |
| a = 0 and b ≠ 0 | one: t = −c / b. The equation is linear. |
| a = 0 and b = 0 | none. The "curve" is a straight segment parallel to the line. (If c were also 0, it would lie on the line; the tests don't have that.) |

The a = 0 case is common in real fonts. For a horizontal line, a is 0 whenever the
control point's y is halfway between the end points' y, and the quadratic formula would divide
by 0 there.

Sort the roots: when a < 0, the second formula in the table gives the smaller t.

### The roots that count

Keep only the roots with 0 ≤ t ≤ 1, ends included: t = 0 and t = 1 are where the line passes through
p1 or p3. Anything outside that range belongs to the polynomial beyond the curve's ends. Each
kept root gives the point P(t) = A t² + B t + C.

### Precision

Every coordinate is a multiple of 0.25 between −1000 and 1000, so a, b, c and D are exact in
`double`.

- In tangent cases D comes out as 0 with no rounding error, and so does a in linear cases.
  Comparing with 0 works.
- A tiny tolerance works too. Every root other than 0 and 1 is at least 0.01 away from 0 and
  1, and two different roots are at least 0.01 apart, so accepting t within 1e-9 of the ends
  gives the same answers.

## Requirements

Each test checks one of these. After a failure the checker shows how many pass for each requirement
and adds a `likely cause` line singling one out when it can.

- **R1** A line that crosses the curve twice gives both points. The line is infinite: where l1
  and l2 sit along it makes no difference.
- **R2** Only roots with 0 ≤ t ≤ 1 count: if one root is on the curve and the other is beyond
  an end, the answer is the one point.
- **R3** If no root has 0 ≤ t ≤ 1 (or there are no real roots), the answer is `none`.
- **R4** A line that touches the curve without crossing it (D = 0) gives the touching point
  once.
- **R5** If a = K · A is 0, the equation is linear: t = −c / b, or no root if b is also 0.
- **R6** Points are in increasing order of t, whichever way the line points.
- **R7** Roots at t = 0 and at t = 1 count.

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
| P(0.2), P(0.8) | A t² + B t + C | (20, 32) and (80, 32) |

### Example 2: the linear case (test `13-R5-scanline`)

```
input:   curve 0 0 10 5 0 10 line -10 5 10 5
         curve 100 0 160 50 100 100 line 0 30 1 30

output:  5 5
         125.2 30
```

Take the first line. A = (−20, 0) and K = (0, −20), so a = 0 and the quadratic formula is out.
b = K · (20, 10) = −200 and c = K · ((0, 0) − (−10, 5)) = 100, which gives t = −c / b = 0.5 and
P(0.5) = (5, 5). Both curves bulge sideways, so a horizontal line crosses each once.

### Example 3: a tangent (test `13-R4-arch-top`)

```
input:   curve 0 0 5 10 10 0 line 0 5 10 5
output:  5 5
```

Here a = 200, b = −200 and c = 50, so D = 40000 − 40000 = 0. The one root, t = 0.5, is the top
of the arch where the line grazes it. Print that point once.

## Constraints

- Coordinates are multiples of 0.25 between −1000 and 1000. l1 ≠ l2. In no test does the curve lie
  along the line.
- Every root other than 0 and 1 is at least 0.01 away from 0 and from 1. Two different roots
  are at least 0.01 apart.
- A test has from 1 to 74 lines.
- 35 tests: hand-made lines for each rule, random curves and lines, and one horizontal line
  against every curve of 'o' and 'S' (JetBrains Mono Bold) and 'あ' (Noto Sans JP).
- Cases time out at 10 seconds; the intended solution needs milliseconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Write `solveQuadratic(a, b, c)` by itself first and try it by hand: (1, −3, 2) gives 1 and 2;
(1, 2, 1) gives −1 once; (1, 0, 1) gives nothing; (0, 2, −1) gives 0.5. Once that behaves,
what's left of the function is a few dot products.
</details>

<details><summary>Hint 2: the approach</summary>

A, B and C come from the curve, K from the line. Reduce them to the three numbers a, b, c and
solve. Keep the roots between 0 and 1, sort them, and turn each back into a point with
A t² + B t + C. Example 1 lets you check every step.
</details>

<details><summary>Hint 3: the traps</summary>

- a = 0 is routine with horizontal lines. Divide by 2a anyway and you get `inf` or `nan`, and
  the crossing vanishes without any error.
- If D = 0, return the root once.
- Sort the roots. The sign of a decides which formula gives the smaller one, and reversing the
  line's direction flips that sign.
- Don't test the points against l1 and l2. The line goes on forever.
- Keep t = 0 and t = 1, so use ≤ at both ends. A half-open range like 0 ≤ t < 1 loses
  crossings at p3.
- Look at D before you take its square root. The root of a negative number is `nan`.
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

This is what a failing test prints:

```
  R4  A tangent line gives its touching point once .........................    1 / 4   FAILED
      x 13-R4-arch-top  a horizontal line touching the top of an arch at t = 0.5
          line 1: expected `5 5`, got `5 5 5 5`
          expected values from: exact arithmetic (fractions.Fraction, 60-digit decimal square roots), root count cross-checked
          reproduce: build/solutions/assignment_13.exe build/cases/13/13-R4-arch-top.in build/cases/13/13-R4-arch-top.out
```

## After you pass: compare with the author's code

[The blog's
listing](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=intersections%20of%20a%20segment%20and%20a%20quadratic)
is one function, `segmentQuadBezierIntersect`, which returns `std::vector<glm::vec2>`. It builds K,
A, B and C the way this page does, calls `solveQuadratic(dot(k, a), dot(k, b), dot(k, c - l1))`, and
keeps the roots with −eps ≤ t ≤ 1 + eps.

It differs from this assignment in these ways:

- Despite the name, it treats l1 and l2 as an infinite line and doesn't check that a point lies
  between them. That suits the blog's fill, whose scanline spans the whole image.
- The blog doesn't show `solveQuadratic`. The author's repository has it in `utils/Geometry.h`,
  in `float`, with `eps` set to `std::numeric_limits<float>::epsilon()`. |a| < eps counts as
  the linear case. That keeps the a = 0 crossings (R5) that the plain quadratic formula would
  lose. If D is within eps of 0, it returns one root. Otherwise it uses the form that
  avoids cancellation: q = −(b + sign(b)·√D) / 2, with the roots q / a and c / q.
- Points come out in whatever order `solveQuadratic` returns the roots, q / a first, and that
  order can run against increasing t. This assignment asks for increasing t so each answer has one
  correct form.
