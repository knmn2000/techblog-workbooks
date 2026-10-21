# 06 · Read a certificate

**Difficulty:** Medium · **Checkpoint** 6 of 16 · **Check:** `./check.sh 06`

**Tags**
- *Language:* recursion · byte slicing
- *Library:* none needed
- *Concepts:* X.509 · ASN.1 · SubjectPublicKeyInfo · BasicConstraints

## Read in the blog first

This checkpoint is prerequisite material, not drawn from eMudhra's post: it reads the specific
fields of an X.509 certificate that the rest of this workbook needs. Read RFC 5280 section 4.1
("Basic Certificate Fields") for the shape of a certificate, and section 4.2.1.9
("Basic Constraints") for what makes a certificate a CA. This page is complete on its own after
that.

## Where this fits

Checkpoint 05 taught you to walk DER's tag-length-value structure. This checkpoint walks a real
certificate's bytes with that same technique and pulls out the handful of fields this workbook's
later checkpoints need: who it's for, who issued it, when it's valid, its public key, and whether
it's allowed to sign other certificates. Checkpoint 07 hashes the public key you read here,
checkpoint 08 checks the signature, and checkpoint 09 chains several certificates together using
exactly these fields.

## The problem

Write a program that reads one or more DER-encoded X.509 certificates and prints the fields this
workbook needs from each one.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p06_read_certificate.py` is a comment and an empty
program: reading the input and writing the output are yours. To start from working input/output
code instead, copy `starters/boilerplate/p06_read_certificate.py` over it, or pick Boilerplate in
the book's editor. The boilerplate reads the input and writes the output; you fill in
`format_lines()`.

### The shape of a certificate

A `Certificate` is a SEQUENCE of exactly three fields: `tbsCertificate` (everything that gets
signed), `signatureAlgorithm`, and `signatureValue`. This checkpoint only reads
`tbsCertificate`, a SEQUENCE whose fields, in file order, are:

| Field | What it is | In this checkpoint |
|---|---|---|
| `version` | `[0]` EXPLICIT INTEGER | present in every certificate here (always v3); read past it, you don't need its value |
| `serialNumber` | INTEGER | not needed here |
| `signature` | SEQUENCE (AlgorithmIdentifier) | repeats the outer signatureAlgorithm; not needed here |
| `issuer` | SEQUENCE (a Name) | read its commonName, below |
| `validity` | SEQUENCE of two Time values | read both, below |
| `subject` | SEQUENCE (a Name) | read its commonName, below |
| `subjectPublicKeyInfo` | SEQUENCE | read the curve and the point, below |
| `extensions` | `[3]` EXPLICIT SEQUENCE OF Extension, **optional** | read BasicConstraints if present, below |

Every certificate in this checkpoint is version 3, so `version` is always there - you can rely on
the first child being `[0]` and skip it (or read it; its value is always 2, meaning v3). There is
no `issuerUniqueID` or `subjectUniqueID` in any certificate here. `extensions` is the only
optional field: some certificates in this checkpoint have no extensions at all.

### Reading a Name's common name

A `Name` is `SEQUENCE OF RelativeDistinguishedName`, and each `RelativeDistinguishedName` is
`SET OF AttributeTypeAndValue`, where `AttributeTypeAndValue` is `SEQUENCE { type OBJECT
IDENTIFIER, value ANY }`. Every name in this checkpoint has exactly one
`RelativeDistinguishedName`, with exactly one attribute: commonName, OID `2.5.4.3`. Find the
attribute whose type is that OID, and read its value's content bytes as text (it's a
PrintableString or UTF8String - either way, the content bytes are the characters).

### Reading validity

`Validity` is `SEQUENCE { notBefore Time, notAfter Time }`. `Time` is `CHOICE { utcTime
UTCTime, generalTime GeneralizedTime }` - either tag can appear, you don't need to tell them
apart. Print the content bytes as text, unchanged (as in checkpoint 05, this isn't a
date-parsing checkpoint).

### Reading the public key

`SubjectPublicKeyInfo` is `SEQUENCE { algorithm AlgorithmIdentifier, subjectPublicKey BIT
STRING }`. `AlgorithmIdentifier` is itself `SEQUENCE { algorithm OBJECT IDENTIFIER, parameters
ANY }`. For every key in this checkpoint:

- `algorithm` is `id-ecPublicKey`, OID `1.2.840.10045.2.1`.
- `parameters` is a single OBJECT IDENTIFIER naming the curve: `1.2.840.10045.3.1.7` for P-256,
  `1.3.132.0.34` for P-384.
- `subjectPublicKey`'s content, after its unused-bits byte (checkpoint 05's BIT STRING rule;
  it is always `0` here), is `0x04` (meaning "uncompressed point") followed by the x-coordinate
  then the y-coordinate, each the curve's coordinate width: 32 bytes for P-256, 48 for P-384.

### Reading BasicConstraints

If `extensions` is present, it's a list of `Extension ::= SEQUENCE { extnID OBJECT IDENTIFIER,
critical BOOLEAN DEFAULT FALSE OPTIONAL, extnValue OCTET STRING }` - so `extnValue` is always
the *last* field of an `Extension`, whether or not `critical` is there. Look for the extension
whose `extnID` is `2.5.29.19` (basicConstraints). Its `extnValue` is itself DER-encoded again
(an OCTET STRING whose content bytes are another complete TLV structure) - parse those bytes as
`BasicConstraints ::= SEQUENCE { cA BOOLEAN DEFAULT FALSE, pathLenConstraint INTEGER OPTIONAL
}`. `cA` is DER's DEFAULT FALSE, so it's only present in the bytes when true - if the SEQUENCE's
first child isn't a BOOLEAN, `cA` is false and whatever's there (if anything) is
`pathLenConstraint`.

**If there is no `extensions` field, or no `basicConstraints` extension among whatever
extensions there are**, this checkpoint reads the certificate as **not a CA, with no path length
constraint**. RFC 5280 section 4.2.1.9 doesn't force this reading - the extension is optional and
the RFC leaves "absent" formally undefined for older certificates - but every modern verifier
(and this workbook) treats absence as "not a CA", since that's the fail-safe direction: a
certificate not marked as a CA can't sign other certificates.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains one kind of line:

| Line | Meaning |
|---|---|
| `cert <label> <hex>` | A full DER-encoded certificate. `label` is a word with no spaces, copied back unchanged. |

### Output

For each `cert` line, in input order, write four lines:

```
cert <label> <subject-cn> <issuer-cn>
validity <notBefore> <notAfter>
key <curve> <pubx> <puby>
ca <true|false> <pathlen>
```

- `<subject-cn>`, `<issuer-cn>`: the commonName text. Neither contains spaces in this checkpoint.
- `<notBefore>`, `<notAfter>`: the raw time string, unchanged.
- `<curve>`: `P-256` or `P-384`.
- `<pubx>`, `<puby>`: lowercase hex, exactly the curve's coordinate width (64 hex digits for
  P-256, 96 for P-384) - pad with leading zeros if the number's own hex form would be shorter.
- `<pathlen>`: the decimal path length constraint, or the word `none` if there isn't one.

The checker ignores extra whitespace.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** A non-CA leaf certificate: subject, issuer, validity and the public key all read
  correctly.
- **R2** A CA certificate (BasicConstraints CA:TRUE) with no path length constraint.
- **R3** A CA certificate with an explicit path length constraint (0, 1, or a larger number).
- **R4** Both curves: P-256 and P-384 public keys read correctly, each at its own coordinate
  width.
- **R5** Subject and issuer can be the same common name (a self-signed certificate) or different,
  independent of whether the certificate is a CA.
- **R6** A certificate with no BasicConstraints extension at all - whether because it has no
  extensions, or because it has other extensions but not that one - defaults to CA:false, no
  path length.

## Examples

### Example 1: a CA certificate with a path length (test `06-R3-pathlen-1`)

```
input:   cert ca 308201763081fea003020102020101300a06082a8648ce3d04030330173115301306035504030c0c4578616d706c652d526f6f74301e170d3235303130313030303030305a170d3236303130313030303030305a301f311d301b06035504030c144578616d706c652d43412d506174686c656e2d313076301006072a8648ce3d020106052b8104002203620004e1623e85fc905a98a7d91c6dc26756f4c066161013d55fa7f7ad67897920f7a685f7bc8dd5ade34e9b1f25b65a9d9e23d97999d8a6638bbaf8def683da109ab03f8030fcd5c939c93a8e56d3ae60979440ee04be5d1288297aa111afebd07bbaa316301430120603551d130101ff040830060101ff020101300a06082a8648ce3d040303036700306402303f51e3de63db3ef3d01bbd44f60d1fd36f0d5ec18414b11dcdd69f3f9d0e8fe911f45d6c16be551aae0e543208537e4e02301895e2b422df6c84e29a69561aca0a7d99fa899950fd26fc130162dd6e0e11d536469c3326458c6e3f9577883571346b

