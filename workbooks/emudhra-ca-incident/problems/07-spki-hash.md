# 07 · Hash the public key (SPKI)

**Difficulty:** Easy · **Assignment** 7 of 16 · **Check:** `.\check 07`

**Tags**
- *Language:* byte slicing · `hashlib.sha256` (or your language's SHA-256)
- *Library:* none needed beyond a SHA-256 implementation
- *Concepts:* SubjectPublicKeyInfo · SPKI pinning · CRLSet blocking

## Read in the blog first

Read Google's security blog post, ["Protecting Chrome and Android Users from Compromised
eMudhra Intermediate CA Certificates"](https://security.googleblog.com/), for how Chrome blocked
the compromised intermediates: by the SHA-256 hash of their SubjectPublicKeyInfo, pushed to every
Chrome install through CRLSet, instead of by their serial numbers or their exact bytes. The post
explains why the mechanism exists; this assignment computes the hash. You can pass using this
page alone.

## Source material

- Google Security Blog, "Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA Certificates"
- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), section 4.1.2.7 (SubjectPublicKeyInfo)

## Where this fits

Your `x509/certificate.py` from assignment 06 finds a certificate's subjectPublicKeyInfo field,
and your `asn1/der.py` (assignment 05) records where each node's bytes start and end. Here, in
`x509/spki.py`, you hash that field. Chrome used this hash to block the compromised eMudhra
intermediates by their key, and the hash stays the same when a CA reissues a certificate for the
same key. Assignment 13 checks a new key against a blocklist of known-compromised keys, and
assignment 15 blocks whole chains by SPKI hashes like these.

## The problem

Write a program that computes the SPKI hash of each certificate it reads: the SHA-256 of the
original bytes of the certificate's `subjectPublicKeyInfo` field.

### What gets hashed

`subjectPublicKeyInfo` is the whole `SEQUENCE { algorithm AlgorithmIdentifier, subjectPublicKey
BIT STRING }`. Assignment 06's `key` line came from the same field: the 7th child of
`tbsCertificate`, counting the version (version, serialNumber, signature, issuer, validity,
subject, then `subjectPublicKeyInfo`).

The hash is the SHA-256 of that whole SEQUENCE's original DER bytes, which include:

- the SEQUENCE's own tag and length bytes;
- the AlgorithmIdentifier, which names the key type and the curve;
- the BIT STRING, with its tag, its length and its unused-bits byte.

Hashing only the point inside the BIT STRING, or only the algorithm identifier, gives a different
hash. Slice the bytes out of the certificate as they are, from the field's first header byte to
its last content byte, and compare your output with the examples: the checker expects the bytes
OpenSSL's own pipeline hashes.

These OpenSSL commands compute the same hash:

```
openssl x509 -pubkey -noout -inform DER -in cert.der | openssl pkey -pubin -outform DER | openssl dgst -sha256
```

The first command extracts the public key as a PEM SubjectPublicKeyInfo block, the second
re-encodes it as DER, and the third hashes those bytes.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains one kind of line:

| Line | Meaning |
|---|---|
| `cert <label> <hex>` | A full DER-encoded certificate, the same shape as assignment 06's input. Each input stands alone: you don't need assignment 06's output. `label` is a word with no spaces. |

### Output

For each `cert` line, in input order, write one line:

```
spki <label> <hash>
```

`<hash>` is the SHA-256 digest as 64 lowercase hex characters. The checker ignores extra
whitespace.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** The SPKI hash is correct for several P-256 certificates.
- **R2** The SPKI hash is correct for several P-384 certificates.
- **R3** Two certificates that carry the same public key give the same hash, even when their
  subject names, validity periods and serial numbers differ. The hash survives reissuance, which
  is why Chrome blocked on it instead of on a certificate's serial number or fingerprint.

## Examples

### Example 1: three different certificates, three different hashes (test `07-R1-p256-several`)

