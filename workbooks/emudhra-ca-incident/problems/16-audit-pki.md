# 16 · Audit a PKI

**Difficulty:** Hard · **Assignment** 16 of 19 (capstone) · **Check:** `.\check 16`

**Tags**
- *Language:* graphs built from dictionaries · structured state
- *Library:* none needed beyond what assignments 05 to 13 already use
- *Concepts:* key linting · chain validation · blast radius

## Read in the blog first

This page is complete on its own. The capstone has no new source material: it combines
assignments 06, 09, 10 and 13 and applies them to a small public key infrastructure (PKI), a set
of trust anchors, certificates and chains, instead of one key or one chain at a time.
For the story behind it, eMudhra's
[statement](https://emudhra.com/en/post/certificate-security-incident) is still the one to read.

## Source material

- Every earlier assignment in this workbook, above all 06, 09, 10 and 13
- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident)

## Where this fits

Each earlier assignment answered one question about one key or one chain. This one asks the
questions an incident response has to answer across a whole PKI: which keys are bad, which chains
a verifier trusts, and, if a given key turned out to be compromised, which chains it would
break. That last question, the key's blast radius, is new. eMudhra, Mozilla and Chrome had to
work it out within hours of the disclosure: what a bad key reaches, as well as whether it's bad.

Your new `pki/audit.py` puts your earlier modules together: `lint_key` from your `pki/lint.py`
(assignment 13), `validate_chain` and `Anchor` from your `pki/chain.py` (assignment 09),
`parse_certificate` from your `x509/certificate.py` (assignment 06), and the curves in your
`ecc/curve.py` and `ecc/curves.py`. This is the last part of your project: `__main__.py` turns it
into a program you can run, `pkiaudit audit <pki-file>`.

## The problem

Write a program that audits a small PKI: it lints every key, validates every chain, and reports,
for every key that signs something, the chains that depend on it.

### The three things you report

1. Lint every key, anchors included, with assignment 13's three checks in the same priority
   order: off-curve, known-compromised (on the blocklist), and weak (a private key `d` or `n - d`
   with `d` at most 4096, found by assignment 10's bounded search). In assignment 13 the blocklist grew as the program read. Here
   every `blocklist` line applies to every key in the file, including keys declared before it.
2. Validate every chain with three of assignment 09's four checks, in the same order:
   signatures, CA permission and path length. The input has no `now` line, so there is no time to
   check a certificate's validity window against. Assignment 09 covers that check, and repeating
   it here would test the same thing twice. A chain here names no anchor: its topmost certificate
   must be signed by any anchor declared anywhere in this PKI. That's assignment 09's "try
   each" rule for several anchors, applied to every anchor in the PKI.
3. Report the blast radius of every key that sits in a signer's position in some chain (an
   intermediate or anchor one step above a leaf or another intermediate): every chain that
   depends on it. This is structural: it follows where a key sits in a chain's list, whether or
   not every signature along that chain verifies. A certificate that names an issuer that didn't
   sign it (`bad-signature`) still has that issuer in its structure, so the issuer still gets an
   `exposed` line for that chain. A chain that depends on a forged link is a finding an audit
   should surface. A leaf's own key gets no report, because it signs nothing.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains, in any order except as noted:

| Line | Meaning |
|---|---|
| `blocklist <curve> <x> <y>` | A known-compromised public key. It applies to every key in the file, wherever the `blocklist` line appears, so read the whole file before you lint any key. |
| `anchor <id> <curve> <x> <y>` | A trust anchor: a public key the verifier already trusts, with no certificate of its own. `id` is a word with no spaces, unique across every `anchor` and `cert` line. |
| `cert <id> <hex>` | A full DER certificate, in the same format as assignments 06 to 09. |
| `chain <chain-id> <id> <id> ...` | A chain: certificate ids only, leaf first, most senior last. No anchor id appears here: your program finds the topmost certificate's signer among all the declared anchors. |

Every `anchor` and `cert` line comes before any `chain` line that uses its id.

### Output

