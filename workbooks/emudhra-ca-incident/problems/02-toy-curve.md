# 02 · Add points on a toy curve

**Difficulty:** Easy · **Checkpoint** 2 of 16 · **Check:** `./check.sh 02`

**Tags**
- *Language:* small integers · modular arithmetic (`pow(a, -1, p)` in Python) · parsing a point
- *Library:* none needed
- *Concepts:* elliptic-curve point addition and doubling · the point at infinity · inverse points

## Prerequisite material

This checkpoint is prerequisite material for the later checkpoints about the eMudhra incident; it
isn't drawn from a specific blog post. Checkpoint 10 (already part of this workbook) uses this
exact curve and generator as a worked example; this checkpoint builds the addition rule that
example's table was computed from. See "Source material" below for where this comes from.

## Where this fits

Checkpoint 1 built the modular arithmetic. This checkpoint uses it to add points on a curve small
enough to check by hand - 17 is small enough to write out every point. Checkpoint 3 does the same
addition on the real, much bigger P-256 and P-384 curves, where multiplying a point by a huge
number needs this addition rule repeated efficiently.

## The problem

Write a program that reads pairs of points on the curve `y² = x³ + 2x + 2 mod 17` and adds them.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p02_toy_curve.py` is a comment and an empty program:
reading the input and writing the output are yours. To start from working input/output code
instead, copy `starters/boilerplate/p02_toy_curve.py` over it, or pick Boilerplate in the book's
editor. The boilerplate reads the input and writes the output; you fill in `add_points()`.

### A tiny example

This is the same curve, with the same generator `G = (5, 1)`, used as a worked example on
checkpoint 10's page: it lists `1*G` through `5*G` as `(5, 1)`, `(6, 3)`, `(10, 6)`, `(3, 1)`,
`(9, 16)`. That table is built by repeatedly adding `G` - exactly the operation this checkpoint
asks you to write. If you've already read that page, this is the rule behind its table; if not,
it's worth a look after you pass, as a second example of what you just built.

### The point at infinity

An elliptic curve's points don't just mean `(x, y)` pairs: there's one more point, called
**infinity**, that acts as the group's identity element - like `0` for addition, or `1` for
multiplication. `P + infinity = P` for any point `P`, and `infinity + infinity = infinity`. It
also shows up as the answer whenever a point and its own negation are added (see below). In this
checkpoint's input and output, infinity is written as the single word `inf`; it never has
coordinates.

### Adding two different points

All arithmetic below is mod 17. To add two points `P = (x1, y1)` and `R = (x2, y2)` with
`x1 != x2`:

```
slope = (y2 - y1) / (x2 - x1)
x3    = slope² - x1 - x2
y3    = slope * (x1 - x3) - y1
```

"Divide by `k`" means multiply by `k`'s modular inverse mod 17 (`pow(k, -1, 17)` in Python; see
checkpoint 1 if you haven't built this yet).

### Doubling a point

Adding a point to itself (`P + P`) uses a different slope, from the curve's tangent line at `P`:

```
slope = (3*x1² + a) / (2*y1)        (a = 2 on this curve)
x3    = slope² - 2*x1
y3    = slope * (x1 - x3) - y1
```

The `x3`, `y3` formulas are the same as above once you have the slope; only how the slope is
found differs. A point with `y1 = 0` would make `2*y1 = 0`, which has no inverse - geometrically,
the tangent there is a vertical line, and the "sum" is infinity. This curve happens to have no
point with `y = 0` (worth checking: scan all 17 values of `x` and see that none of the matching
`y`'s is `0`), so doubling never produces infinity here. Later, real curves (checkpoint 3 onward)
are built so this never happens for the same reason.

### Inverse points

The **negation** of `(x, y)` is `(x, 17 - y mod 17)` - same `x`, the other `y`. Adding a point to
its own negation always gives infinity: `P + (-P) = inf`. Check this before applying either
formula above, since `x1 == x2` there and the ordinary chord formula would divide by zero.

### Input

One line per case:

```
add <P1> <P2>
```

Each of `P1`, `P2` is either the word `inf`, or two space-separated integers `x y` with
`0 <= x, y <= 16` - a point already guaranteed to be on the curve.

### Output

One line per input line: the sum, in the same format (`inf`, or `x y`).

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** Adding two distinct points with different x, using the chord through them.
- **R2** Doubling a point (`P + P`), using the tangent at that point.
- **R3** Identity laws: `P + inf = P`, `inf + P = P`, `inf + inf = inf`.
- **R4** Inverse pairs: `P + (-P) = inf`, where `-P` is `(x, 17 - y)`.
- **R5** Every output other than `inf` is actually a point on the curve (`y² == x³ + 2x + 2 mod
  17`).
- **E2E** A full table covering every one of the curve's 19 points (18 affine points plus
  infinity) at least once, built by repeatedly adding `G` - the same process behind checkpoint
  10's worked table.

## Examples

### Example 1: the first step of the worked table (test `02-R1-small`)

```
input:   add 5 1 6 3

output:  10 6
```

`P1 = (5, 1)` is `1*G`, `P2 = (6, 3)` is `2*G`. Their x's differ, so use the chord slope:
`slope = (3 - 1) / (6 - 5) = 2`. Then `x3 = 2² - 5 - 6 = 4 - 11 = -7 mod 17 = 10`, and
`y3 = 2*(5 - 10) - 1 = -11 mod 17 = 6`. The result, `(10, 6)`, is `3*G` in checkpoint 10's table.

### Example 2: doubling (test `02-R2-g`)

```
input:   add 5 1 5 1

