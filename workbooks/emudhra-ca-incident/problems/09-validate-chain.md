# 09 · Validate a certificate chain

**Difficulty:** Hard · **Assignment** 9 of 19 · **Check:** `.\check 09`

**Tags**
- *Language:* loops over lists · structured state
- *Library:* none needed
- *Concepts:* chain of trust · trust anchors · path length constraints · RFC 5280 path validation

## Read in the blog first

This assignment is background that eMudhra's post leaves out. It is the mechanism behind the
incident's visible effect: once browsers distrusted a CA's intermediate, certificates issued
through it stopped verifying.

- For the full, general algorithm, read RFC 5280 section 6 ("Certification Path Validation
  Algorithm"). This assignment implements its core on a small scale.
- For what happened, read eMudhra's own
  [statement on the incident](https://emudhra.com/en/post/certificate-security-incident): eight
  intermediate CA certificates were found to have been issued with cryptographically weak keys,
  and the major browsers revoked or distrusted them.

You can pass using this page alone.

## Source material

- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), section 6 ("Certification Path Validation Algorithm")
- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident)

## Where this fits

Your `x509/certificate.py` from assignment 06 reads a certificate's fields, and your
`x509/signature.py` from assignment 08 checks whether a given key signed a certificate. In
`pki/chain.py` you string several certificates together and do what a browser does with an
incoming TLS certificate: walk up from the leaf to a key it already trusts, and decide whether
to trust the leaf. Assignment 16 runs your checks over every chain in a PKI.

Once the compromised eMudhra intermediates left the trust store, browsers rejected them the same
way: the chains through them no longer reached a trusted key.

## The problem

Write a program that reads trust anchors and certificate chains and decides, for each chain,
whether a verifier should trust it, and if not, why.

### Trust anchors and chains

- A trust anchor is a public key the verifier already trusts. It has no certificate of its
  own: trust in it is axiomatic, the way a browser's root store works.
- A chain is a list of certificates, leaf first. Certificate 0, the leaf, is the one being
  checked. Certificate 1 (if present) signed it, certificate 2 (if present) signed certificate 1,
  and so on. Every certificate after the leaf is an intermediate.
- One of the trust anchors must have signed the last certificate in the list, the topmost
  one. The list holds no certificate for the anchor itself.

### The four checks, in order

Check a chain in this order, and stop at the first problem:

1. Signatures: the next certificate up must have signed each certificate below the topmost.
   Certificate `i + 1`'s public key must verify certificate `i`'s signature (your check from
   assignment 08). Then one of the trust anchors must have signed the topmost certificate. Try
   each anchor; one match is enough.
2. CA permission: every certificate that signed another one in the chain, which means every
   certificate except the leaf, must have BasicConstraints CA:TRUE (the `ca` field from
   assignment 06). A certificate without it can't sign other certificates, however good its
   signature is.
3. Path length: a certificate's path length constraint (the `pathlen` field from assignment
   06, when it has one) limits how many more intermediates may appear between it and the
   leaf. With the leaf at position 0 in the list, the certificate at position `i` has `i - 1`
   intermediates below it (closer to the leaf). If it has a path length constraint and `i - 1`
   is larger, the chain fails.
4. Validity: every certificate's validity window, `notBefore` through `notAfter`, must cover
   the given `now`. Every time string in this assignment is UTCTime in the same format, with a
   two-digit year (`250601000000Z` is 2025-06-01). Comparing the strings as text puts them in
   time order, so you don't need to parse dates.

If all four hold, the chain is trusted. Otherwise report the first problem, in the order above,
with one of these reasons:

| Reason | Meaning |
|---|---|
| `bad-signature` | A certificate below the topmost was not signed by the next one up |
| `unknown-anchor` | No given trust anchor verifies the topmost certificate's signature. This step has its own reason, separate from `bad-signature` |
| `not-a-ca` | A certificate that signed another one in the chain isn't marked CA:TRUE |
| `path-too-long` | More intermediates follow a certificate than its path length constraint allows |
| `expired` | Some certificate's validity window does not cover `now`. This includes "not yet valid": the assignment doesn't tell the two directions apart |

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file describes one or more chains:

| Line | Meaning |
|---|---|
| `chain <label>` | Starts a new chain. The lines up to the next `chain` line (or the end of the file) belong to it. `label` is a word with no spaces. |
| `now <time>` | The time to check validity against, in the same raw format as assignment 06's `notBefore`/`notAfter`. |
| `anchor <curve> <x> <y>` | A trusted public key: the curve name (`P-384` in these tests), then the point's coordinates in hex. A chain can have more than one. |
| `cert <hex>` | One certificate, DER in hex. Leaf first: each certificate is signed by the one on the next `cert` line. |

### Output

For each `chain` block, in input order, write one line:

```
chain <label> trusted
chain <label> untrusted <reason>
```

The checker ignores extra whitespace.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A valid 2-level chain: a trust anchor signed the leaf, and there are no intermediates.
- **R2** A valid 3-level chain: the leaf, one intermediate, then a trust anchor.
- **R3** No given trust anchor verifies the topmost certificate's signature: `unknown-anchor`.
- **R4** A certificate names the right issuer, but a different key signed it: `bad-signature`.
- **R5** An intermediate that signed another certificate in the chain isn't marked CA:TRUE:
  `not-a-ca`.
- **R6** An intermediate sets a path length constraint, and a later intermediate (closer to the
  leaf) breaks it: `path-too-long`. For contrast, a chain that meets its path length constraint
  with no room to spare is `trusted`.
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

One certificate and no intermediates: the trust anchor's key signed it.

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

The chain is the leaf, `IntB-6`, `IntA-6` and the anchor: three `cert` lines (the leaf, then each
signer going up) plus the anchor.

- `IntA-6` (the third `cert` line) has path length `0`, so no intermediate may appear between it
  and the leaf.
- `IntB-6` (the second `cert` line) sits there, one position closer to the leaf, so the chain
  fails the path length check.
- The key given as the trust anchor, `Root-6`, signed `IntA-6`.

### Example 3: signed by an unlisted root (test `09-R3-unknown-anchor`)

```
input:   chain c3
         now 250601000000Z
         anchor P-384 5101da4433353de6df962daf91e881337ea90bcfc516bd7a9f5237c30660eb8649730bde08dbbf841b2c331558c587b0 3cae8209eab991d23b39f65a1fb48824f58ad9bd3cb98f2ed1046d14564cb3f71c2cfd986522ff2f7c1825df856fcf50
         cert 308201503081d8a003020102020101300a06082a8648ce3d04030330173115301306035504030c0c556e6b6e6f776e2d526f6f74301e170d3235303530323030303030305a170d3236303630313030303030305a3011310f300d06035504030c064c6561662d333076301006072a8648ce3d020106052b81040022036200048cc1cbcb31f30b3f7452e79a4ac4cc3f8f9849b9398c6de3f7213c207a8e92cc0434ed0b70cc6a9de61c75ef8e74a53cd910fa5aceb8a8f7fb005c473ebf4e20348b708295629f29b04f8a421c3d29fe304f4b0c401a35469796dac357cb2e6d300a06082a8648ce3d0403030367003064023023538226362bdd8a133ac7528a797e8c2c2681d46c8eb33dbfa64edbbce5e2c270c2e7a4646865244d1aa4e143b25c6f0230655e8e82c7530fa3eccd1f3be1b634e70fcdb4b65208be30a8ddd272d428d08aaad661c951530f433da99857ee87251f

output:  chain c3 untrusted unknown-anchor
```

This certificate's issuer field says "Unknown-Root". The checks ignore names: what decides the
verdict is that no given `anchor` key verifies its signature. The `anchor` line here belongs to a
different, unrelated root.

## Constraints