output:  cert ca Example-CA-Pathlen-1 Example-Root
         validity 250101000000Z 260101000000Z
         key P-384 e1623e85fc905a98a7d91c6dc26756f4c066161013d55fa7f7ad67897920f7a685f7bc8dd5ade34e9b1f25b65a9d9e23 d97999d8a6638bbaf8def683da109ab03f8030fcd5c939c93a8e56d3ae60979440ee04be5d1288297aa111afebd07bba
         ca true 1
```

The certificate carries a BasicConstraints extension whose content decodes to `SEQUENCE {
BOOLEAN true, INTEGER 1 }` - `cA` is present (true) and `pathLenConstraint` is `1`.

### Example 2: no extensions at all (test `06-R6-no-basic-constraints`)

```
input:   cert plain 308201233081caa003020102020101300a06082a8648ce3d040302301f311d301b06035504030c144e6f2d457874656e73696f6e732d497373756572301e170d3235303130313030303030305a170d3236303130313030303030305a30183116301406035504030c0d4e6f2d457874656e73696f6e733059301306072a8648ce3d020106082a8648ce3d03010703420004fdefa4845516df81e692b44605f484718dc2fe2edcf5d0b79ad85fbb655dc72ce86f7ee0ed72f65e897ecada18a82d161eb1feb3fa8b0798582f21fbe45451ea300a06082a8648ce3d0403020348003045022100b009db1bcf6a306229bb122b3271e64a5d44ad6874e22067f59a4dc1230d2a350220674d5f5b01adc3d5f8859190bd5016a1301facff5a28b5993d9f1bc65fa608ca

