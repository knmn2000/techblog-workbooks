# 14 · Check a key ceremony

**Difficulty:** Medium · **Checkpoint** 14 of 16 · **Check:** `./check.sh 14`

**Tags**
- *Language:* parsing a small log format · dictionaries · sha256 (`hashlib` in Python)
- *Library:* `hashlib` for sha256 (or print the fingerprints directly; no crypto library needed)
- *Concepts:* chain of custody · key wrap/unwrap · attested fingerprints · process auditing

## Read in the blog first

This page is complete on its own. Read eMudhra's
[Update 3](https://emudhra.com/en/post/certificate-security-incident#:~:text=An%20Update%20on%20Our%20Global%20TLS%20Intermediate%20CA%20Incident),
"How it happened": the keys were generated in a Key Generation Ceremony (KGC) in April 2025, on
FIPS 140-2 Level 3 hardware security modules, and "a flaw in one step of that process... produced
a second, weak set of keys alongside the original strong keys." The post also mentions "similar
labels" among the materials handled.

**eMudhra has not confirmed the exact root cause.** This checkpoint is **not** a reconstruction
of their actual ceremony software; nobody outside eMudhra has described it in public. What
follows is a plausible shape that matches their own vague description: a step that wraps a key
for transport and later unwraps it could, if it has a bug, hand back different key material than
it was given, and a mix-up between similarly-named artifacts is exactly the kind of thing that
would let that go unnoticed. Treat the log format below as a teaching model built for this
workbook, not as eMudhra's real file format or process.

## Where this fits

Checkpoint 12 showed the one step that should always go right: turning random bytes into a
key. This checkpoint is about a different, later step: making sure a key that started out fine is
still the same key by the time it gets published. A linter like checkpoint 13 can only catch a
bad key if it's given the chance to look at it; this checkpoint is about catching the moment the
key stopped being the one that was really generated.

## The problem

A ceremony log is a list of steps, one per line, recording what happened to a set of keys as
they moved through a Key Generation Ceremony. Each step names one or two **labels**: words used
to refer to a key artifact at some point in the ceremony. Write a program that reads the log and
reports two kinds of problem: a label that's ambiguous because it was generated twice, and a
published key whose material doesn't match what was attested when it was generated.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
Each line is one ceremony step:

| Line | Meaning |
|---|---|
| `generate <label> <curve>` | A brand new key is generated and given the name `label`. This always starts a new key, even if `label` was used by an earlier `generate` (see R3). `curve` is `P-256` or `P-384`; it has no effect on this checkpoint's logic. |
| `wrap <label> <wrapped-label>` | The key currently called `label` is wrapped (encrypted for transport or backup); the result is given the name `wrapped-label`. A correct wrap always carries the same key material forward. |
| `unwrap <wrapped-label> <label>` | The artifact called `wrapped-label` is unwrapped back into a usable key, given the name `label`. **This is the step eMudhra's account points to**: a flawed unwrap can hand back different key material than what was wrapped. |
| `fingerprint <label> <hex>` | Right after `label` was just created (by `generate`, `wrap`, or `unwrap`), the ceremony software records its fingerprint: a hash of the actual key bytes, as 64 lowercase hex characters. This line always immediately follows the step that created `label`. |
| `publish <label>` | The key currently called `label` is the one that gets published. |

A label is just a name: once it's been used by `generate`, `wrap`, or `unwrap`, it refers to
whatever key material that step produced, until the log uses it again. `wrap` and `unwrap` always
carry forward whatever key is currently under their source label; only `unwrap` can be defective.

### Output

For each `generate` step whose label was already used by an **earlier** `generate` step, in the
order it's seen:

```
duplicate <label>
```

For each `publish` step, in the order it appears, write exactly one line:

```
publish <label> ok                    the key currently under <label> matches what was attested when it was generated
publish <label> MISMATCH <origin>     it doesn't; <origin> is the label it was originally generated under
publish <label> undefined             <label> was never generated, wrapped, or unwrapped
```

Both kinds of output line are written interleaved, in the order their triggering step appears in
the log (a `duplicate` line appears at its `generate` step; a `publish` line appears at its
`publish` step). The checker ignores extra whitespace.

### What "matches what was attested" means

Every `generate` step starts a key's **chain of custody**. The very first `fingerprint` line
recorded for a freshly generated label is that chain's attested ground truth: the fingerprint of
the key as it was actually created. `wrap` and `unwrap` carry a key's chain of custody forward to
their target label, whatever that label's text is. At `publish`, look up the chain of custody for
the label being published, and compare its current fingerprint (the most recent `fingerprint`
line recorded for that exact label) with the ground truth recorded at the start of its chain. If
they're equal: `ok`. If not: `MISMATCH`, naming the label the chain started at.

**A reused label does not retroactively disturb an earlier chain.** If `generate` creates a key
under a label, that key is wrapped away, and only *afterward* the same label is reused by another
`generate` step, the key that was already wrapped away still traces back to the *first*
`generate`, unaffected by the second one reusing the name. The second `generate` starts its own,
completely separate chain of custody. The duplicate label is still flagged (it's exactly the kind
of mix-up that makes a ceremony harder to audit), but it doesn't corrupt a key that was already
somewhere else by the time the label was reused.

## Requirements

Each test case is designed around one of these. A failing test also prints the requirement the
difference most likely comes from.

- **R1** A clean ceremony (`generate`, `wrap`, a correct `unwrap`, `publish`) reports `ok`. So
  does publishing a key straight from `generate` with no wrap/unwrap round trip at all.
- **R2** A defective `unwrap` that hands back different key material is caught at `publish`:
  `MISMATCH`, naming the label the key was originally generated under.
- **R3** A label reused by a second `generate` step is flagged `duplicate <label>`, whether or
  not anything downstream of it actually breaks. A chain already wrapped away under the label's
  earlier identity still resolves correctly: the duplicate doesn't disturb it.
- **R4** A `publish` of a label that was never generated, wrapped, or unwrapped is flagged
  `undefined`.
- **R5** Several keys in one ceremony, only one of them defective: every `publish` line reflects
  its own key correctly, not a blanket `MISMATCH` or a blanket `ok`.

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

The key was fine right up through the wrap. The unwrap step produced something with a different
fingerprint than what went in, and that's exactly what gets published. `k1` is named because
that's where this chain of custody started.

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

`stashed` was wrapped away from the *first* `first-use`, before the label was ever reused. Even
though `first-use` later gets reassigned to a second, different key (flagged as a duplicate),
`recovered` (unwrapped from `stashed`) still traces back to the *first* key, and its fingerprint
(hash A) still matches what was attested for it. The duplicate is reported, but `recovered` is
still `ok`.

## Constraints

- Every line is one of the five step kinds above; there are no blank lines.
- Every label that's fingerprinted was just created by the immediately preceding `generate`,
  `wrap`, or `unwrap` step for that same label.
- An input has at most 20 steps and at most 6 `publish` lines.
- Each case has a 10-second limit; this checkpoint does no heavy computation at all.
- There are 10 tests: 2 for R1, 2 for R2, 2 for R3, 1 for R4, 2 for R5 and 1 end-to-end case
  mixing several keys, a duplicate label, a defective unwrap and an undefined reference in one
  ceremony. Part of the set is random and changes with `-Fresh`.

## Source material

- eMudhra, [Statement on Recent Certificate Security Incident](https://emudhra.com/en/post/certificate-security-incident), Update 3 ("How it happened", and the statement that the root cause is not yet confirmed)
- Checkpoint 12 (`problems/12-generate-key.md`): the step that should always go right, before any ceremony log even starts

## Hints

<details><summary>Hint 1: where to start</summary>

Work through the log top to bottom, keeping track, for every label you've seen, which key it
currently refers to. "Which key" is the hard part: don't track it by label text alone, since a
label can be reused.
</details>

<details><summary>Hint 2: the approach</summary>

Give every `generate` step its own identity (a counter works well: 1, 2, 3, ...), even if it
reuses a label. Keep a dictionary from label to "the identity it currently points to," updated by
`generate` (a brand new identity), `wrap` and `unwrap` (whatever identity the source label
currently points to). Keep a second dictionary from identity to its attested ground-truth
fingerprint (set once, by the very first `fingerprint` line for a freshly generated label), and a
third from label to its most recently recorded fingerprint. At `publish`, look up the label's
current identity and compare.
</details>

<details><summary>Hint 3: the traps</summary>

- A label used twice by `generate` needs its own fresh identity the second time; don't let the
  second `generate` overwrite the ground truth of the first one's identity.
- `wrap` and `unwrap` look up whatever identity their *source* label currently points to, at the
  moment they run, not at some later point.
- `publish` of an unknown label never had an identity at all: check for that before doing
  anything else with it.
- The MISMATCH message names the label the chain started at (the `generate` step), not the
  `wrap`/`unwrap` step that corrupted it, and not the label being published.
- `duplicate` lines and `publish` lines are interleaved in log order, not grouped separately.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
points_at = {}        # label -> identity id
generated_as = {}      # identity id -> label it was generated under
ground_truth = {}      # identity id -> fingerprint attested at generation
current_fp = {}        # label -> most recent fingerprint recorded for it
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
        current_fp[label] = hex
        id = points_at[label]
        if id not yet in ground_truth: ground_truth[id] = hex
    if step is publish(label):
        if label not in points_at: emit "publish " + label + " undefined"; continue
        id = points_at[label]
        if current_fp[label] == ground_truth[id]: emit "publish " + label + " ok"
        else: emit "publish " + label + " MISMATCH " + generated_as[id]
```
</details>

## Checking your solution

```
./check.sh 14                                     run every test
./check.sh 14 -Case 14-R2-bad-unwrap               one test, showing its full input, expected output and your output
./check.sh 14 -Fresh                               a new set of tests (new random seed), to confirm on data you haven't seen
./check.sh 14 -Dispute <id> "why"                  set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R2  A defective unwrap that substitutes a different token is caught ... .    1 / 2   FAILED
      x 14-R2-bad-unwrap  the unwrap step silently substitutes a different token: MISMATCH at publish
          line 1: expected `publish k1b MISMATCH k1`, got `publish k1b ok`
          likely cause: R2 - A defective unwrap that substitutes a different token is caught at publish: `MISMATCH <origin>`
          expected values from: definitional: fingerprint = sha256(token) in hex, computed by hashlib in this generator
          reproduce: python3 -P tools/run_py.py solutions 14 build/cases/14/14-R2-bad-unwrap.in build/cases/14/14-R2-bad-unwrap.out
```

## After you pass: compare with the post

The post describes the outcome of a ceremony gone wrong, in the vaguest possible terms, and says
plainly that the root cause isn't confirmed; there's no author's code to compare against here.
What you built is one way a ceremony-log checker could have caught something shaped like what
they described, without claiming to know what their software actually does.

**Something to look for:** the post's mention of "similar labels" is doing real work in this
checkpoint. A ceremony that lets the same name mean two different things at different times is a
process hazard worth flagging on its own, R3's point, separate from whether a key's material
actually got corrupted along the way.
