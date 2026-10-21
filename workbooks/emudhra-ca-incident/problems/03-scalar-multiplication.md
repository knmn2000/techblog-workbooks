# 03 · Multiply a point by a number

**Difficulty:** Medium · **Checkpoint** 3 of 16 · **Check:** `./check.sh 03`

**Tags**
- *Language:* big integers · bit shifting · a loop
- *Library:* none needed
- *Concepts:* elliptic-curve scalar multiplication (double-and-add) · private and public keys

## Prerequisite material

This checkpoint is prerequisite material for the later checkpoints about the eMudhra incident; it
isn't drawn from a specific blog post. It builds the forward direction of what checkpoint 10
(already part of this workbook) does in reverse by brute force. See "Source material" below.

## Where this fits

Checkpoint 2 added two points on a small curve. This checkpoint multiplies a point by a number -
on the real, 256-bit and 384-bit curves this workbook uses from here on. `d*G` is exactly how a
real private key `d` becomes its matching public key. Checkpoint 10 already asked you to search
for small `d` given `Q = d*G`; this checkpoint computes `Q` from any `d`, however large.

## The problem

Write a program that reads a curve name and a private key `d`, and writes the public key `d*G`.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p03_scalar_multiplication.py` is a comment and an
empty program: reading the input and writing the output are yours. To start from working
input/output code instead, copy `starters/boilerplate/p03_scalar_multiplication.py` over it, or
pick Boilerplate in the book's editor. The boilerplate reads the input and writes the output; you
fill in `scalar_multiply()`.

### Why not just add G to itself d times

Checkpoint 10 computed `d*G` by starting at `G` and adding `G` again and again, d times. That
works when `d` is small (at most 1000 there). Here, `d` can be close to the full width of the
curve's order - hundreds of bits, so up to roughly `2^384` for P-384. Adding `G` that many times
would never finish.

### Double-and-add

The same trick that made checkpoint 1's `modexp` fast works here: walk `d`'s bits from the lowest
to the highest. Keep two running points: one that doubles every step (`G`, `2G`, `4G`, `8G`, ...),
and a separate result that starts at the point at infinity and gets the doubling point added into
it whenever the current bit of `d` is 1. This takes about `log2(d)` point operations - a few
hundred, however large `d` is - instead of `d` of them.

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

`result + addend` and `addend + addend` are the same point addition and doubling you wrote for
checkpoint 2, just on a much bigger curve. `result` starts at infinity so the very first addition
(when the lowest bit is 1) correctly gives back `addend` unchanged.

### The curves

| | P-256 | P-384 |
|---|---|---|
| `p` | `ffffffff00000001000000000000000000000000ffffffffffffffffffffffff` | `fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff` |
| `a` | `p - 3` | `p - 3` |
| `Gx` | `6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296` | `aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7` |
| `Gy` | `4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5` | `3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f` |
| `n` (order) | `ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551` | `ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973` |

All numbers are hexadecimal. The point add/doubling formulas are the same ones from checkpoint 2
(with `b` unused, same as there): for distinct points `slope = (y2-y1)/(x2-x1)`; for doubling,
`slope = (3x1² + a)/(2y1)`; then `x3 = slope² - x1 - x2`, `y3 = slope*(x1-x3) - y1`, all mod `p`.

### Input

```
mul <curve> <d>
```

`curve` is `P-256` or `P-384`. `d` is a decimal integer with `1 <= d < n` (the curve's order
above).

### Output

One line per input line: `d*G`'s coordinates, in lowercase hex, each zero-padded to the curve's
full width (64 hex digits for P-256, 96 for P-384) - the same format checkpoint 10 uses for its
keys.

```
<x> <y>
```

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** Small `d` (1, 2, 3) matches the curve's own generator table: `d=1` is `G` itself, `d=2`
  needs the doubling formula, `d=3` needs an ordinary addition.
- **R2** `d` with different bit patterns - all 1 bits, a single high bit, alternating bits -
  exercises every branch of double-and-add (a loop that only handles some bit patterns correctly
  would still pass simple cases).
- **R3** `d = n - 1` gives the negation of `G`: `(Gx, p - Gy)`.
- **R4** Both curves work: P-256 and P-384 each use their own `p` and `G`.
- **R5** A large, random `d` - hundreds of bits - finishes well under the time limit. This is the
  requirement that rules out adding `G` to itself `d` times: that loop would still be running long
  after the time limit, while double-and-add needs only a few hundred steps regardless of how
  large `d` is.

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

`d=1` is `11` in... no, `d=1` is just `1` in binary: the loop's only step adds `G` (`result`
starts at infinity) into `result`, giving `G` itself. `d=2` is `10` in binary: the lowest bit is
0, so the first step only doubles `addend` to `2G`; the next step's bit is 1, adding `2G` into
`result` (still infinity), giving `2G` - which needs the doubling formula to compute, since the
doubling of `addend` from `G` to `2G` is where it happens. `d=3` is `11`: the first step adds `G`
into `result` (bit 0 is 1), then doubles `addend` to `2G`; the second step adds `2G` into `result`
(bit 1 is 1, and `result` is now `G`), giving `G + 2G = 3G` - an ordinary addition of two distinct
points.

### Example 2: the negation of G (test `03-R3-negation-p384`)

```
input:   mul P-384 39402006196394479212279040100143613805079739270465446667946905279627659399113263569398956308152294913554433653942642

