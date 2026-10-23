# 14 · Check a key ceremony

**Difficulty:** Medium · **Assignment** 14 of 19 · **Check:** `.\check 14`

**Tags**
- *Language:* parsing a small log format · dictionaries · string normalisation
- *Library:* none needed (the log gives every fingerprint as hex, so you compare text and compute no hash)
- *Concepts:* key identity · public-key fingerprints (assignment 07) · ceremony deviations · label collisions · process auditing

## Read in the blog first

This page is complete on its own. eMudhra's
[Update 3](https://emudhra.com/en/post/certificate-security-incident#:~:text=An%20Update%20on%20Our%20Global%20TLS%20Intermediate%20CA%20Incident),
says eMudhra generated the keys in a Key Generation Ceremony (KGC) on April 30, 2025, on FIPS
140-2 Level 3 hardware security modules. Under "How it happened" it names the step: "The problem
was a flaw in one step of the ceremony procedure, not the absence of HSMs. During the ceremony, a
key wrap/unwrap step produced a second, weak set of keys alongside the original strong keys."

eMudhra gave a fuller account in Mozilla bug 2083449, comments 10 and 11. These are eMudhra's own
statements, unverified by anyone else:

- a set of original ECC keys "were created onboard as expected";
- "an approved deviation to our usual KGC to test a wrap/unwrap was introduced";
- "a flaw in the code resulted in the second pair of keys being created onboard which were weaker";
- the weaker pair "were used by mistake to create the csr (because the key labels were similar)";
- the CSR from the weaker keys "were also sent over to Sectigo for cross signing";
- on human error: "There were human errors in multiple steps of the process".

eMudhra has not confirmed a root cause. Commenters in the bug (Thor Simon, comment 31; Jacob
Durham, comments 32 and 33) and in Hacker News thread 50166579 ask the questions the account
leaves open: which call created the second pair (key-pair generation or unwrapping a key), who
approved the deviation, and whether an auditor watched it. They also ask for the KGC script, the
ceremony and witness reports, the HSM model and firmware, and a record of any imported or restored
keys. Those are questions, and any answer a commenter guesses at is speculation.

Utimaco, which made the HSM that generated these keys, gave its reading on October 23. Based on
what eMudhra has disclosed, it writes that "a scripting error seems to have created alternative
keys" and used them in place of the keys the HSM created, and it says its HSMs offer no way to request an EC
private key with a chosen value. Neither eMudhra nor Utimaco has published the script.

This assignment models one failure shape that fits eMudhra's account and Utimaco's reading of it. The log format below is a
teaching model built for this workbook. It is not eMudhra's file format or process, and it makes
no claim about what their software did.

## Source material

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3 ("How it happened", and the statement that the root cause is not yet confirmed)
- Mozilla, [bug 2083449](https://bugzilla.mozilla.org/show_bug.cgi?id=2083449): eMudhra's account in comments 10 and 11, Chrome's root program's questions in comment 30, other questions to eMudhra in comments 31 to 33
- Utimaco, [Compromised private keys in eMudhra certificates](https://utimaco.com/news/blog-posts/compromised-private-keys-emudhra-certificates) (October 23, 2026): the HSM vendor's reading of eMudhra's account
- Hacker News, [thread 50166579](https://news.ycombinator.com/item?id=50166579)
- Assignment 07 (`problems/07-spki-hash.md`): hashing a public key to get a name for it that survives reissuance
- Assignment 13 (`problems/13-key-linter.md`): the check on the key itself

## Where this fits

Assignment 07 hashed a certificate's public key, which gave you a name for the key that no label
can change. Assignment 12 built a key by the standard procedure and assignment 13 linted a key it could look
at. This assignment audits the steps between those: whether the key a ceremony used for its CSR is
the key the witnesses approved.

Your new `pki/ceremony.py` needs none of your earlier modules, because the log carries each
fingerprint ready-made, and no later assignment uses it.

## The problem

Write a program that replays a ceremony log and checks, at each CSR and each publish, that the key
used is the key the witnesses approved. It also flags labels that collide and deviations from the
ceremony's script.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Each line is one step of the ceremony:

| Line | Meaning |
|---|---|
| `generate <label> <fp>` | The HSM creates a key pair and names it `label`. `fp` is the fingerprint of its public key. |
| `approve <label> <fp>` | The witnesses approve the key with fingerprint `fp` under `label`, for use in a CSR. |
| `deviation <approver>` | The ceremony departs from its script. `approver` is the name of the person who signed off, or `none` when no one signed off. |
| `csr <label> <fp>` | The operator picks the key named `label` and creates a CSR. `fp` is the fingerprint of the public key the CSR carries. |
| `publish <label>` | The ceremony signs the latest CSR made under `label` and publishes the certificate. |

A fingerprint is the SHA-256 of a public key, written as 64 lowercase hex characters. It is the
same idea as the SPKI hash in assignment 07. The log gives you every fingerprint, so you compare
text and compute no hash. A label is a word of ASCII letters, digits, `-`, `_` and `.` with at
least one letter or digit. People and software choose labels, and nothing makes them unique.

### Output

Each step writes zero or one line, in log order:

| Step | Line it writes |
|---|---|
| `generate` | `duplicate <label>` or `similar <label> <earlier-label>`, or nothing when neither applies |
| `approve` | nothing |
| `deviation` | `deviation <approver> approved`, or `deviation none UNAPPROVED` |
| `csr` | `csr <label> <status>` |
| `publish` | `publish <label> <status>` |

```
duplicate ica-g3b-dv
similar ICA_G3B_DV ica-g3b-dv
deviation alice approved
deviation none UNAPPROVED
csr ica-g3b-dv MISMATCH ICA_G3B_DV
publish ica-g3b-dv BLOCKED
```

The checker ignores extra whitespace. If several findings apply to one step, the step writes only
the one listed first below.

`csr` status, first rule that applies:

| Status | When |
|---|---|
| `UNVERIFIED` | An earlier step was `deviation none`. |
| `NOT-APPROVED` | The ceremony holds no approval for this exact label. |
| `MISMATCH <key-label>` | The fingerprint approved for the label differs from the CSR's. `<key-label>` is the label of the `generate` line with the CSR's fingerprint (no two `generate` lines share one, see Constraints), or `unknown` when no `generate` line has it. |
| `ok` | The approved fingerprint equals the CSR's. |

`publish` status, first rule that applies:

| Status | When |
|---|---|
| `undefined` | No `csr` line has used this exact label so far. |
| `UNVERIFIED` | An earlier step was `deviation none`. |
| `BLOCKED` | The latest `csr` under this label did not write `ok`. |
| `ok` | The latest `csr` under this label wrote `ok`. |

A `publish` looks only at the outcome of that latest CSR and at whether the ceremony is still
verified. It does not look at approvals again, so a later approved deviation doesn't change it.

`generate` finding, first rule that applies: `duplicate` when an earlier `generate` used this same
label, character for character, then `similar` when an earlier `generate` label matches this one
after normalisation (see Label collisions), naming the earliest such label. Only `generate` labels
take part.

### Identifying a key

A label says which slot an operator meant. The fingerprint says which key is in it. Two keys can
share a label, or carry labels that differ by a case or a separator, and a CSR line gives the label
the operator picked next to the fingerprint of the key that went into the CSR. Only the fingerprint
names that key.

`approve` binds a label to a fingerprint. A later `approve` for the same label replaces the earlier
one. At `csr`, compare the approved fingerprint for that exact label with the CSR's fingerprint, as
text. The match is exact for labels (`ICA-G3B-DV` and `ica-g3b-dv` are different labels here) and for
fingerprints. To name the key a mismatched CSR carried, look its fingerprint up among the
`generate` lines.

The log may approve a fingerprint that no `generate` line recorded, and a CSR may carry one. The
rules above still apply, and `unknown` names the key of a CSR that matches no `generate` line.

### Label collisions

Two labels are similar when they are equal after this normalisation: lowercase every ASCII letter,
then delete every `-`, `_` and `.`. Labels have no spaces, so nothing else needs removing. Digits
and other letters stay.

| Label | Normalised | Similar to |
|---|---|---|
| `ICA-G3B-OV` | `icag3bov` | `ica_g3b_ov`, `ica.g3b.ov`, `icag3bov` |
| `ica-g3b-ov2` | `icag3bov2` | none of the above |
| `ica-g3b-0v` | `icag3b0v` | none of the above (the digit `0` is not the letter `o`) |

Each `generate` is checked against earlier `generate` labels only. An earlier label gets no finding
for a later one.

### Deviations

A deviation is a departure from the script, and the witnesses approved the keys against the
script as it stood.

- `deviation <name>`, with a name: someone signed off. The step writes `deviation <name> approved`
  and clears every approval, so each key needs an `approve` again before its CSR counts.
- `deviation none`: no one signed off. The step writes `deviation none UNAPPROVED`, and every later
  `csr` and `publish` is `UNVERIFIED`, whatever the later lines say, including a later approved
  deviation and fresh approvals. Steps before it keep their results. `generate` findings don't
  depend on verification and still appear.

`none` is not an approver's name, and no label is `none` or `unknown`.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A `csr` whose fingerprint equals the one approved for its label writes `ok`, and its `publish` writes `ok`. The check compares fingerprints and does not look at the key's strength.
- **R2** A `csr` whose fingerprint differs from the approved one writes `MISMATCH <key-label>`, naming the label of the `generate` line with that fingerprint, or `unknown`. The fingerprint tells apart two keys that share a label.
- **R3** A `csr` under a label with no current approval writes `NOT-APPROVED`. Labels match as written, and a later `approve` replaces an earlier one for the same label.
- **R4** An approved deviation clears every approval, so a `csr` needs a new `approve` after it.
- **R5** After `deviation none`, every later `csr` and `publish` writes `UNVERIFIED`, and nothing later restores verification.
- **R6** A `publish` writes `undefined` when no `csr` used its label, `BLOCKED` when the latest `csr` under the label did not write `ok`, and `ok` otherwise.
- **R7** A `generate` whose label an earlier `generate` already used writes `duplicate <label>`.
- **R8** A `generate` whose label equals an earlier `generate` label after lowercasing and removing `-`, `_` and `.` writes `similar <label> <earlier-label>`, naming the earliest match.
- **R9** When several findings apply to one step, the step writes only the first in the priority order above.
- **R10** The output follows log order: one line per `deviation`, `csr` and `publish`, a line per `generate` only when it has a finding, and nothing for `approve`.

## Examples

### Example 1: a weak pair used by mistake (test `14-R2-weak-pair-substituted`)

```
input:   generate ica-g3b-dv 1c40841efcb5adebe4f6342814989255d8ffb92c3007ec4d21fe583c4cf104c1
         approve ica-g3b-dv 1c40841efcb5adebe4f6342814989255d8ffb92c3007ec4d21fe583c4cf104c1
         deviation alice
         generate ICA_G3B_DV ea5397c853863a1f8786a821aaae1d3aca3c6c4b1a176f2670e9fd6677aa9621
         approve ica-g3b-dv 1c40841efcb5adebe4f6342814989255d8ffb92c3007ec4d21fe583c4cf104c1
         csr ica-g3b-dv ea5397c853863a1f8786a821aaae1d3aca3c6c4b1a176f2670e9fd6677aa9621
         publish ica-g3b-dv

output:  deviation alice approved
         similar ICA_G3B_DV ica-g3b-dv
         csr ica-g3b-dv MISMATCH ICA_G3B_DV
         publish ica-g3b-dv BLOCKED
```

The deviation clears the first approval, and the witnesses approve the intended key again after
it. A second pair appears under `ICA_G3B_DV`, which normalises to the same text as `ica-g3b-dv`,
so the step writes `similar`. The operator picks `ica-g3b-dv` and the CSR carries the second
pair's fingerprint, `ea5397...`. That differs from the approved `1c4084...`, so the CSR is a
`MISMATCH`, and the `generate` line with that fingerprint gives the label `ICA_G3B_DV`. The publish
is `BLOCKED`.

### Example 2: an approved key that is itself weak (test `14-R1-approved-weak-key-passes`)

```
input:   generate ica-g3c-dv a177c2bfa7e95678341780c2f4fde9a764fa1e546a634fc79b8f719634ea0574
         generate ica-g3c-ov ea5397c853863a1f8786a821aaae1d3aca3c6c4b1a176f2670e9fd6677aa9621
         approve ica-g3c-ov ea5397c853863a1f8786a821aaae1d3aca3c6c4b1a176f2670e9fd6677aa9621
         csr ica-g3c-ov ea5397c853863a1f8786a821aaae1d3aca3c6c4b1a176f2670e9fd6677aa9621
         publish ica-g3c-ov

output:  csr ica-g3c-ov ok
         publish ica-g3c-ov ok
```

The fingerprint `ea5397...` belongs to a key whose private value is 4. The witnesses approved that
key, the CSR carries it, and every comparison passes. A fingerprint names a key and says nothing
about its strength, so this check can't tell.

### Example 3: a deviation nobody approved (test `14-R5-only-later-csrs-affected`)

```
input:   generate k1 e2f5eb64d7cd11d077fac1fcfaf23fb3fed588e8fc01321753aa8a8f855988d6
         generate k2 a781428686099d5f292b46bb110b969efa6f5849b76b7e490c14abb763b5cd8e
         approve k1 e2f5eb64d7cd11d077fac1fcfaf23fb3fed588e8fc01321753aa8a8f855988d6
         approve k2 a781428686099d5f292b46bb110b969efa6f5849b76b7e490c14abb763b5cd8e
         csr k1 e2f5eb64d7cd11d077fac1fcfaf23fb3fed588e8fc01321753aa8a8f855988d6
         deviation none
         csr k1 e2f5eb64d7cd11d077fac1fcfaf23fb3fed588e8fc01321753aa8a8f855988d6
         csr k2 a781428686099d5f292b46bb110b969efa6f5849b76b7e490c14abb763b5cd8e

output:  csr k1 ok
         deviation none UNAPPROVED
         csr k1 UNVERIFIED
         csr k2 UNVERIFIED
```

The first CSR happened before the deviation and keeps its `ok`. After `deviation none`, both later
CSRs have approved fingerprints that match, and both write `UNVERIFIED`, for either label.

## Constraints

- Every line is one of the five step kinds above; there are no blank lines.
- A fingerprint is 64 lowercase hex characters, and no two `generate` lines share one.
- A label is ASCII letters, digits, `-`, `_` and `.` with at least one letter or digit, and is not `none` or `unknown`. An approver's name is a word without spaces.
- An input has at most 50 steps and at most 8 `publish` lines.
- Each case has a 10-second limit; this assignment does no heavy computation.
- There are 30 tests: 2 for R1, 4 for R2, 2 for R3, 2 for R4, 3 for R5, 5 for R6, 2 for R7, 3 for R8,
  3 for R9, 2 for R10 and 2 end-to-end cases, one with the failure shape of Example 1 and one random
  ceremony. Part of the set is random and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Go through the log from top to bottom and decide each step's line from what came before it. For a
CSR, ask which key it carries, and answer from the fingerprint. The label on the line is
only what the operator typed.
</details>

<details><summary>Hint 2: the approach</summary>

Keep four things in `Ceremony`: a list of `(label, fingerprint)` pairs, one per `generate`, in log
order; a dictionary `approved` from label to fingerprint; a dictionary from label to whether its
latest `csr` wrote `ok`; and a flag `unverified`. Each method returns the line its step writes (or
None) and then updates that state. For `similar`, write `normalise(label)` once and compare it with
the normalised form of each earlier `generate` label, earliest first. `csr` and `publish` each
check their statuses in the order the tables list them and stop at the first that applies.
</details>

<details><summary>Hint 3: the traps</summary>

- A `csr` compares fingerprints. Comparing labels passes a CSR that uses a different key under the same label.
- A `generate` writes at most one line, and `duplicate` wins over `similar`, even when the label is also similar to an older one.
- Approvals use exact labels, so `ICA-G3B-DV` and `ica-g3b-dv` differ there. Only the `generate` check normalises.
- `MISMATCH` names the label of the `generate` line with the CSR's fingerprint. It doesn't name the approved key or the label on the `csr` line.
- A failed `csr` still replaces the stored result of an earlier `ok` for its label, because `publish` follows the latest one.
- An approved deviation clears approvals and writes a line. `deviation none` sets the flag, and nothing later clears it.
- `approve` writes nothing, and `generate` findings still appear after `deviation none`.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
generated = []        # (label, fingerprint), in log order
approved = {}         # label -> fingerprint
csr_ok = {}           # label -> did its latest csr write ok
unverified = False

normalise(label): lowercase, delete "-", "_" and "."

for step in log:
    generate(label, fp):
        if label in [l for l, _ in generated]: emit "duplicate " + label
        else if some earlier l has normalise(l) == normalise(label): emit "similar " + label + " " + (earliest such l)
        append (label, fp) to generated
    approve(label, fp):
        approved[label] = fp
    deviation(who):
        if who == "none": unverified = True; emit "deviation none UNAPPROVED"
        else: approved = {}; emit "deviation " + who + " approved"
    csr(label, fp):
        if unverified: status = "UNVERIFIED"
        else if label not in approved: status = "NOT-APPROVED"
        else if approved[label] != fp: status = "MISMATCH " + (label of the generated entry with fp, or "unknown")
        else: status = "ok"
        csr_ok[label] = (status == "ok")
        emit "csr " + label + " " + status
    publish(label):
        if label not in csr_ok: status = "undefined"
        else if unverified: status = "UNVERIFIED"
        else if not csr_ok[label]: status = "BLOCKED"
        else: status = "ok"
        emit "publish " + label + " " + status
```
</details>

## Checking your solution

```
.\check 14                                  run every test
.\check 14 -Case 14-R2-weak-pair-substituted   one test, showing its full input, expected output and your output
.\check 14 -Fresh                           a new set of tests (new random seed), to confirm on data you haven't seen
.\check 14 -Dispute <id> "why"              set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this, from a solution that writes `ok` when a `generate` line with the same
label carries the CSR's key:

```
  R2  A `csr` whose fingerprint differs from the approved one writes `MISMATCH <key-label>`, ... .    3 / 4   FAILED
      x 14-R2-identical-labels-different-keys  two keys share one label; the CSR uses the unapproved one, so only the finger...
          line 2: expected `csr ica-g3b-dv MISMATCH ica-g3b-dv`, got `csr ica-g3b-dv ok`  (in `duplicate ica-g3b-dv`)
          likely cause: R2 - A `csr` whose fingerprint differs from the approved one writes `MISMATCH <key-label>`, naming the label of the `generate` line with that fingerprint, or `unknown`
          expected values from: definitional: fingerprint = sha256 of the uncompressed P-384 public point, computed by hashlib from OpenSSL's d*G; expected lines follow the page's rules
          reproduce: py -P tools/run_py.py solutions 14 build/cases/14/14-R2-identical-labels-different-keys.in build/cases/14/14-R2-identical-labels-different-keys.out
```

The checker groups output lines by the word the first expected line starts with, and `(in ...)`
names the most recent line in that group. Here that word is `duplicate`, so the note points at
the `duplicate ica-g3b-dv` line above the failing `csr` line. The failing line is still line 2.

## After you pass: compare with the post

eMudhra has published an account of the ceremony and no code, so there is no author's code to
compare with. You built one way a checker could have caught a failure of the shape that account
describes. It makes no claim about what their software did.

The check catches a second key pair that replaces the approved one by mistake. Example 1 is that
case: the label was similar, and the check names the key by fingerprint. It also works when the
two keys carry an identical label, which a check by label cannot separate. It
refuses to call anything verified after an unapproved deviation, and after an
approved one it makes the witnesses approve the keys again.

The check cannot catch a weak pair that the ceremony planned and the witnesses approved. Example 2
passes with `ok` on every line because the CSR carries the key the witnesses approved, and that
key has the private value 4. A fingerprint is a name for a key. It tells nothing about the
key's strength, so comparing fingerprints can only show that the key used is the key
approved. Whether the approved key is any good needs a check on the key itself, which is what the
linter from assignment 13 does: it finds a weak key whether or not anyone approved it, and it can't
tell that a good key replaced another good one. Each check covers a gap in the other, and a
ceremony needs both.

The model leaves out what eMudhra's account leaves open. It doesn't say which call created the
second pair, so `generate` records only a fingerprint. eMudhra says it approved the deviation,
so the `deviation none` rule describes a case the account doesn't mention. Whether the witnesses
approved the keys again after that deviation is also unknown. Chrome's root program asked eMudhra
why the later CRL re-signing did not trigger a halt. A `BLOCKED` publish models one answer to that
kind of question in a log: a failed check stops the signing.

The reference solution's `Ceremony.csr` keeps only whether the latest CSR under a label passed,
and `Ceremony.publish` uses that and the `unverified` flag. It doesn't look at approvals again, as
the Output section specifies. A design that re-checked approvals at publish would block a CSR made
before a later approved deviation, and the tests rule that design out.
