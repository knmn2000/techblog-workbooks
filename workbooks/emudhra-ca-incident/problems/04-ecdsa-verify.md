# 04 · Verify an ECDSA signature

**Difficulty:** Medium · **Checkpoint** 4 of 16 · **Check:** `./check.sh 04`

**Tags**
- *Language:* big integers · parsing hex
- *Library:* none needed
- *Concepts:* ECDSA signatures · modular inverse · elliptic-curve scalar multiplication

## Prerequisite material

This checkpoint is prerequisite material for the later checkpoints about the eMudhra incident; it
isn't drawn from a specific blog post. Checkpoints 8 and 9, later in this workbook, check a real
certificate's signature and a certificate chain - both need the equation built here. See "Source
material" below for where it comes from.

## Where this fits

Checkpoint 3 turned a private key into a public key. This checkpoint is the other half of what
makes a signed document checkable: given a public key, a message's hash, and a signature, decide
whether the signature is genuine. Checkpoint 8 runs this exact check on a real certificate's
signature; checkpoint 9 runs it down a whole chain.

## The problem

Write a program that reads a public key, a hashed message, and a signature, and decides whether
the signature is valid.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p04_ecdsa_verify.py` is a comment and an empty
program: reading the input and writing the output are yours. To start from working input/output
code instead, copy `starters/boilerplate/p04_ecdsa_verify.py` over it, or pick Boilerplate in the
book's editor. The boilerplate reads the input and writes the output; you fill in `verify()`.

### Constraint: P-384 and SHA-384 only

A real ECDSA signature can pair any curve with any hash function, and when the hash is wider than
the curve's order, the hash has to be truncated to the order's bit length before it's used as a
number - a detail with its own rules. This checkpoint sidesteps that: it only covers P-384 keys
signing a SHA-384 hash. SHA-384 produces exactly 48 bytes, and P-384's order is also 384 bits (48
bytes) wide, so the hash is used exactly as it comes, with no truncation. **Out of scope:** hash
digests longer or shorter than the curve's order, which need truncation rules this checkpoint
doesn't cover.

### The verification equation

Let `n` be the curve's order, `G` its generator, `Q` the public key point, and `z` the hash,
read as one big number (already at most `n`'s bit length here, so no truncation is needed). Given
a signature `(r, s)`:

1. If `r` isn't in `[1, n-1]`, or `s` isn't in `[1, n-1]`, the signature is **invalid**. Stop here
   - don't compute anything else.
2. Otherwise compute:
   ```
   w  = s^-1 mod n
   u1 = z*w mod n
   u2 = r*w mod n
   point = u1*G + u2*Q
   ```
3. If `point` is the point at infinity, the signature is **invalid**.
4. Otherwise, the signature is **valid** exactly when `point.x mod n == r`, and **invalid**
   otherwise.

`u1*G` and `u2*Q` are the scalar multiplication from checkpoint 3; the final `+` is the point
addition from checkpoint 2. Use the point add/doubling formulas from those checkpoints' pages (the
same style as checkpoint 10's reference uses) - don't reach for a cryptography library's own
verify function; implementing the equation yourself is the point of this checkpoint.

### The curve

P-384 only, for this checkpoint:

| | P-384 |
|---|---|
| `p` | `fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff` |
| `a` | `p - 3` |
| `Gx` | `aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7` |
| `Gy` | `3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f` |
| `n` | `ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973` |

### Input

```
verify <pubx> <puby> <hash> <r> <s>
```

All five values are lowercase hexadecimal, no `0x` prefix:

| Field | Meaning |
|---|---|
| `pubx`, `puby` | The public key's coordinates, each zero-padded to 96 hex characters (48 bytes) |
| `hash` | The signed message's SHA-384 digest, exactly 96 hex characters (48 bytes) |
| `r`, `s` | The signature, each up to 96 hex characters - **not necessarily zero-padded**, since they're just integers, not fixed-width field elements |

### Output

One line per input line: `valid` or `invalid`.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** A genuinely valid signature verifies as `valid`.
- **R2** `r` or `s` outside `[1, n-1]` is `invalid` without needing the point computation - this
  includes `0`, and `n` or larger; it also includes a signature where `r` and `s` are both in
  range but the recomputed point is itself the point at infinity (step 3 above), which must also
  read `invalid`.
- **R3** Changing the signature by 1 - in `r`, in `s`, or in the signed hash - flips a valid
  signature to `invalid`.
- **R4** A signature checked against a different public key than the one that made it is
  `invalid`.
- **R5** `r == n-1` or `s == n-1` (the top of the legal range) verifies `valid` when the signature
  is otherwise genuine - don't confuse "out of range" with "large but legal". `r == n` (one past
  it) must still read `invalid`.

## Examples

### Example 1: an altered hash flips a valid signature (test `04-R3-altered-hash`)

```
input:   verify fcc453ee5f97b9ddaeb17d5ea130809a155d4ddb1b29945195c8808f05adc7872de17d78fdd6a02454310684ecbb6d81 a3de74f3e2a9c7fd89fe2ed606fd4bc8c666c03c8e1d602af12d5719afc2f782ac7806ff285969cdd73726bf0c984a75 398d099cf112f66595f0abc09fdfb6354059c6cd56912a57d859629a714c45740b7fdb376e282013b1bd5fdafa800f8d 4178df420ffdba693ac6af03e1902974fc235200b8c39548052e6fb730a5606ee94250e5ebe067b067a79f4e3f35c58f 4fd6b587265228551753c369d91125df28e88bf10d16130ef240de8bd1f789e72c91790d76827d4734640883de3b979e
         verify fcc453ee5f97b9ddaeb17d5ea130809a155d4ddb1b29945195c8808f05adc7872de17d78fdd6a02454310684ecbb6d81 a3de74f3e2a9c7fd89fe2ed606fd4bc8c666c03c8e1d602af12d5719afc2f782ac7806ff285969cdd73726bf0c984a75 398d099cf112f66595f0abc09fdfb6354059c6cd56912a57d859629a714c45740b7fdb376e282013b1bd5fdafa800f8e 4178df420ffdba693ac6af03e1902974fc235200b8c39548052e6fb730a5606ee94250e5ebe067b067a79f4e3f35c58f 4fd6b587265228551753c369d91125df28e88bf10d16130ef240de8bd1f789e72c91790d76827d4734640883de3b979e

