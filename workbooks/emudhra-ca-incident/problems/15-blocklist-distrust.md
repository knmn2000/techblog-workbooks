# 15 · Block and distrust

**Difficulty:** Easy · **Assignment** 15 of 19 · **Check:** `.\check 15`

**Tags**
- *Language:* parsing a small log format · sets
- *Library:* none needed
- *Concepts:* SPKI pinning/blocking · root distrust · CRLSet-style revocation · response speed vs. blast radius

## Read in the blog first

This page is complete on its own. eMudhra's
[Update 1](https://emudhra.com/en/post/certificate-security-incident#:~:text=Update%201)
quotes Mozilla's response through OneCRL/NSS. Alongside the browser statements, Google's security
blog post, "Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA
Certificates," describes Chrome's response in two parts: blocking the compromised keys by their
SPKI hash through Chrome's CRLSet, and, as a separate precaution, removing all trust in the
affected root. This assignment models both mechanisms and the difference between them.

## Source material

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 1 (quoting Mozilla's OneCRL/NSS response)
- Google Security Blog, "Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA Certificates": Chrome's CRLSet-based SPKI blocking, and the separate decision to remove trust in the affected root
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

## Constraints

- `blocked-spki` and `distrusted-root` lines, and `chain`/`cert` blocks, may appear in any order,
  but a `blocked-spki` or `distrusted-root` line only ever affects chains that come after it.
- Every chain has exactly one `leaf`, at least one `intermediate`, and exactly one `root`, leaf to
  root in that order. An input has at most 8 chains.
- Each case has a 10-second limit; this assignment does no heavy computation.
- There are 9 tests: 1 for R1, 3 for R2 (one per role), 1 for R3, 1 for R4, 2 for R5, and 1
  end-to-end case with five chains covering every verdict in one input. Part of the set is
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

Neither source describes a single "policy" the way this assignment states one. They describe two
separate actions taken during the same incident. You gave the distinction between them a name: one
mechanism that's surgical and fast, another that's broad and precautionary, and a rule for which
one to report when both apply.

This is also the last assignment in the workbook about policy alone,
with no cryptography. Assignment 16 is the capstone: it puts the earlier assignments' pieces
together into one audit of a small, synthetic PKI.
