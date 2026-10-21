# 14 · Check a key ceremony

**Difficulty:** Medium · **Assignment** 14 of 16 · **Check:** `.\check 14`

**Tags**
- *Language:* parsing a small log format · dictionaries · sets
- *Library:* none needed (the log gives every fingerprint as hex, so you compare text and compute no hash)
- *Concepts:* chain of custody · key wrap/unwrap · attested fingerprints · process auditing

## Read in the blog first

This page is complete on its own. Read eMudhra's
[Update 3](https://emudhra.com/en/post/certificate-security-incident#:~:text=An%20Update%20on%20Our%20Global%20TLS%20Intermediate%20CA%20Incident),
"How it happened": the keys were generated in a Key Generation Ceremony (KGC) in April 2025, on
FIPS 140-2 Level 3 hardware security modules, and "a flaw in one step of that process... produced
a second, weak set of keys alongside the original strong keys." The post also mentions "similar
labels" among the materials handled.

**eMudhra has not confirmed the exact root cause.** This assignment is **not** a reconstruction
of their ceremony software, which nobody outside eMudhra has described in public. It models a
plausible shape that fits their own description. A step that wraps a key for transport and later
unwraps it could, with a bug, hand back different key material than it received, and a mix-up
between artifacts with similar names is the kind of slip that would let that go unnoticed. Treat
the log format below as a teaching model built for this workbook, not as eMudhra's file format or
process.

## Source material

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3 ("How it happened", and the statement that the root cause is not yet confirmed)
- Assignment 12 (`problems/12-generate-key.md`): the step that should go right every time, before any ceremony log starts

## Where this fits

Assignment 12's `ecc/keys.py` turned random bytes into a key, the step that should go right every
time. This assignment checks a later step: that a key which started out fine is still the same key
when the ceremony publishes it. Your linter from assignment 13 can only catch a bad key it gets to
look at, and this checker finds the moment the key stopped being the one the ceremony generated.

Your new `pki/ceremony.py` needs none of your earlier modules, and no later assignment uses it.

## The problem

A **ceremony log** is a list of steps, one per line, recording what happened to a set of keys as
they moved through a Key Generation Ceremony. Each step names one or two **labels**: words that
refer to a key artifact at some point in the ceremony. Write a program that reads the log and
reports two kinds of problem: a label that's ambiguous because two `generate` steps used it, and a
published key whose material doesn't match the fingerprint attested when it was generated.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Each line is one ceremony step:

| Line | Meaning |
|---|---|
| `generate <label> <curve>` | The ceremony generates a new key and names it `label`. This starts a new key every time, even if an earlier `generate` used the same `label` (see R3). `curve` is `P-256` or `P-384`; it has no effect on this assignment's logic. |
| `wrap <label> <wrapped-label>` | The ceremony wraps (encrypts for transport or backup) the key that `label` names now, and names the result `wrapped-label`. A correct wrap carries the same key material forward. |
| `unwrap <wrapped-label> <label>` | The ceremony unwraps the artifact that `wrapped-label` names back into a usable key, named `label`. **This is the step eMudhra's account points to**: a flawed unwrap can hand back different key material from what went in. |
| `fingerprint <label> <hex>` | The ceremony software records the fingerprint of `label`, a hash of the key bytes, as 64 lowercase hex characters. This line comes straight after the step (`generate`, `wrap` or `unwrap`) that created `label`. |
| `publish <label>` | The ceremony publishes the key that `label` names now. |

A label is a name. Once a `generate`, `wrap` or `unwrap` step has used it, it refers to whatever key
material that step produced, until the log uses it again. `wrap` and `unwrap` carry forward the key
their source label names at that moment, and only `unwrap` can be defective.

### Output

For each `generate` step whose label was already used by an **earlier** `generate` step, in the
order you meet it:

```
duplicate <label>
```

For each `publish` step, in the order it appears, write one line:

```
publish <label> ok                    the key currently under <label> matches what was attested when it was generated
publish <label> MISMATCH <origin>     it doesn't; <origin> is the label it was originally generated under
publish <label> undefined             <label> was never generated, wrapped, or unwrapped
```

Write both kinds of line interleaved, in the order their triggering steps appear in the log: a
`duplicate` line at its `generate` step, a `publish` line at its `publish` step. The checker
ignores extra whitespace.

### Chains of custody

Every `generate` step starts a key's **chain of custody**, the record of where that key goes. The
first `fingerprint` line recorded for the new key is the chain's **attested fingerprint**: the
fingerprint of the key as the ceremony created it. `wrap` and `unwrap` carry a
key's chain of custody forward to their target label, whatever that label's text is.

At `publish`, find the chain of custody for the label being published. Compare the label's current
fingerprint (the latest `fingerprint` line recorded for that exact label) with the attested
fingerprint at the start of its chain:

- If they're equal, the key is `ok`.
- If they differ, report `MISMATCH`, naming the label the chain started at.

**A reused label leaves an earlier chain alone.** Suppose `generate` creates a key under a label, a
`wrap` moves that key away, and only *afterward* another `generate` reuses the label. The key that
was wrapped away still traces back to the *first* `generate`, and the second `generate` starts its
own, separate chain of custody. Your program still flags the duplicate label, because that kind of
mix-up makes a ceremony harder to audit, but the reuse doesn't corrupt a key that had already moved
elsewhere.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** A clean ceremony (`generate`, `wrap`, a correct `unwrap`, `publish`) reports `ok`. So
  does publishing a key straight from `generate`, with no wrap/unwrap round trip.
- **R2** A defective `unwrap` that hands back different key material shows up at `publish`:
  `MISMATCH`, naming the label the key was first generated under.
- **R3** A label that a second `generate` step reuses gets a `duplicate <label>` line, whether or
  not anything downstream of it breaks. A chain already wrapped away under the label's earlier
  identity still resolves to that identity: the duplicate doesn't disturb it.
- **R4** A `publish` of a label that no step generated, wrapped or unwrapped reports `undefined`.
- **R5** With several keys in one ceremony and only one of them defective, every `publish` line
  judges its own key, so only the defective key's line says `MISMATCH`.

## Examples

### Example 1: a defective unwrap, caught at publish (test `14-R2-bad-unwrap`)

```
input:   generate k1 P-384
         fingerprint k1 <hash of the real key>
         wrap k1 wk1
         fingerprint wk1 <the same hash: wrap preserved it>
         unwrap wk1 k1b
         fingerprint k1b <a DIFFERENT hash: the unwrap substituted something else>
         publish k1b

output:  publish k1b MISMATCH k1
```

The key stayed the same through the wrap. The unwrap produced something with a different
fingerprint from what went in, and that's the key the ceremony publishes. The output names `k1`
because this chain of custody started there.

### Example 2: a duplicate label that doesn't disturb an earlier chain (test `14-R3-duplicate-does-not-disturb-earlier-wrap`)

```
input:   generate first-use P-384
         fingerprint first-use <hash A>
         wrap first-use stashed
         fingerprint stashed <hash A>
         generate first-use P-384
         fingerprint first-use <hash B>
         unwrap stashed recovered
         fingerprint recovered <hash A>
         publish recovered

output:  duplicate first-use
         publish recovered ok
```

The `wrap` moved the *first* `first-use` key to `stashed` before the label was reused. The second
`generate` points `first-use` at a different key, and your program flags it as a duplicate.
`recovered`, unwrapped from `stashed`, still traces back to the *first* key, and its fingerprint
(hash A) matches the one attested for that key. The output reports the duplicate, and `recovered`
is `ok`.

## Constraints

- Every line is one of the five step kinds above; there are no blank lines.
- A `fingerprint` line names the label that the step right before it (`generate`, `wrap` or
  `unwrap`) created.
- An input has at most 50 steps and at most 8 `publish` lines.
- Each case has a 10-second limit; this assignment does no heavy computation.
- There are 10 tests: 2 for R1, 2 for R2, 2 for R3, 1 for R4, 2 for R5 and 1 end-to-end case
  mixing several keys, a duplicate label, a defective unwrap and an undefined reference in one
  ceremony. Part of the set is random and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Work through the log from top to bottom and keep track, for every label you've seen, of the key it
names now. A second `generate` can reuse a label, so the label's text alone doesn't tell you which
key it is: give each key something of its own to track it by.
</details>

<details><summary>Hint 2: the approach</summary>

Give every `generate` step its own identity (a counter works: 1, 2, 3, ...), even when it reuses a
label. In `Ceremony`, the dictionary `points_at` maps a label to the identity it names now:
`generate` sets it to a new identity, and `wrap` and `unwrap` copy the identity of their source
label. A second dictionary, `attested`, maps an identity to its attested fingerprint, set once by
the first `fingerprint` line after the key's generation. A third, `latest`, maps a label to the last
fingerprint recorded for it. At `publish`, look up the label's identity and compare.
</details>

<details><summary>Hint 3: the traps</summary>

- A label used by a second `generate` needs a new identity. Don't let the second `generate`
  overwrite the attested fingerprint of the first one's identity.
- `wrap` and `unwrap` look up the identity their *source* label names at the moment they run, not
  at some later point.
- A `publish` of an unknown label has no identity to look up: check for that before anything else.
- The `MISMATCH` line names the label the chain started at (the `generate` step), not the `wrap`
  or `unwrap` step that corrupted it, and not the label being published.
- `duplicate` lines and `publish` lines go out interleaved in log order, not grouped by kind.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
points_at = {}        # label -> identity id
generated_as = {}      # identity id -> label it was generated under
attested = {}          # identity id -> fingerprint attested at generation
latest = {}            # label -> most recent fingerprint recorded for it
next_id = 0

for step in log:
    if step is generate(label, curve):
        if label in points_at: emit "duplicate " + label
        next_id += 1
        points_at[label] = next_id
        generated_as[next_id] = label
    if step is wrap(label, wrapped_label) or unwrap(wrapped_label=label, target):
        points_at[target] = points_at[source]
    if step is fingerprint(label, hex):
        latest[label] = hex
        id = points_at[label]
        if id not yet in attested: attested[id] = hex
    if step is publish(label):
        if label not in points_at: emit "publish " + label + " undefined"; continue
        id = points_at[label]
        if latest[label] == attested[id]: emit "publish " + label + " ok"
        else: emit "publish " + label + " MISMATCH " + generated_as[id]
```
</details>

## Checking your solution

```
.\check 14                                  run every test
.\check 14 -Case 14-R2-bad-unwrap           one test, showing its full input, expected output and your output
.\check 14 -Fresh                           a new set of tests (new random seed), to confirm on data you haven't seen
.\check 14 -Dispute <id> "why"              set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R2  A defective unwrap that substitutes a different token is caught ... .    1 / 2   FAILED
      x 14-R2-bad-unwrap  the unwrap step silently substitutes a different token: MISMATCH at publish
          line 1: expected `publish k1b MISMATCH k1`, got `publish k1b ok`
          likely cause: R2 - A defective unwrap that substitutes a different token is caught at publish: `MISMATCH <origin>`
          expected values from: definitional: fingerprint = sha256(token) in hex, computed by hashlib in this generator
          reproduce: py -P tools/run_py.py solutions 14 build/cases/14/14-R2-bad-unwrap.in build/cases/14/14-R2-bad-unwrap.out
```

## After you pass: compare with the post

The post describes the outcome of a ceremony gone wrong in vague terms and says that the root
cause isn't confirmed, so there's no author's code to compare with here. You built one way a
ceremony-log checker could have caught a failure of the shape they described, with no claim about
what their software does.

**Something to look for:** the post's mention of "similar labels" matters in this assignment. A
ceremony that lets one name mean two different things at different times is a process hazard worth
flagging on its own (R3's point), whether or not a key's material changed along the way.
