# 02 · Add points on a toy curve

**Difficulty:** Easy · **Assignment** 2 of 16 · **Check:** `.\check 02`

**Tags**
- *Language:* small integers · modular arithmetic (`pow(a, -1, p)` in Python) · parsing a point
- *Library:* none needed
- *Concepts:* elliptic-curve point addition and doubling · the point at infinity · inverse points

## Prerequisite material

This assignment is background for the later assignments about the eMudhra incident; it doesn't
come from a blog post. Assignment 10's page uses this curve and generator as a worked example, and
here you build the addition rule behind that example's table. "Source material" below lists where
the rule comes from.

## Source material

- Assignment 10's page (`problems/10-find-weak-key.md`), its tiny example: the same curve, the
  same `G`, and the table this assignment's addition rule produces.
- Washington, *Elliptic Curves: Number Theory and Cryptography*, chapter 2 ("The Group Law"), for
  the chord-and-tangent construction and why the result is another point on the curve.
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 2.2.1, for
  the same addition and doubling formulas stated for a general field.

## Where this fits

Your `ecc/modmath.py` from assignment 01 does arithmetic mod a prime. In this assignment you write
`ecc/curve.py`, which adds two points with it, and `ecc/curves.py`, which holds the curve. The
curve is small enough to check by hand: with `p = 17` you can write out every point.

Assignment 03 adds P-256 and P-384 to `ecc/curves.py` and multiplies points on them by huge
numbers, which repeats this addition a few hundred times. Write `ecc/curve.py` for any curve, with
`p` and `a` taken from the curve, so that it runs there unchanged.

## The problem

Write a program that reads pairs of points on the curve `y² = x³ + 2x + 2 mod 17` and adds them.

### A tiny example

Assignment 10's page uses this curve, with the same generator `G = (5, 1)`, as a worked example.
Its table lists `1*G` to `5*G` as `(5, 1)`, `(6, 3)`, `(10, 6)`, `(3, 1)`, `(9, 16)`. Each entry
is the one before it plus `G`, which is the operation you write in this assignment. After you
pass, that table gives you a second example to check your rule against.

### The point at infinity

Besides its `(x, y)` pairs, an elliptic curve has one more point, called infinity. It is the
group's identity element, the way `0` is for addition of numbers:

- `P + inf = P` and `inf + P = P` for any point `P`;
- `inf + inf = inf`;
- a point plus its own negation gives `inf` (see "Inverse points" below).

In this assignment's input and output, infinity is the single word `inf`, with no coordinates. The
Boilerplate's `ecc/curve.py` represents it as `None`, under the name `INFINITY`.

### Adding two different points

All arithmetic below is mod 17. To add two points `P = (x1, y1)` and `R = (x2, y2)` with
`x1 != x2`:

```
slope = (y2 - y1) / (x2 - x1)
x3    = slope² - x1 - x2
y3    = slope * (x1 - x3) - y1
```

"Divide by `k`" means multiply by `k`'s modular inverse mod 17: your `modinv` from assignment 01,
or `pow(k, -1, 17)` in Python.

### Doubling a point

Adding a point to itself (`P + P`) takes its slope from the curve's tangent line at `P`:

```
slope = (3*x1² + a) / (2*y1)        (a = 2 on this curve)
x3    = slope² - 2*x1
y3    = slope * (x1 - x3) - y1
```

Once you have the slope, `x3` and `y3` come from the same formulas as above, with `x2 = x1`.

A point with `y1 = 0` would make `2*y1 = 0`, which has no inverse. On the curve's graph, the
tangent there is a vertical line, and the sum is infinity. This curve has no point with `y = 0` (you can check
by trying all 17 values of `x`), so doubling never gives infinity here. A point with `y = 0` can
only exist on a curve with an even number of points. This curve has 19 points, and P-256 and P-384
(from assignment 03 on) each have an odd, prime number of points, so they have no such point
either.

### Inverse points

The negation of `(x, y)` is `(x, 17 - y mod 17)`: the same `x` and the other `y`. A point plus
its own negation is infinity: `P + (-P) = inf`. Check for this before you apply either formula,
because `x1 == x2` there and the chord formula would divide by zero.

### Input

One line per case:

```
add <P1> <P2>
```

Each of `P1` and `P2` is either the word `inf` or two space-separated integers `x y` with
`0 <= x, y <= 16`, a point already on the curve.

### Output

One line per input line: the sum, in the same format (`inf`, or `x y`).

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** Adding two distinct points with different x, using the chord through them.
- **R2** Doubling a point (`P + P`), using the tangent at that point.
- **R3** Identity laws: `P + inf = P`, `inf + P = P`, `inf + inf = inf`.
- **R4** Inverse pairs: `P + (-P) = inf`, where `-P` is `(x, 17 - y)`.
- **R5** Every output other than `inf` is a point on the curve (`y² == x³ + 2x + 2 mod 17`).
- **E2E** A table that reaches all 19 points of the curve (18 affine points plus infinity) by adding `G` again and again, as in assignment 10's worked table.