Three kinds of line, in this order:

```
key <id> <ok|off-curve|known-compromised|weak>
chain <chain-id> <trusted|untrusted <reason>>
exposed <id> <chain-id> <chain-id> ...
```

- One `key` line per declared `anchor` or `cert`, in input order.
- One `chain` line per `chain` line, in input order. `<reason>` is one of `bad-signature`,
  `unknown-anchor`, `not-a-ca` and `path-too-long`, four of assignment 09's five words. `expired`
  never appears, because the input has no `now` line to check validity windows against (see
  "Validate every chain" above).
- One `exposed` line per key that sits in a signer's position in some chain (by structure,
  as above), in input order. It lists every chain id that depends on the key, separated by
  spaces, in the order the input declares those chains. A key that no chain depends on gets no
  `exposed` line, not even an empty one.

The checker ignores extra whitespace.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** Every key is linted, anchors included, in input order: off-curve, known-compromised,
  weak or ok, in that priority. A key that is both weak and blocklisted reports
  known-compromised, because that check runs first.
- **R2** Every chain is validated in input order with three of assignment 09's checks
  (signatures, CA permission and path length, but not validity, which the input has no `now`
  line for) and four of its reason words. The topmost certificate's signer is any declared
  anchor, since the chain names none.
- **R3** Every key that sits in a signer's position in at least one chain gets an `exposed` line
  listing every chain that depends on it. A leaf's own key gets none.
- **R4** A key shared by two chains (the same intermediate, or the same anchor, signs both) is
  exposed by both. This is the blast-radius lesson: one compromised key can threaten more than
  one chain at once.
- **R5** Keys on both curves get the right lint finding. Full chain validation here is P-384 only, matching the
  scope of assignments 06 to 09 (a P-256 certificate would need SHA-256 instead of SHA-384), so a
  P-256 key is linted but never put in a chain.

## Examples

### Example 1: an anchor key off the curve, alongside a clean chain (test `16-R1-off-curve`)

```
input:   anchor off-curve-anchor P-384 f3ef666c9d167c1b012da9b0343fe017dec1597a2ef6fdbcd6a03ed878e09e499a05b8b3bd035fd09efe358b97a62de7 f69e63e4fc03a6fbfe16d399f5c0dcfa4a1ca59209a7591488e99540bc0796ceadabd4282cf42c9425ffaabe89396787
         anchor root1 P-384 f3ef666c9d167c1b012da9b0343fe017dec1597a2ef6fdbcd6a03ed878e09e499a05b8b3bd035fd09efe358b97a62de7 f69e63e4fc03a6fbfe16d399f5c0dcfa4a1ca59209a7591488e99540bc0796ceadabd4282cf42c9425ffaabe89396786
         cert leaf1 <hex, a certificate issued by root1>
         chain c1 leaf1

output:  key off-curve-anchor off-curve
         key root1 ok
         key leaf1 ok
         chain c1 trusted
         exposed root1 c1
```

`off-curve-anchor` has the same x as `root1`, with y one higher, so it fails the curve equation.
No chain uses it, but your program lints every declared key. `root1` signs `leaf1`, so the chain is
trusted against it, and `root1` gets an `exposed` line.

### Example 2: the recovered incident value (test `16-R1-weak-d4`)

```
input:   anchor root2 P-384 <...>
         cert int-weak <hex, a CA certificate issued by root2, private key d=4>
         cert leaf-under-weak <hex, issued by int-weak>
         chain c1 leaf-under-weak int-weak

output:  key root2 ok
         key int-weak weak
         key leaf-under-weak ok
         chain c1 trusted
         exposed root2 c1
         exposed int-weak c1
```

`int-weak`'s private key is 4, the value assignment 10 recovers for the real incident's example
key. The chain still validates as `trusted`, because linting and chain validation are separate
questions. `int-weak`'s own `key` line and its `exposed` line are what this assignment is for:
they say that the key is bad and what depends on it.

### Example 3: the leaf's real signer was never declared (test `16-R2-unknown-anchor`)