output:  aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7 c9e821b569d9d390a26167406d6d23d6070be242d765eb831625ceec4a0f473ef59f4e30e2817e6285bce2846f15f1a0
```

The input is `n - 1` for P-384, written in decimal (the input format), not the hex shown in the
table above. The output's x matches `Gx` exactly; its y is `p - Gy`.

## Constraints

- `d` is a decimal integer with `1 <= d < n`.
- Each case has a 10-second limit. Double-and-add finishes in well under a millisecond, even for
  `d` near the full width of `n`; a loop that adds `G` to itself `d` times would need on the order
  of `2^384` additions for the largest `d` here, which no computer finishes in the lifetime of the
  universe, let alone 10 seconds.
- There are 9 tests: 2 for R1, 2 for R2, 2 for R3, 1 for R4, and 2 for R5, each covering both
  curves except R4, which mixes both in one input. Part of the set is random and changes with
  `-Fresh`.

## Source material

- Checkpoint 10's page (`problems/10-find-weak-key.md`): the same curves, the same point
  add/doubling formulas, used there to search for a small `d` given `Q`; this checkpoint computes
  `Q` from `d` directly.
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 3.2.1
  ("Elliptic Curve Public Key Pair Generation Primitive") and section 2.2.1 (point multiplication
  algorithms, including double-and-add).
- NIST, [SP 800-186: Recommendations for Discrete Logarithm-based Cryptography](https://csrc.nist.gov/pubs/sp/800/186/final), for the P-256 and P-384 domain parameters.

## Hints

<details><summary>Hint 1: where to start</summary>

You already wrote point addition and doubling for checkpoint 2. This checkpoint reuses exactly
that arithmetic (on a bigger curve) and adds one new idea: walking `d`'s bits to decide when to
add the current doubling point into the result.
</details>

<details><summary>Hint 2: the approach</summary>

Keep two points: `addend`, which starts at `G` and doubles every loop iteration, and `result`,
which starts at infinity and only changes when the current bit of `d` is 1 (then it becomes
`result + addend`). Shift `d` right by one bit each iteration and stop when `d` is 0. `result` is
the answer.
</details>

<details><summary>Hint 3: the traps</summary>

- `result` starts at infinity (not at `G`). Adding any point to infinity gives that point back
  unchanged - this is what makes the very first real addition work correctly.
- Double `addend` every iteration, even on iterations where the bit is 0 - skipping it breaks
  every later step.
- Use the doubling formula only when adding a point to itself (`addend + addend`); use the
  ordinary chord formula for `result + addend` (they are different points once `result` is no
  longer infinity).
- Don't stop the loop early because `d`'s remaining bits look like zero on top - only stop when
  `d` reaches exactly 0.
- Print both coordinates in lowercase hex, zero-padded to the curve's full width, even when the
  value happens to start with zero bits.
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

(`add` is the same function you wrote for checkpoint 2, generalised to this curve's `p` and `a`,
and to handle infinity on either side.)
</details>

## Checking your solution

```
./check.sh 03                         run every test
./check.sh 03 -Case 03-R3-negation-p384  one test, showing its full input, expected output and your output
./check.sh 03 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 03 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R5  A large, random d (hundreds of bits) finishes well under the time ... .    0 / 2   FAILED
      x 03-R5-large-p256-s1  P-256: three large random d, each nearly the full bit length (seed 1)
          Time Limit Exceeded (over 10 s)
          likely cause: R5 - A large, random d (hundreds of bits) finishes well under the time limit
          expected values from: cryptography 41.0.7 (OpenSSL): d*G computed by deriving a private key with value d
          reproduce: python3 -P tools/run_py.py solutions 03 build/cases/03/03-R5-large-p256-s1.in build/cases/03/03-R5-large-p256-s1.out
```

## After you pass: nothing to compare

There is no blog code for this checkpoint to compare against: it's the forward direction of
checkpoint 10's search, not something the post describes. What you wrote - double-and-add - is
exactly how a real certificate authority's HSM turns a freshly generated private key into the
public key that goes in a certificate.
