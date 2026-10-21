# 15 · Block and distrust

**Difficulty:** Easy · **Checkpoint** 15 of 16 · **Check:** `./check.sh 15`

**Tags**
- *Language:* parsing a small log format · sets
- *Library:* none needed
- *Concepts:* SPKI pinning/blocking · root distrust · CRLSet-style revocation · response speed vs. blast radius

## Read in the blog first

This page is complete on its own. eMudhra's
[Update 1](https://emudhra.com/en/post/certificate-security-incident#:~:text=Update%201)
quotes Mozilla's response through OneCRL/NSS. Alongside the browser statements, Google's security
blog post, "Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA
Certificates," describes Chrome's response in two parts: blocking the exact compromised keys by
their SPKI hash through Chrome's CRLSet, and, separately, removing trust in the affected root
entirely as a precaution. This checkpoint models both mechanisms and the difference between them.

## Where this fits

Checkpoint 13 found a bad key by inspecting it directly. This checkpoint is what happens next, at
the scale of a browser trust store: once a bad key (or a bad root) is known, how is trust in it
actually withdrawn, for every certificate it ever signed, everywhere.

## The problem

Write a program that decides, for each certificate chain it's given, whether anything in it is
blocked.

Two independent mechanisms can block a chain:

1. **SPKI blocking.** A specific public key, identified by its SPKI hash, is blocked everywhere it
   appears, in any certificate, no matter which chain it's part of. This is fast to issue and
   exact: it blocks one exact key and nothing else. This is what Chrome's CRLSet did in the real
   incident, within hours.
2. **Root distrust.** An entire root certificate, identified by an id, is distrusted. Every chain
   that leads back to that root is blocked, even certificates whose own keys were never
   individually flagged. This is coarser (it can affect certificates that were never themselves a
   problem) and was the precautionary step taken in this incident.

A chain is blocked by whichever mechanism applies; if a chain's own certificates would trigger
both, **SPKI blocking is reported**, because it's the more specific, faster-acting mechanism, and
it's the one that would have actually been issued first in a response like this one.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains these kinds of lines, which may be mixed in any order before and between
`chain` blocks:

| Line | Meaning |
|---|---|
| `blocked-spki <hash>` | Adds one SPKI hash to the blocklist. It applies to every `chain` that follows it, in any certificate, at any position. |
| `distrusted-root <root-id>` | Adds one root id to the distrust set. It applies to every `chain` that follows it, whenever that chain's own root carries this id. |
| `chain <id>` | Starts a certificate chain. Every `cert` line after it, until the next `chain` line (or the end of the input), belongs to this chain. |
| `cert <role> <spki-hash> <root-id>` | One certificate in the current chain. `role` is `leaf`, `intermediate` or `root`, and the certs for one chain are given leaf to root. `spki-hash` is that certificate's public key's SPKI hash. `root-id` is the identifier checked against the distrust set, and is only meaningful for a `root` cert; for a `leaf` or `intermediate` cert it is always the placeholder `-`. |

This checkpoint is about the blocking policy, not about parsing real certificates (checkpoints
5-9 already cover that): an SPKI hash and a root id are just given directly, as plain hex or
word tokens, standing in for what a real chain's DER would carry.

### Output

For each `chain` block, in input order, write one line:

```
chain <id> trusted                     nothing in the chain is blocked
chain <id> blocked spki <role>         the FIRST cert (leaf to root) whose SPKI hash is blocklisted
chain <id> blocked root <root-id>      the chain's root id is in the distrust set, and no SPKI hash matched first
```

`<id>` is copied from the input unchanged. The checker ignores extra whitespace.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** A chain with nothing blocklisted or distrusted anywhere in it is `trusted`.
- **R2** A certificate (leaf, intermediate, or root) whose SPKI hash is directly on the
  blocklist blocks the whole chain: `blocked spki <role>`, naming that certificate, even if
  nothing else about the chain looks wrong.
- **R3** A chain whose root id is on the distrust set, with no SPKI hash anywhere in the chain
  blocklisted, is `blocked root <root-id>`.
- **R4** When a chain's own certificates would trigger both mechanisms (an SPKI hit and a
  distrusted root), the SPKI block is reported, not the root distrust.
- **R5** A blocklist or distrust entry that was declared for some other chain's certificates
  does not affect a chain whose own certificates don't match it.

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

The leaf and root are both fine on their own. The intermediate's exact key is the one that was
compromised, and blocking it by SPKI hash catches every chain built on it, immediately, without
touching the root at all.

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