output:  valid
         invalid
```

The two lines share the same public key and signature; only the last hex digit of the hash
differs (`...f8d` vs `...f8e`). That one-bit change in `z` moves `u1` and `u2` just enough that
`u1*G + u2*Q` lands on a different point, whose x no longer matches `r`.

### Example 2: out of range, no point computation needed (test `04-R2-zero`)

```
input:   verify 73dd98ce5d82a164b2260de8eb1882d814c7c9d370a726ab5383f33019a94d4f986b616a7398c84df197ff688bc3e7f0 e561fa88f0275746472540b9fd8a58ff3b4160ada60b25d9331a07e98d2abc0b95574e995f375a01819e5206d9f26ae2 636e78ac889c47f99165501a022c1df16be3804e95e75b6f013a8b49541ac13537537f389f625850b0ec30d3eed4558a 0 68a1ee58855433779f02878867b9265141619ce9b1e7cb163d58eb4ee74d347b2c8930ffa5d4d693661db4f1ba7b9d98
         verify 73dd98ce5d82a164b2260de8eb1882d814c7c9d370a726ab5383f33019a94d4f986b616a7398c84df197ff688bc3e7f0 e561fa88f0275746472540b9fd8a58ff3b4160ada60b25d9331a07e98d2abc0b95574e995f375a01819e5206d9f26ae2 636e78ac889c47f99165501a022c1df16be3804e95e75b6f013a8b49541ac13537537f389f625850b0ec30d3eed4558a 68a1ee58855433779f02878867b9265141619ce9b1e7cb163d58eb4ee74d347b2c8930ffa5d4d693661db4f1ba7b9d98 0

output:  invalid
         invalid
```

`r = 0` fails step 1's range check directly (`0` isn't in `[1, n-1]`), and so does `s = 0`, in
both cases regardless of what `pubx`, `puby` and `hash` are.

### Example 3: the boundary (test `04-R5-r-boundary`)

```
input:   verify 1a08c29c766684b0b3314dcb562d201db2a13ad45dc731907dc4d4c49c481355376ed6f6e3eb528cab18345c3c63087d 1c76ea92bd5ec70f9c018c120c20bfe397286512e63dabbc062b1f929ce3128f178606b436cc84368ac1963c0b2d8b8b 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52972 1234567890abcdef

