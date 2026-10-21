# 01 · Modular arithmetic

**Difficulty:** Easy · **Assignment** 1 of 16 · **Check:** `.\check 01`

**Tags**
- *Language:* big integers · bit shifting · a loop
- *Library:* none needed. Python's built-in `int` handles numbers as large as these curves use
- *Concepts:* modular exponentiation (square-and-multiply) · modular inverse (extended Euclid)

## Prerequisite material

This assignment is background for the later assignments about the eMudhra incident; it doesn't
come from a blog post. Every later assignment that works with elliptic-curve points needs the two
operations you build here. "Source material" below lists where this arithmetic comes from.

## Source material

- NIST, [SP 800-186: Recommendations for Discrete Logarithm-based Cryptography](https://csrc.nist.gov/pubs/sp/800/186/final), for the P-256 and P-384 primes this arithmetic runs on from assignment 03 on
- Handbook of Applied Cryptography (Menezes, van Oorschot, Vanstone), chapter 2 ("Mathematical
  Background"), for square-and-multiply (there called the "repeated square-and-multiply
  algorithm") and the extended Euclidean algorithm

## Where this fits

This is the first assignment. In `ecc/modmath.py` you write two pieces of arithmetic mod a
number:

- modular exponentiation, which raises a number to an exponent hundreds of bits long, mod a
  prime, in about `log2(exp)` steps;
- the modular inverse, which is how you divide mod a prime, since there are no fractions.

Your `ecc/curve.py` divides with the inverse when it adds points in assignment 02, and your
`ecc/ecdsa.py` divides with it when it checks a signature in assignment 04. Assignment 03
multiplies a point by a number with the same bit-by-bit loop as square-and-multiply.

## The problem

Write a program that reads lines asking for a modular exponentiation or a modular inverse, and
writes the answer to each, in order.

### Modular exponentiation

Computing `base ** exp mod mod` the ordinary way multiplies `base` by itself `exp` times. The
exponents here are hundreds of bits long, so that loop would run for longer than the universe has
existed. Square-and-multiply gets the same answer in about `log2(exp)` multiplications:

- look at `exp` one bit at a time, starting from the lowest;
- keep a running power of `base` and square it at every step (`base`, `base^2`, `base^4`, ...);
- whenever the current bit is 1, multiply that power into the result.

### Modular inverse

Arithmetic mod a number has no division. Instead, the modular inverse of `a` mod `mod` is the
number `b` with `a * b mod mod == 1`, and multiplying by `b` acts like dividing by `a`. The inverse
exists when `gcd(a, mod) == 1`, and only then.

The extended Euclidean algorithm finds it. It runs the steps of computing `gcd(a, mod)`, which
replace the larger of two numbers with the remainder of dividing it by the smaller. Along the way
it also writes each remainder as some multiple of `a` plus some multiple of `mod`. The multiple of
`a` written for the remainder 1 is the inverse; reduce it mod `mod` to bring it into range.

### Input

| Line | Meaning |
|---|---|
| `modexp <base> <exp> <mod>` | Compute `base ** exp mod mod`. `mod >= 1`, `exp >= 0`, `base >= 0`. |
| `modinv <a> <mod>` | Compute `a`'s inverse mod `mod`. `mod >= 1`, `a >= 0`. |

Every number is a plain decimal integer, with no sign and no separators. `base` can be equal to or
larger than `mod`, and so can `a`.

### Output

For each input line, in the same order, write one line:

```
modexp <result>      the value of base ** exp mod mod, 0 <= result < mod
modinv <result>      a's inverse mod mod, 0 <= result < mod
modinv none          when gcd(a, mod) != 1: a has no inverse mod mod
```

### Special cases

- `base ** 0` is 1 for every base, including `base = 0`. This is the ordinary mathematical
  convention, and modular arithmetic keeps it.
- `mod = 1` is a valid modulus. Every number is congruent to 0 mod 1, so `modexp` answers `0` there
  for every `base` and `exp`. By the same reasoning `modinv ... 1` answers `0` too: the one value
  mod 1 is its own "inverse", since `0 * 0 mod 1 == 0 == 1 mod 1`. Python's own `pow(a, -1, 1)`
  returns the same, if you want a second source for this convention.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** One output line per input line, in order: `modexp <result>` or `modinv <result>` /
  `modinv none`.
- **R2** `exp = 0` gives `1 mod m` (even when `base = 0`), except `mod = 1`, which gives `0`.
- **R3** `exp = 1` gives `base mod m`.
- **R4** Exponents hundreds of bits long finish well under the time limit. A loop that multiplies
  `exp` times can't; square-and-multiply needs about `log2(exp)` multiplications.
- **R5** `base >= mod` is valid input, and is reduced mod `mod` before exponentiating.
- **R6** `modinv` returns the correct inverse when `gcd(a, mod) == 1`.
- **R7** `modinv` returns `none` when `gcd(a, mod) != 1`. This includes `a = 0` (with `mod > 1`,
  since `gcd(0, mod) == mod`), and `a` sharing a prime factor with a composite `mod`.
- **R8** `mod = 1`: `modexp` answers `0` for every input, and `modinv` answers `0` by the
  convention above.
- **E2E** A real curve prime, P-384's `p`, used for one `modexp` and one `modinv`.

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

Take `2 ** 3 mod 5`. `exp = 3` is `11` in binary. Start with `result = 1` and `base = 2`:

1. Bit 0 (the low bit) is 1, so `result = 1 * 2 mod 5 = 2`. Square `base` to `4`.
2. Bit 1 is 1, so `result = 2 * 4 mod 5 = 8 mod 5 = 3`.

That was the last bit, so the answer is `3`. Check: `2**3 = 8`, and `8 mod 5 = 3`.

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
No number multiplied by `21` gives something congruent to `1` mod `35`.

## Constraints

- Every line is well formed: `modexp <base> <exp> <mod>` or `modinv <a> <mod>`, in decimal, with
  no sign and no blank lines.
- `mod >= 1` on every line. The examples above use `mod >= 2`; a few cases use `mod = 1` to test
  that edge.
- Numbers can be a few hundred bits long, as large as the P-256 and P-384 primes in later
  assignments.
- Each case has a 10-second limit. The R4 cases use exponents and moduli several hundred bits
  long. Square-and-multiply finishes them in well under a millisecond; a loop of `exp` plain
  multiplications wouldn't finish in time.
- There are 27 tests: 3 for R1, 3 for R2, 3 for R3, 4 for R4, 3 for R5, 3 for R6, 4 for R7, 2 for
  R8, and 2 end-to-end cases using the real P-384 field prime. Part of the set is random and
  changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Both functions are short, well-known algorithms, so look them up instead of deriving them. Write
`modexp` as a loop over the bits of `exp`, and `modinv` as a loop that computes `gcd(a, mod)` and
tracks one extra pair of numbers along the way.
</details>

<details><summary>Hint 2: the approach</summary>

For `modexp`: keep `result = 1` and a running `base` (already reduced mod `mod`). While `exp > 0`:
if the lowest bit of `exp` is 1, multiply `base` into `result`; square `base` and mod it on every
pass; then shift `exp` right by one bit. Stop when `exp` is 0.

For `modinv`: keep two pairs, `(old_r, old_s) = (a mod mod, 1)` and `(r, s) = (mod, 0)`. Repeat:
let `q = old_r // r`; replace `(old_r, r)` with `(r, old_r - q*r)` and `(old_s, s)` with
`(s, old_s - q*s)`; stop when `r` is 0. If `old_r` isn't 1 at that point, there's no inverse.
Otherwise the inverse is `old_s mod mod` (it may have gone negative along the way).
</details>

<details><summary>Hint 3: the traps</summary>

- Handle `mod = 1` first, in both functions, by returning `0`.
- Reduce `base` (and `a`) mod `mod` before using them. A loop that doesn't will often still get
  the right `modexp` answer, but it can get `modinv` wrong and it runs slower than it needs to.
- `exp = 0` must give `1`, not `0`, for any `base` (except through the `mod = 1` rule above).
- The extended Euclid coefficients can go negative partway through. Take `% mod` only at the
  end: in some languages `%` of a negative number gives a negative result.
- Check `gcd(a, mod) == 1` (the final `old_r == 1`) before you trust a computed inverse, and
  print `none` when it fails.
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
.\check 01                              run every test
.\check 01 -Case 01-R7-prime-factor     one test, showing its full input, expected output and your output
.\check 01 -Fresh                       a new set of tests (new random seed), to confirm on data you haven't seen
.\check 01 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R7  modinv returns `none` when gcd(a, mod) != 1, including a = 0 and a ....    0 / 4   FAILED
      x 01-R7-zero  a = 0, mod > 1 (gcd is mod, never 1)
          line 1: expected `modinv none`, got `modinv 0`
          likely cause: R7 - modinv returns `none` when gcd(a, mod) != 1, including a = 0 and a sharing a prime factor with mod
          expected values from: Python's built-in pow(base, exp, mod) and pow(a, -1, mod), cross-checked with math.gcd
          reproduce: py -P tools/run_py.py solutions 01 build/cases/01/01-R7-zero.in build/cases/01/01-R7-zero.out
```

## After you pass: nothing to compare

This assignment has no blog code to compare with: the post doesn't describe this arithmetic, and
the later assignments build on it. Cryptography libraries build on the two algorithms you wrote,
square-and-multiply and extended Euclid, often in faster variants. That includes the library the
later assignments' tests use as an independent source of expected answers.
