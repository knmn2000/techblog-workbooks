# 10 · Lerp and quadratic Bezier curves

**Difficulty:** Easy · **Checkpoint** 10 of 18 · **Check:** `.\check 10`

**Tags**
- *Language:* floating-point arithmetic (`double`) · small structs with `+`, `-` and `*` operators
- *Library:* none needed (the boilerplate's input/output uses `std::istringstream`) · optional: `glm::dvec2` from `third_party/glm-1.0.1`
- *Concepts:* linear interpolation (lerp) · quadratic Bezier curves · control points · de Casteljau's algorithm · curve parameter t

## Read in the blog first

This page is complete on its own; the blog tells the story behind it. Read the start of the
blog's **"Renderer: Curve Rendering"** section:
[Definition of Bézier Curves](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Definition%20of%20B%C3%A9zier%20Curves)
and [De Casteljau's algorithm](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=De%20Casteljau,algorithm).
Stop at the sentence that introduces the code. The author's code (the listing "Lerp for a
segment and a quadratic Bézier curve") comes right after it. "TrueType Bézier curves" belongs
to checkpoint 11.

## Where this fits

Checkpoint 8 drew glyph outlines with straight lines only. Real glyphs are made of quadratic
Bezier curves: an on-curve start point, an off-curve control point and an on-curve end point.
This checkpoint computes points along such a curve. Checkpoint 11 draws each curve by joining
many of these points with short straight lines.

## The problem

Write a program that reads a list of requests, one per line, and prints the point that each
one asks for.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p10_bezier.cpp` is a comment and an empty `main`:
the includes, reading the input and writing the output are yours. To start from working
input/output code instead, copy `starters/boilerplate/p10_bezier.cpp` over it, or pick
Boilerplate in the book's editor. The boilerplate reads the input and writes the output; you
fill in `lerp()` and `bezier()`.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains two kinds of lines:

| Line | Meaning |
|---|---|
| `lerp ax ay bx by t` | The point a fraction `t` of the way along the straight segment from a = (ax, ay) to b = (bx, by). |
| `bezier ax ay bx by cx cy t` | The point at parameter `t` on the quadratic Bezier curve that starts at a = (ax, ay), ends at c = (cx, cy), and is pulled toward the control point b = (bx, by). |

Every number is a decimal such as `12`, `-3.25` or `0.0625`. `t` is always between 0 and 1,
inclusive. Note the order on a `bezier` line: start, **control point**, end.

### Output

One line per input line, in the same order: the point's coordinates `x y`, separated by a
space.

The checker accepts any number within 0.001 of the expected value, so `25`, `25.0` and
`25.0000` all match `25`. When a value isn't whole, print enough decimals to be within 0.001
(4 is plenty). The boilerplate's `number()` does this: whole numbers plainly, others rounded to 4 decimals with trailing zeros dropped (`37.5`, `0.0625`).

### Linear interpolation

The point a fraction t of the way from a to b is

```
lerp(a, b, t) = a + (b − a) · t
```

Work it out for x and y separately. t = 0 gives a, t = 1 gives b and t = 0.5 gives the
midpoint. Because t is measured from a, `lerp(a, b, 0.25)` is close to a, and
`lerp(b, a, 0.25)` is close to b.

### A point on a quadratic Bezier curve

A quadratic Bezier curve is defined by three points: the start a, the control point b and the
end c. The curve leaves a heading toward b and arrives at c coming from the direction of b. It
is pulled toward b but doesn't pass through it (unless all three points lie on one line).

The point at parameter t takes three lerps, all with the same t. This is **de Casteljau's
construction**:

1. p = lerp(a, b, t), a point on the leg from a to the control point
2. q = lerp(b, c, t), a point on the leg from the control point to c
3. The curve point is lerp(p, q, t).

Multiplying it out gives the same point as one formula, which you may use instead:

```
B(t) = (1 − t)² · a  +  2 (1 − t) t · b  +  t² · c
```

The three weights, (1 − t)², 2(1 − t)t and t², always add up to 1. At t = 0 the curve is at
a; at t = 1 it is at c.

| t | (1 − t)² | 2(1 − t)t | t² |
|---|---|---|---|
| 0 | 1 | 0 | 0 |
| 0.25 | 0.5625 | 0.375 | 0.0625 |
| 0.5 | 0.25 | 0.5 | 0.25 |
| 1 | 0 | 0 | 1 |

## Requirements

Each test case is designed around one of these.

- **R1** A `lerp` line gives the point a fraction t of the way from a to b.
- **R2** A `bezier` line gives the point at t on the curve that starts at a, ends at c and is
  pulled toward the control point b (the **middle** point on the line).
- **R3** The ends are exact: t = 0 gives the first point and t = 1 the last one. For a curve,
  that is c, not the control point b.
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

On the first line, b − a = (40, 80). A quarter of that is (10, 20), and a + (10, 20) =
(20, 40). The second line swaps a and b, so the quarter is measured from (50, 100) instead.

### Example 2: the middle of an arch (test `10-R2-midpoint`)

```
input:   bezier 0 0 50 100 100 0 0.5
output:  50 50
```

| Step | Computation | Result |
|---|---|---|
| p = lerp(a, b, 0.5) | halfway from (0, 0) to (50, 100) | (25, 50) |
| q = lerp(b, c, 0.5) | halfway from (50, 100) to (100, 0) | (75, 50) |
| lerp(p, q, 0.5) | halfway from (25, 50) to (75, 50) | **(50, 50)** |

The control point is at height 100, but the curve only reaches 50. With the formula:
0.25 · (0, 0) + 0.5 · (50, 100) + 0.25 · (100, 0) = (50, 50).

### Example 3: the end of a curve is c, not b (test `10-R3-control-not-on-curve`)

```
input:   bezier 0 0 0 100 100 100 1
         bezier 0 0 0 100 100 100 0.5

output:  100 100
         25 75
```

At t = 1 every weight except t² is 0, so the curve ends at c = (100, 100). The control point
(0, 100) only bends the curve: at t = 0.5, p = (0, 50), q = (50, 100) and the point is (25, 75).

## Constraints

- Every coordinate in the input is between −1000 and 1000, and has at most 4 digits after the
  decimal point. `t` is between 0 and 1, inclusive.
- The input is well-formed: each line has the keyword and the right count of numbers.
- A test has from 1 to about 80 lines.
- There are 24 tests: hand-made lines for each rule, random lines, and every line and curve of
  'S' and 'o' (JetBrains Mono Bold) and 'あ' (Noto Sans JP), plus one curve of '3' cut into 16
  steps.
- Each case has a 10-second limit. A correct solution takes milliseconds.
- 32-bit `float` is accurate enough for these tests, but `double` is the safer habit.

## Source material

- Apple, *TrueType Reference Manual*, [Digitizing Letterform Designs](https://developer.apple.com/fonts/TrueType-Reference-Manual/RM01/Chap1.html), on quadratic curves in TrueType outlines
- Microsoft, *OpenType specification*, [glyf: Glyph Data](https://learn.microsoft.com/en-us/typography/opentype/spec/glyf), where on-curve and off-curve points are defined
- Pomax, *A Primer on Bézier Curves*, [de Casteljau's algorithm](https://pomax.github.io/bezierinfo/#decasteljau), with interactive drawings
- The blog: [De Casteljau's algorithm](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=De%20Casteljau,algorithm)

## Hints

<details><summary>Hint 1: where to start</summary>

Write `lerp` first and test it on Example 1. A curve point can be built from three calls to
`lerp`, so once `lerp` works, `bezier` is one line.
</details>

<details><summary>Hint 2: the approach</summary>

Treat a point as a pair and apply the same arithmetic to x and y. For a curve, lerp along the
leg a → b and along the leg b → c with the same t, then lerp between those two results, again
with the same t. Check yourself on Example 2, where every step lands on a round number.
</details>

<details><summary>Hint 3: the traps</summary>

- It is (b − a) · t, not (a − b) · t. At t = 0.25 the point is closer to a.
- On a `bezier` line the middle point is the control point and the last point is the end. At
  t = 1 the answer is c.
- Use the same t in all three lerps, and lerp from the first leg's point to the second leg's
  point, not the other way round.
- If you use the expanded formula, don't drop the 2 on the middle term. The weights must add
  up to 1.
- Read the numbers as floating point. Inputs like `46.5` and `0.0625` are common.
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

A failing test looks like this:

```
  R2  bezier: the point at t on the curve from a to c, pulled toward b .....    0 / 7   FAILED
      x 10-R2-midpoint  an arch from (0,0) to (100,0) pulled toward (50,100): t = 0.5
          line 1: expected `50 50`, got `37.5 25`
          expected values from: exact arithmetic with Python fractions.Fraction
          reproduce: build/p10.exe build/cases/10/10-R2-midpoint.in build/cases/10/10-R2-midpoint.out
```

## After you pass: compare with the author's code

[The blog's listing](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Lerp%20for%20a%20segment)
has two short functions on `glm::vec2`. `lerp` asserts that t is between 0 and 1 and returns
a + (b − a) · t. `bezierLerp` nests three `lerp` calls in de Casteljau's order, as in
Example 2. The expanded formula appears only in the blog's prose, not in its code.

**Something to look for:** the drawing code in the next section ("TrueType Bézier curves")
calls the curve function `quadBezierLerp`, while this listing names it `bezierLerp`. They are
the same function. If you follow along in C++, pick one name.