output:  cert plain No-Extensions No-Extensions-Issuer
         validity 250101000000Z 260101000000Z
         key P-256 fdefa4845516df81e692b44605f484718dc2fe2edcf5d0b79ad85fbb655dc72c e86f7ee0ed72f65e897ecada18a82d161eb1feb3fa8b0798582f21fbe45451ea
         ca false none
```

`tbsCertificate` simply has no eighth field - its last child is `subjectPublicKeyInfo`. There is
nothing to look inside; the default applies directly.

### Example 3: several certificates, one chain-shaped input (test `06-E2E-chain-shaped`)

```
input:   cert root 3082016f3081f5a003020102020101300a06082a8648ce3d04030330183116301406035504030c0d576f726b626f6f6b2d526f6f74301e170d3235303130313030303030305a170d3236303130313030303030305a30183116301406035504030c0d576f726b626f6f6b2d526f6f743076301006072a8648ce3d020106052b8104002203620004507ddbbe1b5b4597fc94fa596afd5ea790ac82c752252ffe9e9b95cd696bbcf103cd95cac83c0b40fdb9d8d792defb500ccf0104f13d368f620e6de88ce4b96aa8190b9b968da2ef552251f69940df65343559faa197374de240d48ee4d99028a3133011300f0603551d130101ff040530030101ff300a06082a8648ce3d0403030369003066023100c50214aa231c11efa95960923e47a020dd7cb43d7113da0acb9918a6ff007a2f1954ce263527a21c66b5057d855f10c7023100c1cadfb71f2a8e07f02f9988d99fe08c0688ee3920dd400cc0496f7db5899af7d1e5ee1f349c13b98377aeb172b68987
         cert intermediate 3082017a30820100a003020102020101300a06082a8648ce3d04030330183116301406035504030c0d576f726b626f6f6b2d526f6f74301e170d3235303130313030303030305a170d3236303130313030303030305a3020311e301c06035504030c15576f726b626f6f6b2d496e7465726d6564696174653076301006072a8648ce3d020106052b810400220362000465fcfdf22ddb0828646fa09dd6ac70346910523bc4dc5685f99ece135247f11246abb5a9b1a2566ccbc9722707e38be2da9f61bf80f5ee378b911bf1fdc5b7d0bd16863e3dfc1fe45032a3ce0f6aa8d4f38ce5f59095592f155e15db7c636b64a316301430120603551d130101ff040830060101ff020100300a06082a8648ce3d0403030368003065023009ae7a7120d47ffc17a9961dae82bbaa12cc61edeb3772c42b1472bdadc2b3b62442f31d80280d0506447f561265390e023100a52b34c76fd7d65fe173ba0338700418bf8b42a5f6747ad9bb98c04a4785810a21bc9fc8d81dd3051869e811a31c9cb7
         cert leaf 308201603081e8a003020102020101300a06082a8648ce3d0403033020311e301c06035504030c15576f726b626f6f6b2d496e7465726d656469617465301e170d3235303130313030303030305a170d3236303130313030303030305a30183116301406035504030c0d576f726b626f6f6b2d4c6561663076301006072a8648ce3d020106052b8104002203620004e7b3aed763622f0e4776aa889b41b42354653dc964aea513a4498d785b0bb38952130cb33a0fe971f521257b484ba0bbb3d3be8724e1337d27043c65e65bcd10e10aa2b47d0e0091200e9c44328a8ac461b3b58a958e88b57c5acaa9a0514cc5300a06082a8648ce3d0403030367003064023028bde61493a39b95a28d3d84665ec4f879a27663704fb8fec2b47c2bf2dfa855bd47dfe08db7eee289dde50a0f14a5b202304365bf93be614e348762c9123dfc35fb5e15ee9c21762f07a371bf1e6371a559753e836fe94e20ad107c76352cc167ab