```
input:   cert c0 308201163081bda003020102020101300a06082a8648ce3d04030230153113301106035504030c0a53706b692d3235362d30301e170d3235303130313030303030305a170d3236303130313030303030305a30153113301106035504030c0a53706b692d3235362d303059301306072a8648ce3d020106082a8648ce3d03010703420004ced431f7289c6d75c5623eb85b4275dd362b23203dd10bcc6b9946311d4dcb1e1afa1d9d441a621c540410022bbd4e8fff9941f6ffcd8695c680283f33f537ff300a06082a8648ce3d04030203480030450220273de61de73efd9c3d9355e45a03703e8340ab82a7975a931505e57e65c17810022100997017fe6bf998e05cf7b7811d8e05ee9e001895df0d592efde8b973082fbd3f
         cert c1 308201153081bda003020102020102300a06082a8648ce3d04030230153113301106035504030c0a53706b692d3235362d31301e170d3235303130313030303030305a170d3236303130313030303030305a30153113301106035504030c0a53706b692d3235362d313059301306072a8648ce3d020106082a8648ce3d03010703420004bd5bf4e49987117744158d14f97ae8a2887779289bdfad1dadc43b7f7dbb6120d3dab6a986aba4607e28b3d127831864f45dfc082019d728c8a0311d0d4ecd64300a06082a8648ce3d040302034700304402206e0cd6d3966c5abb6ad3c6804c289af52598ee8d175d4414bb99520987802f270220274e06ef0ff0de69071809c586cd80cf3667b78c1c8ca0383d0dd4b5471b5676
         cert c2 308201153081bda003020102020103300a06082a8648ce3d04030230153113301106035504030c0a53706b692d3235362d32301e170d3235303130313030303030305a170d3236303130313030303030305a30153113301106035504030c0a53706b692d3235362d323059301306072a8648ce3d020106082a8648ce3d03010703420004c8e2bbb166515fa4870b60d4c7a10a7a44dba14d391b835d892177b0ccd01c47f96073cc78e247fd7e5cc136d05a6720bb91b7c2a1da0aba4a6c60fb1145bede300a06082a8648ce3d04030203470030440220655d837d396c54c476aff98686a235cf7aff790ede30b515229c25bf2dae0248022028c6e4a5ade40f47cc8f3f6a484c345fa46e3a0af3a058de0beef268e12a35f4

output:  spki c0 aa07b611245aa91ac5e6ffbb5a5bd5f0c31fa21edfca50e09ccc447571370938
         spki c1 5227c43bfb92248caa17da1360257dc01fc0d2df24772b73368ba4851d4edf67
         spki c2 06501fbecdfc4a2d42b5c156b9dbee39bb4fec752df7ecbb3d4bef94360430ef
```

Three unrelated keys give three different hashes.

### Example 2: reissued key, same hash (test `07-R3-same-key-reissued`)

```
input:   cert original 308201563081dca003020102020101300a06082a8648ce3d04030330163114301206035504030c0b52656973737565642d5631301e170d3234303130313030303030305a170d3235303130313030303030305a30163114301206035504030c0b52656973737565642d56313076301006072a8648ce3d020106052b8104002203620004dbe011d744b5f545db67dee9d9007aaed7fcb936d1d03d3b74fb7437fe188bb5df65ebe2c39c7e1a177d2a787c0d035ed89d25f8a63076bfa1d89a658ea6727885bbb6574d3c3ee1b2dae545d4e0d83c2ed2162467d33ea1b98596cf49ce4ad6300a06082a8648ce3d0403030369003066023100cd3dca49a78349954c04d3278d9e438cfc92f55a2bd56941c5265d30cbb663f928feec453d09dad12f9bf82c363231ec023100f780c528a0955ad8a6a02f703cc8bda8c620b827a68434027373c5df7c12edb048f047a680c2ae497d5974526913964e
         cert reissued 308201733081faa003020102020102300a06082a8648ce3d04030330253123302106035504030c1a52656973737565642d56322d446966666572656e742d4e616d65301e170d3235303630313030303030305a170d3236303630313030303030305a30253123302106035504030c1a52656973737565642d56322d446966666572656e742d4e616d653076301006072a8648ce3d020106052b8104002203620004dbe011d744b5f545db67dee9d9007aaed7fcb936d1d03d3b74fb7437fe188bb5df65ebe2c39c7e1a177d2a787c0d035ed89d25f8a63076bfa1d89a658ea6727885bbb6574d3c3ee1b2dae545d4e0d83c2ed2162467d33ea1b98596cf49ce4ad6300a06082a8648ce3d0403030368003065023100d494b78182205bd3f8a4fdc29bffd4b02806381182da7d46090ef63428fb9f13869f7c57112464b4114a4e1f63a465a70230071472b150800adf9f3085fa4e6f8a43b01d41984b9a393dbe86dc12695bd43fc8929e02b0f6a090440d9adda72c5c59

output:  spki original 119d012a158acc40f0a6790aa182b23f5cdb5e6be3ce0773cf69d3486b7b18e7
         spki reissued 119d012a158acc40f0a6790aa182b23f5cdb5e6be3ce0773cf69d3486b7b18e7
```

