# 16 · Audit a PKI

**Difficulty:** Hard · **Checkpoint** 16 of 16 (capstone) · **Check:** `./check.sh 16`

**Tags**
- *Language:* graphs built from dictionaries · structured state
- *Library:* none needed beyond what checkpoints 5-13 already use
- *Concepts:* key linting · chain validation · blast radius

## Read in the blog first

This is the capstone: it has no new source material of its own. Everything it asks for is a
combination of checkpoints 6, 9, 10 and 13, applied to a small public key infrastructure (PKI)
instead of one key or one chain at a time. If you want the story behind it, eMudhra's
[statement](https://emudhra.com/en/post/certificate-security-incident) is still the one to read.

## Where this fits

Every earlier checkpoint in this workbook answered one question about one key or one chain.
This one asks the question a real incident response actually has to answer: across an entire
PKI, which keys are bad, which chains are trusted, and if a given key turned out to be
compromised, **which chains would that actually break**? That last question, blast radius, is
new: it's exactly what eMudhra, Mozilla and Chrome had to work out within hours of disclosure,
not just "is this key bad" but "what does it reach."

## The problem

Write a program that audits a small PKI: every key gets linted, every chain gets validated, and
every key that signs something gets a report of which chains depend on it.

Only the program's output is checked, so you can structure it however you like and use any
language or library. The starter `solutions/p16_audit_pki.py` is a comment and an empty program:
reading the input and writing the output are yours. To start from working input/output code
instead, copy `starters/boilerplate/p16_audit_pki.py` over it, or pick Boilerplate in the book's
editor. The boilerplate reads the input and writes the output; you fill in `lint_key()`,
`parse_certificate()`, `validate_chain()` and `blast_radius()`.

### The three things you report

1. **Lint every key**, anchors included, with checkpoint 13's three checks in the same priority
   order: off-curve, known-compromised (on a blocklist), weak (a small private key, found by
   checkpoint 10's bounded search).
2. **Validate every chain**, with three of checkpoint 9's four checks, in the same order:
   signatures, CA permission, path length. This checkpoint's input has no `now` line, so there
   is nothing to check a certificate's validity window against: checkpoint 9 already covers that
   check thoroughly, and repeating it here would test the same thing twice, not teach anything
   new. One difference from checkpoint 9's other three checks: a chain here never names one
   specific anchor. Its topmost certificate must be signed by **any** anchor declared anywhere in
   this PKI, exactly like checkpoint 9's "try each" rule for multiple anchors, just applied
   across the whole PKI instead of one chain at a time.
3. **Report blast radius.** For every key that occupies a signer's position in some chain - an
   intermediate or anchor one step above a leaf or another intermediate - report every chain
   that depends on it. This is structural: it's about where a key sits in a chain's list, not
   whether every signature along that chain turned out to actually verify. A certificate that
   claims an issuer but didn't really get signed by it (`bad-signature`) still names that issuer
   as part of its structure, and the issuer still gets an `exposed` line for that chain - knowing
   a chain depends on a forged link is exactly the kind of thing an audit should surface, not
   hide. A leaf's own key never gets a report: nothing is signed with it.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains, in any order except as noted:

| Line | Meaning |
|---|---|
| `blocklist <curve> <x> <y>` | A known-compromised public key. Applies to every key declared after it (checkpoint 13's rule). |
| `anchor <id> <curve> <x> <y>` | A trust anchor: a public key the verifier already trusts, no certificate of its own. `id` is a word with no spaces, unique across every `anchor` and `cert` line. |
| `cert <id> <hex>` | A full DER certificate, same format as checkpoints 6-9. |
| `chain <chain-id> <id> <id> ...` | A chain: certificate ids only, leaf first, most-senior last. **No anchor id appears here** - the topmost certificate's signer is found among every declared anchor, not named in the chain. |

Every `anchor` and `cert` line must come before any `chain` line that uses its id.

### Output

Three kinds of line, in this order:

```
key <id> <ok|off-curve|known-compromised|weak>
chain <chain-id> <trusted|untrusted <reason>>
exposed <id> <chain-id> <chain-id> ...
```

- One `key` line per declared `anchor` or `cert`, in input order.
- One `chain` line per `chain` block, in input order. `<reason>` is one of `bad-signature`,
  `unknown-anchor`, `not-a-ca`, `path-too-long` - four of checkpoint 9's five words. `expired`
  never appears here: this checkpoint has no `now` line, so there is nothing to check a
  certificate's validity window against (see "Validate every chain" above).
- One `exposed` line per key that occupies a signer's position in **some** chain (structurally,
  as above), in input order, listing every chain id that depends on it (space-separated, in the
  order those chains were declared). A key nothing depends on gets no `exposed` line at all - not
  even an empty one.

The checker ignores extra whitespace.

## Requirements

Each test case is designed around one of these. A failing test also shows which requirement it
was written to cover.

- **R1** Every key is linted, anchors included, in input order: off-curve, known-compromised,
  weak or ok, in that priority. A key that is both weak and blocklisted reports
  known-compromised, because that check runs first.
- **R2** Every chain is validated in input order, with three of checkpoint 9's checks
  (signatures, CA permission, path length - not validity, which this checkpoint has no `now`
  line to check against) and four of its reason words, except that the topmost certificate's
  signer is any declared anchor, not one named in the chain.
- **R3** Every key that occupies a signer's position in at least one chain gets an `exposed`
  line listing every chain that depends on it. A leaf's own key gets none.
- **R4** A key shared by two chains (the same intermediate, or the same anchor, signs both) is
  exposed by both - the actual blast-radius lesson: one compromised key can threaten more than
  one chain at once.
- **R5** Both curves' keys lint correctly. Full chain validation in this checkpoint is P-384
  only, matching checkpoints 6-9's own scope (a P-256 certificate would need SHA-256 instead of
  SHA-384); a P-256 key here is linted but never put in a chain.

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

`off-curve-anchor` has the same x as `root1` but y shifted by 1, so it fails the curve equation.
It isn't used by any chain, but every declared key still gets linted. `root1` really does sign
`leaf1`, so the chain is trusted against it, and `root1` picks up an `exposed` line.

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

`int-weak`'s private key is exactly 4, the value checkpoint 10 recovers for the real incident's
example key. The chain is still structurally `trusted` - linting and chain validation are
separate questions - but `int-weak`'s own `key` line, and its `exposed` line, are exactly what
this checkpoint is for: knowing both that the key is bad and what depends on it.

### Example 3: the leaf's real signer was never declared (test `16-R2-unknown-anchor`)

```
input:   anchor rootF P-384 <...>
         cert leafF <hex, issued by "Unrelated-Root", a key never declared as an anchor here>
         chain c-unknown leafF

output:  key rootF ok
         key leafF ok
         chain c-unknown untrusted unknown-anchor
```

`leafF` is a perfectly well-formed certificate, and `rootF` is a perfectly good anchor - they
just have nothing to do with each other. No declared anchor's key verifies `leafF`'s signature,
so the chain is `unknown-anchor`. Neither key gets an `exposed` line: `rootF` never actually
signed anything in this PKI, and `leafF` is the chain's own leaf.

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
compromised, both chains would need to be re-issued, not just one. `rootG` is exposed by both for
the same reason, one level further up.

## Constraints

- Every certificate is P-384, matching checkpoints 6-9's scope. A P-256 key may appear as an
  `anchor` or a standalone `cert` for linting, but never inside a `chain` line.
- Ids (`anchor` and `cert` together) are unique within one input. A `chain` line's ids all refer
  to already-declared `cert` lines.
- There is no `now` line and no `expired` reason in this checkpoint: validity was already
  checkpoint 9's lesson, and this checkpoint's own new idea is blast radius, not a repeat of
  that check.
- Each case has a 10-second limit. Checkpoint 10's bounded search (used for linting) is the same
  budget as checkpoint 13's, not a larger one.
- There are 12 tests: the examples above, both curves, a key that's both weak and blocklisted
  (R1), every checkpoint-9-style reason reached through this checkpoint's own "any anchor" rule
  (R2), a 2-level chain confirming a leaf gets no `exposed` line (R3), and an end-to-end PKI
  shaped like the real incident: one root, a weak intermediate signing two leaves, a strong
  intermediate signing a third. Part of the set is random and changes with `-Fresh`.

## Source material

- Every earlier checkpoint in this workbook, especially 6, 9, 10 and 13
- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident)

