# 09 · Validate a certificate chain

**Difficulty:** Hard · **Checkpoint** 9 of 16 · **Check:** `./check.sh 09`

**Tags**
- *Language:* loops over lists · structured state
- *Library:* none needed
- *Concepts:* chain of trust · trust anchors · path length constraints · RFC 5280 path validation

## Read in the blog first

This checkpoint is prerequisite material, not drawn from eMudhra's post, but it is the mechanism
behind the sentence everyone took away from the incident: once a CA's intermediate was
distrusted, certificates issued through it stopped verifying. Read RFC 5280 section 6
("Certification Path Validation Algorithm") for the real, general algorithm - this checkpoint
implements its core idea in miniature. Then read eMudhra's own
[statement on the incident](https://emudhra.com/en/post/certificate-security-incident) for what
actually happened: eight intermediate CA certificates were found to have been issued with
cryptographically weak keys, and were revoked/distrusted by the major browsers. This page is
complete on its own after that.

## Where this fits

Checkpoint 06 taught you to read a certificate's fields, and checkpoint 08 taught you to check
whether one certificate was really signed by a given key. This checkpoint strings several
certificates together into the thing a browser actually does with an incoming TLS
certificate: decide whether to trust it, by walking up from the leaf to a key it already trusts.
This is the mechanism that let browsers reject the compromised eMudhra intermediates once they
were removed from the trust store - not by checking anything special about the intermediates
themselves, but simply because the chain no longer reached anywhere trusted.

## The problem

Write a program that, given a list of trust anchors and one or more certificate chains, decides
whether each chain is trusted, and if not, why.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p09_validate_chain.py` is a comment and an empty
program: reading the input and writing the output are yours. To start from working input/output
code instead, copy `starters/boilerplate/p09_validate_chain.py` over it, or pick Boilerplate in
the book's editor. The boilerplate reads the input and writes the output; you fill in
`validate_chain()`.

### The model

A **trust anchor** is a public key the verifier already trusts, given directly (no certificate of
its own - trust in it is axiomatic, the way a browser's root store works). A **chain** is a list
of certificates, leaf first: certificate 0 is the one actually being checked, certificate 1 (if
present) signed it, certificate 2 (if present) signed certificate 1, and so on. The most senior
certificate in the list - the last one - must itself be signed by one of the trust anchors
directly. There is no certificate for the trust anchor itself in the list.

Checking a chain means checking all of the following, **in this order**, and stopping at the
first problem found:

1. **Signatures.** Certificate `i` must really be signed by certificate `i + 1`'s public key
   (checkpoint 08's check, with the curve constants `p`, `a`, `G` and `n` from checkpoint 08's
   page), for every `i` from the leaf up to the second-to-last certificate. The last certificate
   must really be signed by **one of** the given trust anchors (try each; any match is enough).
2. **CA permission.** Every certificate that signed another one in this chain - that is, every
   certificate except the leaf - must have BasicConstraints CA:TRUE (checkpoint 06's `ca` field).
   A certificate that isn't marked as a CA can't be trusted to sign other certificates, no matter
   how good its signature is.
3. **Path length.** A certificate's path length constraint (checkpoint 06's `pathlen`, when it
   has one) bounds how many **more** intermediate certificates may appear between it and the
   leaf. Counting from the leaf's immediate signer upward, the certificate at position `i` in
   the list (1-indexed: position 1 is the leaf's signer) has exactly `i - 1` intermediates below
   it (closer to the leaf). If that certificate has a path length constraint and `i - 1` exceeds
   it, the chain is invalid.
4. **Validity.** Every certificate's validity window - `notBefore` through `notAfter` - must
   cover the given "now". All the time strings in this checkpoint are UTCTime in the same format
   (two-digit year, so e.g. `250601000000Z` is 2025-06-01), so plain text comparison gives you
   chronological order directly; you don't need to parse dates.

If all four hold, the chain is **trusted**. If not, report the **first** problem found, in the
order above, using this fixed vocabulary:

| Reason | Meaning |
|---|---|
| `bad-signature` | A non-topmost certificate in the chain was not really signed by the next one up |
| `unknown-anchor` | The topmost certificate's signature doesn't check out against **any** given trust anchor - this is its own, separate step (see "The model" above), never reported as `bad-signature` |
| `not-a-ca` | A certificate that signed another one in the chain isn't marked CA:TRUE |
| `path-too-long` | A certificate's path length constraint was violated by how many more intermediates follow it |
| `expired` | Some certificate's validity window does not cover `now` (this includes "not yet valid", not only "expired" in the everyday sense - this checkpoint doesn't distinguish the two directions) |

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file describes one or more chains:

| Line | Meaning |
|---|---|
| `chain <label>` | Starts a new chain. Everything until the next `chain` line (or the end of the file) belongs to it. `label` is a word with no spaces. |
| `now <time>` | The time to check validity against, in the same raw format as checkpoint 06's `notBefore`/`notAfter`. |
| `anchor <curve> <x> <y>` | A trusted public key. May appear more than once (more than one trust anchor). |
| `cert <hex>` | One certificate. Leaf first; each later `cert` line is signed by the next one. |

### Output

For each `chain` block, in input order, write one line:

```
chain <label> trusted
chain <label> untrusted <reason>
```

The checker ignores extra whitespace.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** A valid 2-level chain: the leaf is signed directly by a trust anchor, no intermediates
  at all.
- **R2** A valid 3-level chain: leaf, one intermediate, then a trust anchor.
- **R3** The topmost certificate's signature doesn't check out against any given trust anchor:
  `unknown-anchor`.
- **R4** A certificate claims the right issuer but isn't really signed by it (a different key
  signed it than the one it names): `bad-signature`.
- **R5** An intermediate that signed another certificate in the chain isn't marked CA:TRUE:
  `not-a-ca`.
- **R6** An intermediate asserts a path length constraint that a later (more-leaf-ward)
  intermediate violates: `path-too-long`. (And, for contrast, a path length that's exactly
  respected still gives `trusted`.)
- **R7** A certificate's validity window doesn't cover `now`, in either direction: `expired`.

## Examples

### Example 1: a valid 2-level chain (test `09-R1-two-level`)

```
input:   chain c1
         now 250601000000Z
         anchor P-384 8c37c3bb0940a707a89dbb651a719c644c6a463d38564bd2d1356c0035dc5d93721b9bf3d4bae3125e77e5ad688251e9 f2b9602ae1162423b84924c3691f20e296704c451e07f381ee9ef096bc0cee11155f5cae3971b4d4864d356ec77e42d5
         cert 3082014a3081d2a003020102020102300a06082a8648ce3d0403033011310f300d06035504030c06526f6f742d31301e170d3235303530323030303030305a170d3236303630313030303030305a3011310f300d06035504030c064c6561662d313076301006072a8648ce3d020106052b8104002203620004350c9b8d51a04832daf850430e93435c42c227286ebf291baf26e4c4331200ee6a4143ae46372dd0b7d6ab2311a2646b3e3706e4d8522542d64efd922cd0e1ee6c5b2abad474a4db8f6b3d1081a2025f5a9b7c01a5a69545c005bc92ceadb5b0300a06082a8648ce3d0403030367003064023061c30b5456592ee538c43db0491ab97fd05f005a36b3ec6a7a884c86ccbc31c6c8f642a236627423a34bd124ae2c5d9802302e14ff224299ba519255daa213d5128aba4ff91fbb115678b555a20dd50dad8e5e574e48baa120f71007e07a341963b3

output:  chain c1 trusted
```

One certificate, no intermediates: it is signed directly by the trust anchor key.

### Example 2: path length violated (test `09-R6-path-too-long`)

```
input:   chain c6
         now 250601000000Z
         anchor P-384 abbe83dd2afe21268be6efbf9da6c2db82bc6ae27d7acc374d02d42a843211371de592e7b0dda82cb7035bd27d0eeeef 25ef6c5a8b0252526764515e026f39f6e1516dac422ab9764f096d432a28fc18184aee07470f4433eb853b095268f3b0
         cert 3082014b3081d2a003020102020104300a06082a8648ce3d0403033011310f300d06035504030c06496e74422d36301e170d3235303530323030303030305a170d3236303630313030303030305a3011310f300d06035504030c064c6561662d363076301006072a8648ce3d020106052b8104002203620004759b040031e94a644a5f991cb79507ec0f5508e79a481b2092b9a321af911f51c2f2603a0f6bbb00f8a93e66509da1c5f23b8c23ab79691af588b23a780f69e1c48cc27657eee3e281f6a23548168fe442597a6fbaf1c1dfefa48dfb3c4ae99f300a06082a8648ce3d04030303680030650230703fbc346dc74c042b9122cc666c06693834d90e548bb0589eff8041993d003feb3c642a150ea0c1a684305e7c034ec7023100e033bf2a52aa40a5cb64beaf335123ae85b7190cbc015d3b22078b9c0c471f27d7eec95bd190d508ba66ceaa0f4bbd8d
         cert 3082015f3081e7a003020102020103300a06082a8648ce3d0403033011310f300d06035504030c06496e74412d36301e170d3235303530323030303030305a170d3236303630313030303030305a3011310f300d06035504030c06496e74422d363076301006072a8648ce3d020106052b8104002203620004a1eecf375b3b1d82f876ba1cd024c14e85888cc57229963cacb411a0c174b22906ea48cf6b13d2109b18d2a2aec33d60874ab51aec3bedcca9a0b58c4a02887474cbfff060835e9c20ba0b0b12adaadb80a838996a532a6f22047256e161ab27a3133011300f0603551d130101ff040530030101ff300a06082a8648ce3d04030303670030640230398f8e436952fa2ac7a7a089ad1a541103ae030da68afff4fd8910fb5b559449e2345d3a34d661ff45681c74a7a07b9702306c04a5524bb543a3ee1d1a0e60d50c9ae362fb39135d63e2298079b592ea2aa5bc374999838e9780f5367895e7f25462
         cert 308201623081eaa003020102020102300a06082a8648ce3d0403033011310f300d06035504030c06526f6f742d36301e170d3235303530323030303030305a170d3236303630313030303030305a3011310f300d06035504030c06496e74412d363076301006072a8648ce3d020106052b810400220362000463c3efe46957be3a716c233a9a2da8ff7e4038f2bdd915c5e61c18ab08c0118680e254d096a8e3c92365cc5cb44442ec580d5fe60f79f6122185c1e74a2e0168b68b9b3eb7de971b501967f43182659e4bd98ca05b2b35de9b6deb4116a02abaa316301430120603551d130101ff040830060101ff020100300a06082a8648ce3d0403030367003064023044d2f2492a62ffea89aaf305fdbc5744357c5489860c802ddf01c9eb8ebfbbe3a55c64013ced53807ff339cad23bcf910230374d32d6c8b6a74cbe0f088d2061829494d6ad3401f561fb72e66d2fa72dca50fa875eaf60c77c4ed9385b875f68ef6d

output:  chain c6 untrusted path-too-long
```

The chain is leaf, `IntB-6`, `IntA-6`, anchor: three `cert` lines (leaf, then each signer going
up), plus the anchor. `IntA-6` (the third `cert` line) carries path length `0` - meaning no
intermediate may appear between it and the leaf - but `IntB-6` (the second `cert` line) does
exactly that, one position closer to the leaf. (`IntA-6` itself is signed by the key given as
the trust anchor, `Root-6`.)

### Example 3: signed by an unlisted root (test `09-R3-unknown-anchor`)

```
input:   chain c3
         now 250601000000Z
         anchor P-384 5101da4433353de6df962daf91e881337ea90bcfc516bd7a9f5237c30660eb8649730bde08dbbf841b2c331558c587b0 3cae8209eab991d23b39f65a1fb48824f58ad9bd3cb98f2ed1046d14564cb3f71c2cfd986522ff2f7c1825df856fcf50
         cert 308201503081d8a003020102020101300a06082a8648ce3d04030330173115301306035504030c0c556e6b6e6f776e2d526f6f74301e170d3235303530323030303030305a170d3236303630313030303030305a3011310f300d06035504030c064c6561662d333076301006072a8648ce3d020106052b81040022036200048cc1cbcb31f30b3f7452e79a4ac4cc3f8f9849b9398c6de3f7213c207a8e92cc0434ed0b70cc6a9de61c75ef8e74a53cd910fa5aceb8a8f7fb005c473ebf4e20348b708295629f29b04f8a421c3d29fe304f4b0c401a35469796dac357cb2e6d300a06082a8648ce3d0403030367003064023023538226362bdd8a133ac7528a797e8c2c2681d46c8eb33dbfa64edbbce5e2c270c2e7a4646865244d1aa4e143b25c6f0230655e8e82c7530fa3eccd1f3be1b634e70fcdb4b65208be30a8ddd272d428d08aaad661c951530f433da99857ee87251f

output:  chain c3 untrusted unknown-anchor
```

This certificate's own issuer field even says "Unknown-Root", but that's just a name - what
actually matters is that no given `anchor` key makes its signature check out. The `anchor` line
given here is for a different, unrelated root.

## Constraints

- Every certificate is P-384 (checkpoint 08's own constraint carries over).
- Every chain has at least one certificate (the leaf) and at most three (leaf plus two
  intermediates) in these tests.
- All time strings - every certificate's `notBefore`/`notAfter`, and every `now` - are UTCTime
  with a two-digit year in this checkpoint's data, so plain string comparison is chronological
  order. (This wouldn't generally be true across a change of century; it's true here because
  every date in this checkpoint's tests falls in 2000-2099.)
- There are 13 tests: 1 each for R1-R5, 2 for R6 (one violation, one respected), 2 for R7 (both
  directions), and 4 end-to-end chains, including the shape of the real incident: a leaf's
  intermediate verifies while the intermediate's own signer is a recognised anchor, and stops
  verifying the moment that signer is no longer offered as one - modelling what "distrusting an
  intermediate" actually does to every certificate under it. Part of the set is random and
  changes with `-Fresh`.

## Source material

- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), section 6 ("Certification Path Validation Algorithm")
- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident)

## Hints

<details><summary>Hint 1: where to start</summary>

Parse each certificate with checkpoint 06's field reading (you need `ca`, `pathlen`,
`notBefore`, `notAfter`, the public key) and checkpoint 08's signature pieces (`tbsCertificate`'s
bytes, `r`, `s`). Then this checkpoint is mostly bookkeeping: four short loops over the list of
certificates, each one a direct translation of one bullet in "The model" above.
</details>

<details><summary>Hint 2: the approach</summary>

Process the chain once per check, not once overall: a loop over adjacent pairs for signatures,
a loop over everything-but-the-leaf for CA status, a loop (with a running count) for path
length, a loop over everything for validity. Stop and return as soon as any loop finds a
problem - don't collect every problem and then decide, since this checkpoint only ever reports
the first one, by the order given on this page.
</details>

<details><summary>Hint 3: the traps</summary>

- The topmost certificate's signer isn't "the next certificate" - there isn't one. It's checked
  against the trust anchors directly, and matching **any** anchor is enough.
- "Every certificate that signed another one" is everything except the leaf (certificate 0),
  not everything except the topmost one. A 3-certificate chain has exactly one signer that
  needs checking for CA status and path length: the intermediate.
- Path length counts intermediates **below** a certificate (closer to the leaf), not including
  the leaf and not including the certificate itself. A path length of `0` on the certificate
  that signs the leaf directly is fine - it's a constraint on what's allowed *below* that
  certificate, not on it signing a leaf.
- "Expired" here covers both directions: a certificate not yet valid at `now`, and one whose
  validity has already ended. Don't only check one side.
- If the input gives more than one `anchor` line, trying just the first one (instead of all of
  them) will wrongly reject a chain that really does lead to one of the later ones.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
validate_chain(now, anchors, certs):   # certs: leaf first
    for i in 0 .. len(certs) - 2:
        if not signed_by(certs[i], certs[i + 1]):
            return untrusted, "bad-signature"
    if not any(signed_by(certs[-1], anchor) for anchor in anchors):
        return untrusted, "unknown-anchor"

    for c in certs[1:]:
        if not c.ca:
            return untrusted, "not-a-ca"

    for i in 1 .. len(certs) - 1:
        below = i - 1
        if certs[i].pathlen is not none and below > certs[i].pathlen:
            return untrusted, "path-too-long"

    for c in certs:
        if not (c.notBefore <= now <= c.notAfter):
            return untrusted, "expired"

    return trusted
```
</details>

## Checking your solution

```
./check.sh 09                              run every test
./check.sh 09 -Case 09-R6-path-too-long    one test, showing its full input, expected output and your output
./check.sh 09 -Fresh                       a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 09 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R6  An intermediate's path length constraint is violated by how many...    1 / 2   FAILED
      x 09-R6-path-too-long  IntA-6 asserts path length 0, but IntB-6 follows it before the leaf
          line 1: expected `chain c6 untrusted path-too-long`, got `chain c6 trusted`
          likely cause: R6 - An intermediate's path length constraint is violated by how many more intermediates follow it: path-too-long
          expected values from: openssl verify -attime <epoch> -CAfile <root> -untrusted <intermediates> <leaf> (OpenSSL's own path validation, independent of this workbook's reference)
          reproduce: python3 -P tools/run_py.py solutions 09 build/cases/09/09-R6-path-too-long.in build/cases/09/09-R6-path-too-long.out
```

## After you pass: compare with the post

eMudhra's statement describes the outcome (browsers blocked certificates through the affected
intermediates) without publishing any verification code - there's no author's snippet to compare
against. The reference solution is in `_spoilers/reference/`: it reuses `common/certlib.py`'s
`parse_certificate` and `verify_ecdsa_sha384`, checking signatures, then CA status, then path
length, then validity, in that fixed order, returning on the first failure.

**Something to look for:** since every chain in this checkpoint's tests has at most one problem,
the order of those four checks doesn't actually change any test's answer - a correct solution
that checks validity first and signatures last passes exactly the same tests. What the order
*does* fix is which single reason gets reported when more than one thing is wrong with a chain,
which these tests don't exercise. If you want to see this for yourself, try building a chain with
two unrelated problems and see which reason your program reports first.
