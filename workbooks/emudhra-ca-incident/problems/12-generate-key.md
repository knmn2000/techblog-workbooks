# 12 · Generate a key correctly

**Difficulty:** Easy · **Assignment** 12 of 16 · **Check:** `.\check 12`

**Tags**
- *Language:* big integers · parsing hex · a loop with early return
- *Library:* none needed. Python's built-in `int` handles 384-bit numbers
- *Concepts:* uniformly random private keys · rejection sampling · FIPS 186-5 / SEC1 key generation

## Read in the blog first

You can pass using this page alone. eMudhra's
[Update 3](https://emudhra.com/en/post/certificate-security-incident#:~:text=An%20Update%20on%20Our%20Global%20TLS%20Intermediate%20CA%20Incident)
says the keys were generated in a Key Generation Ceremony on FIPS 140-2 Level 3 hardware, and
that a later step "produced a second, weak set of keys alongside the original strong keys." It
does not say what a correct key-generation step looks like. In this assignment you write one: the
plain procedure every key generator must follow so that a number like the ones recovered in this
incident can't come out of it.

**eMudhra has not confirmed the exact root cause.** Assignment 14 models one plausible shape that
would match their description, and this assignment doesn't depend on that question. It is the
standard, published procedure for turning random bytes into a private key, the one assignments
01 to 03 assumed had already happened.

## Source material

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3
- NIST, [FIPS 186-5: Digital Signature Standard (DSS)](https://csrc.nist.gov/pubs/fips/186-5/final), Appendix A.2 (extra random bits and rejection methods for generating a per-key secret value)
- NIST, [SP 800-186: Recommendations for Discrete Logarithm-based Cryptography](https://csrc.nist.gov/pubs/sp/800/186/final), for the order `n` of P-256 and P-384
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 3.2.1 (key pair generation)

## Where this fits

Your `attack/weak_key.py` from assignment 10 asks whether a key is weak by searching for its
private key, and assignment 13's linter asks the same question with rules. In `ecc/keys.py` you
go one step earlier, to the generator that makes the key. A correct generator can't produce a
weak key as long as it follows one rule every time: never hand out a candidate outside the valid
range. Your generator reads the order `n` from the `Curve` type in your `ecc/curve.py`, and the
program finds each curve in your `ecc/curves.py`.

## The problem

Write a program that turns recorded random draws into private keys, the way a correct key
generator does.

A private key for an elliptic curve is a whole number `d` with `1 <= d <= n - 1`, where `n` is
the curve's **order**: the number of points that `G` generates (see the table below). A key
generator gets raw bytes from its random number source and has to turn them into a number in that
range. It must not favor small numbers, large numbers or any other pattern an attacker could
exploit.

### Rejection sampling

The standard method, from FIPS 186-5 and SEC 1, is **rejection sampling**:

1. Draw as many random bytes as the curve's order needs: 32 bytes for P-256, 48 for P-384. That
   covers every value below `n`, with no bits to spare.
2. Read those bytes as one big-endian unsigned integer: the **candidate**.
3. If the candidate is `0`, or `n` or greater, **reject** it and draw a fresh set of random bytes
   (step 1 again).
4. Otherwise **accept** the candidate. It is `d`.

The method adds no bias: every candidate in range is equally likely to be drawn, and the
generator throws away any candidate out of range. Reducing an out-of-range candidate modulo `n`
instead would make small values of `d` more likely, among other problems.

Your generator gets its candidates by calling the random source it is given, with the number of
bytes it wants. For the tests, the program passes it a source that returns recorded blocks in
the order they were drawn, so each answer is exact and reproducible.

### The curves

| | P-256 | P-384 |
|---|---|---|
| `n` (order) | `ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551` | `ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973` |
| bytes per candidate | 32 | 48 |

All numbers are in hexadecimal.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Each line of the input is:

```
draw <label> <curve> <hex-block> [<hex-block> ...]
```

- `label` is a word with no spaces.
- `curve` is `P-256` or `P-384`.
- Each `hex-block` is one candidate: lowercase hexadecimal with no `0x` prefix, zero-padded to
  the curve's byte length (64 hex characters for P-256, 96 for P-384).
- The blocks come in the order they were drawn. A correct generator must reject every block
  except the last, and must accept the last one.

### Output

For each `draw` line, in input order, write one line:

```
key <label> <d>
```

Copy `<label>` from the input unchanged. `<d>` is the accepted private key in lowercase
hexadecimal, zero-padded to the curve's byte length (64 hex characters for P-256, 96 for P-384).
The checker ignores extra whitespace.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A single draw, accepted with no rejections, gives that `d`.
- **R2** The generator rejects a draw of `0` and moves on to the next draw in the list.
- **R3** The generator rejects a draw of `n` or anything above it. It accepts a draw of `n - 1`,
  the largest private key there is.
- **R4** Several draws in a row fail, for different reasons, before the generator accepts one.
- **R5** Both curves work. Each uses its own `n` and its own byte length; a program that mixes
  them up (for example, padding a P-256 key to 48 bytes, or comparing a P-384 candidate with
  P-256's `n`) fails here.

## Examples

### Example 1: four rejections, then acceptance (test `12-R4-many-rejects-p256`)

```
input:   draw k P-256 0000000000000000000000000000000000000000000000000000000000000000 ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551 ffffffff552b82f7be3edc0a1ef2a4f008c7385e833d1342acfa32b0fa7a7881 ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff 6c0f3459f79b17aeefba91fc803468b6b610a9f7f9270f4fb8b333a8e5446dd4

output:  key k 6c0f3459f79b17aeefba91fc803468b6b610a9f7f9270f4fb8b333a8e5446dd4
```

The input is one line with five 64-digit blocks. The test's draws, in order:

- all zeros: rejected;
- `n` itself: rejected, because a key must be below `n`;
- a value above `n`: rejected;
- all `ff`: rejected;
- a value in `[1, n-1]`: accepted, and it is `d`.

### Example 2: the boundary that must be accepted (test `12-R3-n-minus-1-p384`)

```
input:   draw k P-384 ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52972

output:  key k ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52972
```

The candidate is `n - 1` for P-384, the largest number a private key can be. The generator must
accept it on the first draw.

## Constraints

- Every line is a `draw` line; there are no blank lines.
- A `draw` line has at most 6 candidates. Labels have no spaces. An input has at most 10 `draw`
  lines.
- Each case has a 10-second limit. This assignment does no point arithmetic, only integer
  comparisons, so it finishes in milliseconds.
- There are 14 tests: 2 for R1, 2 for R2, 6 for R3 (including both boundary directions), 2 for R4,
  1 for R5 and 1 end-to-end case mixing both curves and every kind of rejection. Part of the set
  changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Your generator doesn't make randomness. It calls the `random_bytes` function it is given, and in
the tests that function returns the input's blocks in the order they were drawn. Your work is the
accept/reject rule, applied to each candidate in turn, stopping at the first one accepted.
</details>

<details><summary>Hint 2: the approach</summary>

Work out the byte length of the curve's `n` (32 for P-256, 48 for P-384) and ask `random_bytes`
for that many bytes. Read them as one big-endian, non-negative integer
(`int.from_bytes(block, "big")` in Python) and compare it with `curve.n`. Return the first
candidate from 1 to `n - 1`, and draw again after any other. If you parse the hex yourself, hex
text read left to right is already big-endian.
</details>

<details><summary>Hint 3: the traps</summary>

- At the low end, reject only `0`. A candidate of `1` is a valid private key, weak as it is, and
  this assignment accepts it.
- The upper bound is exclusive: reject `n` itself; `n - 1` is the largest value to accept.
- Each curve has its own `n` and its own byte length (32 bytes for P-256, 48 for P-384). Don't
  share one table entry between them.
- Print `d` in hex, zero-padded to the curve's byte length, not in decimal.
- Stop at the first accepted candidate. Real data has no blocks after it (there is nothing left
  to draw once one is accepted), but don't make your code depend on that.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
generate_private_key(curve, blocks):
    n = ORDER[curve]
    for hexblock in blocks:
        candidate = int(hexblock, base=16)
        if 1 <= candidate <= n - 1:
            return candidate
    # every block in the real input eventually hits this; the test data guarantees it
```
</details>

## Checking your solution

```
.\check 12                              run every test
.\check 12 -Case 12-R3-n-minus-1-p384   one test, showing its full input, expected output and your output
.\check 12 -Fresh                       a new set of tests (new random seed), to confirm on data you haven't seen
.\check 12 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R3  A draw of exactly n (or any value at or above it) is rejected; a ... .    4 / 6   FAILED
      x 12-R3-n-exact-p256  P-256: a draw of exactly n (the order) must be rejected
          line 1: expected `key k afbd67f9619699cfe1988ad9f06c144a025b413f8a9a021fa648a7dd06839eb9`, got `key k ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551`
          likely cause: R3 - A draw of exactly n (or any value at or above it) is rejected; a draw of n - 1 is accepted (the largest valid key)
          expected values from: FIPS 186-5 / SEC1 rejection sampling: accept iff 1 <= candidate <= n - 1 (n from tools/curves.py)
          reproduce: py -P tools/run_py.py solutions 12 build/cases/12/12-R3-n-exact-p256.in build/cases/12/12-R3-n-exact-p256.out
```

## After you pass: compare with the post

The post describes the outcome of a ceremony step going wrong, and not the mechanics of correct
key generation, so there is no author's code to compare with. You wrote the textbook procedure a
Key Generation Ceremony should follow at the moment it chooses a private key. The reference
`ecc/keys.py` draws from `os.urandom` unless the caller passes another source, which is how the
program replays the recorded blocks.

**Something to look for:** this assignment computes no public key. A generator that follows this
rule can still feed a broken step afterwards, such as the wrap/unwrap step assignment 14 models.
Getting this part right is necessary, and on its own it isn't enough. A Key Generation Ceremony
has that shape: several steps, and each one has to be correct on its own.
