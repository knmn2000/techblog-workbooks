# 04 · Verify an ECDSA signature

**Difficulty:** Medium · **Assignment** 4 of 16 · **Check:** `.\check 04`

**Tags**
- *Language:* big integers · parsing hex
- *Library:* none needed
- *Concepts:* ECDSA signatures · modular inverse · elliptic-curve scalar multiplication

## Prerequisite material

This assignment is background for the later assignments about the eMudhra incident; it doesn't
come from a blog post. Assignments 08 and 09 check a real certificate's signature and a
certificate chain, and both need the equation you build here. "Source material" below lists where
it comes from.

## Source material

- ANSI X9.62 / FIPS 186-5, the Elliptic Curve Digital Signature Algorithm (ECDSA). The
  verification equation on this page is the standard one, stated for example in NIST FIPS 186-5,
  section 6.4.2 ("ECDSA Signature Verification Algorithm").
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 4.1.4
  ("Verifying Operation").
- NIST, [SP 800-186: Recommendations for Discrete Logarithm-based Cryptography](https://csrc.nist.gov/pubs/sp/800/186/final), for the P-384 domain parameters.

## Where this fits

Your `ecc/curve.py` from assignments 02 and 03 turns a private key into a public key. This
assignment builds the other half of what makes a signed document checkable: given a public key, a
message's hash and a signature, decide whether the signature is genuine. You write it in
`ecc/ecdsa.py`, with your inverse from `ecc/modmath.py` and P-384 from your `ecc/curves.py`.

Your `x509/signature.py` runs this check on a real certificate's signature in assignment 08, and
assignment 09 runs it down a whole chain. Assignment 11 adds signing to `ecc/ecdsa.py`.

## The problem

Write a program that reads a public key, a hashed message and a signature, and decides whether the
signature is valid.

### Constraint: P-384 and SHA-384 only

An ECDSA signature can pair any curve with any hash function. The verifier truncates a hash wider
than the curve's order to the order's bit length before using it as a number, and that step has
rules of its own. This assignment avoids them: it covers only P-384 keys signing
a SHA-384 hash. SHA-384 produces 48 bytes, and P-384's order is also 384 bits (48 bytes) wide, so
you use the hash as it comes, with no truncation. Hash digests longer or shorter than the curve's
order are out of scope.

### The verification equation

Let `n` be the curve's order, `G` its generator, `Q` the public key point, and `z` the hash, read
as one big number. Here `z` has at most `n`'s bit length, so no truncation applies. Given a signature
`(r, s)`:

1. If `r` isn't in `[1, n-1]`, or `s` isn't in `[1, n-1]`, the signature is invalid. Stop
   here, without computing anything else.
2. Otherwise compute `w`, `u1`, `u2` and `point` as the block below shows.
3. If `point` is the point at infinity, the signature is invalid.
4. Otherwise the signature is valid when `point.x mod n == r`, and invalid when it isn't.

```
w  = s^-1 mod n
u1 = z*w mod n
u2 = r*w mod n
point = u1*G + u2*Q
```

`u1*G` and `u2*Q` are your scalar multiplication from assignment 03, and the final `+` is your
point addition from assignment 02. Write the equation with those functions instead of calling a
cryptography library's verify function: implementing it is the point of this assignment.

### The curve

P-384 only, for this assignment. Your `ecc/curves.py` from assignment 03 already holds it:

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

All five values are lowercase hexadecimal, with no `0x` prefix:

| Field | Meaning |
|---|---|
| `pubx`, `puby` | The public key's coordinates, each zero-padded to 96 hex characters (48 bytes) |
| `hash` | The signed message's SHA-384 digest: 96 hex characters (48 bytes) |
| `r`, `s` | The signature, each up to 96 hex characters. They are plain integers, not fixed-width field elements, so the input doesn't zero-pad them |

### Output

One line per input line: `valid` or `invalid`.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A signature made with the matching private key verifies as `valid`.
- **R2** `r` or `s` outside `[1, n-1]` is `invalid` without the point computation. This includes
  `0`, and `n` or larger. R2 also covers a signature whose `r` and `s` are both in range but whose
  recomputed point is the point at infinity (step 3 above), which must also read `invalid`.
- **R3** Changing `r`, `s` or the signed hash by 1 flips a valid signature to `invalid`.
- **R4** A signature checked against a different public key than the one that made it is
  `invalid`.
- **R5** `r == n-1` or `s == n-1`, the top of the legal range, verifies `valid` when the signature
  is otherwise genuine: a large value can still be legal. `r == n`, one past it, must still read
  `invalid`.
- **E2E** A mixed batch of signatures: some valid, some altered, some out of range, some checked against the wrong key.

## Examples

### Example 1: an altered hash flips a valid signature (test `04-R3-altered-hash`)

```
input:   verify fcc453ee5f97b9ddaeb17d5ea130809a155d4ddb1b29945195c8808f05adc7872de17d78fdd6a02454310684ecbb6d81 a3de74f3e2a9c7fd89fe2ed606fd4bc8c666c03c8e1d602af12d5719afc2f782ac7806ff285969cdd73726bf0c984a75 398d099cf112f66595f0abc09fdfb6354059c6cd56912a57d859629a714c45740b7fdb376e282013b1bd5fdafa800f8d 4178df420ffdba693ac6af03e1902974fc235200b8c39548052e6fb730a5606ee94250e5ebe067b067a79f4e3f35c58f 4fd6b587265228551753c369d91125df28e88bf10d16130ef240de8bd1f789e72c91790d76827d4734640883de3b979e
         verify fcc453ee5f97b9ddaeb17d5ea130809a155d4ddb1b29945195c8808f05adc7872de17d78fdd6a02454310684ecbb6d81 a3de74f3e2a9c7fd89fe2ed606fd4bc8c666c03c8e1d602af12d5719afc2f782ac7806ff285969cdd73726bf0c984a75 398d099cf112f66595f0abc09fdfb6354059c6cd56912a57d859629a714c45740b7fdb376e282013b1bd5fdafa800f8e 4178df420ffdba693ac6af03e1902974fc235200b8c39548052e6fb730a5606ee94250e5ebe067b067a79f4e3f35c58f 4fd6b587265228551753c369d91125df28e88bf10d16130ef240de8bd1f789e72c91790d76827d4734640883de3b979e

output:  valid
         invalid
```

The two lines share the public key and the signature; only the last hex digit of the hash differs
(`...f8d` against `...f8e`). That change of 1 in `z` changes `u1 = z*w mod n`, so `u1*G + u2*Q`
lands on a different point, whose x no longer matches `r`.

### Example 2: out of range, no point computation needed (test `04-R2-zero`)

```
input:   verify 73dd98ce5d82a164b2260de8eb1882d814c7c9d370a726ab5383f33019a94d4f986b616a7398c84df197ff688bc3e7f0 e561fa88f0275746472540b9fd8a58ff3b4160ada60b25d9331a07e98d2abc0b95574e995f375a01819e5206d9f26ae2 636e78ac889c47f99165501a022c1df16be3804e95e75b6f013a8b49541ac13537537f389f625850b0ec30d3eed4558a 0 68a1ee58855433779f02878867b9265141619ce9b1e7cb163d58eb4ee74d347b2c8930ffa5d4d693661db4f1ba7b9d98
         verify 73dd98ce5d82a164b2260de8eb1882d814c7c9d370a726ab5383f33019a94d4f986b616a7398c84df197ff688bc3e7f0 e561fa88f0275746472540b9fd8a58ff3b4160ada60b25d9331a07e98d2abc0b95574e995f375a01819e5206d9f26ae2 636e78ac889c47f99165501a022c1df16be3804e95e75b6f013a8b49541ac13537537f389f625850b0ec30d3eed4558a 68a1ee58855433779f02878867b9265141619ce9b1e7cb163d58eb4ee74d347b2c8930ffa5d4d693661db4f1ba7b9d98 0

output:  invalid
         invalid
```

`r = 0` fails step 1's range check, since `0` isn't in `[1, n-1]`, and `s = 0` fails it too. Both
lines are `invalid` whatever `pubx`, `puby` and `hash` are.

### Example 3: the boundary (test `04-R5-r-boundary`)

```
input:   verify 1a08c29c766684b0b3314dcb562d201db2a13ad45dc731907dc4d4c49c481355376ed6f6e3eb528cab18345c3c63087d 1c76ea92bd5ec70f9c018c120c20bfe397286512e63dabbc062b1f929ce3128f178606b436cc84368ac1963c0b2d8b8b 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 ffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52972 1234567890abcdef

output:  valid
```

`r` here is `n - 1`, the largest value that step 1's range check must accept. This signature is
genuine (built so that the equation in steps 2 to 4 holds), so the answer is `valid`. A range
check written as `r < n - 1` instead of `r <= n - 1` gets this case wrong and passes the others.

## Constraints

- Every input line is `verify <pubx> <puby> <hash> <r> <s>`, all lowercase hex, with no `0x`
  prefix.
- `pubx`, `puby` and `hash` are 96 hex characters (48 bytes) on every line. `r` and `s` can be
  shorter, down to 1 character for small values such as the R2 zero cases.
- Every `pubx`, `puby` pair is a valid point on P-384.
- There are 13 tests: 1 for R1 (itself 3 signatures from 3 different keys), 4 for R2, 3 for R3,
  1 for R4, 3 for R5, and one end-to-end test that mixes several of these in one batch, the way a
  verifier sees them while it checks a batch of certificates. Part of the set is random and
  changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Check the range of `r` and `s` first, and return `invalid` straight away if either is out of
range. That handles several requirements before you need any curve arithmetic. The rest is your
scalar multiplication from assignment 03 (twice) and your point addition from assignment 02
(once), followed by one comparison.
</details>

<details><summary>Hint 2: the approach</summary>

In your `verify` in `ecc/ecdsa.py`, compute `w = s^-1 mod n` with your `modinv` from
`ecc/modmath.py`. Compute `u1 = z*w mod n` and `u2 = r*w mod n`. Compute `u1*G` and `u2*Q` with
your `scalar_multiply` (two different starting points), add them with your `add_points`, and
check whether the result is infinity or has `x mod n == r`.
</details>

<details><summary>Hint 3: the traps</summary>

- Check that `r` and `s` are both in `[1, n-1]`, not `[0, n-1]` and not `[1, n]`. `0` is invalid,
  and so is `n` itself.
- The final check is `point.x mod n == r`, not `point.x == r`. `point.x` is a field element mod
  `p`, `r` is a number mod `n`, and on this curve `p` and `n` are close but different numbers.
- `u1*G + u2*Q` can be the point at infinity, when `u1*G` and `u2*Q` are negations of each
  other. That's a different failure from an out-of-range `r` or `s`. Check for it and return
  `invalid`, so that your code doesn't crash reading the x of `None`.
- `r` and `s` in the input aren't zero-padded like the public key and hash. Parse them as hex the
  same way, without assuming a fixed width.
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
.\check 04                              run every test
.\check 04 -Case 04-R5-r-boundary       one test, showing its full input, expected output and your output
.\check 04 -Fresh                       a new set of tests (new random seed), to confirm on data you haven't seen
.\check 04 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R5  r == n-1 or s == n-1 (the top of the legal range) verifies `valid... .    1 / 3   FAILED
      x 04-R5-s-boundary  a genuine signature with s == n - 1 exactly
          line 1: expected `valid`, got `invalid`
          likely cause: R5 - r == n-1 or s == n-1 (the top of the legal range) verifies `valid` when the signature is otherwise genuine
          expected values from: cryptography 41.0.7 (OpenSSL): ec.ECDSA(utils.Prehashed(hashes.SHA384())), the library's own verification
          reproduce: py -P tools/run_py.py solutions 04 build/cases/04/04-R5-s-boundary.in build/cases/04/04-R5-s-boundary.out
```

## After you pass: nothing to compare

This assignment has no blog code to compare with: it's the other half of the arithmetic the later
assignments build on, and the post doesn't describe it. In assignment 08 your code runs this
ECDSA verification equation on a real certificate's signature bytes. Browsers and certificate
authorities run the same check before they trust a certificate.
