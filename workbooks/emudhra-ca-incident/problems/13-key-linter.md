# 13 · Lint a public key

**Difficulty:** Medium · **Assignment** 13 of 16 · **Check:** `.\check 13`

**Tags**
- *Language:* big integers · modular arithmetic · parsing hex · sets
- *Library:* none needed
- *Concepts:* curve membership · weak-key search (assignment 10) · key blocklists · check ordering

## Read in the blog first

This page is complete on its own. eMudhra's
[Update 3](https://emudhra.com/en/post/certificate-security-incident#:~:text=An%20Update%20on%20Our%20Global%20TLS%20Intermediate%20CA%20Incident)
says the weak keys went undetected for about 18 months, across two audit cycles. It doesn't say
what an audit would check. This assignment gives one answer: the small set of checks that a
certificate authority, or anyone about to trust a public key, could run before publishing it.

## Source material

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3
- Assignment 10 (`problems/10-find-weak-key.md`): the weak-key search this assignment reuses
- Google Security Blog, [Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA Certificates](https://security.googleblog.com/): describes blocking specific compromised keys by their SPKI hash, the real-world version of this assignment's blocklist (assignment 15 models that mechanism)
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 3.2.2 (public key validation)

## Where this fits

Your `attack/weak_key.py` from assignment 10 finds a key's private value when it's small. In this
assignment that search becomes one of three checks in a new module, `pki/lint.py`. The other two
test that the key is a point on its curve and look it up in a list of keys already known to be
bad. The curve test uses the `Curve` type from your `ecc/curve.py` (assignment 02) and the curves
in your `ecc/curves.py` (assignment 03).

Assignment 16 lints every key of a whole PKI with your `lint_key`. Assignment 15 turns to the next
step: once someone finds a bad key, how a browser stops trusting it.

## The problem

Write a program that reads public keys one at a time, along with a blocklist that grows as it
reads, and decides whether each key passes every check a linter runs before trusting it.

### The three checks

A key fails for one of three reasons. Run the checks in this order and stop at the first one that
fails:

1. `off-curve`: the point doesn't satisfy the curve's equation. If that's true, nothing else
   about the key means anything, so this check runs first.
2. `known-compromised`: the point's exact coordinates, on the same curve, appear on the
   blocklist of keys already known to be bad (for example, keys published in an earlier
   incident). This is a cheap lookup, so it runs before the search.
3. `weak`: the point equals `d*G` for some whole number `d` with `1 <= d <= 4096`, small
   enough for an attacker to find by brute force with the search from assignment 10. This is
   the most expensive check, so it runs last.

A key that fails none of these passes.

A linter auditing real keys would use a bound many orders of magnitude higher than 4096. The
incident's keys turned up in a search of values up to about 2^8, but a thorough audit tries far
more, often with faster methods than a search that adds `G` one step at a time. This assignment
keeps the bound at 4096 so that every test finishes well inside the time limit with the loop
from assignment 10. The idea is the same at a smaller budget.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains two kinds of lines:

| Line | Meaning |
|---|---|
| `blocklist <curve> <x> <y>` | Adds one entry to the blocklist. It applies to every `key` line that follows it in the input (earlier `blocklist` lines keep applying too; the blocklist only grows). |
| `key <label> <curve> <x> <y>` | A public key to check. `label` is a word with no spaces. `curve` is `P-256` or `P-384`. `x` and `y` are hexadecimal, lowercase, with no `0x` prefix, zero-padded to the curve's byte length. |

Unlike assignment 10's keys, the point on a `key` line may not be on its curve. Checking that is
part of the problem.

### Output

For each `key` line, in input order, write one line:

```
ok <label>                     the key passes every check
fail <label> <reason>          the key fails, for the first reason that applies (see above)
```

`<reason>` is one of `off-curve`, `known-compromised` and `weak`, as "The three checks" above
defines them. Copy `<label>` from the input unchanged. The checker ignores extra whitespace.

### The curves

| | P-256 | P-384 |
|---|---|---|
| `p` | `ffffffff00000001000000000000000000000000ffffffffffffffffffffffff` | `fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff` |
| `a` | `p - 3` | `p - 3` |
| `b` | `5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b` | `b3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef` |
| `Gx` | `6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296` | `aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7` |
| `Gy` | `4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5` | `3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f` |

A point `(x, y)` is on the curve when `y^2 = x^3 + a*x + b (mod p)`. Finding `d` for a weak key
uses the point-addition rules from assignment 10: the formula for adding two different points,
and the doubling formula when the running total reaches `G` a second time.

### What this assignment does not ask

The point at infinity is the curve's identity element. It has no `(x, y)` form, and SEC 1 encodes it
as a single zero byte. Every key in this input is an explicit `(x, y)` pair, so
the input has no way to spell the identity, and this assignment has no separate `identity`
reason. An attempt to encode it would be some pair of numbers that either satisfies the curve
equation (and is a normal point) or doesn't (and fails as `off-curve`).

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A strong, valid key that isn't on the blocklist passes every check: `ok`.
- **R2** A point that doesn't satisfy the curve equation fails with `off-curve`, before any other
  check runs.
- **R3** A key whose private value is at most 4096 fails with `weak`. One at 4097 does not.
- **R4** A key that isn't weak, and whose exact coordinates an earlier `blocklist` line added,
  fails with `known-compromised`. A blocklist entry for a different key doesn't affect it.
- **R5** When more than one reason applies to the same point, `off-curve` wins over
  `known-compromised`, and `known-compromised` wins over `weak`.

## Examples

### Example 1: an off-curve point that's also blocklisted (test `13-R5-offcurve-beats-blocklist-p256`)

```
input:   blocklist P-256 <the perturbed, off-curve coordinates>
         key a P-256 <the same, off-curve coordinates>

output:  fail a off-curve
```

The exact coordinates are on the blocklist, but the point isn't on the curve, so `off-curve` wins.
That check runs first, and nothing after it matters.

### Example 2: a weak key that's also blocklisted (test `13-R5-blocklist-beats-weak-p384`)

```
input:   blocklist P-384 <coordinates of 4*G on P-384>
         key a P-384 <the same coordinates>

output:  fail a known-compromised
```

The point is on the curve, and its private key is 4, well under the bound, so the weak-key search
would catch it too. The blocklist check runs first and reports `known-compromised`.

### Example 3: a blocklist entry that doesn't apply (test `13-R4-blocklist-does-not-apply-p256`)

```
input:   blocklist P-256 <coordinates of some strong key>
         key a P-256 <coordinates of a different strong key>

output:  ok a
```

A blocklist entry matches only its own exact coordinates. A different key that comes after it in
the input passes.

## Constraints

- Every line is a `blocklist` or a `key` line; there are no blank lines.
- An input has at most 10 `key` lines and at most 5 `blocklist` lines. Labels have no spaces.
- Each case has a 10-second limit. A bound of 4096, stepped one addition at a time as in
  assignment 10, finishes well inside it even with several keys in one input.
- There are 24 tests: 2 for R1, 2 for R2, 10 for R3 (both curves, several small `d`, the bound
  itself, and one past it), 4 for R4, 4 for R5 and 2 end-to-end cases mixing every reason in one
  input with a growing blocklist. Part of the set is random and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

The linter is three separate checks: `on_curve` for the equation, a set lookup for the blocklist,
and your `find_private_key` from assignment 10 for a weak key. Write `on_curve` first, then make
`lint_key` call the checks in the order the page lists, returning as soon as one fails. Keep them
as separate steps rather than one combined pass.
</details>

<details><summary>Hint 2: the approach</summary>

For curve membership, put `x` and `y` into `y^2 = x^3 + a*x + b (mod p)` and compare both sides.
The program keeps the blocklist as a `set` of `(curve name, (x, y))` pairs, adding to it as
`blocklist` lines arrive, so `lint_key` checks whether the key's own pair is in it. For a weak key,
call `find_private_key` with the bound: it starts at `G`, adds `G` at every step and compares with
the target point, up to the bound.
</details>

<details><summary>Hint 3: the traps</summary>

- Check curve membership before anything else. The weak-key search's point addition runs on an
  off-curve point without crashing and finds no match, so the key would come out `ok` when it
  should fail with `off-curve`.
- The blocklist only grows. An entry declared early in the input still applies to a `key` line
  much later.
- The weak-key bound is inclusive: `d = 4096` is `weak`, `d = 4097` is `ok` (if nothing else is
  wrong with it).
- A blocklist entry matches only its own exact `(curve, x, y)`. Matching only `x`, or ignoring
  the curve, blocks keys that happen to share a coordinate.
- Coordinates arrive as hex text, parsed as base 16. Store the blocklist's coordinates as the
  same kind of value (integers) you parse keys into, or a lookup finds nothing and no error
  tells you.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
lint_key(curve, public_key, blocklist):
    if not on_curve(curve, public_key):
        return "off-curve"
    if (curve.name, public_key) in blocklist:
        return "known-compromised"
    if find_private_key(curve, public_key, bound=4096) is not None:
        return "weak"
    return None   # ok
```
</details>

## Checking your solution

```
.\check 13                                          run every test
.\check 13 -Case 13-R5-blocklist-beats-weak-p384    one test, showing its full input, expected output and your output
.\check 13 -Fresh                                   a new set of tests (new random seed), to confirm on data you haven't seen
.\check 13 -Dispute <id> "why"                      set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R5  Priority: off-curve is reported before known-compromised, and kno... .    3 / 4   FAILED
      x 13-R5-blocklist-beats-weak-p384  P-384: d = 4 (weak) whose coordinates are also blocklisted: known-compromised wins
          line 1: expected `fail a known-compromised`, got `fail a weak`
          likely cause: R5 - Priority: off-curve is reported before known-compromised, and known-compromised before weak
          expected values from: cryptography 41.0.7 (OpenSSL) for curve membership and real key points; exact coordinate match for the blocklist
          reproduce: py -P tools/run_py.py solutions 13 build/cases/13/13-R5-blocklist-beats-weak-p384.in build/cases/13/13-R5-blocklist-beats-weak-p384.out
```

## After you pass: compare with the post

The post describes what an audit missed and gives no code, so there's nothing of the author's to
compare with here. You built one plausible shape for the audit step. Run on these eight keys
before they were published, it would have stopped the incident at publication instead of about
18 months later.

The post says the weak keys went undetected "across two audit cycles,"
without describing what either audit checked. This assignment makes no claim about those audits.
It's the minimum a key linter could do, built from checks that earlier assignments covered.
