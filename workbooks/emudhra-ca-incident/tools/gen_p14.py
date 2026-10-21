"""Test cases for checkpoint 14 (check a key ceremony).

This checkpoint models, in simplified form, the shape eMudhra's own account suggests for its
incident: a key generation step, then a wrap/unwrap round trip, then publication - with the
possibility that an unwrap step silently substitutes different key material. eMudhra has not
confirmed its root cause; this is a teaching model of a plausible failure shape, not a factual
reconstruction of their ceremony software.

The oracle here is definitional, not computed by any second algorithm: each `generate` step gets
a real 32-byte token (the generator's own ground truth, never shown to the learner's program),
and `fingerprint` lines in the log carry sha256(token) in hex, computed the same way the
"expected" values below are computed - with hashlib, directly, by hand, right here. A correctly
behaving `wrap`/`unwrap` pair always carries the same token forward; a planted defect (built
explicitly, never by chance) swaps in a fresh, different token during `unwrap`. Whether a
published key's current fingerprint matches what was attested for it at its *origin* `generate`
step is just a hex-string comparison - there is nothing to validate this against except the
construction being honest, which the asserts below check.

    python3 -P tools/gen_p14.py                                  # tests/14 (seed 1)
    python3 -P tools/gen_p14.py --seed 777 --out build/fresh/14  # what `check 14 -Fresh` runs
"""

import hashlib
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import wbcore  # noqa: E402

LIB = "definitional: fingerprint = sha256(token) in hex, computed by hashlib in this generator"

REQUIREMENTS = [
    ("R1", "A clean ceremony (generate, wrap, a correct unwrap, publish) reports `ok`"),
    ("R2", "A defective unwrap that substitutes a different token is caught at publish: `MISMATCH <origin>`"),
    ("R3", "A label reused by a second `generate` step is flagged `duplicate <label>`"),
    ("R4", "A `publish` of a label never generated, wrapped, or unwrapped is flagged `undefined`"),
    ("R5", "Several keys in one ceremony, only one defective: each publish line is judged on its own"),
    ("E2E", "A longer ceremony mixing wraps, unwraps, a duplicate label and several publishes"),
]
EXPLAIN = "_lines=R1"


def sha256_hex(token_hex: str) -> str:
    return hashlib.sha256(bytes.fromhex(token_hex)).hexdigest()


class Ceremony:
    """Builds one ceremony log and, alongside it, the output a correct checker must produce.
    All bookkeeping here (`tokens`, `identity_token`) is the generator's own ground truth; none of
    it appears in the log text the learner's program reads. Only `generate`'s curve name,
    `wrap`/`unwrap`'s labels, and `fingerprint`'s hex digest are ever written to the log.

    Every `generate` starts a brand new identity (tracked here by a counter), even when it reuses
    a label an earlier `generate` already used. That reuse is flagged (`duplicate`) on its own,
    but it never retroactively changes what an earlier `wrap`/`unwrap` chain - already pointing at
    the old identity - resolves to: a label is only ever "the current name for some identity"."""

    def __init__(self, rng):
        self.rng = rng
        self.lines = []
        self.expected = []
        self.tokens = {}          # label -> the real 32-byte token currently there (hidden)
        self.identity_of = {}     # label -> the identity id it currently refers to
        self.identity_token = {}  # identity id -> the token attested at ITS OWN generation
        self.identity_label = {}  # identity id -> the label it was generated under
        self.known = set()
        self.next_id = 0

    def _token(self):
        return bytes(self.rng.randrange(256) for _ in range(32)).hex()

    def generate(self, label, curve):
        if label in self.known:
            self.expected.append(f"duplicate {label}")
        token = self._token()
        self.next_id += 1
        identity = self.next_id
        self.tokens[label] = token
        self.identity_of[label] = identity
        self.identity_token[identity] = token
        self.identity_label[identity] = label
        self.known.add(label)
        self.lines.append(f"generate {label} {curve}")
        self.lines.append(f"fingerprint {label} {sha256_hex(token)}")

    def wrap(self, label, wrapped_label):
        token = self.tokens[label]  # wrap is always correctly reversible in this model
        self.tokens[wrapped_label] = token
        self.identity_of[wrapped_label] = self.identity_of[label]
        self.known.add(wrapped_label)
        self.lines.append(f"wrap {label} {wrapped_label}")
        self.lines.append(f"fingerprint {wrapped_label} {sha256_hex(token)}")

    def unwrap(self, wrapped_label, label, defect=False):
        token = self.tokens[wrapped_label]
        if defect:
            fresh = self._token()
            assert fresh != token, "a planted defect must actually be a different token"
            token = fresh
        self.tokens[label] = token
        self.identity_of[label] = self.identity_of[wrapped_label]
        self.known.add(label)
        self.lines.append(f"unwrap {wrapped_label} {label}")
        self.lines.append(f"fingerprint {label} {sha256_hex(token)}")

    def publish(self, label, undefined=False):
        self.lines.append(f"publish {label}")
        if undefined:
            assert label not in self.known, "an 'undefined' publish must name a label never introduced"
            self.expected.append(f"publish {label} undefined")
            return
        identity = self.identity_of[label]
        truth = sha256_hex(self.identity_token[identity])
        actual = sha256_hex(self.tokens[label])
        if truth == actual:
            self.expected.append(f"publish {label} ok")
        else:
            origin_label = self.identity_label[identity]
            assert self.tokens[label] != self.identity_token[identity]  # a real mismatch, not a typo
            self.expected.append(f"publish {label} MISMATCH {origin_label}")