output:  cert root Workbook-Root Workbook-Root
         validity 250101000000Z 260101000000Z
         key P-384 507ddbbe1b5b4597fc94fa596afd5ea790ac82c752252ffe9e9b95cd696bbcf103cd95cac83c0b40fdb9d8d792defb50 0ccf0104f13d368f620e6de88ce4b96aa8190b9b968da2ef552251f69940df65343559faa197374de240d48ee4d99028
         ca true none
         cert intermediate Workbook-Intermediate Workbook-Root
         validity 250101000000Z 260101000000Z
         key P-384 65fcfdf22ddb0828646fa09dd6ac70346910523bc4dc5685f99ece135247f11246abb5a9b1a2566ccbc9722707e38be2 da9f61bf80f5ee378b911bf1fdc5b7d0bd16863e3dfc1fe45032a3ce0f6aa8d4f38ce5f59095592f155e15db7c636b64
         ca true 0
         cert leaf Workbook-Leaf Workbook-Intermediate
         validity 250101000000Z 260101000000Z
         key P-384 e7b3aed763622f0e4776aa889b41b42354653dc964aea513a4498d785b0bb38952130cb33a0fe971f521257b484ba0bb b3d3be8724e1337d27043c65e65bcd10e10aa2b47d0e0091200e9c44328a8ac461b3b58a958e88b57c5acaa9a0514cc5
         ca false none
