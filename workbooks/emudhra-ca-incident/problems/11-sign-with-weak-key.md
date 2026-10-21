# 11 · Sign a certificate with a recovered key

**Difficulty:** Hard · **Assignment** 11 of 16 · **Check:** `.\check 11`

**Tags**
- *Language:* big integers · modular arithmetic · parsing hex
- *Library:* none needed. Python's built-in `int` handles 384-bit numbers
- *Concepts:* ECDSA signing · the private key's role · why a compromised CA key is catastrophic

This assignment works only on the workbook's own test data: no real certificate authority, domain
or production system appears in it. In code you write yourself, you see what an attacker needs
once an intermediate key is weak: the arithmetic below, and nothing more.

## Source material

- NIST, [FIPS 186-5: Digital Signature Standard](https://csrc.nist.gov/pubs/fips/186-5/final), section 6.4 (ECDSA signature generation)
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 4.1.3
- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3
- Assignment 04 of this workbook (ECDSA verify), whose equation this assignment inverts
- Assignment 10 of this workbook (find a weak private key), which produces the `d` this assignment signs with

## Where this fits

Assignment 10 found a private key `d` from its public key when `d` was small, and assignment 04
checked a signature against a public key. In this assignment you add signing to your
`ecc/ecdsa.py` from assignment 04, next to `verify`. You build it from `scalar_multiply` in your
`ecc/curve.py` (assignment 03) and `modinv` in your `ecc/modmath.py` (assignment 01).

Signing is what an attacker does with `d` once they have it. It is the same arithmetic as
verifying, run forwards. With `d`, a few lines of code produce a signature anyone will accept,
on a message that says anything the attacker likes. eMudhra's eight intermediate keys were
therefore a risk from the moment they were weak, whether or not anyone had used them yet.

## The problem

Write a program that computes an ECDSA signature from a private key, a message's hash and a
one-time random number called the nonce (written `k`).

### The signing equation

A real signer draws `k` at random for each signature and never reuses it. Here the input gives
you `k`, so the answer is exact and the checker can compare it. "After you pass" on this page
explains why reusing `k` would be a disaster of its own.

With `n` the curve's order (`curve.n` in your `ecc/curves.py`) and `G` the generator:

```
R = k * G
r = R.x mod n
s = k^-1 * (z + r * d) mod n
```

- `z` is the message's hash, already reduced to an integer the way assignment 04 uses it.
- The signature is the pair `(r, s)`.
- The equation is assignment 04's verification equation solved for `s`. A relying party who
  later checks `(r, s)` with assignment 04's procedure gets `valid`, because the equation
  guarantees it.
- `k` can be any size up to `n`, so `k * G` needs double-and-add, the way your `scalar_multiply`
  from assignment 03 computes it. A loop that adds `G` to itself `k` times would not finish.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Each line is one signature to produce:

```
sign <id> <curve> <d> <z> <k>
```

| Field | Meaning |
|---|---|
| `id` | A label with no spaces. Print it back unchanged. |
| `curve` | `P-256` or `P-384`. |
| `d` | The private key in hex, zero-padded to the curve's field width (64 hex digits for P-256, 96 for P-384). |
| `z` | The message's hash, in hex of the same width as `d`, already an integer in range. |
| `k` | The nonce, in hex of the same width. It is a valid value: `1 <= k <= n - 1`. |

### Output

One line per input, in order:

```
signature <id> <r> <s>
```

Write `r` and `s` in lowercase hex, zero-padded to the same width as the input values. The
checker ignores extra whitespace.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** One output line per input, in order, in the format above.
- **R2** Both curves work. P-256 and P-384 each use their own `p`, `a`, `G` and `n`.
- **R3** Every nonce works, including `k = 1` (`R` is `G` itself), `k = 2` (the first doubling),
  `k = n - 1` (the largest valid nonce) and a large random `k`. Compute `k * G` by
  double-and-add: `k` here can be as large as the curve's order, and a loop that runs `k` times
  would not finish.
- **R4** The private key can be any value, including small ones. `d = 4` (the value reported for
  the real incident) works the same way as a large, well-generated key: the formula doesn't
  depend on how anyone chose `d`.
- **R5** The hash `z` can be any value in range, including `0` and `n - 1`.

## Examples

### Example 1: the smallest nonce (test `11-R3-k1-p384`)

```
input:   sign 11-R3-k1-p384 P-384 5d5f576cdeb8fc4c7b297d0b0e5e18baf320cd576d14475b349aae908fb5262cc703806984c8199a21167d8fcf23cae8 0067dba8589890086a17b9af5b569643d037cdff7c240d4969d495dd81355c53f0e642f43328ad088ded3c9691eb79fa 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001

output:  signature 11-R3-k1-p384 aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7 5b4e039c405a0366fd8a91c3ce8a07c479ed10e65fa1eb03d083c668d4f73196c82ed628f6f2df7f526e3ffcffbf23fa
```

`k = 1`, so `R = 1*G = G`, and `r` is the x-coordinate of `G` (`Gx` in assignment 10's curve
table, `curve.g[0]` in your code). `s` still depends on `d` and `z`.

### Example 2: the recovered incident value (test `11-R4-d4-p384`)

```
input:   sign 11-R4-d4-p384 P-384 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004 412a9849a82088207e9248cc2161b5a2504f5106fdabba32233c11e86a3f24af60ac1342c1aca015d7033d3b97e1442a 6d21f4cda185cc8ea8ea37f7523d2a54cdaaac43936aa40cacc66a576518093d07dbf924a6048457861e02ec39235bc2

output:  signature 11-R4-d4-p384 db8e7ab807a931d856adfb75bd2b1fb1270041e58b6afb3aae9cf6e62f77588876d2fdc8a758dd27721fecf5d7d7ae78 8c3f085c5e97b23aa36e0c2c79284edec8ad1075a441324c936668856b7ed3d8fb51fe0dbd133897c54b3b7cd23e2bf2
```

`d = 4` is the value assignment 10 recovers for the real incident's example key. The signature
comes from the same arithmetic as any other. Checking it with assignment 04's verification
equation and the matching public key (`4 * G`, from assignment 03) gives `valid`.

## Constraints

- `d`, `z` and `k` are well-formed: `1 <= d < n`, `0 <= z < n`, `1 <= k < n`.
- Every test gives non-zero `r` and `s`. A real signer has to check for zero and draw a new `k`
  if either comes out zero; no test exercises that check.
- Each case has a 10-second limit. Double-and-add for `k * G` takes well under a second, even for
  the largest `k` in the tests.
- There are 21 tests: the examples above, both curves, the nonce values described in R3, several
  small and large private keys including the incident's, and the hash boundaries in R5.

## Hints

<details><summary>Hint 1: where to start</summary>

You already have the pieces from assignments 01 to 04. `k * G` is your `scalar_multiply` from
assignment 03, and the formula for `s` is assignment 04's verification equation rearranged to
solve for `s`.
</details>

<details><summary>Hint 2: the approach</summary>

Compute `R = k * G` with `scalar_multiply`. Take `r` as `R`'s x-coordinate reduced mod `n`; the
curve's field prime `p` and its order `n` are different numbers. Compute the modular inverse of
`k` mod `n` with your `modinv`. Then `s = k_inverse * (z + r * d) mod n`.
</details>

<details><summary>Hint 3: the traps</summary>

- Reduce `r` mod `n`, the curve's order. The field prime `p` of the point coordinates is a
  different number.
- The modular inverse in the `s` formula is mod `n`, the same modulus as `r` and `s`.
- `k * G` needs double-and-add. A loop that adds `G` to itself `k` times won't finish for the
  large `k` values in the tests.
- `d`, `z` and `k` are separate hex fields on the input line, in that order after the curve name.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
sign(curve, d, z, k):
    R = multiply(k, G)          # double-and-add, as in assignment 03
    r = R.x mod n
    s = inverse(k, n) * (z + r * d) mod n
    return (r, s)
```
</details>

## Checking your solution

```
.\check 11                              run every test
.\check 11 -Case 11-R4-d4-p384          one test, showing its full input, expected output and your output
.\check 11 -Fresh                       a new set of tests (new random seed)
.\check 11 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R1  One output line per input, in order: `signature <id> <r> <s>`, in... .    0 / 1   FAILED
      x 11-R1-three-signatures  three signatures in one input, two curves
          line 1: expected `signature mixed-0 3bf088ee725c0b640b5448c4ef03ce7668531395f8630f7c0836e3ce68ec32ae 26b9...`, got `signature mixed-0 3bf088ee725c0b640b5448c4ef03ce7668531395f8630f7c0836e3ce68ec32ae a76d...`
          likely cause: R1 - One output line per input, in order: `signature <id> <r> <s>`, in lowercase hex
          expected values from: cryptography 41.0.7 (OpenSSL): r from scalar multiplication, the signature confirmed by verifying it
          reproduce: py -P tools/run_py.py solutions 11 build/cases/11/11-R1-three-signatures.in build/cases/11/11-R1-three-signatures.out
```

## After you pass: why real signing never gives you `k`

The reference adds `sign` to `ecc/ecdsa.py` in four lines, with `scalar_multiply` from
`ecc/curve.py` and `modinv` from `ecc/modmath.py`.

This assignment hands you `k` so the answer is exact and the checker can compare it. A real
signer draws `k` from a secure random source and never writes it down. Two mistakes with `k`,
which this assignment's tests don't exercise, show why.

Reusing `k` for two different messages leaks `d`. Two signatures `(r, s1)` and `(r, s2)` with
the same `k` share `r`, since `r` depends only on `k`. They satisfy
`s1 - s2 = k^-1 * (z1 - z2) mod n`, so `k = (z1 - z2) * (s1 - s2)^-1 mod n`, and then
`d = (s1*k - z1) * r^-1 mod n`. Sony's PlayStation 3 signing key leaked this way in 2010: the
group fail0verflow found that Sony's signer used a fixed `k` for every signature, where it should
have drawn a fresh one each time, and recovered the key from two signatures.

A `k` that is a little less than uniformly random (biased, short, or predictable from a weak
random number generator) lets an attacker recover `d` from a handful of real signatures with
lattice methods, without ever seeing `k`. This attack differs from assignment 10's and is
harder, but it starts from the same place: a key generation process that doesn't do its job.

eMudhra's incident involved a weak key, and both of these mistakes concern the nonce, so
neither applies to it directly. Both teach assignment 10's lesson from another angle: in ECDSA,
every number that should be unpredictable has to be unpredictable, or the private key stops
being private.