output:  6 3
```

Both points are `G = (5, 1)`, so use the tangent slope: `slope = (3*5² + 2) / (2*1) = 77 / 2`.
`77 mod 17 = 9`, and `2`'s inverse mod 17 is `9` (`2 * 9 = 18 = 1 mod 17`), so
`slope = 9 * 9 mod 17 = 81 mod 17 = 13`. Then `x3 = 13² - 5 - 5 = 169 - 10 = 159 mod 17 = 6`, and
`y3 = 13*(5 - 6) - 1 = -14 mod 17 = 3`. The result, `(6, 3)`, is `2*G`.

### Example 3: an inverse pair (test `02-R4-g-and-negation`)

```
input:   add 5 1 5 16

output:  inf
```

`(5, 16)` is `G`'s negation (`17 - 1 = 16`), so the sum is `inf` without needing either formula.

## Constraints

- Every input line is `add <P1> <P2>`, with each `P` either `inf` or two integers in `0..16`.
- Every point given is guaranteed to already be a point on the curve, or `inf`.
- There are 15 tests: 4 for R1, 2 for R2, 3 for R3, 3 for R4, 2 for R5, and one end-to-end test
  that walks the full 19-point cycle. The end-to-end test's id carries the seed and is rebuilt
  by `-Fresh`, though on this fixed, tiny curve its content doesn't change between seeds.

## Source material

- Checkpoint 10's page (`problems/10-find-weak-key.md`), "A tiny example": the same curve, the
  same `G`, and the table this checkpoint's addition rule produces.
- Washington, *Elliptic Curves: Number Theory and Cryptography*, chapter 2 ("The Group Law"), for
  the chord-and-tangent construction and why the result is always another point on the curve.
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 2.2.1, for
  the same addition and doubling formulas stated for a general field.

## Hints

<details><summary>Hint 1: where to start</summary>

Handle the easy cases first and get them right before touching the formulas: infinity on either
side, and a point plus its own negation. Only then do you need the two slope formulas, and only
one of those two formulas runs per call - pick which one by checking whether the two points are
equal.
</details>

<details><summary>Hint 2: the approach</summary>

Write one function that takes two points (each either `None` for infinity, or an `(x, y)` pair)
and returns their sum in the same representation. Check, in order: is either point infinity (if
so, return the other); are the two points negations of each other (if so, return infinity); are
the two points equal (use the tangent slope); otherwise (use the chord slope). The last two cases
share the same `x3`, `y3` formulas once you have a slope.
</details>

<details><summary>Hint 3: the traps</summary>

- `inf` has no coordinates. Parse it before trying to read two numbers.
- Check "is this a negation pair" using `x1 == x2 and (y1 + y2) % 17 == 0` - don't compare `y1`
  to a precomputed `17 - y2`, which can go wrong when `y2` is 0 (not that it occurs on this curve,
  but the check above is the one that generalises correctly).
- Doubling uses a different slope formula than ordinary addition - check `p1 == p2` before
  deciding which one to use, not just "are the x's equal" (a point and its negation also share an
  x, but isn't a doubling case).
- All arithmetic, including subtraction, is mod 17. A negative intermediate result (`x1 - x3`, for
  instance) needs `% 17` to land back in `0..16` in languages where `%` can return negative.
- The modular inverse needs `k` and `17` to be coprime. Since `17` is prime, this only fails if
  `k mod 17 == 0` - which can't happen for `2*y1` or `x2 - x1` given the checks above already
  ruled out the bad cases.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
add_points(p1, p2):
    if p1 is inf: return p2
    if p2 is inf: return p1
    (x1, y1) = p1
    (x2, y2) = p2
    if x1 == x2 and (y1 + y2) mod 17 == 0:
        return inf
    if p1 == p2:
        slope = (3*x1*x1 + 2) * inverse(2*y1)  mod 17
    else:
        slope = (y2 - y1) * inverse(x2 - x1)  mod 17
    x3 = slope*slope - x1 - x2  mod 17
    y3 = slope*(x1 - x3) - y1  mod 17
    return (x3, y3)
```
</details>

## Checking your solution

```
./check.sh 02                         run every test
./check.sh 02 -Case 02-R2-g           one test, showing its full input, expected output and your output
./check.sh 02 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 02 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  Inverse pairs: P + (-P) = inf, where -P is (x, 17 - y) .............    2 / 3   FAILED
      x 02-R4-g-and-negation  G plus its own negation
          line 1: expected `inf`, got `6 3`
          likely cause: R4 - Inverse pairs: P + (-P) = inf, where -P is (x, 17 - y)
          expected values from: brute-force search over the curve's 19 points, validated by polynomial root-multiplicity (see tools/gen_p02.py)
          reproduce: python3 -P tools/run_py.py solutions 02 build/cases/02/02-R4-g-and-negation.in build/cases/02/02-R4-g-and-negation.out
```

## After you pass: nothing to compare

There is no blog code for this checkpoint to compare against: it's arithmetic every later
checkpoint builds on, not something the post describes. What you wrote - the chord-and-tangent
rule - is exactly the "point addition" step inside every elliptic-curve library, just run on a
curve small enough to check by hand.