```

Twelve output lines from three input certificates: four lines each, in order. (This checkpoint
doesn't check that `intermediate`'s signature really came from `root` - that's checkpoint 08.)

## Constraints

- Every certificate is version 3, self-consistent DER, built from real ECDSA P-256 or P-384 keys.
- Subject and issuer common names never contain spaces or exceed 64 characters.
- There is at most one `RelativeDistinguishedName` and one `AttributeTypeAndValue` per Name, and
  exactly one BasicConstraints extension when extensions are present (never two).
- There are 17 tests: 3 for R1, 2 for R2, 3 for R3, 2 for R4, 2 for R5, 3 for R6, and 2
  end-to-end cases, including a random mix of five certificates and a three-certificate
  chain-shaped input. Part of the set is random and changes with `-Fresh`.

## Source material

- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), sections 4.1 (certificate fields) and 4.2.1.9 (Basic Constraints)
- RFC 5480, [Elliptic Curve Cryptography Subject Public Key Information](https://www.rfc-editor.org/rfc/rfc5480), for the id-ecPublicKey SubjectPublicKeyInfo shape and the uncompressed point format

## Hints

<details><summary>Hint 1: where to start</summary>

Parse the certificate the way checkpoint 05 parses anything: one top-level SEQUENCE
(`Certificate`), whose first child is another SEQUENCE (`tbsCertificate`). Everything you need is
a child of that second SEQUENCE, in the fixed order given on this page.
</details>

<details><summary>Hint 2: the approach</summary>

Walk `tbsCertificate`'s direct children in order: skip the first one (version, always present and
always `[0]`), then serialNumber, then signature (skip it too), then issuer, validity, subject,
subjectPublicKeyInfo - six fields read in a fixed sequence. After that, there may or may not be a
seventh child; if there is, and it's tagged `[3]`, that's extensions.
</details>

<details><summary>Hint 3: the traps</summary>

- `version` is `[0]` EXPLICIT, meaning its content is itself a complete TLV node (an INTEGER),
  not the raw integer bytes directly in the `[0]` wrapper.
- `signature` (inside `tbsCertificate`) repeats the same algorithm as the outer
  `signatureAlgorithm`. Don't confuse the two or double-count a field.
- An `Extension`'s `critical` field is optional, so `extnValue` is sometimes the second child and
  sometimes the third. It's always the *last* one.
- `extnValue` is an OCTET STRING whose content bytes are themselves a complete DER structure -
  you parse it a second time, independently of the outer walk.
- `cA BOOLEAN DEFAULT FALSE` means the encoder leaves it out entirely when false. A
  BasicConstraints SEQUENCE with only an INTEGER child means `cA` is false and that INTEGER is
  the path length - not the other way around.
- Pad `pubx` and `puby` to the full coordinate width. A coordinate that happens to start with a
  zero byte is one hex digit shorter if you don't pad it, and the checker will catch that.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
read_certificate(bytes):
    cert = parse_top_level_sequence(bytes)
    tbs = cert.children[0]
    children = tbs.children
    i = 1 if children[0] is context-tag-0 else 0   # skip version if present
    i += 1                                          # skip serialNumber
    i += 1                                          # skip signature
    issuer_cn = read_common_name(children[i]); i += 1
    not_before, not_after = read_two_times(children[i]); i += 1
    subject_cn = read_common_name(children[i]); i += 1
    curve, x, y = read_public_key(children[i]); i += 1
    ca, pathlen = false, none
    if i < len(children) and children[i] is context-tag-3:
        ca, pathlen = read_basic_constraints(children[i])
    return subject_cn, issuer_cn, not_before, not_after, curve, x, y, ca, pathlen
```
</details>

## Checking your solution

```
./check.sh 06                               run every test
./check.sh 06 -Case 06-R3-pathlen-1         one test, showing its full input, expected output and your output
./check.sh 06 -Fresh                        a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 06 -Dispute <id> "why"           set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R6  A certificate with no BasicConstraints extension at all defaults...    2 / 3   FAILED
      x 06-R6-other-extension-no-basic-constraints  a different extension is present...
          key[0]: expected (curve=P-256, pubx=07539bc9..., puby=...), got (curve=P-256, pubx=7539bc9..., puby=...) - differs in pubx
          likely cause: R6 - A certificate with no BasicConstraints extension at all defaults to CA:false, no path length
          expected values from: cryptography 41.0.7 (OpenSSL): fields are read back from the built certificate with a separate parse call, and validity strings with openssl asn1parse
          reproduce: python3 -P tools/run_py.py solutions 06 build/cases/06/06-R6-other-extension-no-basic-constraints.in build/cases/06/06-R6-other-extension-no-basic-constraints.out
```

## After you pass: compare with the post

The post contains no code for this (it's prerequisite material, not drawn from the post), so
there is no author's version to compare. The reference solution is in `_spoilers/reference/`,
built on `common/certlib.py`'s `parse_certificate`.

**Something to look for:** the reference checks for `extensions` by testing whether there's an
extra child *and* that it carries tag `[3]` - it doesn't just check "is there one more field
than expected", because a certificate could in principle have a stray extra field that isn't
extensions at all. Compare that with whatever check you wrote.
