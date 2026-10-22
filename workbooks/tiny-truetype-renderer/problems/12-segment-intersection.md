# 12 · Intersect two segments

**Difficulty:** Medium · **Assignment** 12 of 18 · **Check:** `.\check 12`

**Tags**
- *Language:* floating-point arithmetic (`double`) · `std::optional` for "no answer" · small structs
- *Library:* none needed (the boilerplate's input/output uses `std::istringstream`)
- *Concepts:* 2D cross product · which side of a line a point is on · parametric form of a segment · parallel and collinear lines · closed segments (endpoints included)

## Read in the blog first

You can pass using this page alone. For the background, in the blog's
"Renderer: Filling Glyph" section, read the start of
[Even-odd Rule](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Even%2Dodd%20Rule)
and then [intersection of line segments](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=intersection%20of%20line%20segments).
Stop after the formula for t. The author's code (the listing "Function to find a
intersections of 2 segments") follows it.

## Source material

- cp-algorithms, [Check if two segments intersect](https://cp-algorithms.com/geometry/check-segments-intersection.html), the side test with endpoints and collinear cases
- cp-algorithms, [Finding intersection of two segments](https://cp-algorithms.com/geometry/segments-intersection.html)
- Wikipedia, [Line–line intersection: given two points on each line segment](https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line_segment), the parameters t and u in closed form
- The blog: [intersection of line segments](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=intersection%20of%20line%20segments)

## Where this fits

The blog's even-odd fill finds where each row's scanline, a horizontal line across the glyph,
meets each straight edge of the outline with this function, and fills between pairs of those
points. Here you write it: the point where two segments meet, endpoints included. In assignment
13 you do the same for a curved edge, and both go into your `utils/Geometry.h`.

Your fill in assignment 14 doesn't call this function. For a scanline through a vertex, this
function reports that point for both edges that meet there, while the fill's half-open rule
counts it once. The fill works out each crossing's x from the edge instead.

## The problem

Your program reads pairs of line segments. For each pair it writes the point where the two
segments meet, or `none`.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Every line of the input file has the same form:

| Line | Meaning |
|---|---|
| `segments a1x a1y a2x a2y b1x b1y b2x b2y` | Segment A runs from a1 = (a1x, a1y) to a2 = (a2x, a2y). Segment B runs from b1 = (b1x, b1y) to b2 = (b2x, b2y). |

### Output

Write one line per input line, in the same order: the meeting point as `x y`, or the word
`none`.

The checker accepts any number within 0.001 of the expected value, so `5`, `5.0` and
`5.0000` all match `5`. If a value isn't whole, print enough decimals to land within 0.001;
4 decimals are enough. The boilerplate's `number()` prints whole numbers with no decimal point
and rounds the others to 4 decimals, dropping trailing zeros (`37.5`, `0.0625`).

### The rules

1. Segments include their endpoints. If the two segments meet only at an endpoint, that
   point is the answer. This covers two edges of a polygon that share a corner, and a
   T-junction, where one segment ends on the middle of the other.
2. Parallel segments give `none`. That includes collinear segments, which lie on the
   same line, even when they overlap, touch end to end, or are identical. They have no single
   meeting point. (For filling this is harmless: an edge that lies along the scanline adds no
   crossing.)
3. Otherwise the answer is the one point the two segments share, or `none` if they don't
   share one. Two lines that aren't parallel cross at one point, but that point may lie
   beyond the end of one segment or both.

### The 2D cross product

```
cross(u, v) = u.x · v.y − u.y · v.x
```

- It is 0 when u and v are parallel or one of them is zero, and only then.
- Its sign says which way you turn going from the direction of u to the direction of v.

The side value tells you which side of a line a point is on. For a line through s and e, and
a point p, it is:

```
side(p; s, e) = cross(e − s, p − s)
```

The result is positive on one side of the line, negative on the other, and 0 when p lies on
the line.

### Step 1: the side test

Segment B can reach segment A's line only if b1 and b2 don't lie on the same side of it, where
a point on the line counts as on neither side. The same goes for A and B's line. Both
conditions must hold:

```
side(b1; a1, a2) · side(b2; a1, a2) ≤ 0     and     side(a1; b1, b2) · side(a2; b1, b2) ≤ 0
```

If either product is positive, the answer is `none`. Use ≤, not <: when an endpoint lies on
the other segment's line, its side value is 0, so the product is 0 and a touching pair passes.

### Step 2: the meeting point

Let v1 = a2 − a1 and v2 = b2 − b1. If cross(v1, v2) = 0, the segments are parallel or
collinear: the answer is `none` (rule 2). Collinear segments pass the side test, because every
side value is 0, so you need this check even after Step 1. Otherwise:

```
t = cross(b1 − a1, v2) / cross(v1, v2)
point = a1 + t · v1
```

The formula comes from writing a point on A as a1 + t·v1 and a point on B as b1 + s·v2. If
you set them equal and take the cross product of both sides with v2, s drops out, because
cross(v2, v2) = 0. After Step 1, t is between 0 and 1.

You can get the same answers another way: also compute s = cross(b1 − a1, v1) / cross(v1, v2),
and accept the point only when t and s are both between 0 and 1, inclusive.

### Exact arithmetic

Every coordinate is a multiple of 0.25 between −1000 and 1000. In `double` arithmetic every
side value and cross product above is then exact:

- Touching gives a side value of 0, and parallel segments give a cross product of 0, with no
  rounding error in either.
- If you multiply two side values to compare their signs, the product can round, but its sign
  is still exact. If you compare the two signs without multiplying, nothing rounds.
- A tolerance such as `|cross(v1, v2)| < 1e-9` also works: when two segments in the tests
  aren't parallel, |cross(v1, v2)| is at least 0.25.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** Segments that cross at a point inside both give that point.
- **R2** Touching counts: if the segments meet at an endpoint of either one (a shared corner
  or a T-junction), that point is the answer.
- **R3** If the lines cross outside either segment, the answer is `none`.
- **R4** Parallel segments give `none`, and so do collinear ones, even when they overlap or
  meet end to end.
- **R5** Vertical, horizontal, negative and fractional coordinates work like any others.

## Examples

### Example 1: a crossing (test `12-R1-off-center`)

```
input:   segments 0 0 8 4 2 6 6 -2
output:  4 2
```

| Step | Computation | Result |
|---|---|---|
| side(b1; a1, a2), side(b2; a1, a2) | cross((8, 4), (2, 6)), cross((8, 4), (6, −2)) | 40, −40: opposite sides |
| side(a1; b1, b2), side(a2; b1, b2) | cross((4, −8), (−2, −6)), cross((4, −8), (6, −2)) | −40, 40: opposite sides |
| cross(v1, v2) | 8 · (−8) − 4 · 4 | −80 |
| cross(b1 − a1, v2) | 2 · (−8) − 6 · 4 | −40 |
| t, point | −40 / −80 = 0.5, (0, 0) + 0.5 · (8, 4) | (4, 2) |

### Example 2: a horizontal line through a corner (test `12-R2-scanline-vertex`)

```
input:   segments -100 5 100 5 3 5 7 12
         segments -100 5 100 5 0 0 3 5

output:  3 5
         3 5
```

The horizontal line y = 5 passes through (3, 5), where the two edges meet. On the
first line, side(b1; a1, a2) = cross((200, 0), (103, 0)) = 0, so the product is 0 and the
touch counts. Both edges report the same corner. A fill that counts crossings would count this
corner twice; the blog fixes that in "Removal of fill errors" (assignment 15 builds one piece
of that fix).

### Example 3: collinear segments (test `12-R4-collinear-overlap`)

```
input:   segments 0 0 10 10 5 5 15 15
         segments 0 0 10 0 2 0 8 0
         segments 0 0 10 0 8 0 2 0

output:  none
         none
         none
```

Every side value is 0, so the side test passes. cross(v1, v2) is 0, so the answer is `none`.

## Constraints

- Every coordinate is between −1000 and 1000 and is a multiple of 0.25. No segment has zero
  length.
- For two segments that aren't parallel, |cross(v1, v2)| ≥ 0.25.
- A test has from 1 to 20 lines.
- There are 34 tests: hand-made pairs for each rule, random pairs aimed at R1 to R4, random
  pairs on a small grid (where touching and collinear pairs are common), and horizontal lines
  across every edge of 'K' and 'Z' from JetBrains Mono Bold, once between corners and once
  through a corner.
- Each case has a 10-second limit. A correct solution takes milliseconds.

## Hints

<details><summary>Hint 1: where to start</summary>

Write `cross(u, v)` first and check it by hand: cross((1, 0), (0, 1)) = 1 and
cross((2, 4), (1, 2)) = 0. You build the side test, the parallel check and the formula for t
from it.
</details>

<details><summary>Hint 2: the approach</summary>

Work in three steps, in this order. Reject the pair if either side-test product is positive.
Reject it if cross(v1, v2) is 0. Otherwise compute t and return a1 + t·v1. Work through
Example 1 and have your code print each intermediate value.
</details>

<details><summary>Hint 3: the traps</summary>

- Use ≤ 0 in the side test. With < 0, every touching case (R2) gives `none`.
- Without the side test you get the crossing of two infinite lines, which can lie outside the
  segments (R3).
- Check cross(v1, v2) before dividing by it. Collinear segments pass the side test, and 0 / 0
  gives `nan`.
- The order inside `cross` matters: cross(u, v) = −cross(v, u). If you swap the arguments in
  only one of the two cross products for t, the point lands on the wrong side of a1.
- t belongs to segment A, so the point is a1 + t·v1, not b1 + t·v2.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
cross(u, v) = u.x * v.y - u.y * v.x
side(p, s, e) = cross(e - s, p - s)

intersect(a1, a2, b1, b2):
    if side(b1, a1, a2) * side(b2, a1, a2) > 0: return none
    if side(a1, b1, b2) * side(a2, b1, b2) > 0: return none
    v1 = a2 - a1
    v2 = b2 - b1
    d = cross(v1, v2)
    if d == 0: return none                  # parallel or collinear
    t = cross(b1 - a1, v2) / d
    return a1 + t * v1
```
</details>

## Checking your solution

```
.\check 12                               run every test
.\check 12 -Case 12-R2-scanline-vertex   one test, showing its full input, expected output and your output
.\check 12 -Fresh                        a new set of tests (new random seed), to confirm on data you haven't seen
.\check 12 -Dispute <id> "why"           set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R3  Lines that cross outside either segment -> none ......................    0 / 4   FAILED
      x 12-R3-beyond-end  the lines cross at (5, 5) but the first segment stops at (4, 4)
          line 1: expected `none`, got `5 5`
          likely cause: R3 - Lines that cross outside either segment -> none
          expected values from: exact arithmetic with Python fractions.Fraction (parametric solve, cross-checked)
          reproduce: build/solutions/assignment_12.exe build/cases/12/12-R3-beyond-end.in build/cases/12/12-R3-beyond-end.out
```

## After you pass: compare with the author's code

[The blog's listing](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=intersections%20of%202%20segments)
is one function, `segmentsIntersect`, that returns `std::optional<glm::vec2>`. Inside, a
lambda `region` computes the side value and a lambda `cross` the cross product. `region` uses
the opposite sign from this page's `side`, which makes no difference to a product. The
function runs the side test with ≤ 0 as here, then checks the denominator, then returns
a1 + t·v1.

The parallel check compares |cross(v1, v2)| with an `eps` that the
listing doesn't define. Any small value works for glyph outlines, because two edges that
aren't parallel have a cross product far from 0. In the blog's fill, one of the two segments
is the scanline itself, running from x = 0 to the image width.
