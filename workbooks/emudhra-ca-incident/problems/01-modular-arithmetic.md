# 01 · Modular arithmetic

**Difficulty:** Easy · **Checkpoint** 1 of 16 · **Check:** `./check.sh 01`

**Tags**
- *Language:* big integers · bit shifting · a loop
- *Library:* none needed. Python's built-in `int` handles numbers as large as these curves use
- *Concepts:* modular exponentiation (square-and-multiply) · modular inverse (extended Euclid)

## Prerequisite material

This checkpoint is prerequisite material for the later checkpoints about the eMudhra incident; it
isn't drawn from a specific blog post. Every later checkpoint that touches elliptic-curve points
needs the two operations built here. See "Source material" below for where this arithmetic comes
from.

## Where this fits

This is the first checkpoint. It builds the two pieces of arithmetic that checkpoints 2 and 3 use
to turn a private number into a public key, and that checkpoint 4 uses to check a signature: doing
a huge exponent mod a prime quickly, and dividing mod a prime (which only makes sense through a
modular inverse, since there's no fraction).

## The problem

Write a program that reads lines asking for a modular exponentiation or a modular inverse, and
writes the answer to each, in order.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p01_modular_arithmetic.py` is a comment and an empty
program: reading the input and writing the output are yours. To start from working input/output
code instead, copy `starters/boilerplate/p01_modular_arithmetic.py` over it, or pick Boilerplate in
the book's editor. The boilerplate reads the input and writes the output; you fill in `modexp()`
and `modinv()`.

### Modular exponentiation

`base ** exp mod mod` the ordinary way means multiplying `base` by itself `exp` times. For the
exponents here, hundreds of bits long, that is far too slow. **Square-and-multiply** gets the same
answer in about `log2(exp)` multiplications: look at `exp` one bit at a time, squaring a running
value every step, and multiplying it by `base` whenever that bit is 1.

### Modular inverse

There's no division mod a number. Instead, `a`'s **modular inverse** mod `mod` is a number `b`
such that `a * b mod mod == 1` - multiplying by it acts like dividing by `a`. It exists exactly
when `gcd(a, mod) == 1`. The **extended Euclidean algorithm** finds it: it runs the same steps as
computing `gcd(a, mod)` (repeatedly replacing the larger of two numbers with its remainder when
divided by the smaller), while also tracking, at each step, how to write the current remainder as
some multiple of `a` plus some multiple of `mod`. When the remainder reaches 1, the multiple of
`a` is the inverse (reduced mod `mod` so it comes out in range).

### Input

| Line | Meaning |
|---|---|
| `modexp <base> <exp> <mod>` | Compute `base ** exp mod mod`. `mod >= 2`, `exp >= 0`, `base >= 0`. |
| `modinv <a> <mod>` | Compute `a`'s inverse mod `mod`. `mod >= 2`, `a >= 0`. |

All three numbers on a line are plain decimal integers, with no sign and no separators. `base` can
be equal to or larger than `mod`; `a` can be equal to or larger than `mod` too.

### Output

For each input line, in the same order, write one line:

```
modexp <result>      the value of base ** exp mod mod, 0 <= result < mod
modinv <result>      a's inverse mod mod, 0 <= result < mod
modinv none          when gcd(a, mod) != 1: a has no inverse mod mod
```

### Special cases

- `base ** 0` is 1, for every base, including `base = 0`. (This is the ordinary mathematical
  convention, not specific to modular arithmetic.)
- `mod = 1` is a valid modulus. Every number is congruent to 0 mod 1, so `modexp` always answers
  `0` there, whatever `base` and `exp` are. By the same reasoning `modinv ... 1` answers `0` too:
  the one value mod 1 is trivially its own "inverse" since `0 * 0 mod 1 == 0 == 1 mod 1`. This
  matches what Python's own `pow(a, -1, 1)` returns, if you want a second source for this
  convention.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** One output line per input line, in order: `modexp <result>` or `modinv <result>` /
  `modinv none`.
- **R2** `exp = 0` gives `1 mod m` (even when `base = 0`), except `mod = 1`, which always gives
  `0`.
- **R3** `exp = 1` gives `base mod m`.
- **R4** Exponents hundreds of bits long finish well under the time limit. This rules out a loop
  that multiplies `exp` times; square-and-multiply does it in about `log2(exp)` multiplications.
- **R5** `base >= mod` is reduced mod `mod` before exponentiating (not treated as an error, and
  not left unreduced in the arithmetic).
- **R6** `modinv` returns the correct inverse when `gcd(a, mod) == 1`.
- **R7** `modinv` returns `none` when `gcd(a, mod) != 1`. This includes `a = 0` (with `mod > 1`,
  since `gcd(0, mod) == mod`), and `a` sharing a prime factor with a composite `mod`.
- **R8** `mod = 1`: `modexp` always answers `0`, and `modinv` answers `0` by the convention above.

## Examples

### Example 1: square-and-multiply by hand (test `01-R1-all-modexp`)

```
input:   modexp 2 3 5
         modexp 5 5 11
         modexp 7 2 13
         modexp 9 9 17

output:  modexp 3
         modexp 1
         modexp 10
         modexp 15
```

`2 ** 3 mod 5`: `exp = 3` is `11` in binary. Start with `result = 1`, `base = 2`. Bit 0 (the low
bit) is 1, so `result = 1 * 2 mod 5 = 2`; square `base` to `4`. Bit 1 is 1, so
`result = 2 * 4 mod 5 = 8 mod 5 = 3`; that's the last bit, so the answer is `3`. Check:
`2**3 = 8`, and `8 mod 5 = 3`.

### Example 2: a modular inverse (test `01-R6-small-prime-mod`)

```
input:   modinv 3 7

output:  modinv 5
```

`3 * 5 = 15`, and `15 mod 7 = 1`, so `5` is `3`'s inverse mod `7`.

### Example 3: no inverse exists (test `01-R7-prime-factor`)

```
input:   modinv 21 35

output:  modinv none
```

`35 = 5 * 7`, and `21 = 3 * 7` shares the factor `7` with `35`, so `gcd(21, 35) = 7`, not `1`.
There is no number you can multiply `21` by to get something congruent to `1` mod `35`.

## Constraints

- Every line is well formed: exactly `modexp <base> <exp> <mod>` or `modinv <a> <mod>`, decimal,
  no sign, no blank lines.
- `mod >= 1` in every line (the examples above use `mod >= 2`; a few cases use `mod = 1`
  specifically to test that edge).
- Numbers can be as large as a few hundred bits - as large as the primes used by P-256 and P-384
  in later checkpoints.
- Each case has a 10-second limit. The R4 cases use exponents and moduli several hundred bits
  long; square-and-multiply finishes in well under a millisecond, but a loop of `exp` plain
  multiplications would still be running long after the universe ends.
- There are 24 tests: 3 for R1, 3 for R2, 3 for R3, 4 for R4, 3 for R5, 3 for R6, 4 for R7, 2 for
  R8, and 2 end-to-end cases using the real P-384 field prime. Part of the set is random and
  changes with `-Fresh`.

## Source material

- NIST, [SP 800-186: Recommendations for Discrete Logarithm-based Cryptography](https://csrc.nist.gov/pubs/sp/800/186/final), for the P-256 and P-384 primes this arithmetic will run on from checkpoint 3 onward
- Handbook of Applied Cryptography (Menezes, van Oorschot, Vanstone), chapter 2 ("Mathematical
  Background"), for square-and-multiply (there called the "repeated square-and-multiply
  algorithm") and the extended Euclidean algorithm

## Hints

<details><summary>Hint 1: where to start</summary>

Both functions are short, well-known algorithms. Don't try to derive them from scratch: write
`modexp` as a loop over the bits of `exp`, and `modinv` as a loop that mimics computing
`gcd(a, mod)` but tracks one extra pair of numbers along the way.
</details>

<details><summary>Hint 2: the approach</summary>

For `modexp`: keep `result = 1` and a running `base` (already reduced mod `mod`). While `exp > 0`:
if the lowest bit of `exp` is 1, multiply it into `result`; always square `base` and mod it; then
shift `exp` right by one bit. Stop when `exp` is 0.

For `modinv`: keep two pairs, `(old_r, old_s) = (a mod mod, 1)` and `(r, s) = (mod, 0)`. Repeat:
let `q = old_r // r`; replace `(old_r, r)` with `(r, old_r - q*r)` and `(old_s, s)` with
`(s, old_s - q*s)`; stop when `r` is 0. If `old_r` isn't 1 at that point, there's no inverse.
Otherwise the inverse is `old_s mod mod` (it may have gone negative along the way).
</details>

<details><summary>Hint 3: the traps</summary>

- `mod = 1` first: handle it before anything else, in both functions, by returning `0`.
- Reduce `base` (and `a`) mod `mod` before using them; a loop that doesn't will still often get
  the right modexp answer but can get `modinv` wrong, and will run slower than it needs to.
- `exp = 0` must give `1`, not `0`, for any `base` (except through the `mod = 1` rule above).
- The extended Euclid coefficients can go negative partway through. Take `% mod` only at the very
  end, or you'll reduce a negative number incorrectly in some languages.
- Check `gcd(a, mod) == 1` (equivalently: the final `old_r == 1`) before trusting any computed
  inverse - don't just always print a number.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
modexp(base, exp, mod):
    if mod == 1: return 0
    base = base mod mod
    result = 1
    while exp > 0:
        if exp is odd: result = (result * base) mod mod
        base = (base * base) mod mod
        exp = exp >> 1
    return result

modinv(a, mod):
    if mod == 1: return 0
    (old_r, r) = (a mod mod, mod)
    (old_s, s) = (1, 0)
    while r != 0:
        q = old_r // r
        (old_r, r) = (r, old_r - q*r)
        (old_s, s) = (s, old_s - q*s)
    if old_r != 1: return none
    return old_s mod mod
```
</details>

## Checking your solution

```
./check.sh 01                         run every test
./check.sh 01 -Case 01-R7-prime-factor  one test, showing its full input, expected output and your output
./check.sh 01 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 01 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R7  modinv returns `none` when gcd(a, mod) != 1, including a = 0 and a ....    0 / 4   FAILED
      x 01-R7-zero  a = 0, mod > 1 (gcd is mod, never 1)
          line 1: expected `modinv none`, got `modinv 0`
          likely cause: R7 - modinv returns `none` when gcd(a, mod) != 1, including a = 0 and a sharing a prime factor with mod
          expected values from: Python's built-in pow(base, exp, mod) and pow(a, -1, mod), cross-checked with math.gcd
          reproduce: python3 -P tools/run_py.py solutions 01 build/cases/01/01-R7-zero.in build/cases/01/01-R7-zero.out
```

## After you pass: nothing to compare

There is no blog code for this checkpoint to compare against: it's the arithmetic every later
checkpoint builds on, not something the post describes. What you wrote - square-and-multiply and
extended Euclid - is the same pair of algorithms used inside every general-purpose cryptography
library, including the one later checkpoints use as an independent oracle.
