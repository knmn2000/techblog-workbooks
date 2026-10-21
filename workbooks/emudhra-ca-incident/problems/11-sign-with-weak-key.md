# 11 · Sign a certificate with a recovered key

**Difficulty:** Hard · **Checkpoint** 11 of 16 · **Check:** `./check.sh 11`

**Tags**
- *Language:* big integers · modular arithmetic · parsing hex
- *Library:* none needed. Python's built-in `int` handles 384-bit numbers
- *Concepts:* ECDSA signing · the private key's role · why a compromised CA key is catastrophic

Everything in this checkpoint stays inside the workbook's own test data. There is no real
certificate authority, domain or production system anywhere in it. The point is to see, in code
you write yourself, exactly what a weak intermediate key buys an attacker: nothing more than the
arithmetic below.

## Where this fits

Checkpoint 10 found a private key `d` from a public key, when `d` was small. Checkpoint 4
checked whether a signature was valid, given a public key. This checkpoint is what an attacker
does with `d` once they have it: signing is the *same* arithmetic as verifying, run forwards
instead of checked backwards. If you have `d`, producing a signature anyone will accept takes a
few lines of code, for a message saying anything you like. That is the entire reason eMudhra's
eight intermediate keys mattered the moment they were weak, regardless of whether anyone had
used them yet.

## The problem

Write a program that computes an ECDSA signature, given a private key, a message's hash, and a
one-time random number called the nonce (written `k`).

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p11_sign_with_weak_key.py` is a comment and an empty
program: reading the input and writing the output are yours. To start from working input/output
code instead, copy `starters/boilerplate/p11_sign_with_weak_key.py` over it, or pick Boilerplate
in the book's editor. The boilerplate reads the input and writes the output; you fill in
`sign()`.

### The signing equation

Real signing draws `k` at random, once per signature, and never reuses it. Here `k` is given to
you directly, so the answer is exact and checkable; the problem page's "After you pass" explains
why reusing `k` would be a disaster of its own.

With `n` the curve's order (from checkpoint 10's table) and `G` the generator:

```
R = k * G
r = R.x mod n
s = k^-1 * (z + r * d) mod n
```

`z` is the message's hash, already reduced to an integer the same way checkpoint 4 uses it. The
signature is the pair `(r, s)`. This is literally checkpoint 4's verification equation solved for
`s` instead of checked: a relying party who later wants to check `(r, s)` runs checkpoint 4's
procedure and it comes back valid, because that is what the equation guarantees.

`k * G` needs the same double-and-add approach as checkpoint 3 (`k` can be any size up to `n`),
not a loop that adds `G` to itself `k` times.

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
| `d` | The private key, hex, zero-padded to the curve's field width (64 hex digits for P-256, 96 for P-384). |
| `z` | The message's hash, same hex width as `d`, already an integer in range. |
| `k` | The nonce, same hex width. Always a valid value: `1 <= k <= n - 1`. |

### Output

One line per input, in order:

```
signature <id> <r> <s>
```

`r` and `s`, in lowercase hex, zero-padded to the same width as the input values. The checker
ignores extra whitespace.

## Requirements

Each test case is designed around one of these. A failing test also shows which requirement it
was written to cover.

- **R1** One output line per input, in order, in the format above.
- **R2** Both curves work. P-256 and P-384 each use their own `p`, `a`, `G` and `n`.
- **R3** Every nonce works, including `k = 1` (`R` is `G` itself), `k = 2` (the first doubling),
  `k = n - 1` (the largest valid nonce), and a large random `k`. `k * G` must come from
  double-and-add, not a loop that runs `k` times: `k` here is as large as the curve's order, so a
  per-step loop would not finish.
- **R4** The private key can be any value, including small ones. `d = 4` (the value reported for
  the real incident) works exactly the same way as a large, properly generated key. The formula
  does not know or care how `d` was chosen.
- **R5** The hash `z` can be any value in range, including `0` and `n - 1`.

## Examples

### Example 1: the smallest nonce (test `11-R3-k1-p384`)

```
input:   sign 11-R3-k1-p384 P-384 5d5f576cdeb8fc4c7b297d0b0e5e18baf320cd576d14475b349aae908fb5262cc703806984c8199a21167d8fcf23cae8 0067dba8589890086a17b9af5b569643d037cdff7c240d4969d495dd81355c53f0e642f43328ad088ded3c9691eb79fa 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001

output:  signature 11-R3-k1-p384 aa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7 5b4e039c405a0366fd8a91c3ce8a07c479ed10e65fa1eb03d083c668d4f73196c82ed628f6f2df7f526e3ffcffbf23fa
```

`k = 1`, so `R = 1*G = G`, and `r` is exactly `G`'s x-coordinate from checkpoint 10's curve table.
`s` still depends on `d` and `z` as usual.

### Example 2: the recovered incident value (test `11-R4-d4-p384`)

```
input:   sign 11-R4-d4-p384 P-384 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004 412a9849a82088207e9248cc2161b5a2504f5106fdabba32233c11e86a3f24af60ac1342c1aca015d7033d3b97e1442a 6d21f4cda185cc8ea8ea37f7523d2a54cdaaac43936aa40cacc66a576518093d07dbf924a6048457861e02ec39235bc2