## Hints

<details><summary>Hint 1: where to start</summary>

Nothing here is new arithmetic. `lint_key` is checkpoint 13's function, unchanged.
`parse_certificate` is checkpoint 6's field reading (plus checkpoint 8's `tbs_bytes`, `sig_r`,
`sig_s`, which `validate_chain` needs). The only genuinely new piece is `blast_radius`, and
that's bookkeeping, not cryptography.
</details>

<details><summary>Hint 2: the approach</summary>

Keep every declared key (anchor or cert) in one lookup from id to its curve, x, y and - for
certs only - its parsed certificate. Lint every one of them up front. For each chain, walk its
certificate ids exactly like checkpoint 9, except the very last step: instead of checking one
named anchor, loop over every declared anchor and stop at the first one that verifies. Remember
*which* anchor matched (or that none did) - you need that for blast radius, not just for the
chain's own `trusted`/`untrusted` line.
</details>

<details><summary>Hint 3: the traps</summary>

- The priority order for linting is off-curve, then known-compromised, then weak. A key that's
  both weak and blocklisted must report known-compromised.
- "Any declared anchor" means looping over all of them for the topmost certificate, not stopping
  at the first one declared - a chain can validate against an anchor that comes after an
  unrelated one in the input.
- Blast radius counts a cert's signer position (every id in a chain's list except the leaf,
  position 0) **and** whichever anchor actually verified the topmost cert - both contribute
  `exposed` lines, not just the certs.
