# 15 · Block and distrust

**Difficulty:** Easy · **Assignment** 15 of 19 · **Check:** `.\check 15`

**Tags**
- *Language:* parsing a small log format · sets
- *Library:* none needed
- *Concepts:* SPKI pinning/blocking · root distrust · cross-signing · CRLSet-style revocation · response speed vs. blast radius

## Read in the blog first

This page is complete on its own. Google's post
[Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA Certificates](https://blog.google/security/protecting-chrome-and-android-users-from-compromised-emudhra-intermediate-ca-certificates/#:~:text=blocks%20by%20SPKI)
(October 20, 2026) describes Chrome's response in two parts. At 19:45 UTC on October 17, Chrome
landed a CRLSet update that blocked the SPKI hashes of the affected intermediate CAs, and the post
says that because the update "blocks by SPKI, Chrome users were immediately protected against all
certificates sharing those keys". Chrome also removes the root above them, emSign ECC Root CA - G3,
from the Chrome Root Store, "to support other consumers of the Chrome Root Store that do not
consume CRLSet updates"; the post expects that change to reach users on October 27. eMudhra's
[Update 1](https://emudhra.com/en/post/certificate-security-incident#:~:text=Update%201)
quotes Mozilla's response through OneCRL and NSS.

The weak keys also sat under a second root. Sectigo cross-signed the eight intermediates under its
AAA Certificate Services root in May 2025, so each key appears in two certificates, 16 in all
(Scott Helme; Mozilla bug 2083449, comment 2). A chain through a Sectigo cross-certificate ends at
AAA Certificate Services and doesn't reach the emSign root, so distrusting the emSign root leaves
it alone. A block by SPKI hash stops both copies of a key, because both certificates carry the
same public key. This assignment models both mechanisms and the difference between them.

## Source material

- Google, [Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA Certificates](https://blog.google/security/protecting-chrome-and-android-users-from-compromised-emudhra-intermediate-ca-certificates/) (Chrome and Android Security Teams, October 20, 2026): the CRLSet update that blocked the intermediates' SPKI hashes, and the removal of emSign ECC Root CA - G3 from the Chrome Root Store
- Mozilla, [bug 2083449](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449): comment 0 (the OneCRL block, and eMudhra notifying Sectigo), comment 2 (CRLSet sequence 10843 lists the six TLS keys as revoked; the eight Sectigo cross-certificates), comment 6 (Sectigo on which root stores trust AAA Certificate Services), comment 13 (Sectigo revokes the cross-certificates), comment 30 (Chrome Root Store v43 and its expected date)
- Scott Helme, [Eight bits of trust](https://scotthelme.co.uk/eight-bits-of-trust-emudhras-ca-keys-cracked-in-milliseconds/): the Sectigo cross-signing, 16 certificates for 8 keys, and the CRLSet and OneCRL blocks
- Cisco Talos, [Compromised intermediate certificates](https://blog.talosintelligence.com/compromised-intermediate-certificates/): Go's SPKI filter, and Microsoft's block of the two code-signing certificates
- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 1 (quoting Mozilla's OneCRL/NSS response)
- Assignment 13 (`problems/13-key-linter.md`): the blocklist idea this assignment extends across a whole chain

## Where this fits

Your `pki/lint.py` from assignment 13 found a bad key by inspecting it. This assignment covers the
next step, at the scale of a browser's trust store: once someone knows that a key or a root is bad,
the browser withdraws trust in it for every certificate it signed.

The SPKI hash is the value your `x509/spki.py` computes in assignment 07. Here the input gives it
to you, so your new `pki/trust.py` needs none of your earlier modules. Assignment 19 calls your `check_chain`
once per client.

## The problem

Write a program that decides, for each certificate chain it reads, whether anything in it is
blocked.

### Two ways to block a chain

1. SPKI blocking: the browser blocks one public key, named by its SPKI hash (a hash of the
   certificate's SubjectPublicKeyInfo, the field that holds its public key), wherever it appears,
   in any certificate of any chain. It's fast to issue and exact, because it blocks that one key
   and nothing else. Chrome's CRLSet did this in the real incident, within hours.
2. Root distrust: the browser distrusts a whole root certificate, named by an id. Every chain
   that leads back to that root is blocked, including certificates whose own keys aren't on any
   blocklist. This is coarser, since it can affect certificates that were fine on their own, and
   it was the precautionary step in this incident.

Root distrust reaches only the chains that end at the distrusted root. A cross-certificate puts the
same key under a second root, and a chain through it ends at that second root. If the client still
trusts the second root, root distrust leaves the chain trusted, and only an SPKI block stops it.

The two mechanisms are independent, and either one blocks a chain on its own. If a chain's own
certificates trigger both, report the SPKI block: it's the more specific, faster-acting
mechanism, and the one a response like this one would issue first.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains these kinds of lines, which may come in any order before and between
`chain` blocks:

| Line | Meaning |
|---|---|
| `blocked-spki <hash>` | Adds one SPKI hash to the blocklist. It applies to every `chain` that follows it, in any certificate, at any position. |
| `distrusted-root <root-id>` | Adds one root id to the distrust set. It applies to every `chain` that follows it, whenever that chain's own root carries this id. |
| `chain <id>` | Starts a certificate chain. Every `cert` line after it, until the next `chain` line (or the end of the input), belongs to this chain. |
| `cert <role> <spki-hash> <root-id>` | One certificate in the current chain. `role` is `leaf`, `intermediate` or `root`, and a chain's certs come leaf to root. `spki-hash` is the SPKI hash of that certificate's public key. `root-id` is the identifier checked against the distrust set, and only means something for a `root` cert; for a `leaf` or `intermediate` cert it is always the placeholder `-`. |

This assignment covers the blocking policy. Parsing real certificates was the work of assignments
05 to 09, so the input gives each SPKI hash and root id as a plain hex or word token, standing in
for what a real chain's DER would carry.

### Output

For each `chain` block, in input order, write one line:

```
chain <id> trusted                     nothing in the chain is blocked
chain <id> blocked spki <role>         the FIRST cert (leaf to root) whose SPKI hash is blocklisted
chain <id> blocked root <root-id>      the chain's root id is in the distrust set, and no SPKI hash matched first
```

Copy `<id>` from the input unchanged. The checker ignores extra whitespace.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A chain with nothing blocklisted or distrusted anywhere in it is `trusted`.
- **R2** A certificate (leaf, intermediate or root) whose SPKI hash is on the blocklist blocks the
  whole chain: `blocked spki <role>`, naming that certificate, even if nothing else about the
  chain looks wrong.
- **R3** A chain whose root id is in the distrust set, with no SPKI hash anywhere in the chain on
  the blocklist, is `blocked root <root-id>`.
- **R4** When a chain's own certificates trigger both mechanisms (an SPKI hit and a distrusted
  root), the output reports the SPKI block, not the root distrust.
- **R5** A blocklist or distrust entry meant for some other chain's certificates doesn't affect a
  chain whose own certificates don't match it, and an entry affects only the chains that come after
  it in the input.
- **R6** A blocked key blocks every chain it appears in, including a cross-signed chain that ends
  at a root that is not distrusted. With the root distrust alone, that chain stays `trusted`.

## Examples

### Example 1: an intermediate's key is blocked everywhere (test `15-R2-spki-blocked-intermediate`)

```
input:   blocked-spki <hash of the compromised intermediate's key>
         chain c1
         cert leaf <leaf's own hash> -
         cert intermediate <the compromised hash> -
         cert root <root's own hash> root-beta

output:  chain c1 blocked spki intermediate
```

The leaf and the root are fine on their own. The intermediate's key is the compromised one, and
blocking it by SPKI hash stops every chain built on it at once, without touching the root.

### Example 2: both mechanisms could apply (test `15-R4-spki-wins-over-root`)

```
input:   blocked-spki <hash>
         distrusted-root root-both
         chain c1
         cert leaf <hash> -
         cert intermediate <the same blocked hash> -
         cert root <hash> root-both

output:  chain c1 blocked spki intermediate
```

The root is also on the distrust list, but the output reports the SPKI block. It's the more
specific finding: it names the key that's bad, which tells a responder more than "this whole root
is under precautionary distrust".

### Example 3: a cross-signed copy of a blocked key (test `15-R6-distrust-alone-misses-cross-sign`)

```
input:   distrusted-root root-home
         chain own-root
         cert leaf f04fcaed90842c2289cc99580382798a76cc64cb5b3260d7619ef836cc7136ec -
         cert intermediate 4991a86aee63e9d1e8d8a3d184b67b03e2c24ceb137b36e817cf7319cbf834df -
         cert root de420ff5d0fdee7e5decf09a715ce8174acd2af25b278023f87df5117ecc8c8c root-home
         chain cross-before
         cert leaf 246e051559f96349b724a19295200eb13c0d9f7bd154e973d0704aadcb6cd480 -
         cert intermediate 4991a86aee63e9d1e8d8a3d184b67b03e2c24ceb137b36e817cf7319cbf834df -
         cert root d448388dee04104134f164b8d89307fbab6e4ac6639b126233ad838fe9b074ca root-other
         blocked-spki 4991a86aee63e9d1e8d8a3d184b67b03e2c24ceb137b36e817cf7319cbf834df
         chain cross-after
         cert leaf 246e051559f96349b724a19295200eb13c0d9f7bd154e973d0704aadcb6cd480 -
         cert intermediate 4991a86aee63e9d1e8d8a3d184b67b03e2c24ceb137b36e817cf7319cbf834df -
         cert root d448388dee04104134f164b8d89307fbab6e4ac6639b126233ad838fe9b074ca root-other

output:  chain own-root blocked root root-home
         chain cross-before trusted
         chain cross-after blocked spki intermediate
```

All three chains carry the intermediate key `4991a8...`. The first ends at `root-home`, which is
distrusted. The second reaches the same key through a cross-certificate and ends at `root-other`,
which the input doesn't distrust, so with only the root distrusted it is `trusted`. Once `blocked-spki` names
the key, the third chain, identical to the second, is `blocked spki intermediate`.

## Constraints

- `blocked-spki` and `distrusted-root` lines, and `chain`/`cert` blocks, may appear in any order,
  but a `blocked-spki` or `distrusted-root` line only ever affects chains that come after it.
- Every chain has exactly one `leaf`, at least one `intermediate`, and exactly one `root`, leaf to
  root in that order. An input has at most 8 chains.
- Each case has a 10-second limit; this assignment does no heavy computation.
- There are 11 tests: 1 for R1, 3 for R2 (one per role), 1 for R3, 1 for R4, 2 for R5, 2 for R6
  (a blocked key in a chain to the distrusted root and in a cross-signed chain to another root),
  and 1 end-to-end case with five chains covering every verdict in one input. Part of the set is
  random and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Treat this as two separate checks in a fixed order. First, look for a certificate in the chain
whose key is on the blocklist. Only if there's none, check whether the chain's root is distrusted.
Keep them as two steps rather than one combined check.
</details>

<details><summary>Hint 2: the approach</summary>

The program keeps two sets that grow as it reads the input: blocked SPKI hashes and distrusted
root ids. Your `check_chain` scans the chain's certificates leaf to root, and the first one whose
SPKI hash is on the blocklist decides the verdict. If none match, it looks at the chain's `root`
certificate (a chain has only one) and checks its root id against the distrust set.
</details>

<details><summary>Hint 3: the traps</summary>

- A `blocked-spki` or `distrusted-root` line only applies to chains that come after it in the
  input, the same way assignment 10's `bound` line works. Don't apply it to earlier chains.
- The SPKI check runs first, over every certificate in the chain, including the leaf and the
  intermediates. The compromised key could belong to a leaf, an intermediate or a root.
- Only a `root` certificate's `root-id` field means anything. A `leaf` or `intermediate`
  certificate's third field is the placeholder `-`, so don't compare it with the distrust set.
- An entry in either set that matches nothing in a particular chain has no effect on that chain.
  Keep one chain's problem out of another chain's verdict.
- The same key can sit under two roots. Check the blocklist on every chain, whatever root it ends
  at.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
check_chain(chain, blocked_spki, distrusted_roots):
    for cert in chain:                            # leaf to root
        if cert.spki in blocked_spki:
            return Block("spki", cert.role)
    for cert in chain:
        if cert.role == "root" and cert.root_id in distrusted_roots:
            return Block("root", cert.root_id)
    return None   # trusted
```
</details>

## Checking your solution

```
.\check 15                                         run every test
.\check 15 -Case 15-R4-spki-wins-over-root         one test, showing its full input, expected output and your output
.\check 15 -Fresh                                  a new set of tests (new random seed), to confirm on data you haven't seen
.\check 15 -Dispute <id> "why"                     set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  When both could apply to the same chain, the SPKI block is report... .    0 / 1   FAILED
      x 15-R4-spki-wins-over-root  the intermediate is SPKI-blocklisted AND the root is distrusted: the SPKI block is reported
          line 1: expected `chain c1 blocked spki intermediate`, got `chain c1 blocked root root-both`
          likely cause: R4 - When both could apply to the same chain, the SPKI block is reported, not the root distrust
          expected values from: definitional: two structurally different restatements of the blocking policy, cross-checked before each case is written
          reproduce: py -P tools/run_py.py solutions 15 build/cases/15/15-R4-spki-wins-over-root.in build/cases/15/15-R4-spki-wins-over-root.out
```

## After you pass: compare with the post

Google's post describes two actions and publishes no code, so there is no author's code to compare
with. It gives a reason for the second action: the root removal reaches consumers of the Chrome Root
Store that don't take CRLSet updates. The rule for which block to report when both apply is this
workbook's. The post doesn't state one.

Root distrust also missed the Sectigo copies of the keys. A chain through a cross-certificate ends
at AAA Certificate Services and never reaches emSign ECC Root CA - G3, which is what
`15-R6-distrust-alone-misses-cross-sign` shows with synthetic ids: with only the root distrusted,
the cross-signed chain is `trusted`. Sectigo wrote in the bug (comment 6) that Chrome and Mozilla
had already removed AAA Certificate Services, and that Microsoft and Apple still trusted it. A
client whose bundle still holds that root keeps the cross-signed path after its bundle drops the
emSign root. It stops trusting the path only if it checks revocation and sees Sectigo's revocation
of the cross-certificates on October 19 (comment 13), or if it blocks the keys themselves.

Go is one non-browser client that got a key blocklist. Helme notes that tools such as Terraform
and kubectl use Go, and that clients like them trust a CA bundle on disk and don't check
revocation by default. Talos reports that Go 1.27.3 and 1.26.10 filter out chains containing the
SPKI hashes of all eight intermediates (CVE-2026-111943), so programs built with those versions
reject both copies of each key without a CRLSet.

Assignment 16 puts the earlier assignments' pieces together into one audit of a small, synthetic
PKI, and assignment 19 calls your `check_chain` once per client.
