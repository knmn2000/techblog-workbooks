# 13 · Lint a public key

**Difficulty:** Medium · **Checkpoint** 13 of 16 · **Check:** `./check.sh 13`

**Tags**
- *Language:* big integers · modular arithmetic · parsing hex · sets
- *Library:* none needed
- *Concepts:* curve membership · weak-key search (checkpoint 10) · key blocklists · check ordering

## Read in the blog first

This page is complete on its own. eMudhra's
[Update 3](https://emudhra.com/en/post/certificate-security-incident#:~:text=An%20Update%20on%20Our%20Global%20TLS%20Intermediate%20CA%20Incident)
says the weak keys went undetected for about 18 months, across two audit cycles. It doesn't say
what an audit would actually check. This checkpoint is one answer: the small set of checks a
certificate authority, or anyone about to trust a public key, could run before publishing it.

## Where this fits

Checkpoint 10 built a search that finds a key's private value if it's small. This checkpoint
turns that search into one of three checks a linter runs on every public key it sees, alongside
checking the key is a real point at all and checking it against a list of keys already known to
be bad. Checkpoint 15 picks up from here: once a bad key is found, how does a browser actually
stop trusting it.

## The problem

Write a program that reads public keys, one at a time, and a blocklist that grows as the input is
read, and decides whether each key passes every check a linter runs before trusting it.

A key fails for exactly one of three reasons, checked in this order, stopping at the first one
that applies:

1. **`off-curve`** — the point doesn't satisfy the curve's equation at all. Nothing else about the
   key means anything if this is true, so it's checked first.
2. **`known-compromised`** — the point's exact coordinates appear on a blocklist of keys already
   known to be bad (for example, keys published in a previous incident). This is a cheap lookup:
   checking it before running a search is the obvious order.
3. **`weak`** — the point equals `d*G` for some whole number `d` with `1 <= d <= 4096`: small
   enough that an attacker could find it by brute force, the same search checkpoint 10 built.
   This is the most expensive check, so it runs last.

A key that fails none of these passes.

**Why the bound is only 4096.** A real linter auditing real keys would want a bound many orders
of magnitude higher than this (the actual incident's keys were found by trying values up to
roughly 2^8, but a thorough audit tries far more, often with faster methods than this
checkpoint's one-step-at-a-time search). This checkpoint keeps the bound at 4096 so every test
finishes almost instantly using the same simple loop as checkpoint 10: it's the same idea, not a
production-grade budget.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains two kinds of lines:

| Line | Meaning |
|---|---|
| `blocklist <curve> <x> <y>` | Adds one entry to the blocklist. It applies to every `key` line that follows it in the input (earlier `blocklist` lines keep applying too; the blocklist only grows). |
| `key <label> <curve> <x> <y>` | A public key to check. `label` is a word with no spaces. `curve` is `P-256` or `P-384`. `x` and `y` are hexadecimal, lowercase, with no `0x` prefix, zero-padded to the curve's byte length. |

Unlike checkpoint 10's keys, a `key` line here is **not** guaranteed to be a valid point: checking
that is part of the problem.

### Output

For each `key` line, in input order, write one line:

```
ok <label>                     the key passes every check
fail <label> <reason>          the key fails, for the first reason that applies (see above)
```

`<reason>` is one of `off-curve`, `known-compromised`, `weak`. `<label>` is copied from the input
unchanged. The checker ignores extra whitespace.

### The curves

| | P-256 | P-384 |
|---|---|---|
| `p` | `ffffffff00000001000000000000000000000000ffffffffffffffffffffffff` | `fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff` |
| `a` | `p - 3` | `p - 3` |
| `b` | `5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b` | `b3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef` |
| `Gx` | `6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296` | `aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7` |
| `Gy` | `4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5` | `3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f` |

A point `(x, y)` is on the curve when `y^2 = x^3 + a*x + b (mod p)`. Finding `d` for a weak key
uses the same point-addition rules as checkpoint 10 (the ordinary formula for adding two
different points, the doubling formula when the running total reaches `G` a second time).

### What this checkpoint does not ask

The point at infinity (the curve's identity element) has no `(x, y)` form; it's usually written
as a single zero byte instead. Since every key in this input is given as an explicit `(x, y)`
pair, there's no way to spell "the identity" that way, so this checkpoint has no separate
`identity` reason: an attempt to encode it would just be some pair of numbers, which either
satisfies the curve equation (and is a perfectly normal point) or doesn't (and is `off-curve`,
which already covers it).

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** A genuinely strong, valid key that isn't on the blocklist passes every check: `ok`.
- **R2** A point that doesn't satisfy the curve equation fails with `off-curve`, before any other
  check runs.
- **R3** A key whose private value is at most 4096 fails with `weak`. One at 4097 does not.
- **R4** A key that is not weak, but whose exact coordinates were added to the blocklist by an
  earlier line, fails with `known-compromised`. A blocklist entry for a different key must not
  affect it.
- **R5** When more than one reason could apply to the same point, `off-curve` is reported before
  `known-compromised`, and `known-compromised` is reported before `weak`.

## Examples

### Example 1: an off-curve point that's also blocklisted (test `13-R5-offcurve-beats-blocklist-p256`)

```
input:   blocklist P-256 <the perturbed, off-curve coordinates>
         key a P-256 <the same, off-curve coordinates>

output:  fail a off-curve
```

Even though the exact coordinates are on the blocklist, the point isn't on the curve at all, so
`off-curve` wins: it's checked first, and nothing past it matters.

### Example 2: a weak key that's also blocklisted (test `13-R5-blocklist-beats-weak-p384`)

```
input:   blocklist P-384 <coordinates of 4*G on P-384>
         key a P-384 <the same coordinates>

output:  fail a known-compromised
```

The point is on the curve, and its private key is 4, well under the bound, so it would also be
caught by the weak-key search. The blocklist check runs first and reports `known-compromised`.

### Example 3: a blocklist entry that doesn't apply (test `13-R4-blocklist-does-not-apply-p256`)

```
input:   blocklist P-256 <coordinates of some strong key>
         key a P-256 <coordinates of a different strong key>

output:  ok a
```

A blocklist entry only ever matches its own exact coordinates. A key that happens to arrive after
it in the input, but isn't the same point, is unaffected.

## Constraints

- Every line is a `blocklist` or a `key` line; there are no blank lines.
- An input has at most 10 `key` lines and at most 5 `blocklist` lines. Labels have no spaces.
- Each case has a 10-second limit. A bound of 4096, stepped one addition at a time as in
  checkpoint 10, finishes well inside it even with several keys in one input.
- There are 24 tests: 2 for R1, 2 for R2, 10 for R3 (both curves, several small `d`, the bound
  itself, and one past it), 4 for R4, 4 for R5 and 2 end-to-end cases mixing every reason in one
  input with a growing blocklist. Part of the set is random and changes with `-Fresh`.

## Source material

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3
- Checkpoint 10 (`problems/10-find-weak-key.md`): the weak-key search this checkpoint reuses
- Google Security Blog, [Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA Certificates](https://security.googleblog.com/): describes blocking specific compromised keys by their SPKI hash, the real-world version of this checkpoint's blocklist (checkpoint 15 models that mechanism directly)
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 3.2.2 (public key validation)

## Hints

<details><summary>Hint 1: where to start</summary>

This checkpoint has three separate, independent checks. Write each one as its own small function,
then call them in the order the problem lists, returning as soon as one fails. Don't try to
combine them into one pass.
</details>

<details><summary>Hint 2: the approach</summary>

For curve membership, plug `x` and `y` into `y^2 = x^3 + a*x + b (mod p)` and compare both sides.
For the blocklist, keep a Python `set` of `(curve, x, y)` tuples, adding to it as `blocklist`
lines arrive, and check membership before each `key` line's other checks. For weak keys, reuse
checkpoint 10's walk: start at `G`, add `G` repeatedly, and compare with the target point at each
step, stopping at the bound.
</details>

<details><summary>Hint 3: the traps</summary>

- Check curve membership before anything else. The weak-key search's point addition still runs
  without crashing on an off-curve point; it just never finds a match, which is the wrong way to
  report "off-curve" (it would wrongly say `ok`).
- The blocklist only ever grows. An entry declared early in the input still applies to a `key`
  line much later.
- The weak-key bound is inclusive: `d = 4096` is `weak`, `d = 4097` is `ok` (if nothing else is
  wrong with it).
- A blocklist entry matches only its own exact `(curve, x, y)`. Matching only `x`, or ignoring
  `curve`, over-blocks keys that happen to share a coordinate.
- Coordinates are hex text, parsed as base 16. The blocklist set should store them as the same
  kind of value (integers) you parse keys into, or comparisons will silently never match.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
lint_key(curve, x, y, blocklist):
    if not on_curve(curve, x, y):
        return "off-curve"
    if (curve, x, y) in blocklist:
        return "known-compromised"
    if find_small_private_key(curve, x, y, bound=4096) is not None:
        return "weak"
    return None   # ok
```
</details>

## Checking your solution

```
./check.sh 13                                      run every test
./check.sh 13 -Case 13-R5-blocklist-beats-weak-p384   one test, showing its full input, expected output and your output
./check.sh 13 -Fresh                               a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 13 -Dispute <id> "why"                  set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R5  Priority: off-curve is reported before known-compromised, and kno... .    3 / 4   FAILED
      x 13-R5-blocklist-beats-weak-p384  P-384: d = 4 (weak) whose coordinates are also blocklisted: known-compromised wins
          line 1: expected `fail a known-compromised`, got `fail a weak`
          likely cause: R5 - Priority: off-curve is reported before known-compromised, and known-compromised before weak
          expected values from: cryptography 41.0.7 (OpenSSL) for curve membership and real key points; exact coordinate match for the blocklist
          reproduce: python3 -P tools/run_py.py solutions 13 build/cases/13/13-R5-blocklist-beats-weak-p384.in build/cases/13/13-R5-blocklist-beats-weak-p384.out
```

## After you pass: compare with the post

The post describes what an audit missed, not how one is supposed to run; there's no author's
code to compare here. What you built is a plausible shape for the audit step that, run on these
eight keys before they were published, would have stopped the incident at the point of
publication rather than roughly 18 months later.

**Something to look for:** the post says the weak keys went undetected "across two audit cycles,"
without describing what either audit checked. This checkpoint doesn't claim to reconstruct those
audits; it's the minimum a key linter could do, built from checks this workbook has already
covered.
