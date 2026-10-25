# 12 · Intersect two segments

**Difficulty:** Medium · **Assignment** 12 of 18 · **Check:** `.\check 12`

**Tags**
- *Language:* [floating-point arithmetic](#primer/floating-point) (`double`) · [`std::optional`](#primer/optional) for "no answer" · small [structs](#primer/struct-class)
- *Library:* none for the maths itself · the boilerplate's input and output code uses [`std::istringstream`](#primer/sstream), [`std::snprintf`](#primer/cstdio) and [`std::isnan`/`std::isinf`](#primer/cmath)
- *Concepts:* [2D cross product](#primer/cross-product) · [which side of a line a point is on](#primer/cross-product) · [parametric form of a segment](#primer/segment-intersection) · [parallel and collinear lines](#primer/segment-intersection) · [closed segments](#primer/segment-intersection) (endpoints included)

## Read in the blog first

The page alone gets you through. The background is in the blog's "Renderer: Filling Glyph"
section: the start of
[Even-odd Rule](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=Even%2Dodd%20Rule),
then [intersection of line segments](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=intersection%20of%20line%20segments).
Read through the formula for t and stop. The author's listing, "Function to find a
intersections of 2 segments", follows it.

## Learning material

- [The 2D cross product and the side test](#primer/cross-product): `Geometry.h` needs a `cross`
  and a `side` helper, and the segment test builds on them.
- [Intersecting two segments](#primer/segment-intersection): `segmentsIntersect` in
  `utils/Geometry.h` takes two segments and gives back their meeting point.
- [Floating-point tolerances](#primer/epsilon): the coordinates here are multiples of 0.25, so
  the arithmetic stays exact, and a test against `0` and one against a small tolerance such as
  `1e-9` both pass.
- [`<optional>`](#primer/optional): `segmentsIntersect` returns a `std::optional<Vec2>`, and the
  program writes `none` when it comes back empty.

## Source material

- cp-algorithms, [Check if two segments intersect](https://cp-algorithms.com/geometry/check-segments-intersection.html), the side test with endpoints and collinear cases
- cp-algorithms, [Finding intersection of two segments](https://cp-algorithms.com/geometry/segments-intersection.html)
- Wikipedia, [Line–line intersection: given two points on each line segment](https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection#Given_two_points_on_each_line_segment), the parameters t and u in closed form
- The blog: [intersection of line segments](https://yayo1.com/en/blog/tiny-truetype-renderer/#:~:text=intersection%20of%20line%20segments)

## Where this fits

The blog's even-odd fill sends a scanline, a horizontal line across the glyph, through every
row and uses this function to find where it crosses each straight edge; the fill then paints
between pairs of crossings. You write the function here, endpoints included. Assignment 13 does
the same job for a curved edge, and both end up in `utils/Geometry.h`.

Your own fill in assignment 14 skips this function. For a scanline through a vertex, this function
reports that point for each edge meeting there, while the fill's half-open rule has to count it once, so
the fill works out each crossing's x from the edge.

## The problem

Each input line gives two line segments. Print the point where they meet, or `none`.

### Input

The checker starts your program in the workbook folder as `<program> <input-file> <output-file>`.
All lines of the input have one form:

| Line | Meaning |
|---|---|
| `segments a1x a1y a2x a2y b1x b1y b2x b2y` | Segment A runs from a1 = (a1x, a1y) to a2 = (a2x, a2y). Segment B runs from b1 = (b1x, b1y) to b2 = (b2x, b2y). |

### Output

Answer each input line with one line, keeping the order: the meeting point as `x y`, or the word
`none`.

The checker accepts numbers within 0.001 of the expected one, so `5`, `5.0` and `5.0000` all match `5`. For
a fractional value 4 decimals are plenty. `number()` in the boilerplate does the formatting: whole
numbers lose the decimal point; any other value prints with 4 decimals and no trailing zeros
(`37.5`, `0.0625`).

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
- Its sign tells you which way you turn going from the direction of u to the direction of v.

A side value says which side of a line a point is on. For a line through s and e, and a point
p:

```
side(p; s, e) = cross(e − s, p − s)
```

Positive on one side of the line, negative on the other, 0 when p lies on it.

### Step 1: the side test

Segment B can reach segment A's line only if b1 and b2 aren't on the same side of it, with a
point on the line counting as on neither side. The same goes for A against B's line. Both
conditions must hold:

```
side(b1; a1, a2) · side(b2; a1, a2) ≤ 0     and     side(a1; b1, b2) · side(a2; b1, b2) ≤ 0
```

If either product is positive, the answer is `none`. Use ≤, not <. An endpoint lying on the
other segment's line has side value 0, which makes the product 0, and that's how a touching
pair gets through.

### Step 2: the meeting point

Let v1 = a2 − a1 and v2 = b2 − b1. If cross(v1, v2) = 0, the segments are parallel or
collinear, and the answer is `none` (rule 2). Collinear segments pass the side test, since every
side value is 0, so you still need this check after Step 1. Otherwise:

```
t = cross(b1 − a1, v2) / cross(v1, v2)
point = a1 + t · v1
```

The formula comes from writing a point on A as a1 + t·v1 and a point on B as b1 + s·v2,
setting them equal, and taking the cross product of both sides with v2. The s term vanishes
because cross(v2, v2) = 0. After Step 1, t lies between 0 and 1.

Another route gives the same answers. Also compute s = cross(b1 − a1, v1) / cross(v1, v2), and
accept the point only when t and s are both between 0 and 1, inclusive.

### Exact arithmetic

Coordinates are multiples of 0.25 between −1000 and 1000, so in `double` arithmetic every
side value and cross product above is exact:

- A touch gives a side value of 0 and parallel segments give a cross product of 0, with no
  rounding error in either.
- Multiplying two side values to compare signs can round the product, but the sign survives.
  Comparing the two signs without multiplying avoids the question.
- A tolerance such as `|cross(v1, v2)| < 1e-9` also works: for two segments in the tests that
  aren't parallel, |cross(v1, v2)| is at least 0.25.

## Requirements

Every test exercises one of these requirements. A failure report gives counts under each, and
sometimes a `likely cause` line aimed at the requirement your difference resembles.

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

The horizontal line y = 5 passes through (3, 5), where the two edges meet. On the first line,
side(b1; a1, a2) = cross((200, 0), (103, 0)) = 0, so the product is 0 and the touch counts.
Both edges report the same corner. A fill that counts crossings would count this corner twice.
The blog deals with that in "Removal of fill errors", and assignment 15 builds one piece of the
fix.

### Example 3: collinear segments (test `12-R4-collinear-overlap`)

```
input:   segments 0 0 10 10 5 5 15 15
         segments 0 0 10 0 2 0 8 0
         segments 0 0 10 0 8 0 2 0

output:  none
         none
         none
```

Every side value is 0, so the side test lets all three through. Then cross(v1, v2) is 0 and the
answer is `none`.

## Constraints

- Every coordinate is between −1000 and 1000 and is a multiple of 0.25. No segment has zero
  length.
- For two segments that aren't parallel, |cross(v1, v2)| ≥ 0.25.
- Between 1 and 20 lines per test.
- 34 tests: hand-made pairs for each rule, random pairs aimed at R1 to R4, random
  pairs on a small grid (where touching and collinear pairs are common), and horizontal lines
  across every edge of 'K' and 'Z' from JetBrains Mono Bold, once between corners and once
  through a corner.
- 10 seconds per case, and milliseconds are enough.

## Hints

<details><summary>Hint 1: where to start</summary>

Write `cross(u, v)` first and check it by hand: cross((1, 0), (0, 1)) = 1 and
cross((2, 4), (1, 2)) = 0. The side test, the parallel check and the formula for t all come out
of it.
</details>

<details><summary>Hint 2: the approach</summary>

Three steps, in this order. Reject the pair if either side-test product is positive. Reject it
if cross(v1, v2) is 0. Otherwise compute t and return a1 + t·v1. Work through Example 1 and have
your code print each intermediate value to compare.
</details>

<details><summary>Hint 3: the traps</summary>

- The side test takes ≤ 0. With < 0, every touching case (R2) comes out as `none`.
- Skip the side test and you get the crossing of two infinite lines, which can lie outside the
  segments (R3).
- Check cross(v1, v2) before dividing by it. Collinear segments pass the side test, and 0 / 0
  gives `nan`.
- Argument order inside `cross` matters: cross(u, v) = −cross(v, u). Swap the arguments in only
  one of the two cross products for t and the point lands on the wrong side of a1.
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

Failing, a test reads:

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
is a single function, `segmentsIntersect`, returning `std::optional<glm::vec2>`. Inside it, a
lambda `region` computes the side value and a lambda `cross` the cross product. `region` takes
the opposite sign from this page's `side`, which can't change a product. The flow matches: the
side test with ≤ 0, then the denominator check, then a1 + t·v1.

The parallel check compares |cross(v1, v2)| with an `eps` that the listing leaves undefined. The
author's repository sets it in `Geometry.h` to `std::numeric_limits<float>::epsilon()`, about
1.2 × 10⁻⁷. Any small value works for glyph outlines, since two edges that aren't parallel have
a cross product far from 0. In the blog's fill, one of the two segments is the scanline itself,
running from x = 0 to the image width.

The blog's names for the two segment parameters are t and u. Here they are t and s.
