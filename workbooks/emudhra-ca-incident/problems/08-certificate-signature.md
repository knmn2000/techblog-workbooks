# 08 · Check a certificate's signature

**Difficulty:** Hard · **Checkpoint** 8 of 16 · **Check:** `./check.sh 08`

**Tags**
- *Language:* byte slicing · big integers · modular arithmetic
- *Library:* a SHA-384 implementation
- *Concepts:* tbsCertificate · ECDSA verification · DER's canonical encoding

## Read in the blog first

This checkpoint is prerequisite material, not drawn from eMudhra's post: it teaches the
mechanism that connects an issuer's private key to a certificate it signed, which is what a
revoked or distrusted intermediate's key compromise actually threatens. Read RFC 5280 section
4.1.1.3 ("signatureValue") and 4.1.2 ("TBSCertificate") for which bytes get signed and how the
signature is stored. This page is complete on its own after that.

## Where this fits

Checkpoint 04 taught you to verify an ECDSA signature given a message, a signature and a public
key. Checkpoint 06 taught you to read a certificate's fields. This checkpoint connects them: the
"message" is a specific slice of the certificate itself, and checking it tells you whether a
certificate was really signed by a given issuer - the question at the heart of checkpoint 09's
chain validation, and the reason a compromised CA key is dangerous: anyone holding it can produce
a signature that checks out here.

## The problem

Write a program that checks, for each certificate it's given, whether it was really signed by a
specific alleged issuer's public key.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p08_certificate_signature.py` is a comment and an
empty program: reading the input and writing the output are yours. To start from working
input/output code instead, copy `starters/boilerplate/p08_certificate_signature.py` over it, or
pick Boilerplate in the book's editor. The boilerplate reads the input and writes the output; you
fill in `check_signature()`.

### What actually gets signed

A certificate's `signatureValue` is a signature over `tbsCertificate`'s **exact original DER
bytes** - not a re-encoding of its fields, not a recomputed version of the same structure. DER
is supposed to be canonical (one value, one encoding), so re-encoding tbsCertificate yourself
*should* give the same bytes back - but it's an easy way to introduce a subtle bug (get a length
byte's short/long form wrong, for instance) and sign or verify against bytes that are not quite
the ones that were actually used. The safe approach, and the one this checkpoint asks for: slice
the exact bytes out of the original certificate (its first header byte through its last content
byte, tag and length included) and hash **that**.

### The equation

1. Find `tbsCertificate`'s exact original bytes (as above) and hash them with **SHA-384** (this
   checkpoint only covers P-384 certificates, signed `ecdsa-with-SHA384`; a P-256 certificate
   would use SHA-256 instead - out of scope here, see Constraints).
2. `signatureValue` is a BIT STRING whose content (after the unused-bits byte, always `0` here)
   is itself DER: `SEQUENCE { r INTEGER, s INTEGER }`. Parse that inner structure the way
   checkpoint 05 parses anything, to get `r` and `s`.
3. Check `(r, s)` against the hash and the alleged issuer's public key `(x, y)`, using the same
   ECDSA verification equation as checkpoint 04:

```
z  = the hash, as a big integer
w  = s^-1 mod n
u1 = z * w mod n
u2 = r * w mod n
(x3, y3) = u1*G + u2*Q          (Q = the issuer's public key point)
valid if x3 mod n == r
```

`n` is the curve's order (its number of points), from the table below. `u1*G` and `u2*Q` are
each a full scalar multiplication (repeated point addition, as in checkpoint 03), and the two
results are added together with one more point addition. Use the point add/doubling formulas
from checkpoints 2 and 3's pages (the same style as checkpoint 10's reference uses) - don't reach
for a cryptography library's own verify function; implementing the equation yourself is the
point of this checkpoint.

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

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains pairs of lines, each pair describing one check:

| Line | Meaning |
|---|---|
| `cert <label> <hex>` | The certificate to check. |
| `issuer_pubkey <label> <curve> <x> <y>` | Immediately follows the `cert` line with the same `label`. The alleged issuer's public key: `curve` is `P-384` in every test here, `x` and `y` are hexadecimal. |

### Output

For each pair, in input order, write one line:

```
signature <label> valid
signature <label> invalid
```