The root is also on the distrust list, but the SPKI block is reported: it's the more specific
finding, and it's the one that answers "which exact key is bad," which is more useful than "this
whole root is under precautionary distrust."

## Constraints

- `blocked-spki` and `distrusted-root` lines, and `chain`/`cert` blocks, may appear in any order,
  but a `blocked-spki` or `distrusted-root` line only ever affects chains that come after it.
- Every chain has exactly one `leaf`, at least one `intermediate`, and exactly one `root`, leaf to
  root in that order. An input has at most 8 chains.
- Each case has a 10-second limit; this checkpoint does no heavy computation at all.
- There are 8 tests: 1 for R1, 3 for R2 (one per role), 1 for R3, 1 for R4, 1 for R5, and 1
  end-to-end case with five chains covering every verdict in one input. Part of the set is
  random and changes with `-Fresh`.

## Source material

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 1 (quoting Mozilla's OneCRL/NSS response)
- Google Security Blog, "Protecting Chrome and Android Users from Compromised eMudhra Intermediate CA Certificates": Chrome's CRLSet-based SPKI blocking, and the separate decision to remove trust in the affected root
- Checkpoint 13 (`problems/13-key-linter.md`): the blocklist concept this checkpoint reuses and extends across a whole chain

## Hints

<details><summary>Hint 1: where to start</summary>

Treat this as two completely separate questions, checked in a fixed order: "does any certificate
in this chain have a blocklisted key," then, only if the answer is no, "is this chain's root
distrusted." Don't try to combine them into one check.
</details>

<details><summary>Hint 2: the approach</summary>

Keep two growing sets as you read the input: blocklisted SPKI hashes, and distrusted root ids.
For each chain, scan its certificates leaf to root; the first one whose SPKI hash is in the
blocklist decides the verdict. If none match, look at the chain's `root` certificate (there's
exactly one) and check its root id against the distrust set.
</details>

<details><summary>Hint 3: the traps</summary>

- A `blocked-spki` or `distrusted-root` line only applies to chains that come after it in the
  input, the same way checkpoint 10's `bound` line works. Don't apply it to earlier chains.
- The SPKI check runs first, over every certificate in the chain, not just the root. A key could
  be compromised whether it belongs to a leaf, an intermediate, or a root.
- Only a `root` certificate's `root-id` field means anything; a `leaf` or `intermediate`
  certificate's third field is always the placeholder `-` and should never be compared against
  the distrust set.
- An entry on either set that doesn't match anything in a particular chain has no effect on that
  chain. Don't let one chain's problem leak into another's verdict.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
classify_chain(certs, blocked_spki, distrusted_roots):
    for role, spki, root_id in certs:            # leaf to root
        if spki in blocked_spki:
            return ("blocked", "spki", role)
    for role, spki, root_id in certs:
        if role == "root" and root_id in distrusted_roots:
            return ("blocked", "root", root_id)
    return ("trusted",)
```
</details>

## Checking your solution

```
./check.sh 15                                      run every test
./check.sh 15 -Case 15-R4-spki-wins-over-root       one test, showing its full input, expected output and your output
./check.sh 15 -Fresh                               a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 15 -Dispute <id> "why"                  set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R4  When both could apply to the same chain, the SPKI block is report... .    0 / 1   FAILED
      x 15-R4-spki-wins-over-root  the intermediate is SPKI-blocklisted AND the root is distrusted: the SPKI block is reported
          line 1: expected `chain c1 blocked spki intermediate`, got `chain c1 blocked root root-both`
          likely cause: R4 - When both could apply to the same chain, the SPKI block is reported, not the root distrust
          expected values from: definitional: two structurally different restatements of the blocking policy, cross-checked before each case is written
          reproduce: python3 -P tools/run_py.py solutions 15 build/cases/15/15-R4-spki-wins-over-root.in build/cases/15/15-R4-spki-wins-over-root.out
```

## After you pass: compare with the post

Neither source describes a single unified "policy" the way this checkpoint states one; they
describe two separate real actions taken during the same incident. What you built names the
distinction between them explicitly: one mechanism that's surgical and fast, another that's broad
and precautionary, and a rule for which one to report when both would apply.

**Something to look for:** this checkpoint is also the last one in the workbook that's purely
about policy, not cryptography. Checkpoint 16 is the capstone: it asks you to put the earlier
checkpoints' pieces together into one audit over a small, synthetic PKI.