```
input:   anchor rootF P-384 <...>
         cert leafF <hex, issued by "Unrelated-Root", a key never declared as an anchor here>
         chain c-unknown leafF

output:  key rootF ok
         key leafF ok
         chain c-unknown untrusted unknown-anchor
```

`leafF` is a well-formed certificate and `rootF` is a good anchor, but they have nothing to do
with each other. No declared anchor's key verifies `leafF`'s signature, so the chain is
`unknown-anchor`. Neither key gets an `exposed` line: `rootF` signed nothing in this PKI, and
`leafF` is the chain's own leaf.

### Example 4: one intermediate, two chains (test `16-R3-R4-shared-intermediate`)

```
input:   anchor rootG P-384 <...>
         cert sharedG <hex, a CA certificate issued by rootG>
         cert leafG1 <hex, issued by sharedG>
         cert leafG2 <hex, issued by sharedG>
         chain c1 leafG1 sharedG
         chain c2 leafG2 sharedG

output:  key rootG ok
         key sharedG ok
         key leafG1 ok
         key leafG2 ok
         chain c1 trusted
         chain c2 trusted
         exposed rootG c1 c2
         exposed sharedG c1 c2
```

`sharedG` signs both leaves, so both `c1` and `c2` depend on it: if `sharedG`'s key were
compromised, both chains would need new certificates. `rootG` is exposed by both chains for the
same reason, one level further up.

## Constraints

- Every certificate is P-384, matching the scope of assignments 06 to 09. A P-256 key may appear
  as an `anchor` or a standalone `cert` for linting, but never inside a `chain` line.
- Ids (`anchor` and `cert` together) are unique within one input. A `chain` line's ids all refer
  to `cert` lines declared before it.
- The input has no `now` line and no `expired` reason. Validity was assignment 09's lesson, and
  this assignment's new idea is blast radius.
- Each case has a 10-second limit. The bounded search that linting uses (assignment 10's) has the
  same budget as in assignment 13.
- There are 13 tests: the examples above, both curves, an intermediate whose private key is
  `n - 4` and a key that's both weak and blocklisted (R1), the `not-a-ca`, `path-too-long` and `unknown-anchor` reasons reached through this
  assignment's "any anchor" rule (R2), a 2-level chain confirming that a leaf gets no `exposed`
  line (R3), and an end-to-end PKI shaped like the real incident: one root, a weak intermediate
  signing two leaves, and a strong intermediate signing a third. Part of the set is random and
  changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

`lint_key` is your `pki/lint.py` from assignment 13, unchanged.
`parse_certificate` from your `x509/certificate.py` (assignment 06) gives each certificate's curve
and public key. `validate_chain` from your `pki/chain.py` (assignment 09) already tries every
anchor it's given. The new pieces are `read_pki`, `blast_radius`, `audit` and the report's
`lines`, and they're bookkeeping, with no new cryptography.
</details>

<details><summary>Hint 2: the approach</summary>

`read_pki` keeps every declared key (anchor or cert) in one dictionary from id to its curve and
public key, in input order. It also keeps the anchors as a list of `Anchor` values and each
certificate's DER under its id. `audit` lints every key against the whole blocklist, then calls
`validate_chain` on each chain's certificates with every anchor in the PKI and no `now`. Keep each
chain's `ChainResult`: its `anchor` field says which anchor verified the topmost certificate (or
that none did), and `blast_radius` needs that as well as the verdict. If your assignment 09
`validate_chain` leaves `anchor` empty, fill it in now.
</details>

<details><summary>Hint 3: the traps</summary>

- The priority order for linting is off-curve, then known-compromised, then weak. A key that's
  both weak and blocklisted must report known-compromised.
- Every `blocklist` line applies to every key, including keys declared above it. Read the whole
  file before you lint anything.
- "Any declared anchor" means trying all of them for the topmost certificate, not stopping at the
  first one declared. A chain can validate against an anchor that comes after an unrelated one in
  the input.