- Every certificate is P-384 (assignment 08's constraint carries over).
- Every chain has at least one certificate (the leaf) and at most three (the leaf plus two
  intermediates) in these tests.
- Every time string, each certificate's `notBefore`/`notAfter` and each `now`, is UTCTime with a
  two-digit year, so string comparison gives time order. That would fail across a change of
  century; it holds here because every date in these tests falls in 2000-2099.
- There are 13 tests: 1 each for R1-R5, 2 for R6 (one violation, one chain that meets its
  constraint), 2 for R7 (both directions) and 4 end-to-end chains. Two of the end-to-end chains
  have the shape of the real incident. A leaf verifies through its intermediate while the
  intermediate's signer is a recognised anchor, and stops verifying once that signer is no longer
  offered as one. That models what distrusting an intermediate does to every certificate under
  it. Part of the set is random and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Parse each certificate with your `parse_certificate` from assignment 06: you need its `ca`,
`pathlen`, `not_before`, `not_after`, `curve` and `public_key`. Read its signed bytes and its
signature with `read_signed_data` from assignment 08, and `check_signature` tells you whether a
given key signed it. The rest is bookkeeping: four short loops over the certificates, one for
each check under "The four checks, in order".
</details>

<details><summary>Hint 2: the approach</summary>

Run one loop per check:

- signatures: the adjacent pairs, then the topmost certificate against each anchor;
- CA status: every certificate except the leaf;
- path length: the same certificates, with their positions;
- validity: every certificate.

Return as soon as a loop finds a problem. This assignment reports only the first problem, in the
order on this page, so there is no need to collect them all.
</details>

<details><summary>Hint 3: the traps</summary>

- The topmost certificate has no next certificate. Check its signature against the trust anchors,
  and accept a match with any of them.
- "Every certificate that signed another one" means every certificate except the leaf
  (certificate 0), and the topmost one counts. A 3-level chain (the leaf, one intermediate and an
  anchor) has one signer to check for CA status and path length: the intermediate.
- Path length counts the intermediates below a certificate (closer to the leaf). It doesn't
  count the leaf or the certificate itself. A path length of `0` on the certificate that signs
  the leaf is fine: it limits what may sit between that certificate and the leaf, and nothing
  does.
- `expired` covers both directions, so check both ends of the window: a certificate not yet
  valid at `now` fails, and so does one whose validity has ended.
- If the input gives more than one `anchor` line, trying only the first one rejects a chain that
  leads to one of the later ones.
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
.\check 09                              run every test
.\check 09 -Case 09-R6-path-too-long    one test, showing its full input, expected output and your output
.\check 09 -Fresh                       a new set of tests (new random seed), to confirm on data you haven't seen
.\check 09 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R6  An intermediate's path length constraint is violated by how many ... .    1 / 2   FAILED
      x 09-R6-path-too-long  IntA-6 asserts path length 0, but IntB-6 follows it before the leaf
          line 1: expected `chain c6 untrusted path-too-long`, got `chain c6 trusted`
          likely cause: R6 - An intermediate's path length constraint is violated by how many more intermediates follow it: path-too-long
          expected values from: openssl verify -attime <epoch> -CAfile <root> -untrusted <intermediates> <leaf> (OpenSSL's own path validation, independent of this workbook's reference)
          reproduce: py -P tools/run_py.py solutions 09 build/cases/09/09-R6-path-too-long.in build/cases/09/09-R6-path-too-long.out
```

## After you pass: compare with the post

eMudhra's statement describes the outcome (browsers blocked certificates issued through the
affected intermediates) and publishes no verification code, so there is no author's snippet to
compare with. The reference `pki/chain.py` uses `parse_certificate` from `x509/certificate.py`,
and `read_signed_data` and `check_signature` from `x509/signature.py`. It checks signatures, then
CA status, then path length, then validity, in that fixed order, and returns at the first
failure.

Every chain in these tests has at most one problem, so the order of
the four checks doesn't change any test's answer. A correct solution that checks validity first
and signatures last passes the same tests. The order decides which reason you report when a chain
has more than one problem, and no test has such a chain. To see the difference, build a chain
with two unrelated problems and look at which reason your program reports.