output:  valid
```

`r` here is `n - 1` exactly - the largest value step 1's range check must still accept. This
signature is genuine (constructed so the equation in steps 2-4 actually holds), so the answer is
`valid`, not `invalid`. A range check written as `r < n - 1` instead of `r <= n - 1` would
wrongly reject this one case while passing everything else.

## Constraints

- Every input line is `verify <pubx> <puby> <hash> <r> <s>`, all lowercase hex, no `0x` prefix.
- `pubx`, `puby`, and `hash` are always exactly 96 hex characters (48 bytes); `r` and `s` can be
  shorter (as short as 1 character, for small values like the `R2` zero cases).
- Every `pubx`, `puby` given is guaranteed to be a valid point on P-384.
- There are 13 tests: 1 for R1 (itself 3 signatures from 3 different keys), 4 for R2, 3 for R3, 1
  for R4, 3 for R5, and one end-to-end test mixing several of the above in one batch, the way a
  verifier would actually see them while checking a batch of certificates. Part of the set is
  random and changes with `-Fresh`.

## Source material

- ANSI X9.62 / FIPS 186-5, the Elliptic Curve Digital Signature Algorithm (ECDSA) - the
  verification equation used above is the standard one, stated for example in NIST FIPS 186-5,
  section 6.4.2 ("ECDSA Signature Verification Algorithm").
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 4.1.4
  ("Verifying Operation").
- NIST, [SP 800-186: Recommendations for Discrete Logarithm-based Cryptography](https://csrc.nist.gov/pubs/sp/800/186/final), for the P-384 domain parameters.

## Hints

<details><summary>Hint 1: where to start</summary>

Check the range of `r` and `s` first and return `invalid` immediately if either is out of range -
this handles several requirements before you need any curve arithmetic at all. Everything else is
the scalar multiplication from checkpoint 3 (twice) and the point addition from checkpoint 2
(once), finishing with one comparison.
</details>

<details><summary>Hint 2: the approach</summary>

Compute `w = s^-1 mod n` (checkpoint 1's extended Euclid). Compute `u1 = z*w mod n` and
`u2 = r*w mod n`. Compute `u1*G` and `u2*Q` (checkpoint 3's double-and-add, with two different
starting points), add them together (checkpoint 2's addition), and check whether the result is
infinity or has `x mod n == r`.
</details>

<details><summary>Hint 3: the traps</summary>

- Check `r` and `s` are both in `[1, n-1]` - not `[0, n-1]` and not `[1, n]`. `0` is invalid; so is
  `n` itself.
- The final check is `point.x mod n == r`, not `point.x == r`. `point.x` is a field element mod
  `p`; `r` is a number mod `n`; `p` and `n` are close but different numbers for this curve.
- `u1*G + u2*Q` can be the point at infinity (when `u1*G` and `u2*Q` are negations of each other).
  That's a different failure mode than an out-of-range `r`/`s` - don't let your point-addition
  code crash trying to read the x of a `None`/infinity result; check for it and return `invalid`.
- `r` and `s` in the input aren't zero-padded like the public key and hash are. Parsing them as
  hex still works the same way; just don't assume a fixed width for them.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
verify(pubx, puby, z, r, s):
    if not (1 <= r <= n-1 and 1 <= s <= n-1):
        return invalid
    w  = modinv(s, n)
    u1 = (z * w) mod n
    u2 = (r * w) mod n
    point = add(scalar_multiply(u1, G), scalar_multiply(u2, (pubx, puby)))
    if point is infinity:
        return invalid
    return valid if (point.x mod n == r) else invalid
```
</details>

## Checking your solution

```
./check.sh 04                         run every test
./check.sh 04 -Case 04-R5-r-boundary  one test, showing its full input, expected output and your output
./check.sh 04 -Fresh                  a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 04 -Dispute <id> "why"     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R5  r == n-1 or s == n-1 (the top of the legal range) verifies `valid... .    1 / 3   FAILED
      x 04-R5-s-boundary  a genuine signature with s == n - 1 exactly
          line 1: expected `valid`, got `invalid`
          likely cause: R5 - r == n-1 or s == n-1 (the top of the legal range) verifies `valid` when the signature is otherwise genuine
          expected values from: cryptography 41.0.7 (OpenSSL): ec.ECDSA(utils.Prehashed(hashes.SHA384())), the library's own verification
          reproduce: python3 -P tools/run_py.py solutions 04 build/cases/04/04-R5-s-boundary.in build/cases/04/04-R5-s-boundary.out
```

## After you pass: nothing to compare

There is no blog code for this checkpoint to compare against: it's the other half of the
arithmetic every later checkpoint builds on, not something the post describes. What you wrote -
the ECDSA verification equation - is exactly what checkpoint 8 runs on a real certificate's actual
signature bytes, and what every browser and certificate authority runs before trusting a
certificate at all.