- Blast radius counts every id in a chain's list except the leaf (position 0), and whichever
  anchor verified the topmost certificate. Both kinds of key get `exposed` lines.
- A chain that fails with `unknown-anchor` contributes no anchor `exposed` line, since no anchor
  verified it, but its intermediates still do, if it has any. Exposure from a mid-chain signer
  comes from the chain's structure, whether or not the chain validates.
- Don't give a key an `exposed` line with an empty list. If nothing depends on it, leave it out.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
for each declared key (anchor or cert), in order:
    print "key", id, lint_key(curve, (x, y), blocklist) or "ok"

matched = {}  # chain_id -> which anchor verified it, or none
for each chain, in order:
    # your validate_chain(certs, anchors) from assignment 09 does this part
    certs = [parsed cert for each id in the chain]
    ok = true
    for i in 0 .. len(certs) - 2:
        if not signed_by(certs[i], certs[i+1]): ok = false, reason = "bad-signature"; break
    if ok:
        matched[chain_id] = first anchor whose key verifies certs[-1], or none
        if matched[chain_id] is none: ok = false, reason = "unknown-anchor"
    if ok:
        for cert in certs[1:]: if not cert.ca: ok = false, reason = "not-a-ca"; break
    if ok:
        for i in 1 .. len(certs)-1: if path length violated: ok = false, reason = "path-too-long"; break
    # no validity step here: there is no "now" in this assignment's input (assignment 09 covers it)
    print "chain", chain_id, "trusted" if ok else "untrusted " + reason

exposed = {}  # id -> [chain ids]
for each chain:
    for id in chain.ids[1:]: exposed[id].append(chain_id)       # certs that signed something
    if matched[chain_id] is not none: exposed[matched[chain_id]].append(chain_id)  # the anchor
for each declared key, in order:
    if id in exposed: print "exposed", id, *exposed[id]
```
</details>

## Checking your solution

```
.\check 16                                run every test
.\check 16 -Case 16-R2-unknown-anchor     one test, showing its full input, expected output and your output
.\check 16 -Fresh                         a new set of tests (new random seed)
.\check 16 -Dispute <id> "why"            set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R1  Every key is linted (anchors included), in input order: off-curve... .    5 / 6   FAILED
      x 16-R1-priority  a key that is both weak (d=56) and on the blocklist: known-compromised wins (checked first)
          line 2: expected `key weak-and-blocked known-compromised`, got `key weak-and-blocked weak`
          likely cause: R1 - Every key is linted (anchors included), in input order: off-curve, known-compromised, weak or ok, in that priority, by the same rules as assignment 13
          expected values from: cryptography 41.0.7 / OpenSSL (key checks and openssl verify): independent of this assignment's own lint, chain and blast-radius logic
          reproduce: py -P tools/run_py.py solutions 16 build/cases/16/16-R1-priority.in build/cases/16/16-R1-priority.out
```

To run the finished command on the sample PKI in your project, use
`py -P tools/run_py.py solutions -m pkiaudit audit solutions/examples/sample.pki`.

## After you pass: what this assignment doesn't do

A real relying party does more than this. It checks revocation (OCSP, CRLs, OneCRL), enforces
Certificate Transparency, and applies name constraints and extended key usage. This assignment
covers none of them, and the three assignments after it cover part: 17 searches far larger bounds
for a weak key, 18 checks the signature on a revocation list, and 19 works out which clients still
accept a chain once revocation, blocklists and CT disagree. The part of the lesson you built here holds whichever of these mechanisms
catches a weak key in the end: an incident response needs to know which chains a bad key reaches,
as well as that it is bad. That's the work eMudhra, Mozilla and Chrome all did within hours of the
real disclosure.

You've now rebuilt, from modular arithmetic up, the reasoning that made eight weak intermediate
keys a same-day incident: the maths that makes a key pair work, the format that carries a key
between systems, the chain that decides whether to trust it, the search that breaks a bad one,
and the checks that find it before anyone trusts it. Assignments 17 to 19 go further, and the
project is complete without them.
