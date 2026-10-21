# 08 · Check a certificate's signature

**Difficulty:** Hard · **Assignment** 8 of 16 · **Check:** `.\check 08`

**Tags**
- *Language:* byte slicing · big integers · modular arithmetic
- *Library:* a SHA-384 implementation
- *Concepts:* tbsCertificate · ECDSA verification · DER's canonical encoding

## Read in the blog first

eMudhra's post doesn't cover this assignment. It builds the link between an issuer's private key
and the certificates it signs, which is what a compromise of a revoked or distrusted
intermediate's key threatens. For background, read RFC 5280 sections 4.1.1.3 ("signatureValue")
and 4.1.2 ("TBSCertificate"): which bytes the issuer signs and where the signature goes. You can
pass using this page alone.

## Source material

- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), sections 4.1.1.3 and 4.1.2
- ITU-T X.690, section 8.1 (why re-encoding DER should give the same bytes, and why slicing the
  original bytes avoids the risk that it doesn't)
- FIPS 186-5, *Digital Signature Standard (DSS)*, section 6.4.2 (the ECDSA verification equation)

## Where this fits

Your `verify` in `ecc/ecdsa.py` (assignment 04) checks an ECDSA signature on a hash, and your
`x509/certificate.py` (assignment 06) finds a certificate's parts with your `asn1/der.py`
(assignment 05). Here, in `x509/signature.py`, you connect them: the message is a slice of the
certificate itself, and checking the signature tells you whether a given issuer signed it. Your
`pki/chain.py` (assignment 09) checks every link of a chain this way. It's also why a compromised
CA key is dangerous: anyone who holds it can make signatures that pass this check.

## The problem

Write a program that checks, for each certificate it reads, whether a given issuer's public key
signed it.

### What the issuer signs

A certificate's `signatureValue` is a signature over `tbsCertificate`'s original DER bytes, as
they appear in the certificate. DER's rules give each value one encoding (DER is canonical),
so re-encoding `tbsCertificate` from its fields should give the same bytes back. One slip, such as a
length written in the long form where DER uses the short form, gives different bytes, and the
signature no longer checks against them.

Slice the bytes out of the certificate instead, from `tbsCertificate`'s first header byte through
its last content byte, tag and length included, and hash that slice.

### The equation

1. Hash `tbsCertificate`'s original bytes (above) with SHA-384, and read the digest as a
   big-endian number. Every certificate in this assignment is P-384, signed `ecdsa-with-SHA384`.
   A P-256 certificate would use SHA-256 instead, which is out of scope here (see Constraints).
2. `signatureValue` is a BIT STRING. Its content, after the unused-bits byte (`0` here), is DER
   again: `SEQUENCE { r INTEGER, s INTEGER }`. Parse it with your DER reader, as in assignment 05,
   to get `r` and `s`.
3. Check `(r, s)` against the hash and the issuer's public key `(x, y)` with the ECDSA
   verification equation from assignment 04:

```
z  = the hash, as a big integer
w  = s^-1 mod n
u1 = z * w mod n
u2 = r * w mod n
(x3, y3) = u1*G + u2*Q          (Q = the issuer's public key point)
valid if x3 mod n == r
```

`n` is the curve's order (its number of points), from the table below. `u1*G` and `u2*Q` are each
a scalar multiplication (your `scalar_multiply` from assignment 03), and one more point addition
adds the two results. Your `verify` in `ecc/ecdsa.py` already does all of this when you pass it
`z`. Use your own code for the check and leave a cryptography library's verify function alone:
writing the equation yourself is the point of this assignment.

### The curve

P-384 only, for this assignment. These are the constants of your `P384` in `ecc/curves.py`
(assignment 03):

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
| `issuer_pubkey <label> <curve> <x> <y>` | Comes right after the `cert` line with the same `label`. The alleged issuer's public key: `curve` is `P-384` in every test here, and `x` and `y` are hexadecimal. |

### Output

For each pair, in input order, write one line:

```
signature <label> valid
signature <label> invalid
```

The checker ignores extra whitespace.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A self-signed certificate (signed by the key it carries), checked against its own public
  key, is `valid`.
- **R2** A certificate checked against the wrong issuer key is `invalid`.
- **R3** A certificate whose signature has one flipped bit, anywhere in `r` or `s`, is `invalid`,
  though the rest of the certificate and the issuer's real key stay the same.
- **R4** Your program slices `tbsCertificate`'s bytes right when the certificate carries real v3
  extensions, which make the structure large enough that its own length needs DER's long form.

## Examples

### Example 1: a valid self-signed certificate (test `08-R1-self-signed-0`)

```
input:   cert s0 3082014c3081d2a003020102020101300a06082a8648ce3d0403033011310f300d06035504030c0653656c662d30301e170d3235303130313030303030305a170d3236303130313030303030305a3011310f300d06035504030c0653656c662d303076301006072a8648ce3d020106052b810400220362000413799bc39cebcabf392d24625ec169db4dc1d3aa4b413fb92fb3450ea24d9ace0432ae1f242748eb41fae6d6fc190625e915239da017393f8f433efd149645fa8ccd3a38f03645dcf76a908f1dca483a724091b507a040f592d569d6be4406f8300a06082a8648ce3d0403030369003066023100a524602bdb5b7950ac3920ae115ff2658d6e8e80feae9bb515a578f13402b4ff7343be542a7d4fef963c797150d33466023100ce248e60dccf8814ce38576a7d62dbcf3c0c62fa5f9f793f3328f6eb5bf40643000bd1398c2b4f49e590832474ae61bd
         issuer_pubkey s0 P-384 13799bc39cebcabf392d24625ec169db4dc1d3aa4b413fb92fb3450ea24d9ace0432ae1f242748eb41fae6d6fc190625 e915239da017393f8f433efd149645fa8ccd3a38f03645dcf76a908f1dca483a724091b507a040f592d569d6be4406f8

output:  signature s0 valid
```

The public key in `issuer_pubkey` is the certificate's own subject key. The input gives it to you
on its own line; assignment 06 covers reading it out of the certificate.

### Example 2: one bit flipped in the signature (test `08-R3-tampered-0`)

```
input:   cert t0 3082014e3081d6a003020102020114300a06082a8648ce3d04030330133111300f06035504030c0854616d7065722d30301e170d3235303130313030303030305a170d3236303130313030303030305a30133111300f06035504030c0854616d7065722d303076301006072a8648ce3d020106052b8104002203620004b7c32496319e08593b60245d1518bccd35f6236109df147af450aba3253237eeb9acedf9664944dcd9b1119a1cd6367532301c3af7cbdc8626374f8ece577d5d4067fbad012a61489fc14b73a8a9dd9365b1abedacd7daef7336b9e95a70b620300a06082a8648ce3d040303036700306402303503532ecae9d7ae31701e2665a92a062b581e1cfeb49f2b3bdcd94241c8cbb0cc85a088a3136ed8ee858bdca1f0789902304843909e09821bcc3a04fd568f14a080fa0aef6605341933fdd5ba128236de33b8652d66260af57cdbcda63c6c58188c
         issuer_pubkey t0 P-384 b7c32496319e08593b60245d1518bccd35f6236109df147af450aba3253237eeb9acedf9664944dcd9b1119a1cd63675 32301c3af7cbdc8626374f8ece577d5d4067fbad012a61489fc14b73a8a9dd9365b1abedacd7daef7336b9e95a70b620

output:  signature t0 invalid
```

Apart from one bit of the signature, the certificate is as its issuer signed it: the subject,
issuer, key and validity match the original, and `issuer_pubkey` holds the real issuer's key.
Flipping the lowest bit of the signature's last byte is enough to make it `invalid`.

## Constraints

- Every certificate here is P-384, signed `ecdsa-with-SHA384`. A P-256 certificate would need
  SHA-256 instead, by RFC 5280's pairing of algorithms. P-256 is out of scope for this
  assignment, which mirrors the P-384 keys of the real eMudhra incident.
- `issuer_pubkey` comes right after the `cert` line it belongs to, with the same label.
- Each case has a 10-second limit.
- There are 10 tests: 3 for R1, 2 for R2, 2 for R3, 2 for R4, and one end-to-end case that mixes
  valid, wrong-key and tampered signatures in one input. Part of the set is random (fresh keys
  each run) and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Both parts you need are fixed-position children of the certificate's top-level SEQUENCE:
`tbsCertificate` is the first and `signatureValue` the third. Your `certificate_node` from
assignment 06 gives you that SEQUENCE. You don't need any of `tbsCertificate`'s own fields this
time, only where it starts and ends.
</details>

<details><summary>Hint 2: the approach</summary>

Parse the certificate as one top-level SEQUENCE. Its first child's whole node, header included,
gives you the bytes to hash: `data[node.start : node.start + node.total_len]` (`Node.encoding`
in the Boilerplate). Its third child is signatureValue: after the unused-bits byte, parse the
content as DER again to get `r` and `s`. Then run assignment 04's verification with the hash of
the sliced bytes as `z`.
</details>

<details><summary>Hint 3: the traps</summary>

- Hash the bytes from the certificate, not a re-encoding of the fields. If your DER writer and
  reader don't round-trip to the same bytes (a length form, most often), you hash the wrong
  bytes, and real certificates fail as well as the hand-made edge cases.
- `signatureValue` is a BIT STRING. Its first content byte is the unused-bits count (assignment
  05), and the DER-encoded `(r, s)` SEQUENCE starts after it.
- `r` and `s` are each a full DER INTEGER: two's complement, and they may have a leading `0x00`
  pad byte (assignment 05's trap again).
- SHA-384's digest has as many bits as P-384's order `n`, so this assignment never needs to cut
  the hash down. Other pairings of curve and hash can need it.
- One flipped bit anywhere in `r` or `s` makes the signature invalid. If your check compares only
  part of a value, or compares lengths instead of values, it can miss that.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
check_signature(cert_bytes, curve, issuer_x, issuer_y):
    cert = certificate_node(cert_bytes)
    tbs_node = cert.children[0]
    tbs_bytes = cert_bytes[tbs_node.start : tbs_node.start + tbs_node.total_len]

    sig_bitstring = cert.children[2]
    _unused, sig_der = decode_bit_string(sig_bitstring.content)
    sig_seq = parse_all(sig_der)[0]
    r = decode_integer(sig_seq.children[0].content)
    s = decode_integer(sig_seq.children[1].content)

    z = int(sha384(tbs_bytes))
    # your verify(curve, (issuer_x, issuer_y), z, r, s) from assignment 04 does the rest:
    w = modinv(s, n)
    u1, u2 = (z * w) % n, (r * w) % n
    (x3, y3) = add_points(scalar_multiply(u1, G), scalar_multiply(u2, (issuer_x, issuer_y)))
    return (x3 % n) == r
```
</details>

## Checking your solution

```
.\check 08                                run every test
.\check 08 -Case 08-R3-tampered-0         one test, showing its full input, expected output and your output
.\check 08 -Fresh                         a new set of tests (new random seed), to confirm on data you haven't seen
.\check 08 -Dispute <id> "why"            set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  The TBS bytes are re-extracted correctly even when the certifica...    0 / 2   FAILED
      x 08-R4-with-extensions  a self-signed CA certificate with a BasicConstraints extension present
          line 1: expected `signature ext1 valid`, got `signature ext1 invalid`
          likely cause: R4 - The TBS bytes are re-extracted correctly even when the certificate has v3 extensions (a non-trivial TBS structure)
          expected values from: cryptography 41.0.7: public_key.verify(signature, tbs_bytes, ec.ECDSA(hashes.SHA384())), independent of this workbook's modular-arithmetic reference
          reproduce: py -P tools/run_py.py solutions 08 build/cases/08/08-R4-with-extensions.in build/cases/08/08-R4-with-extensions.out
```

## After you pass: compare with the post

eMudhra's post has no code for this, so there is no author's version to compare. The reference
`x509/signature.py` splits the work into three functions. `read_signed_data` slices the TBS bytes
and reads `r` and `s`, with `certificate_node` from assignment 06 and the DER decoders from
assignment 05. `tbs_hash` turns the bytes into `z`, and `check_signature` calls `verify` from
`ecc/ecdsa.py` (assignment 04).

Inside `verify`, the reference's `scalar_multiply` (assignment 03) does double-and-add from the
least significant bit. A correct alternative starts from the most significant bit and doubles the
running result before each add. It gives the same answer with the bits in the opposite order.
Compare it with the version you wrote.
