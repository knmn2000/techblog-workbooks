# 11 · Sign a certificate with a recovered key

**Difficulty:** Hard · **Assignment** 11 of 19 · **Check:** `.\check 11`

**Tags**
- *Language:* big integers · modular arithmetic · parsing hex · writing DER
- *Library:* a SHA-384 implementation. Python's built-in `int` handles 384-bit numbers
- *Concepts:* ECDSA signing · DER encoding of a signature · forging a certificate with a stolen CA key

This assignment works only on the workbook's own test data: no real certificate authority, domain
or production system appears in it, and every name is synthetic (`forged.example` and the like). In
code you write yourself, you see what an attacker does once an intermediate key is weak: sign any
hash, then wrap a certificate around a name of their choosing that your own validator from
assignment 09 trusts.

## Source material

- NIST, [FIPS 186-5: Digital Signature Standard](https://csrc.nist.gov/pubs/fips/186-5/final), section 6.4 (ECDSA signature generation)
- SECG, [SEC 1: Elliptic Curve Cryptography](https://www.secg.org/sec1-v2.pdf), section 4.1.3
- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), section 4.1 (the Certificate and signatureValue structures you assemble)
- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3
- Assignment 04 of this workbook (ECDSA verify), whose equation this assignment inverts
- Assignment 09 of this workbook (validate a chain), which checks the forged certificate
- Assignment 10 of this workbook (find a weak private key), which produces the `d` this assignment signs with

## Where this fits

Assignment 10 found a private key `d` from its public key when `d` was small, assignment 04
checked a signature against a public key, and assignment 09 decided whether to trust a chain of
certificates. This assignment joins them. You add signing to your `ecc/ecdsa.py` from assignment
04, next to `verify`, and then use your `sign` and your `validate_chain` from assignment 09 to
forge a certificate and watch your own validator trust it.

Signing is the same arithmetic as verifying, run forwards. It builds on `scalar_multiply` in your
`ecc/curve.py` (assignment 03) and `modinv` in your `ecc/modmath.py` (assignment 01). With `d`, a
few lines produce a signature anyone will accept, on a message that says anything the attacker
likes. Wrap that signature around a certificate body and you have a certificate for a name you do
not control, chaining to a root the world trusts. eMudhra's eight intermediate keys were a risk
from the moment they were weak. Assignments 13 to 16 build the checks that catch a weak key before
it ships, and assignment 19 decides which clients would still accept a forgery today.

## The problem

Write a program that handles two kinds of line. A `sign` line computes an ECDSA signature from a
private key, a message hash and a nonce. A `forge` line signs a certificate body with a recovered
key, assembles the whole certificate, and runs your chain validator on it.

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

### Forging a certificate

A `forge` line gives you a tbsCertificate (the body of a certificate, DER in hex), the weak
private key `d` of an intermediate CA, a nonce `k`, the intermediate's own certificate and a trust
anchor. Produce the full certificate and check it:

1. Hash the tbsCertificate with SHA-384 and read the digest as a big-endian integer. This is `z`,
   the same hashing assignment 08 does for a P-384 certificate. SHA-384's digest is 384 bits, the
   width of P-384's order, so there is nothing to cut.
2. Sign `z` with the weak key and the nonce, using your `sign`. You get `(r, s)`.
3. Encode the signature as DER: `SEQUENCE { r INTEGER, s INTEGER }`. Each INTEGER is big-endian
   two's complement, with a leading `0x00` byte when the first byte's top bit is 1, so the
   value stays positive (assignment 05's rule, now in reverse). Use the shortest encoding: no
   other leading zero bytes, so a value with fewer than 48 bytes gets a shorter INTEGER.
4. Wrap that SEQUENCE in a BIT STRING: a `0x00` unused-bits byte, then the SEQUENCE's bytes.
5. Assemble the certificate as `SEQUENCE { tbsCertificate, signatureAlgorithm, signatureValue }`,
   where `signatureAlgorithm` is the 12 bytes `300a06082a8648ce3d040303` (ecdsa-with-SHA384) and
   `signatureValue` is the BIT STRING from step 4. Pass the tbsCertificate through byte for byte.
6. Validate the chain made of the forged leaf, then the intermediate, against the anchor, with your
   `validate_chain` from assignment 09 and no current time. The intermediate signed the leaf (its
   key is `d`), and the anchor signed the intermediate, so the verdict is `valid`.

The intermediate's key is `d` because the attacker recovered it in assignment 10. That is what
makes the leaf's signature check out under the intermediate's public key, and what makes the whole
chain reach a trusted root.

### DER lengths

Both the SEQUENCE and the BIT STRING need a length. A length below 128 is one byte. A longer one
is `0x80 + the number of length bytes`, then the length itself, big-endian. A tbsCertificate runs
to a few hundred bytes, so the outer certificate's length uses this long form.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Each line is one of:

```
sign <id> <curve> <d> <z> <k>
forge <id> <curve> <d> <k> <tbs> <intermediate> <anchor-x> <anchor-y>
```

A `sign` line:

| Field | Meaning |
|---|---|
| `id` | A label with no spaces. Print it back unchanged. |
| `curve` | `P-256` or `P-384`. |
| `d` | The private key in hex, zero-padded to the curve's field width (64 hex digits for P-256, 96 for P-384). |
| `z` | The message's hash, in hex of the same width as `d`, already an integer in range. |
| `k` | The nonce, in hex of the same width. It is a valid value: `1 <= k <= n - 1`. |

A `forge` line, P-384 only:

| Field | Meaning |
|---|---|
| `id` | A label with no spaces. Print it back unchanged. |
| `curve` | `P-384` in every `forge` test. |
| `d` | The intermediate's weak private key, in hex, zero-padded to 96 digits. |
| `k` | The nonce, in hex, zero-padded to 96 digits. |
| `tbs` | The tbsCertificate to sign, DER in hex. |
| `intermediate` | The intermediate's certificate, DER in hex. The leaf chains up to it. |
| `anchor-x`, `anchor-y` | The trust anchor's public-key coordinates in hex, the same shape assignment 09 reads from an `anchor` line. |

### Output

One line per input, in order. For a `sign` line:

```
signature <id> <r> <s>
```

Write `r` and `s` in lowercase hex, zero-padded to the same width as the input values. For a
`forge` line:

```
forged <id> <certificate> <verdict>
```

`certificate` is the assembled certificate, DER in lowercase hex. `verdict` is `valid` when your
`validate_chain` trusts the forged chain (assignment 09's `trusted`), or `untrusted <reason>`
when it does not, with 09's reason. The checker
ignores extra whitespace.

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
- **R6** A `forge` line produces the certificate's DER and a `valid` verdict: the tbsCertificate
  hashed with SHA-384, signed with the weak key, wrapped with the ecdsa-with-SHA384 algorithm and
  the signature BIT STRING, and trusted by your `validate_chain` from assignment 09.

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

### Example 3: forge a certificate for a synthetic name (test `11-R6-forge-d4`)

```
input:   forge 11-R6-forge-d4 P-384 000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004 51423286a6ecc31f35263b4519a2105c50806f017a1d556cb62c228e40df7c9a8cda80a34b452123d17f6494e8c2d21b 3081e4a00302010202021234300a06082a8648ce3d040303301a3118301606035504030c0f5765616b2049737375696e67204341301e170d3235313233313030303030305a170d3237303130313030303030305a30193117301506035504030c0e666f726765642e6578616d706c653076301006072a8648ce3d020106052b8104002203620004d493c99caa9c3f5cbc24a07a36e04665c79e48c9eb880f6b2935c27193871e19b0299012b3ca47dab26a53c714ba5e8137523f2166f09e964ff34a61bea918c4234c6dd9dd41babf772725e9360b6d9f2a0c32fce382c3749fe4507b279772b7 308201763081fda003020102020102300a06082a8648ce3d040303301b3119301706035504030c105075626c6963205465737420526f6f74301e170d3235313230323030303030305a170d3237303130313030303030305a301a3118301606035504030c0f5765616b2049737375696e672043413076301006072a8648ce3d020106052b8104002203620004138251cd52ac9298c1c8aad977321deb97e709bd0b4ca0aca55dc8ad51dcfc9d1589a1597e3a5120e1efd631c63e1835cacae29869a62e1631e8a28181ab56616dc45d918abc09f3ab0e63cf792aa4dced7387be37bba569549f1c02b270ed67a316301430120603551d130101ff040830060101ff020100300a06082a8648ce3d0403030368003065023000c61e7a97e53a04a90b8d905476fdbddd6ae7848cf14456cf3ffec0b0ec0176942b3425ff982859ab7482b765d5594d023100ebcee8156de3e869e7cf63de0cdf254bec07516594477795d6648e54de504b57425c9dd6cc455aac174e2f06972240b1 c42c12e7ae0e8518cbf648970e10d23fdcb267ba6b64697fbd3b8387850e0a0341f99f94447b13970c7e9b31c58ced98 5c35eec3b00495bcb11367567d3d3fde0868a82bf022b24b402a153a3c09bf2628b83ff6b6e2afbc02c2f941d3f3ccf5

output:  forged 11-R6-forge-d4 3082015d3081e4a00302010202021234300a06082a8648ce3d040303301a3118301606035504030c0f5765616b2049737375696e67204341301e170d3235313233313030303030305a170d3237303130313030303030305a30193117301506035504030c0e666f726765642e6578616d706c653076301006072a8648ce3d020106052b8104002203620004d493c99caa9c3f5cbc24a07a36e04665c79e48c9eb880f6b2935c27193871e19b0299012b3ca47dab26a53c714ba5e8137523f2166f09e964ff34a61bea918c4234c6dd9dd41babf772725e9360b6d9f2a0c32fce382c3749fe4507b279772b7300a06082a8648ce3d04030303680030650230123c84b89af9f476d0dfb71b73c4271f83b4a1fb3ddfb6225e13e81cb1c2057b1fcfcbbd76616ef628ef9263ae022f84023100ac45329ea29247a474f15020ead511a6038e581d950159be8993be1fbeec06a580763d8a0975962dba20203e99bdc3a1 valid
```

The weak key is `d = 4`, the intermediate's own private key. The tbsCertificate names
`forged.example` as its subject. The output certificate is a SEQUENCE header followed by three parts:

| Part | Bytes |
|---|---|
| Certificate SEQUENCE header | `3082015d` (long-form length, 0x15d bytes follow) |
| tbsCertificate | `3081e4...772b7`, the `tbs` field copied through unchanged |
| signatureAlgorithm | `300a06082a8648ce3d040303`, ecdsa-with-SHA384 |
| signatureValue | `0368 00 3065...` : a BIT STRING, the `00` unused-bits byte, then `SEQUENCE { r, s }` |

Both INTEGERs here begin with `0230` and `0231`: `r` is 48 bytes, and `s` needed a leading `0x00`
pad, so it is 49. The verdict is `valid` because your `validate_chain` walks the leaf up to the
intermediate and the intermediate up to the anchor, and every signature checks out.

## Constraints

- `d`, `z` and `k` are well-formed: `1 <= d < n`, `0 <= z < n`, `1 <= k < n`.
- Every `sign` test gives non-zero `r` and `s`. A real signer has to check for zero and draw a new
  `k` if either comes out zero; no test exercises that check.
- Every `forge` test is P-384, signed ecdsa-with-SHA384, with a valid chain to the anchor, so the
  verdict is always `valid`. The intermediate is a CA and the dates cover any time, so validation
  runs with no current time.
- Each case has a 10-second limit. Double-and-add for `k * G` takes well under a second, even for
  the largest `k` in the tests.
- There are 24 tests: the examples above, both curves, the nonce values described in R3, several
  small and large private keys including the incident's, the hash boundaries in R5, and three
  forged certificates (two for R6 and one end-to-end).

## Hints

<details><summary>Hint 1: where to start</summary>

You already have the pieces from assignments 01 to 09. `k * G` is your `scalar_multiply` from
assignment 03, the formula for `s` is assignment 04's verification equation rearranged, and your
`validate_chain` from assignment 09 gives the `forge` verdict. Get `sign` working first against the
`sign` cases, then build the `forge` handler on top of it.
</details>

<details><summary>Hint 2: the approach</summary>

For `sign`: compute `R = k * G` with `scalar_multiply`, take `r` as `R`'s x-coordinate reduced mod
`n`, compute `k`'s modular inverse mod `n` with your `modinv`, then `s = k_inverse * (z + r * d)
mod n`.

For `forge`: hash the tbsCertificate with SHA-384 to get `z`, call `sign(curve, d, z, k)`, DER-encode
`r` and `s` into `SEQUENCE { r INTEGER, s INTEGER }`, prepend the `0x00` unused-bits byte and wrap
that in a BIT STRING, then build `SEQUENCE { tbs, signatureAlgorithm, signatureValue }`. Feed the
forged certificate and the intermediate to `validate_chain` with the anchor and no current time.
</details>

<details><summary>Hint 3: the traps</summary>

- Reduce `r` mod `n`, the curve's order. The field prime `p` of the point coordinates is a
  different number, and the modular inverse in the `s` formula is mod `n` as well.
- `k * G` needs double-and-add. A loop that adds `G` to itself `k` times won't finish for the
  large `k` values in the tests.
- Hash the tbsCertificate the line gives you, not the whole certificate you build around it.
- A DER INTEGER for `r` or `s` gets a leading `0x00` byte when its first byte's top bit is 1, so
  the number reads as positive. Leaving it out, or adding it when the top bit is 0, changes the
  bytes and the certificate.
- The BIT STRING's first content byte is the unused-bits count, `0x00` here. Then come the
  SEQUENCE's bytes.
- Keep `r` before `s` in the signature SEQUENCE.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
sign(curve, d, z, k):
    R = multiply(k, G)          # double-and-add, as in assignment 03
    r = R.x mod n
    s = inverse(k, n) * (z + r * d) mod n
    return (r, s)

forge(curve, d, k, tbs, intermediate, anchor):
    z = int(sha384(tbs))
    r, s = sign(curve, d, z, k)
    sig = der_sequence(der_integer(r) + der_integer(s))
    signature_value = der_bit_string(0x00 + sig)
    cert = der_sequence(tbs + ecdsa_with_sha384 + signature_value)
    verdict = validate_chain([cert, intermediate], [anchor])   # no current time
    return cert, verdict
```
</details>

## Checking your solution

```
.\check 11                              run every test
.\check 11 -Case 11-R6-forge-d4         one test, showing its full input, expected output and your output
.\check 11 -Fresh                       a new set of tests (new random seed)
.\check 11 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R6  A forged certificate signed with the weak key, assembled into DER... .    0 / 2   FAILED
      x 11-R6-forge-d4  forge forged.example with the incident key d = 4, then validate the chain
          line 1: expected `forged 11-R6-forge-d4 3082015d3081e4a003020102...`, got `forged 11-R6-forge-d4 3082015c3081e4a003020102...`
          likely cause: R6 - A forged certificate signed with the weak key, assembled into DER, is accepted by your own validate_chain from assignment 09
          expected values from: cryptography 41.0.7 and openssl verify: the forged certificate assembled independently and accepted by both
          reproduce: py -P tools/run_py.py solutions 11 build/cases/11/11-R6-forge-d4.in build/cases/11/11-R6-forge-d4.out
```

## After you pass: a certificate your own validator trusts

Your code recovered `d` (assignment 10), signed with it (this assignment), and wrapped a
certificate for `forged.example` that chains to a root your `validate_chain` already trusted. The
same steps forge a certificate for any name. The only thing the attacker needed was a CA private
key small enough to recover, which eight of eMudhra's intermediates were.

No public source reports evidence that anyone recovered or used eMudhra's keys before disclosure,
and none shows that no one did. Scott Helme demonstrated the attack rather than finding it in the
wild: he built a forged chain with a recovered key and served it from a local test server, where
curl with default settings and several other clients accepted it. Assignments 13 to 16 build the
checks that stop a weak key from shipping (a key linter, a ceremony checker, a blocklist and a
full PKI audit), and assignment 19 works out which clients would still accept a forgery today,
given their revocation, blocklist, bundle and Certificate Transparency settings.

### Why real signing never gives you `k`

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
harder, and it starts from the same place: a secret number that is less random than it should be.

eMudhra's incident involved a weak key, and both of these mistakes concern the nonce, so
neither applies to it. Both teach assignment 10's lesson from another angle: in ECDSA,
every number that should be unpredictable has to be unpredictable, or the private key stops
being private.
