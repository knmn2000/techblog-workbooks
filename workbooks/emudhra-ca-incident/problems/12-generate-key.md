# 12 · Generate and validate a key

**Difficulty:** Medium · **Assignment** 12 of 19 · **Check:** `.\check 12`

**Tags**
- *Language:* big integers · parsing hex · a loop with early return
- *Library:* none needed. Python's built-in `int` handles 384-bit numbers
- *Concepts:* private-key range · key validation · probability of a uniform draw · rejection sampling · FIPS 186-5 / SEC 1 key generation

## Read in the blog first

You can pass using this page alone. eMudhra's
[Update 3](https://emudhra.com/en/post/certificate-security-incident#:~:text=An%20Update%20on%20Our%20Global%20TLS%20Intermediate%20CA%20Incident)
says a Key Generation Ceremony on FIPS 140-2 Level 3 hardware security modules generated the keys,
and names the step that failed: "The problem was a flaw in one step of the ceremony procedure, not
the absence of HSMs. During the ceremony, a key wrap/unwrap step produced a second, weak set of keys
alongside the original strong keys." The same update says eMudhra has not yet confirmed the exact
root cause.

On the Mozilla bug for the incident
([bug 2083449](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449), comment 11), eMudhra wrote
that a deviation from the ceremony, made to test wrapping and unwrapping, led to a code flaw
that created a second, weak keypair onboard, and that this keypair was used by mistake. This
workbook has not verified that account. Commenters on the bug, including Thor Simon and Jacob
Durham, argue that an approved key generator inside the module would not output a P-384 private
key below 256. Their argument implies a value supplied to the module, or a key object that came
out of an unwrap. The root cause is unconfirmed, and this assignment doesn't depend on it.

The public record does fix one thing: the keys themselves. Eight P-384 private keys were whole
numbers below 256 (4, 56, 66, 115, 155, 156, 230 and 237), which a 48-byte encoding writes as 47
zero bytes and one byte of value. Each was a valid point on the curve with a valid encoding, so
every structural check on the public key passes. A recovery attempt like the one in assignment 10
exposes them, and so does a check of the private key's size. You write that check and the
generator that applies it. It models the kind of check that would have flagged these keys. It
makes no claim about how they came about.

## Source material

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3
- Mozilla Bugzilla, [bug 2083449](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449): comment 11 is eMudhra's explanation (unverified), and other comments discuss it
- BleepingComputer, [Mozilla, Google, Apple block compromised eMudhra CA certificates](https://www.bleepingcomputer.com/news/security/mozilla-google-apple-block-compromised-emudhra-ca-certificates/): the keys were P-384 private keys with values smaller than 256
- Scott Helme, [Eight Bits of Trust](https://scotthelme.co.uk/eight-bits-of-trust-emudhras-ca-keys-cracked-in-milliseconds/): the eight recovered values, listed against the eight intermediates
- NIST, [FIPS 186-5: Digital Signature Standard (DSS)](https://csrc.nist.gov/pubs/fips/186-5/final), Appendix A.2.1 (key pair generation using extra random bits) and A.2.2 (key pair generation by rejection sampling)
- NIST, [SP 800-186: Recommendations for Discrete Logarithm-based Cryptography](https://csrc.nist.gov/pubs/sp/800/186/final), for the order `n` of P-256 and P-384
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 3.2.1 (key pair generation)

## Where this fits

Your `attack/weak_key.py` from assignment 10 recovers a small private key from its public key,
and assignment 13's linter runs that search, up to 4096, before it trusts a public key. That is
the view of someone who has only the public key and can only search. In `ecc/keys.py` you take
the view of the key's holder, who can compare the private key with a bound far beyond any
search, and then you build a generator on that check. Assignment 14 turns to the steps around
key creation, such as wrapping and unwrapping, which a check on one key can't see. The module
reads the order `n` from the `Curve` type in your `ecc/curve.py` and finds each curve in your
`ecc/curves.py`.

## The problem

Write a program that checks candidate private keys and generates a key from recorded random
draws. It answers each input line in order: a verdict for a candidate, the accepted key for a
draw.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Each line of the input is one of:

| Line | Meaning |
|---|---|
| `validate <label> <curve> <hex>` | A candidate private key to check. |
| `draw <label> <curve> <hex-block> [<hex-block> ...]` | The blocks a key generator drew from its random source, in the order it drew them. |

- `label` is a word with no spaces.
- `curve` is `P-256` or `P-384`.
- Every `hex` and `hex-block` is lowercase hexadecimal with no `0x` prefix, zero-padded to the
  curve's byte length (64 hex characters for P-256, 96 for P-384), and read as one big-endian
  unsigned integer. The value 4 on P-384 is 94 zeros followed by `04`.
- On a `draw` line, a correct generator rejects every block except the last and accepts the last.

### Output

For each line, in input order, write one line:

```
ok <label>                 validate: the key passes both checks
reject <label> <reason>    validate: the key fails; <reason> is the first check it fails
key <label> <d>            draw: the first block that passes, as the private key
```

`<reason>` is `out-of-range` or `weak`, as "The checks" below defines them. `<d>` is lowercase
hexadecimal, zero-padded to the curve's byte length. Copy `<label>` from the input unchanged. The
checker ignores extra whitespace.

### The checks

Your program rejects a key `d` for the first reason in this table that applies, so run the
checks in this order:

| Reason | Applies when |
|---|---|
| `out-of-range` | `d` is 0, or `n` or more. A private key is a whole number from 1 to `n - 1`, where `n` is the curve's order. |
| `weak` | `d` is below `B`, or `n - d` is below `B`. "Weak keys" below defines `B`. |

Zero is below `B` as well, and the first row decides it: 0 is `out-of-range`. The same holds for
`n` and every larger value, where `n - d` is zero or negative.

### Weak keys

Let `L` be the bit length of `n` (256 for P-256, 384 for P-384) and let `B = 2^(L/2)`: `2^128`
for P-256, `2^192` for P-384. A key is weak when it is below `B`, or when `n - d` is below `B`.
This bound is the workbook's own. FIPS 186-5 and SEC 1 define no weak-key bound and reject only
values outside 1 to `n - 1`.

The second half of that rule comes from negation. The public key for `n - d` is the negation of
the public key for `d`: the same x, with y replaced by `p - y`. An attacker who finds that a
public key is `4*G` gets the key for `n - 4` by flipping the sign, so the check treats `n - 4`
like 4. Assignment 10's search makes that comparison against the flipped point at every step,
and reports the public key of `n - 4` as `-4`.

A generator that draws uniformly over 1 to `n - 1` gives a key below a bound `b` with probability
about `b / n`. For `B` that is about 2^-128 on P-256 and 2^-192 on P-384. Adding the top end
doubles each figure, so a uniform key is weak with probability about 2^-127 on P-256 and 2^-191
on P-384. A CA that made 2^64 keys would meet a weak one with probability about 2^-63 on P-256
and 2^-127 on P-384, so a correct generator does not trip the check in practice.

The eight incident keys are all below 256. A uniform P-384 key is below 256 with probability
about 2^-376, and below 2^128, a far looser bound, with probability about 2^-256. A key that
small was not drawn uniformly, whatever produced it.

`B` is a statistical bound and says nothing about attack cost. Searching 2^128 values is out of
reach, so a key one below `B` may be impossible to find. The check flags a key that no uniform
draw would produce, and whatever produces such keys has failed.

You hold `d`, so the comparison costs one subtraction at any bound. The search in assignments 10
and 13 walks one point at a time and stops at 4096 in assignment 13.

A key picked from a small set but written as a large number, such as a hash of a short passphrase,
passes this check.

### Generating a key

A generator turns random bytes into a key by rejection sampling. FIPS 186-5 (Appendix A.2.2)
tests a candidate only for range, and SEC 1 (section 3.2.1) asks for a random `d` from 1 to
`n - 1`. Step 3 below adds the workbook's `weak` test to the range test:

1. Draw as many random bytes as the order needs: 32 for P-256, 48 for P-384.
2. Read them as one big-endian unsigned integer: the candidate.
3. Run the checks from "The checks". If the checks reject the candidate for any reason, discard it
   and go back to step 1.
4. Otherwise accept the candidate. It is `d`.

Your generator gets its randomness from a function it calls with the number of bytes it wants,
and it uses `os.urandom` when the caller passes none. For the tests, the program passes a
function that returns the blocks of a `draw` line in order, so each answer is exact and
reproducible.

A real draw is out of range with probability about 2^-32 on P-256 and 2^-194 on P-384, because `n`
is close to 2^L. A real draw is weak with the probabilities above. The generator redraws about
once in 2^32 keys on P-256, and the tests feed it draws that make it redraw. Excluding the weak
values removes about 2^-127 of the probability on P-256, a change no measurement can see.

Reducing the candidate modulo `n` instead of rejecting it makes every value below `2^L - n`
(about 2^224 on P-256, 2^190 on P-384) twice as likely. On P-384 that moves each such value's
chance from about 2^-384 to about 2^-383. That bias is far too small to measure, and a value like
4 stays as unlikely as any other.

### The curves

| | P-256 | P-384 |
|---|---|---|
| `n` (order) | `ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551` | `ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973` |
| bytes per candidate | 32 | 48 |
| `L`, the bit length of `n` | 256 | 384 |
| `B` | `2^128` (a 1 followed by 32 hex zeros) | `2^192` (a 1 followed by 48 hex zeros) |

All numbers in the `n` row are in hexadecimal.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A key from `B` to `n - B`, both ends included, gets `ok`.
- **R2** Zero and any value of `n` or more get `out-of-range`. Zero gets it although it is also below `B`.
- **R3** A key below `B` gets `weak`, including the eight values from the incident. `B - 1` is the largest of them.
- **R4** A key above `n - B` gets `weak`, because `d` and `n - d` are as easy to guess as each other. `n - 1` is the largest of them.
- **R5** Each curve uses its own order, byte length and `B`: `2^128` for P-256 and `2^192` for P-384. The same number can get `ok` on one curve and `weak` on the other.
- **R6** For a `draw` line, the generator draws, validates and redraws after every rejection, whatever its reason, and the answer is the first block that passes.
- **E2E** One input mixes `validate` and `draw` lines on both curves, with every verdict.

## Examples

### Example 1: a private key of 4 (test `12-R3-d4-p384`)

```
input:   validate v0 P-384 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004

output:  reject v0 weak
```

The value is 4, one of the eight private keys of the incident. It is in `1 .. n - 1`, so
`out-of-range` doesn't apply. It is below `B = 2^192`, so it is `weak`. A uniform P-384 draw
lands there with probability about 2^-376.

### Example 2: the largest possible key (test `12-R4-n-minus-1-p256`)

```
input:   validate v0 P-256 ffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632550

output:  reject v0 weak
```

The value is `n - 1`, the top of the range `out-of-range` allows. Its public key is `-G`, the point
`G` with y replaced by `p - y`, so the key is as guessable as 1. `n - d = 1` is below `B`, which
makes it `weak`.

### Example 3: a draw that stops at the bound (test `12-R6-accept-edge-p256`)

```
input:   draw k P-256 00000000000000000000000000000000ffffffffffffffffffffffffffffffff 0000000000000000000000000000000100000000000000000000000000000000

output:  key k 0000000000000000000000000000000100000000000000000000000000000000
```

The first block is `2^128 - 1`, one below `B`, so it is `weak` and the generator draws again. The
second block is `2^128` itself. It is not below `B`, and `n - d` is far above `B`, so the
generator accepts it.

## Constraints

- Every line is a `validate` or a `draw` line; there are no blank lines. An input has at most 10
  lines, and a `draw` line has at most 8 blocks.
- Each case has a 10-second limit. The program does integer comparisons only and finishes in
  milliseconds.
- There are 42 tests: 6 for R1, 6 for R2, 8 for R3, 7 for R4, 4 for R5, 10 for R6 and 1
  end-to-end case. They include `0`, `1`, `n - 1`, `n`, `B - 1`, `B`, `n - B` and `n - B + 1` on
  both curves, and the eight incident values. Part of the set is random and changes with
  `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Write the validation as one function that takes the curve and a number and returns the reason
for rejection, or `None`. The `validate` lines call it, and the generator calls it on
each candidate it draws. The generator's only extra job is the loop.
</details>

<details><summary>Hint 2: the approach</summary>

Compute `B` from the curve: `1 << (n.bit_length() // 2)` is `2^128` for P-256 and `2^192` for
P-384. Return `out-of-range` when `d < 1` or `d >= n`. Otherwise return `weak` when `d < B` or
`n - d < B`, and `None` after that. In the generator, ask the random source for as many bytes as
`n` needs (`(n.bit_length() + 7) // 8`), read them with `int.from_bytes(block, "big")`, and
return the first candidate that validates. If you parse the hex yourself, hex text read left to
right is already big-endian.
</details>

<details><summary>Hint 3: the traps</summary>

- Zero is below `B` too. Test the range first, or zero comes out as `weak`.
- `n` and every value above it is `out-of-range`. A test of `n - d < B` alone calls it `weak`,
  because `n - d` is zero or negative there.
- `d = B` passes the check and `B - 1` is weak. The mirror image is `n - B` (passes) and
  `n - B + 1` (weak).
- Checking only `d < B` misses the top end: `n - 1` and `n - 4` have public keys `-G` and `-4G`.
- Each curve has its own `n`, byte length and `B`. Taking `B` from one curve for both makes a
  P-384 key below `2^192` look fine, or a P-256 key look weak.
- The generator redraws after a `weak` candidate as well as an `out-of-range` one.
- Print `d` in hex, zero-padded to the curve's byte length, not in decimal.
- Stop at the first accepted candidate. Real data has no blocks after it, but don't make your
  code depend on that.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
validate_private_key(curve, d):
    n = curve.n
    B = 2 ^ (bit_length(n) / 2)          # integer division
    if d < 1 or d >= n:
        return "out-of-range"
    if d < B or n - d < B:
        return "weak"
    return None

generate_private_key(curve, random_bytes):
    loop:
        candidate = big-endian integer of random_bytes(byte length of n)
        if validate_private_key(curve, candidate) is None:
            return candidate
```
</details>

## Checking your solution

```
.\check 12                              run every test
.\check 12 -Case 12-R4-n-minus-1-p256   one test, showing its full input, expected output and your output
.\check 12 -Fresh                       a new set of tests (new random seed), to confirm on data you haven't seen
.\check 12 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  A key above n - B gets `weak`, because d and n - d are as easy to gue... .    0 / 7   FAILED
      x 12-R4-n-minus-1-p256  P-256: d = n - 1 (the public key is -G) is weak
          line 1: expected `reject v0 weak`, got `ok v0`
          likely cause: R4 - A key above n - B gets `weak`, because d and n - d are as easy to guess as each other; n - 1 is the largest of them
          expected values from: Python integers and the published curve orders (SEC 2 / FIPS 186-5); OpenSSL (cryptography) confirms the order, and that d and n - d give negated public keys
          reproduce: py -P tools/run_py.py solutions 12 build/cases/12/12-R4-n-minus-1-p256.in build/cases/12/12-R4-n-minus-1-p256.out
```

## After you pass: compare with the post

The post describes the outcome of a ceremony step going wrong and gives no code, so there is no
author's code to compare with. Run on each of the eight incident keys, your `validate_private_key`
returns `weak`: every one is below 256, far under `B = 2^192`. A ceremony that applied this check
to every private key before using it, including one handed to the module or returned by an unwrap,
would have flagged them. None of the sources above says whether eMudhra's software ran such a
check. Inside an HSM the operators never see `d`, so a ceremony can run this check only if the
module itself performs it. Otherwise the ceremony can run only assignment 13's lint, on the public
key.

The check says nothing about how those keys came to exist. It also passes a key with no obvious
pattern that still came from a small set of inputs. A generator that draws and validates, as
yours does, is necessary and not sufficient: assignment 14 checks the steps after generation, such
as the wrap/unwrap step that Update 3 and the Mozilla bug comment name, where a key can change without any
check on one key noticing.

Your generator draws from `os.urandom` unless the caller passes another source, which is how the
program replays the recorded blocks. Its weak check fires with probability about 2^-127
on P-256 random data and costs one comparison per key.
