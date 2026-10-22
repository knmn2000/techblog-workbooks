# 18 · Verify a revocation list's signature

**Difficulty:** Medium · **Assignment** 18 of 19 · **Check:** `.\check 18`

**Tags**
- *Language:* byte slicing · dictionaries and sets · state that lasts across input lines
- *Library:* a SHA-384 implementation
- *Concepts:* certificate revocation lists (CRLs) · optional DER fields · signature checks after signing · halting on a failure

## Read in the blog first

This page is complete on its own. The background for this assignment comes from Mozilla's
Bugzilla. In [bug 2083449, comment 11](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449#c11),
eMudhra says the weaker keys were used by mistake to make the certificate requests, and that its
CRLs "were signed with the original private keys". Those signatures failed, and "they were
resigned with flawed keys". eMudhra ties this to
[bug 1970728](https://bugzilla.mozilla.org/show_bug.cgi?id=1970728) from June 2025, where six
CRLs of the same six TLS intermediates carried invalid ECDSA signatures.

Dennis Jackson of Mozilla questions the link. In
[comment 5](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449#c5), he cites an Internet
Archive snapshot that shows the six P-384 CRLs failing verification since May 23, 2025. eMudhra
dated the faulty CRLs to May 29, the day it created the A-1 certificates. Jackson writes that if
the snapshot is accurate, it suggests the mismatch is unrelated to creating the A-1 series. This
assignment doesn't settle the question. It builds the check that flags a CRL whose signature
fails, and one rule for what a CA or a client does next.

## Source material

- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), section 5.1 (the CRL's fields) and section 5.1.2.1 (the optional version)
- Mozilla, [Bugzilla bug 1970728](https://bugzilla.mozilla.org/show_bug.cgi?id=1970728), "eMudhra: Invalid CRL signatures". In comment 2, eMudhra lists "automated post-signing signature validation checks in CRL publishing steps" among its fixes.
- Mozilla, [Bugzilla bug 2083449](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449), comments 5 and 11 (above) and comment 30, where Chrome's root program asks "why did eMudhra simply re-sign the CRLs with that second key rather than halting operations"
- `docs/what-we-know.md`, section "Whether the CRL problem shares the cause"
- Assignment 08 (`problems/08-certificate-signature.md`): the signature check this assignment reuses

## Where this fits

You can do this assignment any time after assignment 13. Your `x509/signature.py` from assignment
08 checks a certificate's signature, and a CRL carries its signature the same way, so your
`read_signed_data` and `check_signature` work on a CRL without a change. Your `lint_key` from
assignment 13 adds the weak-key check.

The new file is `pki/crl.py`. It reads the CRL's issuer with your `read_name_cn` from assignment 06
and keeps, for each issuer, its published key and whether its lists are halted. No later
assignment uses it.

## The problem

Write a program that reads issuers' public keys and their CRLs in order, and gives each CRL a
verdict: `ok`, or `halt` with a reason.

### What a CRL is

A certificate revocation list (CRL) is a list of revoked certificate serial numbers that a CA signs
and publishes. A client that uses the list first checks its signature under the issuer's public
key, the key in the issuer's certificate. RFC 5280 section 5.1 defines it as three fields, the same
shape as a certificate:

```
CertificateList  ::= SEQUENCE { tbsCertList, signatureAlgorithm, signatureValue BIT STRING }
TBSCertList      ::= SEQUENCE {
    version              INTEGER OPTIONAL,      v2 CRLs have it (value 1), v1 CRLs leave it out
    signature            AlgorithmIdentifier,
    issuer               Name,
    thisUpdate           Time,                  UTCTime or GeneralizedTime
    nextUpdate           Time OPTIONAL,
    revokedCertificates  SEQUENCE OF ... OPTIONAL,
    crlExtensions        [0] EXPLICIT ... OPTIONAL }
```

Your program reads only the issuer, the signed bytes and the signature. It doesn't need the dates
or the revoked serials.

### What the issuer signs

The CA signs `tbsCertList`'s original DER bytes, header included, as assignment 08's issuer signs
`tbsCertificate`. Slice them out of the CRL, hash them with SHA-384, and read `r` and `s` from the
`signatureValue` BIT STRING after its unused-bits byte. Every CRL here is P-384, signed
`ecdsa-with-SHA384`, so your `check_signature` from assignment 08 does the whole check.

A CRL with 300 entries has a `tbsCertList` over 6,000 bytes, whose length takes DER's long form
(`82` and two length bytes). Slicing the original bytes handles every length form.

### Where the issuer is

The issuer comes right after `signature`, so its index depends on whether `version` is there:

| CRL | Fields of `tbsCertList`, in order | Issuer's position |
|---|---|---|
| v2 | `version`, `signature`, `issuer`, ... | third (index 2) |
| v1 | `signature`, `issuer`, ... | second (index 1) |

Tell them apart by the first field's tag: `version` is an INTEGER and `signature` is a SEQUENCE.
Compare the node's tag with `der.INTEGER` (2) and `der.SEQUENCE` (16); `02` and `30` are the
first bytes of each field, which include the constructed bit. The certificate's version from assignment 06 is a `[0]` field, so the version
skip in your `tbs_fields` doesn't apply here.

The issuer is a `Name`. Its commonName (OID `2.5.4.3`) is the text the `key` lines use, and your
`read_name_cn` reads it. A Name can hold other attributes (country, organization) before the
commonName.

### The four rules

For each CRL, find its issuer and apply these rules in order. The first rule that applies gives
the verdict.

| Rule | When | Verdict | The issuer afterwards |
|---|---|---|---|
| 1 | The issuer is halted | `halt issuer-halted` | stays halted |
| 2 | The signature doesn't verify under the issuer's published key | `halt signature-failed` | halted |
| 3 | The signature verifies, and your `lint_key` from assignment 13, with an empty blocklist, has a finding for the published key | `halt weak-key` | halted |
| 4 | None of the above | `ok` | unchanged |

Rule 1 runs before the signature check: a halted issuer's CRL gets `halt issuer-halted` even when
its signature verifies. Only a `key` line that gives the issuer a different key releases it.

Rule 3 exists because a weak key's private value is easy to find (assignment 10). With the private
key `d = 4`, anyone can sign a CRL that verifies, so a valid signature under that key says nothing
about who made the list.

The halt is this workbook's model of a detection rule: after a failed check, the checker refuses
the issuer's lists, and a list the CA signs again afterwards doesn't count until the published key
changes. The model doesn't describe how eMudhra or any other CA runs its process.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains two kinds of lines:

| Line | Meaning |
|---|---|
| `key <issuer> <curve> <x> <y>` | The public key in the issuer's certificate. `issuer` is the issuer's commonName, a word with no spaces. `curve` is `P-384`. `x` and `y` are lowercase hexadecimal, 96 digits each. The key replaces the issuer's previous one. If the issuer is new, or the key differs from its previous key, the issuer is no longer halted. A `key` line that repeats the issuer's current key changes nothing. |
| `crl <label> <hex>` | A DER CRL, as lowercase hexadecimal. `label` is a word with no spaces. The issuer is the commonName in the CRL's `issuer` field, and a `key` line for that issuer comes earlier in the input. |

### Output

For each `crl` line, in input order, write one line:

```
crl <label> ok
crl <label> halt signature-failed
crl <label> halt weak-key
crl <label> halt issuer-halted
```

Copy `<label>` from the input unchanged. The checker ignores extra whitespace.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A CRL that the issuer's published key signed, where that key is strong, is `ok`. This
  includes CRLs with 0, 2, 3 and 300 revoked entries, so `tbsCertList`'s length takes the short form
  and the long forms `81` and `82`.
- **R2** A CRL whose signature doesn't verify under the issuer's published key is
  `halt signature-failed`: signed by another key, one bit flipped in `r` or in `s`, or a revoked
  serial or the `thisUpdate` date changed after signing. This holds when the published key is
  weak too, because rule 2 runs before rule 3.
- **R3** A CRL that verifies under a published key whose private value `d` is at most 4096 is
  `halt weak-key`. With `d = 4097` it is `ok`.
- **R4** After a halt, every CRL of that issuer is `halt issuer-halted`, whatever its signature,
  until a `key` line gives the issuer a different key. A `key` line with the same key keeps the
  halt, and a halt of one issuer leaves other issuers alone.
- **R5** Your program reads the issuer right in every shape of CRL: v1 without a version, v2 with
  `crlExtensions` and entry extensions, `thisUpdate` as a GeneralizedTime, and an issuer Name with
  a country and an organization before a 39-character commonName.
- **E2E** Two issuers, a weak key, failures, a replayed CRL and a key change in one input, and a
  random input that changes with `-Fresh`.

## Examples

### Example 1: a good CRL, a tampered copy, then the good CRL again (test `18-R4-fail-then-replay`)

```
input:   key Synthetic-CA-A P-384 3843033659c8405b80ef2255c98a3a9e217ba4d001f0ccb86cb166d2b59a29d4a3006c0a1712e132b4ae94ba96769c19 089129a40af845dca7a22254ec43fe797f25f061b8640254a88dd63d27a6b87e2cb4506945b506863e3c81c82ebc3074
         crl a1 3081c03048020101300a06082a8648ce3d04030330193117301506035504030c0e53796e7468657469632d43412d41170d3236303530313030303030305a170d3236303530383030303030305a300a06082a8648ce3d0403030368003065023100a5837c9bc7c4d36a911623023062540fa8341f3c2d7e687a3faf98d316ac1af514cb1c2e8dcd8d96e777bf0e65e98ab50230274fbcfe1ae14dddfb6680521cb7be57d9250e0bc87c5507140f4751e93cbb528833ec27c3c537871fb2b443a5fb7d0c
         crl a2 3081c03048020101300a06082a8648ce3d04030330193117301506035504030c0e53796e7468657469632d43412d41170d3236303530313030303030305a170d3236303530383030303030305a300a06082a8648ce3d0403030368003065023100a5837c9bc7c4d36a911623023062540fa8341f3c2d7e687a3faf98d316ac1af514cb1c2e8dcd8d96e777bf0e65e98ab50230274fbcfe1ae14dddfb6680521cb7be57d9250e0bc87c5507140f4751e93cbb528833ec27c3c537871fb2b443a5fb7d0d
         crl a3 3081c03048020101300a06082a8648ce3d04030330193117301506035504030c0e53796e7468657469632d43412d41170d3236303530313030303030305a170d3236303530383030303030305a300a06082a8648ce3d0403030368003065023100a5837c9bc7c4d36a911623023062540fa8341f3c2d7e687a3faf98d316ac1af514cb1c2e8dcd8d96e777bf0e65e98ab50230274fbcfe1ae14dddfb6680521cb7be57d9250e0bc87c5507140f4751e93cbb528833ec27c3c537871fb2b443a5fb7d0c

output:  crl a1 ok
         crl a2 halt signature-failed
         crl a3 halt issuer-halted
```

`a1` is 195 bytes, and its fields start like this:

| Bytes | Field | Meaning |
|---|---|---|
| `30 81 c0` | CertificateList | a SEQUENCE of 192 (`c0`) content bytes, length in the one-byte long form |
| `30 48` | tbsCertList | a SEQUENCE of 72 bytes: the signed part is these 74 bytes, header included |
| `02 01 01` | version | INTEGER 1, which means v2, so the issuer is the third field |
| `30 0a 06 08 2a8648ce3d040303` | signature | AlgorithmIdentifier `ecdsa-with-SHA384` |
| `30 19 31 17 30 15 06 03 550403 0c 0e 5379...2d41` | issuer | a Name whose commonName is the 14 bytes of `Synthetic-CA-A` |
| `17 0d ...` and `17 0d ...` | thisUpdate, nextUpdate | UTCTime `260501000000Z` and `260508000000Z` |
| `30 0a ...` | signatureAlgorithm | the same AlgorithmIdentifier again |
| `03 68 00 30 65 ...` | signatureValue | a BIT STRING: the unused-bits byte `00`, then `SEQUENCE { r, s }` |

`a2` is `a1` with the last hex digit changed from `c` to `d`, one bit of `s`, so its signature
fails and the issuer is halted. `a3` is `a1` again, and its signature verifies on its own. Rule 1
gives it `halt issuer-halted`, because `a2` halted the issuer and no `key` line has changed the
key since.

### Example 2: a signature that verifies under a weak key (test `18-R3-weak-d4`)

```
input:   key Synthetic-CA-B P-384 138251cd52ac9298c1c8aad977321deb97e709bd0b4ca0aca55dc8ad51dcfc9d1589a1597e3a5120e1efd631c63e1835 cacae29869a62e1631e8a28181ab56616dc45d918abc09f3ab0e63cf792aa4dced7387be37bba569549f1c02b270ed67
         crl d4 3081bf3048020101300a06082a8648ce3d04030330193117301506035504030c0e53796e7468657469632d43412d42170d3236303530313030303030305a170d3236303530383030303030305a300a06082a8648ce3d040303036700306402300d9644165972519fe0e3621f984ee092fb56d96eee92dc9f554555b86f37bc909555a686e632c2b0add53c8c0cdd882302302573ce0795525b41b123b47af00245b1118a585323e28b1ac5639bb15d69a54013472fc77408b25d642e8367e115ed9d

output:  crl d4 halt weak-key
```

The published key is `4*G` on P-384, the same point as assignment 10's example, and the CRL's
signature is correct under it. Your `lint_key` finds `d = 4` in four steps, so rule 3 halts the
issuer.

### Example 3: a failure, then a list signed by the published weak key (test `18-R4-resign-with-weak-key`)

```
input:   key Synthetic-CA-B P-384 138251cd52ac9298c1c8aad977321deb97e709bd0b4ca0aca55dc8ad51dcfc9d1589a1597e3a5120e1efd631c63e1835 cacae29869a62e1631e8a28181ab56616dc45d918abc09f3ab0e63cf792aa4dced7387be37bba569549f1c02b270ed67
         crl c1 3081c03048020101300a06082a8648ce3d04030330193117301506035504030c0e53796e7468657469632d43412d42170d3236303530313030303030305a170d3236303530383030303030305a300a06082a8648ce3d040303036800306502301e9956bd5562d27fb9cd4b67b922ee36ff38cd66fc16d6ad7cddbe9d7460b9b4c740930e5a6b4e4b31d27296d8b081db023100edeb2a95cfd14a8290477edd58a169a1b1441e183140c1879d0a8865a9bcabbe58da5c1b791e30bbd8e8cf47ef580133
         crl c2 3081c03048020101300a06082a8648ce3d04030330193117301506035504030c0e53796e7468657469632d43412d42170d3236303530313030303030305a170d3236303530383030303030305a300a06082a8648ce3d0403030368003065023100e33175531f733f837740502ccaa3cf555229039cf063ea71ab0ea4bc0f205a5dbc14c124e0b1affdefc78bb180a1e5de02300bd21c17080d506b87ee382b47738c73d6655790e0e804ac9474cc591fd7a53fdb71756dd625d370db24ebc88c3ce051

output:  crl c1 halt signature-failed
         crl c2 halt issuer-halted
```

The published key is the weak key of Example 2. This case has the shape of the sequence eMudhra
describes in comment 11, with `d = 4` in place of a real weak key:

| Line | Signed by | Verdict | Why |
|---|---|---|---|
| `c1` | a strong key that the certificate doesn't publish | `halt signature-failed` | it doesn't verify under `4*G`, and the issuer is now halted |
| `c2` | the published weak key | `halt issuer-halted` | rule 1 applies before your program checks the signature or the key |

Without rule 1, `c2` would get `halt weak-key`. Without rules 1 and 3, it would get `ok`, and the
re-signed list would pass. In test `18-R4-resign-with-published-key` the published key is strong,
and only rule 1 stops the second CRL.

## Constraints

- Every key is a point on P-384, and every CRL is P-384, signed `ecdsa-with-SHA384`. A P-256 CRL
  would need SHA-256 and is out of scope, as in assignment 08.
- Every CRL is well-formed DER with three top-level fields, and its issuer Name has one
  commonName. A tampered CRL has the same lengths as the original, so it still parses.
- A `key` line for a CRL's issuer comes before the CRL. Every key is on P-384, so the only finding
  `lint_key` can have here is `weak`, and it counts for rule 3 whichever sign the key has.
- An input has at most 4 `key` lines and at most 6 `crl` lines, and at most 3 of the CRLs get
  `ok`. A hex line is at most about 17,000 characters (the CRL with 300 entries).
- Each case has a 10-second limit. With the reference's arithmetic, one P-384 signature check
  takes about 0.1 s and `lint_key` on a strong key about 0.3 s, so a program that lints the key
  on every CRL that verifies finishes inside it.
- There are 29 tests: 5 for R1, 6 for R2, 5 for R3, 7 for R4, 4 for R5 and 2 end-to-end cases.
  Part of the set is random (fresh keys and signatures each run) and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

A CRL has the same three top-level fields as a certificate. Before you write any parsing, call
your `read_signed_data` from assignment 08 on `a1` from Example 1, and check the result with
`check_signature` under the `key` line's point. The new code is the issuer and the state.
</details>

<details><summary>Hint 2: the approach</summary>

`read_crl` parses the CRL with `certificate_node` from assignment 06, takes the children of its
first field (`tbsCertList`), drops the first child if it is an INTEGER, and reads the commonName of
the field after `signature` with `read_name_cn`. It returns that name and the result of
`read_signed_data`.

`CrlWatch` keeps a dictionary from issuer name to (curve, key) and a set of halted issuers.
`set_key` stores the key and removes the issuer from the set when the key differs from the stored
one. `check` applies the four rules in order and adds the issuer to the set on a halt.
</details>

<details><summary>Hint 3: the traps</summary>

- `version` is optional, and it moves the issuer. A v1 CRL has the issuer at index 1 of
  `tbsCertList`'s fields, a v2 CRL at index 2. Reading a fixed index reads `thisUpdate` as a Name
  for a v1 CRL.
- Check the halt before the signature, and the signature before the weak key. A weak published key
  with a CRL signed by some other key is `signature-failed`.
- A `key` line releases a halt only when its key differs from the issuer's current key.
- The state belongs to each issuer. One halt flag for the whole program blocks every other issuer.
- Look up the key by the issuer the CRL names. The `key` line read last can belong to another
  issuer.
- Hash `tbsCertList`'s original bytes, header included. A hash of the whole CRL is the wrong
  hash, and every CRL fails.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
read_crl(crl_bytes):
    fields = certificate_node(crl_bytes).children[0].children
    if fields[0].tag == INTEGER:
        fields = fields[1:]                  # skip the version
    issuer = read_name_cn(fields[1])         # fields[0] is the signature AlgorithmIdentifier
    return Crl(issuer, read_signed_data(crl_bytes))

set_key(issuer, curve, key):
    if keys.get(issuer) != (curve, key):
        halted.discard(issuer)
    keys[issuer] = (curve, key)

check(crl):
    if crl.issuer in halted:
        return "issuer-halted"
    curve, key = keys[crl.issuer]
    if not check_signature(crl.signed, curve, key):
        halted.add(crl.issuer); return "signature-failed"
    if lint_key(curve, key, empty blocklist) is not None:
        halted.add(crl.issuer); return "weak-key"
    return None                              # ok
```
</details>

## Checking your solution

```
.\check 18                                          run every test
.\check 18 -Case 18-R4-resign-with-weak-key         one test, showing its full input, expected output and your output
.\check 18 -Fresh                                   a new set of tests (new random seed), to confirm on data you haven't seen
.\check 18 -Dispute <id> "why"                      set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this, from a program that doesn't halt an issuer after a failure:

```
  R4  After a halt, the issuer's CRLs are `halt issuer-halted` until a ... .    1 / 7   FAILED
      x 18-R4-resign-with-weak-key  published key d = 4: a CRL signed by another key fails, then one signed by th...
          line 2: expected `crl c2 halt issuer-halted`, got `crl c2 halt weak-key`
          likely cause: R4 - After a halt, the issuer's CRLs are `halt issuer-halted` until a `key` line gives it a different key; other issuers are unaffected
          expected values from: cryptography 41.0.7: crl.is_signature_valid(issuer_key), cross-checked with `openssl crl -CAfile`; weak keys by their known private value (d <= 4096); verdicts from the page's four rules as a state table
          reproduce: py -P tools/run_py.py solutions 18 build/cases/18/18-R4-resign-with-weak-key.in build/cases/18/18-R4-resign-with-weak-key.out
```

## After you pass: what the model leaves out

No source for this assignment has code, so there is no author's version to compare. The reference `pki/crl.py` has `read_crl`, which returns the issuer and the signed data,
and `CrlWatch`, with a dictionary of keys and a set of halted issuers. It runs `lint_key` on every
CRL that verifies. Running the lint once per key in `set_key`, and storing the finding, gives the
same verdicts with fewer searches.

Rule 1 is the workbook's choice. A real CA that finds a misconfigured signer might fix it and sign
the list again with the published key. Under rule 1 that list stays halted until the published key
changes, which treats any failure as a finding to investigate before anyone uses the issuer's lists
again. RFC 5280's CRL processing (section 6.3.3) also checks things this assignment leaves out,
such as whether the CRL is current and whether the issuer's certificate allows CRL signing.

eMudhra's account and Jackson's dates still disagree about whether the CRL failures in 2025 came
from the key mix-up. This assignment shows how a checker flags a failing CRL signature. It doesn't
show what caused the failures in 2025.