- A chain that fails at "unknown-anchor" contributes no anchor `exposed` line (no anchor
  verified it), but its intermediates still do, if it has any - exposure from a mid-chain
  signature is about structure, not about whether the chain ultimately validates.
- Don't give a key an `exposed` line with an empty list. If nothing depends on it, leave it out
  entirely.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
for each declared key (anchor or cert), in order:
    print "key", id, lint_key(curve, x, y, blocklist) or "ok"

matched = {}  # chain_id -> which anchor verified it, or none
for each chain, in order:
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
    # no validity step here: there is no "now" in this checkpoint's input (checkpoint 9 covers it)
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
./check.sh 16                              run every test
./check.sh 16 -Case 16-R2-unknown-anchor   one test, showing its full input, expected output and your output
./check.sh 16 -Fresh                       a new set of tests (new random seed)
./check.sh 16 -Dispute <id> "why"          set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R1  Every key is linted (anchors included), in input order: off-curve... .    4 / 5   FAILED
      x 16-R1-priority  a key that is both weak (d=56) and on the blocklist: known-compromised wins (checked first)
          line 2: expected `key weak-and-blocked known-compromised`, got `key weak-and-blocked weak`
          likely cause: R1 - Every key is linted (anchors included), in input order: off-curve, known-compromised, weak or ok, in that priority - same rules as checkpoint 13
          expected values from: cryptography 41.0.7 / OpenSSL (key checks and openssl verify): independent of this checkpoint's own lint, chain and blast-radius logic
          reproduce: python3 -P tools/run_py.py solutions 16 build/cases/16/16-R1-priority.in build/cases/16/16-R1-priority.out
```

## After you pass: what this checkpoint doesn't do

A real relying party does more than this: it checks revocation (OCSP, CRLs, OneCRL), enforces
Certificate Transparency, and applies name constraints and extended key usage, none of which this
workbook covers. What you've built here is the part of the lesson that doesn't change: a weak key
is a weak key regardless of which of these mechanisms eventually catches it, and knowing what a
key reaches is what turns "this key is bad" into an actual incident response, the same shape of
work eMudhra, Mozilla and Chrome all did within hours of the real disclosure.

You've now rebuilt, from modular arithmetic up, the exact chain of reasoning that made eight
weak intermediate keys a same-day incident instead of a quiet footnote: the maths that makes a
key pair work, the format that carries a key between systems, the chain that decides whether to
trust it, the search that breaks a bad one, and the checks that would have caught it first.