## Examples

### Example 1: the first step of the worked table (test `02-R1-small`)

```
input:   add 5 1 6 3

output:  10 6
```

`P1 = (5, 1)` is `1*G` and `P2 = (6, 3)` is `2*G`. Their x's differ, so use the chord slope:
`slope = (3 - 1) / (6 - 5) = 2`. Then `x3 = 2² - 5 - 6 = 4 - 11 = -7 mod 17 = 10`, and
`y3 = 2*(5 - 10) - 1 = -11 mod 17 = 6`. The result, `(10, 6)`, is `3*G` in assignment 10's table.

### Example 2: doubling (test `02-R2-g`)

```
input:   add 5 1 5 1

output:  6 3
```

Both points are `G = (5, 1)`, so use the tangent slope: `slope = (3*5² + 2) / (2*1) = 77 / 2`.
`77 mod 17 = 9`, and the inverse of `2` mod 17 is `9` (`2 * 9 = 18 = 1 mod 17`), so
`slope = 9 * 9 mod 17 = 81 mod 17 = 13`. Then `x3 = 13² - 5 - 5 = 169 - 10 = 159 mod 17 = 6`, and
`y3 = 13*(5 - 6) - 1 = -14 mod 17 = 3`. The result, `(6, 3)`, is `2*G`.

### Example 3: an inverse pair (test `02-R4-g-and-negation`)

```
input:   add 5 1 5 16

output:  inf
```

`(5, 16)` is the negation of `G` (`17 - 1 = 16`), so the sum is `inf`, and neither formula runs.

## Constraints

- Every input line is `add <P1> <P2>`, with each `P` either `inf` or two integers in `0..16`.
- Every point given is on the curve, or is `inf`.
- There are 15 tests: 4 for R1, 2 for R2, 3 for R3, 3 for R4, 2 for R5, and one end-to-end test
  that walks the full 19-point cycle. The end-to-end test's id carries the seed and `-Fresh`
  rebuilds it, but on this fixed, tiny curve its content is the same for every seed.

## Hints

<details><summary>Hint 1: where to start</summary>

Get the easy cases right before you touch the formulas: infinity on either side, and a point plus
its own negation. After those, each call needs one of the two slope formulas; pick it by checking
whether the two points are equal.
</details>

<details><summary>Hint 2: the approach</summary>

Your `add_points` in `ecc/curve.py` takes a curve and two points (each `None` for infinity, or an
`(x, y)` pair) and returns their sum in the same form. Check, in order:

1. If either point is infinity, return the other one.
2. If the two points are negations of each other, return infinity.
3. If the two points are equal, use the tangent slope.
4. Otherwise, use the chord slope.

The last two cases share the `x3`, `y3` formulas once you have a slope.
</details>

<details><summary>Hint 3: the traps</summary>

- `inf` has no coordinates. Parse it before trying to read two numbers.
- Check for a negation pair with `x1 == x2 and (y1 + y2) % 17 == 0`. Comparing `y1` with a
  precomputed `17 - y2` goes wrong when `y2` is 0, because `17 - 0` is 17, not 0. No point on this
  curve has `y = 0`, but the check above is the one that carries over to other curves.
- Doubling uses a different slope from ordinary addition. Choose it by checking `p1 == p2`, not by
  comparing the x's: a point and its negation share an x too, and that pair isn't a doubling.
- All arithmetic, subtraction included, is mod 17. In languages where `%` can return a negative
  number, a negative intermediate result such as `x1 - x3` needs `% 17` to land back in `0..16`.
- The modular inverse needs `k` and `17` to be coprime. Since `17` is prime, it fails only when
  `k mod 17 == 0`, and the checks above have ruled that out for `2*y1` and `x2 - x1`.
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

The pseudocode uses this curve's `p = 17` and `a = 2`. Your `add_points` reads both from its curve
argument, so assignment 03 can run it on P-256 and P-384.
</details>

## Checking your solution

```
.\check 02                              run every test
.\check 02 -Case 02-R2-g                one test, showing its full input, expected output and your output
.\check 02 -Fresh                       a new set of tests (new random seed), to confirm on data you haven't seen
.\check 02 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  Inverse pairs: P + (-P) = inf, where -P is (x, 17 - y) .............    2 / 3   FAILED
      x 02-R4-g-and-negation  G plus its own negation
          line 1: expected `inf`, got `6 3`
          likely cause: R4 - Inverse pairs: P + (-P) = inf, where -P is (x, 17 - y)
          expected values from: brute-force search over the curve's 19 points, validated by polynomial root-multiplicity (see tools/gen_p02.py)
          reproduce: py -P tools/run_py.py solutions 02 build/cases/02/02-R4-g-and-negation.in build/cases/02/02-R4-g-and-negation.out
```

## After you pass: nothing to compare

This assignment has no blog code to compare with: the post doesn't describe this arithmetic, and
the later assignments build on it. The chord-and-tangent rule you wrote is the point-addition
step inside elliptic-curve libraries, run here on a curve small enough to check by hand.
