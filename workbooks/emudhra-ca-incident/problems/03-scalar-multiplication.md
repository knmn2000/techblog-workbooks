# 03 · Multiply a point by a number

**Difficulty:** Medium · **Assignment** 3 of 16 · **Check:** `.\check 03`

**Tags**
- *Language:* big integers · bit shifting · a loop
- *Library:* none needed
- *Concepts:* elliptic-curve scalar multiplication (double-and-add) · private and public keys

## Prerequisite material

This assignment is background for the later assignments about the eMudhra incident; it doesn't
come from a blog post. It builds the forward direction of the search that assignment 10 runs
backwards by brute force. "Source material" below lists where it comes from.

## Source material

- Assignment 10's page (`problems/10-find-weak-key.md`): the same curves and the same addition
  and doubling formulas, used there to search for a small `d` given `Q`. This assignment computes
  `Q` from `d`.
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 3.2.1
  ("Elliptic Curve Public Key Pair Generation Primitive") and section 2.2.1 (point multiplication
  algorithms, including double-and-add).
- NIST, [SP 800-186: Recommendations for Discrete Logarithm-based Cryptography](https://csrc.nist.gov/pubs/sp/800/186/final), for the P-256 and P-384 domain parameters.

## Where this fits

Your `ecc/curve.py` from assignment 02 adds two points on a small curve. In this assignment you add
scalar multiplication to it: `d*G`, the point `G` added to itself `d` times. You also add the
real curves this workbook uses from here on, the 256-bit P-256 and the 384-bit P-384, to your
`ecc/curves.py`.

`d*G` is how a private key `d` becomes its public key. Your `ecc/ecdsa.py` multiplies points this
way to check a signature in assignment 04 and to make one in assignment 11. Assignment 10 goes the
other way: given `Q = d*G`, it searches for a small `d`.

## The problem

Write a program that reads a curve name and a private key `d`, and writes the public key `d*G`.

### Why not add G to itself d times

Assignment 10's search computes `d*G` by starting at `G` and adding `G` again and again, `d`
times. That works when `d` is small (at most 1000 there). Here `d` can be close to the full width
of the curve's order: hundreds of bits, up to about `2^384` for P-384. Adding `G` that many times
would not finish in the lifetime of the universe.

### Double-and-add

The trick that makes your `modexp` from assignment 01 fast works here too. Walk `d`'s bits from
the lowest to the highest, and keep two running points:

- `addend` starts at `G` and doubles at every step: `G`, `2G`, `4G`, `8G`, ...;
- `result` starts at the point at infinity, and gets `addend` added into it whenever the current
  bit of `d` is 1.

That takes at most about `2 * log2(d)` point operations, a few hundred however large `d` is,
instead of `d` of them.

```
result = infinity
addend = G
while d > 0:
    if d's lowest bit is 1:
        result = result + addend
    addend = addend + addend      (double it)
    d = d >> 1
return result
```

`result + addend` and `addend + addend` are the addition and doubling from your `add_points` in
assignment 02, run on a much bigger curve. `result` starts at infinity, so the first addition
(when the lowest bit is 1) gives back `addend` unchanged.

### The curves

| | P-256 | P-384 |
|---|---|---|
| `p` | `ffffffff00000001000000000000000000000000ffffffffffffffffffffffff` | `fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff` |
| `a` | `p - 3` | `p - 3` |
| `b` | `5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b` | `b3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef` |
| `Gx` | `6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296` | `aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7` |
| `Gy` | `4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5` | `3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f` |
| `n` (order) | `ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551` | `ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973` |

All numbers are hexadecimal. Put both curves in your `ecc/curves.py`, where the program looks
them up by the names `P-256` and `P-384`.

The addition and doubling formulas are the ones from assignment 02, mod this curve's `p`:

- for two distinct points, `slope = (y2-y1)/(x2-x1)`;
- for doubling, `slope = (3x1² + a)/(2y1)`;
- then `x3 = slope² - x1 - x2` and `y3 = slope*(x1-x3) - y1`.

The formulas don't use `b`. Assignment 13 uses it to check that a point lies on its curve.

### Input

```
mul <curve> <d>
```

`curve` is `P-256` or `P-384`. `d` is a decimal integer with `1 <= d < n`, where `n` is the
curve's order from the table above.

### Output

One line per input line: the coordinates of `d*G` in lowercase hex, each zero-padded to the
curve's full width (64 hex digits for P-256, 96 for P-384). Assignment 10 writes its keys in the
same format.

```
<x> <y>
```

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** Small `d` (1, 2, 3) matches the curve's own generator table: `d=1` is `G` itself, `d=2`
  needs the doubling formula, `d=3` needs an ordinary addition.
- **R2** `d` with different bit patterns (all 1 bits, a single high bit, alternating bits)
  exercises every branch of double-and-add. A loop that handles only some bit patterns right
  would still pass the simple cases.
- **R3** `d = n - 1` gives the negation of `G`: `(Gx, p - Gy)`.
- **R4** Both curves work: P-256 and P-384 each use their own `p` and `G`.
- **R5** A large, random `d`, hundreds of bits long, finishes well under the time limit. This
  requirement rules out adding `G` to itself `d` times: that loop would still be running long
  after the time limit, while double-and-add needs a few hundred steps for any `d`.

## Examples

### Example 1: d = 2 needs doubling (test `03-R1-small-p256`)

```
input:   mul P-256 1
         mul P-256 2
         mul P-256 3

output:  6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296 4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5
         7cf27b188d034f7e8a52380304b51ac3c08969e277f21b35a60b48fc47669978 07775510db8ed040293d9ac69f7430dbba7dade63ce982299e04b79d227873d1
         5ecbe4d1a6330a44c8f7ef951d4bf165e6c6b721efada985fb41661bc6e7fd6c 8734640c4998ff7e374b06ce1a64a2ecd82ab036384fb83d9a79b127a27d5032
```

Follow the loop for each `d`:

- `d = 1` is `1` in binary. The loop's only step adds `addend = G` into `result`, which is
  infinity, so the answer is `G` itself.
- `d = 2` is `10`. Bit 0 is 0, so the first step only doubles `addend` to `2G`; that doubling is
  where the tangent formula runs. Bit 1 is 1, so the second step adds `2G` into `result` (still
  infinity), giving `2G`.
- `d = 3` is `11`. The first step adds `G` into `result` and doubles `addend` to `2G`. The second
  step adds `2G` into `result`, which is now `G`, giving `G + 2G = 3G`: an ordinary addition of
  two different points.

### Example 2: the negation of G (test `03-R3-negation-p384`)

```
input:   mul P-384 39402006196394479212279040100143613805079739270465446667946905279627659399113263569398956308152294913554433653942642

output:  aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7 c9e821b569d9d390a26167406d6d23d6070be242d765eb831625ceec4a0f473ef59f4e30e2817e6285bce2846f15f1a0
```

The input is `n - 1` for P-384, written in decimal as the input format requires, not in the hex
of the table above. The output's x is `Gx`, and its y is `p - Gy`.

## Constraints

- `d` is a decimal integer with `1 <= d < n`.
- Each case has a 10-second limit. Double-and-add finishes in well under a millisecond, even for
  `d` near the full width of `n`. A loop that adds `G` to itself `d` times would need on the order
  of `2^384` additions for the largest `d` here.
- There are 9 tests: 2 for R1, 2 for R2, 2 for R3, 1 for R4, and 2 for R5. Each requirement except
  R4 has one test per curve; R4's test mixes both curves in one input. Part of the set is random
  and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

You wrote point addition and doubling in assignment 02. This assignment runs that arithmetic on a
bigger curve and adds one new idea: walking `d`'s bits to decide when to add the current doubling
point into the result.
</details>

<details><summary>Hint 2: the approach</summary>

Your `scalar_multiply` in `ecc/curve.py` keeps two points. `addend` starts at `G` and doubles on
every pass of the loop. `result` starts at infinity and changes only when the current bit of `d`
is 1: then it becomes `result + addend`. Shift `d` right by one bit on each pass and stop when `d`
is 0. `result` is the answer.
</details>

<details><summary>Hint 3: the traps</summary>

- `result` starts at infinity, not at `G`. Adding any point to infinity gives that point back
  unchanged, which makes the first real addition come out right.
- Double `addend` on every pass, including passes where the bit is 0. Skipping it breaks every
  later step.
- Use the doubling formula only when adding a point to itself (`addend + addend`). Use the chord
  formula for `result + addend`: once `result` isn't infinity, the two are different points.
- Stop the loop only when `d` reaches 0, not earlier.
- Print both coordinates in lowercase hex, zero-padded to the curve's full width, even when a
  value starts with zero bits.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
scalar_multiply(curve, d):
    (p, a, G) = curve's parameters
    result = infinity
    addend = G
    while d > 0:
        if d & 1:
            result = add(result, addend)
        addend = add(addend, addend)
        d = d >> 1
    return result
```

(`add` is your `add_points` from assignment 02, which takes `p` and `a` from the curve and handles
infinity on either side.)
</details>

## Checking your solution

```
.\check 03                              run every test
.\check 03 -Case 03-R3-negation-p384    one test, showing its full input, expected output and your output
.\check 03 -Fresh                       a new set of tests (new random seed), to confirm on data you haven't seen
.\check 03 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R5  A large, random d (hundreds of bits) finishes well under the time ... .    0 / 2   FAILED
      x 03-R5-large-p256-s1  P-256: three large random d, each nearly the full bit length (seed 1)
          Time Limit Exceeded (over 10 s)
          likely cause: R5 - A large, random d (hundreds of bits) finishes well under the time limit
          expected values from: cryptography 41.0.7 (OpenSSL): d*G computed by deriving a private key with value d
          reproduce: py -P tools/run_py.py solutions 03 build/cases/03/03-R5-large-p256-s1.in build/cases/03/03-R5-large-p256-s1.out
```

## After you pass: nothing to compare

This assignment has no blog code to compare with: it computes the forward direction of assignment
10's search, and the post doesn't describe it. A certificate authority's HSM does this same step
when it turns a private key it has generated into the public key that goes in a certificate.