output:  signature 11-R4-d4-p384 db8e7ab807a931d856adfb75bd2b1fb1270041e58b6afb3aae9cf6e62f77588876d2fdc8a758dd27721fecf5d7d7ae78 8c3f085c5e97b23aa36e0c2c79284edec8ad1075a441324c936668856b7ed3d8fb51fe0dbd133897c54b3b7cd23e2bf2
```

`d = 4` is the value checkpoint 10 recovers for the real incident's example key. This signature
is computed exactly the same way as any other; feeding it to checkpoint 4's verification equation
with the matching public key (`4 * G`, from checkpoint 3) reports `valid`.

## Constraints

- `d`, `z` and `k` are always well-formed: `1 <= d < n`, `0 <= z < n`, `1 <= k < n`.
- Every test case is constructed so that `r` and `s` both come out non-zero, which a real signer
  must check and redraw `k` for if either happened. That check is not exercised here; the
  constraint guarantees you won't hit it.
- Each case has a 10-second limit. Double-and-add for `k * G` takes well under a second even for
  the largest `k` in the tests.
- There are 21 tests: the examples above, both curves, the nonce values described in R3, several
  small and large private keys including the incident's, and the hash boundaries in R5.

## Source material

- NIST, [FIPS 186-5: Digital Signature Standard](https://csrc.nist.gov/pubs/fips/186-5/final), section 6.4 (ECDSA signature generation)
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 4.1.3
- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3
- Checkpoint 4 of this workbook (ECDSA verify), whose equation this checkpoint inverts
- Checkpoint 10 of this workbook (find a weak private key), which produces the `d` this checkpoint signs with

## Hints

<details><summary>Hint 1: where to start</summary>

You already have everything you need from checkpoints 3 and 4: `k * G` is the same
double-and-add scalar multiplication as checkpoint 3, and the formula for `s` is checkpoint 4's
verification equation rearranged to solve for `s` instead of checking it.
</details>

<details><summary>Hint 2: the approach</summary>

Compute `R = k * G` by double-and-add. Take `r` as `R`'s x-coordinate, reduced mod `n` (not mod
`p`: the curve's field prime and its order are different numbers). Compute `k`'s modular inverse
mod `n`. Then `s = k_inverse * (z + r * d) mod n`.
</details>

<details><summary>Hint 3: the traps</summary>

- `r` is reduced mod `n`, the curve's order, not mod `p`, the field prime used for point
  coordinates. They are different numbers.
- The modular inverse in the `s` formula is mod `n`, matching `r` and `s` themselves, not mod `p`.
- `k * G` needs double-and-add. A loop that adds `G` to itself `k` times will not finish for the
  large `k` values in the tests.
- `d`, `z` and `k` are each independent hex fields on the input line, in that order after the
  curve name. Don't mix them up.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
sign(curve, d, z, k):
    R = multiply(k, G)          # double-and-add, as in checkpoint 3
    r = R.x mod n
    s = inverse(k, n) * (z + r * d) mod n
    return (r, s)
```
</details>

## Checking your solution

```
./check.sh 11                              run every test
./check.sh 11 -Case 11-R4-d4-p384          one test, showing its full input, expected output and your output
./check.sh 11 -Fresh                       a new set of tests (new random seed)
./check.sh 11 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  The private key can be any value, including the recovered inciden... .    5 / 6   FAILED
      x 11-R4-d4-p384  P-384, d = 4: the value recovered for the real incident in checkpoint 10
          line 1: expected `signature 11-R4-d4-p384 db8e7ab8...876d2fdc...`, got `signature 11-R4-d4-p384 db8e7ab8...8fb51fe0...`
          likely cause: R4 - The private key can be any value, including the recovered incident value d = 4: the formula does not care how small or large d is
          expected values from: cryptography 41.0.7 (OpenSSL): r from scalar multiplication, the signature confirmed by verifying it
          reproduce: python3 -P tools/run_py.py solutions 11 build/cases/11/11-R4-d4-p384.in build/cases/11/11-R4-d4-p384.out
```

## After you pass: why real signing never gives you `k`

This checkpoint hands you `k` so the answer is exact and checkable. A real signer draws it from a
secure random source and never writes it down. Two mistakes with `k`, neither exercised by this
checkpoint's tests, are why:

**Reusing `k` for two different messages leaks `d` directly.** Two signatures `(r, s1)` and
`(r, s2)` with the same `k` (the same `r`, since `r` only depends on `k`) satisfy
`s1 - s2 = k^-1 * (z1 - z2) mod n`, so `k = (z1 - z2) * (s1 - s2)^-1 mod n`, and then
`d = (s1*k - z1) * r^-1 mod n`. This is exactly how Sony's PlayStation 3 signing key leaked in
2010: the group fail0verflow found that Sony's signer used a fixed `k` for every signature
instead of drawing a fresh one each time, and recovered the key from two signatures.

**A `k` that is even slightly less than fully random** (biased, short, or predictable from a weak
random number generator) lets an attacker recover `d` from a handful of real signatures using
lattice methods, without ever seeing `k` directly. This is a different, harder attack than
checkpoint 10's, but it starts from the same place: a key generation process that doesn't do what
it's supposed to.

eMudhra's incident was a weak **key**, not a weak **nonce**, so neither of these applies to it
directly. They're here because both are the same lesson as checkpoint 10 from a different angle:
in ECDSA, every number that is supposed to be unpredictable has to actually be unpredictable, or
the private key stops being private.