def main():
    args = wbcore.parse_args("14")
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def scenario(case_id, req, title, build):
        c = Ceremony(random.Random(rng.randrange(1 << 30)))
        build(c)
        cases.add(case_id, req, title, c.lines, c.expected)

    # R1 - a clean ceremony: generate, wrap, a correct unwrap, publish.
    def r1(c):
        c.generate("k1", "P-384")
        c.wrap("k1", "wk1")
        c.unwrap("wk1", "k1b")
        c.publish("k1b")
    scenario("14-R1-clean", "R1", "generate, wrap, a correct unwrap, then publish: ok", r1)

    def r1b(c):
        c.generate("root-key", "P-256")
        c.publish("root-key")  # published directly, no wrap/unwrap round trip at all
    scenario("14-R1-publish-straight-from-generate", "R1",
             "a key published straight from generate, no wrap/unwrap round trip: ok", r1b)

    # R2 - a defective unwrap substitutes a different token; caught at publish.
    def r2(c):
        c.generate("k1", "P-384")
        c.wrap("k1", "wk1")
        c.unwrap("wk1", "k1b", defect=True)
        c.publish("k1b")
    scenario("14-R2-bad-unwrap", "R2",
             "the unwrap step silently substitutes a different token: MISMATCH at publish", r2)

    def r2b(c):
        c.generate("intermediate-1", "P-384")
        c.wrap("intermediate-1", "wrapped-1")
        c.unwrap("wrapped-1", "unwrapped-1")
        c.wrap("unwrapped-1", "wrapped-2")
        c.unwrap("wrapped-2", "unwrapped-2", defect=True)  # the SECOND unwrap is the one that's defective
        c.publish("unwrapped-2")
    scenario("14-R2-bad-unwrap-after-good-one", "R2",
             "a correct wrap/unwrap round trip, then a second one that is defective: still caught", r2b)

    # R3 - a label reused by a second generate is flagged, whatever happens to it afterward.
    def r3(c):
        c.generate("shared", "P-256")
        c.generate("shared", "P-256")  # duplicate flagged here
        c.publish("shared")  # judged against the SECOND generate's own attested fingerprint: ok
    scenario("14-R3-duplicate-label", "R3",
             "a label reused by a second generate step is flagged, even though nothing downstream breaks", r3)

    def r3b(c):
        c.generate("first-use", "P-384")
        c.wrap("first-use", "stashed")
        c.generate("first-use", "P-384")  # duplicate: "first-use" now names a second, different key
        c.unwrap("stashed", "recovered")  # this key really did come from the FIRST "first-use"
        c.publish("recovered")
    scenario("14-R3-duplicate-does-not-disturb-earlier-wrap", "R3",
             "a duplicate generate is flagged on its own, but does not retroactively change a key "
             "already wrapped under the label's earlier, different identity", r3b)

    # R4 - publishing a label that was never generated, wrapped, or unwrapped.
    def r4(c):
        c.generate("a", "P-384")
        c.publish("a")
        c.publish("never-existed", undefined=True)
    scenario("14-R4-undefined-publish", "R4",
             "a publish step names a label that was never generated, wrapped, or unwrapped", r4)

    # R5 - several keys, only one defective: every publish line must be judged on its own.
    def r5(c):
        c.generate("k1", "P-384")
        c.wrap("k1", "wk1")
        c.unwrap("wk1", "k1b")
        c.generate("k2", "P-384")
        c.wrap("k2", "wk2")
        c.unwrap("wk2", "k2b", defect=True)  # only this one is defective
        c.generate("k3", "P-256")
        c.wrap("k3", "wk3")
        c.unwrap("wk3", "k3b")
        c.publish("k1b")
        c.publish("k2b")
        c.publish("k3b")
    scenario("14-R5-only-one-bad", "R5",
             "three keys wrapped and unwrapped; only the second is defective", r5)

    def r5b(c):
        for i in range(4):
            c.generate(f"m{i}", "P-384" if i % 2 else "P-256")
            c.wrap(f"m{i}", f"wm{i}")
            c.unwrap(f"wm{i}", f"m{i}b", defect=(i == 2))
        for i in range(4):
            c.publish(f"m{i}b")
    scenario("14-R5-four-keys-one-bad", "R5",
             "four keys in one ceremony; the third's unwrap is defective, the rest are clean", r5b)

    # E2E - a longer ceremony: several real keys, a duplicate ("similar") label, a defective
    # unwrap, and an undefined reference, mirroring the shape eMudhra's account describes without
    # claiming to reproduce their actual ceremony software.
    def e2e(c, seed):
        labels = [f"intermediate-{i + 1}" for i in range(6)]
        bad = seed % len(labels)
        for i, label in enumerate(labels):
            c.generate(label, "P-384")
            c.wrap(label, f"wrapped-{i}")
            c.unwrap(f"wrapped-{i}", f"final-{i}", defect=(i == bad))
        # a "similar label" slip elsewhere in the ceremony: a slot label gets reused for a second,
        # unrelated key. It doesn't touch any of the six keys above.
        c.generate("spare-slot", "P-384")
        c.generate("spare-slot", "P-384")  # the duplicate
        c.publish("spare-slot")  # judged against the second generate's own attested fingerprint: ok
        for i in range(len(labels)):
            c.publish(f"final-{i}")
        c.publish("intermediate-99", undefined=True)  # never part of this ceremony at all
    scenario(f"14-E2E-ceremony-s{args.seed}", "E2E",
             f"six keys wrapped and unwrapped (one defective), a reused label, and an undefined publish (seed {args.seed})",
             lambda c: e2e(c, args.seed))

    cases.save()


if __name__ == "__main__":
    main()