The checker ignores extra whitespace.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** A genuinely self-signed certificate (the issuer's key is the same key that signed it),
  verified against its own public key, is `valid`.
- **R2** A certificate verified against the wrong issuer key is `invalid`.
- **R3** A certificate whose signature bytes have been tampered with - one flipped bit, anywhere
  in `r` or `s` - is `invalid`, even though every other byte of the certificate (including the
  issuer's real key) is untouched.
- **R4** `tbsCertificate`'s bytes are re-extracted correctly even when the certificate carries
  real v3 extensions, which make the structure large enough that its own length needs the DER
  long form - not just a toy 3-field structure.

## Examples

### Example 1: a valid self-signed certificate (test `08-R1-self-signed-0`)

```
input:   cert s0 3082014c3081d2a003020102020101300a06082a8648ce3d0403033011310f300d06035504030c0653656c662d30301e170d3235303130313030303030305a170d3236303130313030303030305a3011310f300d06035504030c0653656c662d303076301006072a8648ce3d020106052b810400220362000413799bc39cebcabf392d24625ec169db4dc1d3aa4b413fb92fb3450ea24d9ace0432ae1f242748eb41fae6d6fc190625e915239da017393f8f433efd149645fa8ccd3a38f03645dcf76a908f1dca483a724091b507a040f592d569d6be4406f8300a06082a8648ce3d0403030369003066023100a524602bdb5b7950ac3920ae115ff2658d6e8e80feae9bb515a578f13402b4ff7343be542a7d4fef963c797150d33466023100ce248e60dccf8814ce38576a7d62dbcf3c0c62fa5f9f793f3328f6eb5bf40643000bd1398c2b4f49e590832474ae61bd
         issuer_pubkey s0 P-384 13799bc39cebcabf392d24625ec169db4dc1d3aa4b413fb92fb3450ea24d9ace0432ae1f242748eb41fae6d6fc190625 e915239da017393f8f433efd149645fa8ccd3a38f03645dcf76a908f1dca483a724091b507a040f592d569d6be4406f8

output:  signature s0 valid
```

The public key in `issuer_pubkey` is exactly the certificate's own subject key - checked here
directly as input, not re-extracted from the certificate (checkpoint 06 already covers reading
it out).

### Example 2: one bit flipped in the signature (test `08-R3-tampered-0`)

```
input:   cert t0 3082014e3081d6a003020102020114300a06082a8648ce3d04030330133111300f06035504030c0854616d7065722d30301e170d3235303130313030303030305a170d3236303130313030303030305a30133111300f06035504030c0854616d7065722d303076301006072a8648ce3d020106052b8104002203620004b7c32496319e08593b60245d1518bccd35f6236109df147af450aba3253237eeb9acedf9664944dcd9b1119a1cd6367532301c3af7cbdc8626374f8ece577d5d4067fbad012a61489fc14b73a8a9dd9365b1abedacd7daef7336b9e95a70b620300a06082a8648ce3d040303036700306402303503532ecae9d7ae31701e2665a92a062b581e1cfeb49f2b3bdcd94241c8cbb0cc85a088a3136ed8ee858bdca1f0789902304843909e09821bcc3a04fd568f14a080fa0aef6605341933fdd5ba128236de33b8652d66260af57cdbcda63c6c58188c
         issuer_pubkey t0 P-384 b7c32496319e08593b60245d1518bccd35f6236109df147af450aba3253237eeb9acedf9664944dcd9b1119a1cd63675 32301c3af7cbdc8626374f8ece577d5d4067fbad012a61489fc14b73a8a9dd9365b1abedacd7daef7336b9e95a70b620

output:  signature t0 invalid
```

The certificate is otherwise exactly as it was signed - subject, issuer, key, validity, all
untouched - and the issuer's public key given here is the real one. Only the lowest bit of the
signature's very last byte has been flipped, and that alone is enough to make it `invalid`.

## Constraints

- Every certificate here is P-384, signed `ecdsa-with-SHA384`. A P-256 certificate would need
  SHA-256 instead (per RFC 5280's algorithm pairing) - out of scope for this checkpoint, which
  mirrors the real eMudhra incident's P-384 keys specifically.
- `issuer_pubkey` always immediately follows the `cert` line it belongs to, sharing the same
  label.
- There are 10 tests: 3 for R1, 2 for R2, 2 for R3, 2 for R4, and one end-to-end case mixing
  valid, wrong-key and tampered signatures in a single input. Part of the set is random (fresh
  keys each run) and changes with `-Fresh`.

## Source material

- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), sections 4.1.1.3 and 4.1.2
- ITU-T X.690, section 8.1 (why re-encoding DER should be a no-op, and why slicing the original
  bytes sidesteps the risk of it not being one)
- FIPS 186-5, *Digital Signature Standard (DSS)*, section 6.4.2 (the ECDSA verification equation)

## Hints

<details><summary>Hint 1: where to start</summary>

Everything you need to find is a fixed-position child of the certificate's top-level SEQUENCE:
`tbsCertificate` is the first child, `signatureValue` is the third. You don't need to read any of
`tbsCertificate`'s own fields this time - just its outer boundaries.
</details>

<details><summary>Hint 2: the approach</summary>

Parse the certificate as one top-level SEQUENCE. Its first child's node (not its content - the
whole node, header included) gives you the exact bytes to hash: `data[node.start : node.start +
node.total_len]`. Its third child is signatureValue; after stripping the unused-bits byte, parse
that content as DER again to get `r` and `s`. Then it's exactly checkpoint 04's verification
equation, with the hash of those sliced bytes as the message.
</details>

<details><summary>Hint 3: the traps</summary>

- Hash the *bytes*, not a re-encoding of the fields. If your DER writer and reader don't
  round-trip identically (a length-form choice, most commonly), you'll hash the wrong thing and
  every real certificate will fail, not just the hand-crafted edge cases.
- `signatureValue` is a BIT STRING. Its first content byte is the unused-bits count
  (checkpoint 05), not part of the DER-encoded `(r, s)` SEQUENCE.
- `r` and `s` are each a full DER INTEGER - two's complement, possibly with a leading `0x00` pad
  byte (checkpoint 05's trap again).
- SHA-384's digest is exactly as many bits as P-384's order `n`, so this checkpoint never needs
  to truncate the hash. That's not true of every curve/hash pairing in general, just this one.
- A single flipped bit anywhere in `r` or `s` should invalidate the signature. If your
  verification only checks part of the value, or compares by length instead of by value, you can
  miss this.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
check_signature(cert_bytes, curve, issuer_x, issuer_y):
    cert = parse_top_level_sequence(cert_bytes)
    tbs_node = cert.children[0]
    tbs_bytes = cert_bytes[tbs_node.start : tbs_node.start + tbs_node.total_len]

    sig_bitstring = cert.children[2]
    _unused, sig_der = split_bit_string(sig_bitstring.content)
    sig_seq = parse_top_level_sequence(sig_der)
    r = decode_integer(sig_seq.children[0])
    s = decode_integer(sig_seq.children[1])

    z = int(sha384(tbs_bytes))
    w = modinv(s, n)
    u1, u2 = (z * w) % n, (r * w) % n
    (x3, y3) = add(scalar_mult(u1, G), scalar_mult(u2, (issuer_x, issuer_y)))
    return (x3 % n) == r
```
</details>

## Checking your solution

```
./check.sh 08                                run every test
./check.sh 08 -Case 08-R3-tampered-0         one test, showing its full input, expected output and your output
./check.sh 08 -Fresh                         a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 08 -Dispute <id> "why"            set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  The TBS bytes are re-extracted correctly even when the certifica...    0 / 2   FAILED
      x 08-R4-with-extensions  a self-signed CA certificate with a BasicConstraints extension present
          line 1: expected `signature ext1 valid`, got `signature ext1 invalid`
          likely cause: R4 - The TBS bytes are re-extracted correctly even when the certificate has v3 extensions (a non-trivial TBS structure)
          expected values from: cryptography 41.0.7: public_key.verify(signature, tbs_bytes, ec.ECDSA(hashes.SHA384())), independent of this workbook's modular-arithmetic reference
          reproduce: python3 -P tools/run_py.py solutions 08 build/cases/08/08-R4-with-extensions.in build/cases/08/08-R4-with-extensions.out
```

## After you pass: compare with the post

The post contains no code for this (it's prerequisite material, not drawn from the post), so
there is no author's version to compare. The reference solution is in `_spoilers/reference/`: it
reuses `common/certlib.py`'s `parse_certificate` (for `tbs_bytes`, `sig_r`, `sig_s`) and
`verify_ecdsa_sha384`, its own self-contained copy of checkpoint 04's verification equation.

**Something to look for:** the reference's `scalar_mult` does double-and-add starting from the
least significant bit. A correct alternative starts from the most significant bit and doubles
the running result before adding instead of after - same answer, opposite bit order. Compare it
with whatever you wrote.