`original` and `reissued` have different subject names, serial numbers and validity windows, and
the same key, so they have the same SPKI hash. A certificate authority that reissues a
certificate for the same key, or an attacker who reuses a compromised key across several
mis-issued certificates, can't change the hash by changing anything else.

## Constraints

- Every certificate is well-formed DER, the same shape assignment 06 reads.
- Each case has a 10-second limit.
- There are 6 tests: 1 each for R1 and R2 (three certificates each), 2 for R3, and 2 end-to-end
  cases that mix both curves and reissued keys in one input. Part of the set is random and
  changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Your `x509/certificate.py` from assignment 06 already finds `subjectPublicKeyInfo`: it's a
fixed-position child of `tbsCertificate`. This assignment needs that one node's original bytes
and none of the other fields.
</details>

<details><summary>Hint 2: the approach</summary>

Once you have the node, slice the certificate's bytes from the node's first header byte through
its last content byte (tag, length and content) and hash that slice. In the Boilerplate,
`Node.encoding` in `asn1/der.py` returns it. Don't re-encode the SEQUENCE yourself: DER is
canonical, so the bytes you sliced are already the ones to hash.
</details>

<details><summary>Hint 3: the traps</summary>

- Hash the whole SEQUENCE (tag, length and content). The BIT STRING inside it, or the raw key
  bytes inside that, give a different hash.
- Keep the BIT STRING's unused-bits byte: you hash this field's bytes untouched, without decoding
  them.
- Print lowercase hex. The checker compares the text.
- Two certificates that share a key give identical output. If yours differ, your slice includes
  something specific to the certificate, such as the serial number or the validity dates.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
find_spki(cert_bytes):
    return tbs_fields(cert_bytes)[PUBLIC_KEY_INFO]   # as in assignment 06

spki_hash(cert_bytes):
    spki_node = find_spki(cert_bytes)
    raw = cert_bytes[spki_node.start : spki_node.start + spki_node.total_len]
    return sha256(raw) as lowercase hex
```
</details>

## Checking your solution

```
.\check 07                                 run every test
.\check 07 -Case 07-R3-same-key-reissued   one test, showing its full input, expected output and your output
.\check 07 -Fresh                          a new set of tests (new random seed), to confirm on data you haven't seen
.\check 07 -Dispute <id> "why"             set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R3  Two different certificates ... share the same public key hash t...    0 / 2   FAILED
      x 07-R3-same-key-reissued  two certificates with different subject names and different validity periods, same public key
          spki[1]: expected (hash=119d012a158acc40f0a6790aa182b23f5cdb5e6be3ce0773cf69d3486b7b18e7), got (hash=<a different hash>) - differs in hash
          likely cause: R3 - Two different certificates (different subject, different validity) that share the same public key hash the same, so the hash survives reissuance
          expected values from: openssl x509 -pubkey | openssl pkey -pubin -outform DER | openssl dgst -sha256 (three independent OpenSSL commands)
          reproduce: py -P tools/run_py.py solutions 07 build/cases/07/07-R3-same-key-reissued.in build/cases/07/07-R3-same-key-reissued.out
```

## After you pass: compare with the post

Google's post describes the outcome, blocking by SPKI hash through CRLSet, and publishes no code
for computing the hash. The reference `x509/spki.py` reuses `tbs_fields` from
`x509/certificate.py`, the same field-finding code as assignment 06, and hashes the node's
`encoding` with `hashlib.sha256`.

`tbs_fields` finds the SPKI node by its fixed position. Another valid approach looks among
`tbsCertificate`'s children for a SEQUENCE shaped like SubjectPublicKeyInfo (a SEQUENCE followed
by a BIT STRING), without counting positions. Both find the same bytes.
