"""Test cases for assignment 14 (check a key ceremony).

This assignment models one failure shape that fits eMudhra's own account of its incident (Mozilla
bug 2083449, comment 11): the ceremony created the intended keys, a deviation from the usual
script was approved, a second and weaker key pair appeared, and the weaker pair was used for the
CSR "because the key labels were similar". eMudhra has not confirmed a root cause, and nobody
outside eMudhra has described its ceremony software. The log format here is a teaching model,
not eMudhra's format or process.

Where the expected answers come from. A `Key` is a real P-384 public key: the generator derives
d*G with OpenSSL (tools/curves.py), builds the uncompressed point (0x04 || x || y), and the
fingerprint in the log is hashlib's SHA-256 of those bytes (definitional, nothing here
reimplements a hash). Strong keys use a large random d; weak keys use a small d such as 4. The
generator never shows the learner's program anything but fingerprints.

The expected output is computed by `Log`, which tracks keys as bytes (and the key a CSR really
used as a `Key` object), never by comparing the fingerprint strings the learner compares. The rules
it applies are the ones in the problem page, written once more here from the page. Every
hand-made scenario also states its expected lines as a literal, taken from the page's rules, and
the generator asserts that `Log` agrees before writing anything. A few cases show a limit: when
the witnesses approved a weak key, the check says `ok` (R1).

    python3 -P tools/gen_p14.py                                  # tests/14 (seed 1)
    python3 -P tools/gen_p14.py --seed 777 --out build/fresh/14  # what `check 14 -Fresh` runs
"""

import hashlib
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = ("definitional: fingerprint = sha256 of the uncompressed P-384 public point, computed by hashlib "
       "from OpenSSL's d*G; expected lines follow the page's rules")

REQUIREMENTS = [
    ("R1", "A `csr` whose fingerprint equals the one approved for its label writes `ok`, and its `publish` writes `ok`"),
    ("R2", "A `csr` whose fingerprint differs from the approved one writes `MISMATCH <key-label>`, naming the label of the `generate` line with that fingerprint, or `unknown`"),
    ("R3", "A `csr` under a label with no current approval writes `NOT-APPROVED`; labels match as written, and a later `approve` replaces an earlier one"),
    ("R4", "An approved deviation clears every approval, so a `csr` needs a new `approve` after it"),
    ("R5", "After `deviation none`, every later `csr` and `publish` writes `UNVERIFIED`, and nothing later restores verification"),
    ("R6", "A `publish` writes `undefined` when no `csr` used its label, `BLOCKED` when the latest `csr` under the label did not write `ok`, and `ok` otherwise"),
    ("R7", "A `generate` whose label an earlier `generate` already used writes `duplicate <label>`"),
    ("R8", "A `generate` whose label equals an earlier `generate` label after lowercasing and removing `-`, `_` and `.` writes `similar <label> <earlier-label>`"),
    ("R9", "When several findings apply to one step, the step writes only the first in the priority order"),
    ("R10", "The output follows log order: one line per `deviation`, `csr` and `publish`, a line per `generate` only when it has a finding, and nothing for `approve`"),
    ("E2E", "A longer ceremony mixing every event kind, with a substituted weak key, similar labels and deviations"),
]
EXPLAIN = "_lines=R10 duplicate=R7 similar=R8"

N384 = curves.CURVES["P-384"]["n"]
SEPARATORS = re.compile(r"[-_.]")
LABEL = re.compile(r"[A-Za-z0-9._-]*[A-Za-z0-9][A-Za-z0-9._-]*")


class Key:
    """A P-384 key pair: `d` is the private value (never shown to the learner's program)."""

    def __init__(self, d: int):
        x, y = curves.public_point("P-384", d)
        self.d = d
        self.public = b"\x04" + x.to_bytes(48, "big") + y.to_bytes(48, "big")
        self.fp = hashlib.sha256(self.public).hexdigest()


def strong_key(rng) -> Key:
    return Key(rng.randrange(1 << 300, N384))


def weak_key(d: int = 4) -> Key:
    assert 1 <= d <= 4096
    return Key(d)


def squash(label: str) -> str:
    return SEPARATORS.sub("", label.lower())


class Log:
    """One ceremony log and the output a correct checker must produce for it.

    Keys are tracked as `Key` objects: which key a CSR really used, and which label a key was
    generated under, come from object identity and bytes, not from fingerprint strings."""

    def __init__(self):
        self.lines = []
        self.expected = []
        self.generated = []     # (label, Key) in log order
        self.approved = {}      # label -> Key the witnesses approved
        self.csr_passed = {}    # label -> whether the latest csr under it was ok
        self.unverified = False

    @staticmethod
    def _check_label(label):
        assert LABEL.fullmatch(label), f"label {label!r} must be ASCII letters, digits and -_. with one alphanumeric"
        assert label not in ("unknown", "none"), "labels are never `unknown` or `none`"

    def generate(self, label, key):
        self._check_label(label)
        assert all(k.public != key.public for _, k in self.generated), "no two generate lines share a key"
        if any(l == label for l, _ in self.generated):
            self.expected.append(f"duplicate {label}")
        else:
            earlier = [l for l, _ in self.generated if squash(l) == squash(label)]
            if earlier:
                self.expected.append(f"similar {label} {earlier[0]}")
        self.generated.append((label, key))
        self.lines.append(f"generate {label} {key.fp}")

    def approve(self, label, key):
        self._check_label(label)
        self.approved[label] = key
        self.lines.append(f"approve {label} {key.fp}")

    def deviation(self, approver):
        assert approver == "none" or LABEL.fullmatch(approver)
        if approver == "none":
            self.unverified = True
            self.expected.append("deviation none UNAPPROVED")
        else:
            self.approved.clear()
            self.expected.append(f"deviation {approver} approved")
        self.lines.append(f"deviation {approver}")

    def csr(self, label, key):
        self._check_label(label)
        if self.unverified:
            status = "UNVERIFIED"
        elif label not in self.approved:
            status = "NOT-APPROVED"
        elif self.approved[label].public != key.public:
            actual = next((l for l, k in self.generated if k.public == key.public), "unknown")
            status = f"MISMATCH {actual}"
        else:
            status = "ok"
        self.csr_passed[label] = status == "ok"
        self.expected.append(f"csr {label} {status}")
        self.lines.append(f"csr {label} {key.fp}")

    def publish(self, label):
        self._check_label(label)
        if label not in self.csr_passed:
            status = "undefined"
        elif self.unverified:
            status = "UNVERIFIED"
        elif not self.csr_passed[label]:
            status = "BLOCKED"
        else:
            status = "ok"
        self.expected.append(f"publish {label} {status}")
        self.lines.append(f"publish {label}")


def main():
    args = wbcore.parse_args("14")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def scenario(case_id, req, title, build, literal=None):
        """Builds one log; `literal` is the expected output written out from the page's rules."""
        log = Log()
        build(log)
        if literal is not None:
            assert log.expected == literal, f"{case_id}: the oracle says {log.expected}, the page says {literal}"
        assert len(log.lines) <= 50, f"{case_id}: more than 50 lines"
        assert sum(l.startswith("publish ") for l in log.lines) <= 8, f"{case_id}: more than 8 publish lines"
        cases.add(case_id, req, title, log.lines, log.expected)

    def keys(n, weak_ds=()):
        return [strong_key(rng) for _ in range(n)], [weak_key(d) for d in weak_ds]

    # R1 - matching approval and CSR.
    def r1(c):
        (a, b), _ = keys(2)
        c.generate("ica-g3b-dv", a)
        c.generate("ica-g3b-ov", b)
        c.approve("ica-g3b-dv", a)
        c.approve("ica-g3b-ov", b)
        c.csr("ica-g3b-dv", a)
        c.csr("ica-g3b-ov", b)
        c.publish("ica-g3b-dv")
        c.publish("ica-g3b-ov")
    scenario("14-R1-clean-two-keys", "R1", "two keys generated, approved, turned into CSRs and published: ok", r1,
             ["csr ica-g3b-dv ok", "csr ica-g3b-ov ok", "publish ica-g3b-dv ok", "publish ica-g3b-ov ok"])

    def r1b(c):
        (a,), (w,) = keys(1, (4,))
        c.generate("ica-g3c-dv", a)
        c.generate("ica-g3c-ov", w)  # private value 4: anyone can recover it
        c.approve("ica-g3c-ov", w)   # the witnesses approved the weak key themselves
        c.csr("ica-g3c-ov", w)
        c.publish("ica-g3c-ov")
    scenario("14-R1-approved-weak-key-passes", "R1",
             "the key the witnesses approved is itself weak (private value 4): nothing here can tell, ok", r1b,
             ["csr ica-g3c-ov ok", "publish ica-g3c-ov ok"])

    # R2 - the CSR's key is not the approved one.
    def r2(c):
        (s,), (w,) = keys(1, (4,))
        c.generate("ica-g3b-dv", s)
        c.approve("ica-g3b-dv", s)
        c.deviation("alice")
        c.generate("ICA_G3B_DV", w)  # a second pair appears onboard
        c.approve("ica-g3b-dv", s)   # re-verified after the deviation
        c.csr("ica-g3b-dv", w)       # the operator used the weak pair
        c.publish("ica-g3b-dv")
    scenario("14-R2-weak-pair-substituted", "R2",
             "a second pair with a similar label appears after an approved deviation and its key is used for the CSR", r2,
             ["deviation alice approved", "similar ICA_G3B_DV ica-g3b-dv", "csr ica-g3b-dv MISMATCH ICA_G3B_DV",
              "publish ica-g3b-dv BLOCKED"])

    def r2b(c):
        (s,), (w,) = keys(1, (4,))
        c.generate("ica-g3b-dv", s)
        c.generate("ica-g3b-dv", w)  # same label, different key
        c.approve("ica-g3b-dv", s)
        c.csr("ica-g3b-dv", w)
    scenario("14-R2-identical-labels-different-keys", "R2",
             "two keys share one label; the CSR uses the unapproved one, so only the fingerprint tells them apart", r2b,
             ["duplicate ica-g3b-dv", "csr ica-g3b-dv MISMATCH ica-g3b-dv"])

    def r2c(c):
        (s, outside), _ = keys(2)
        c.generate("ica-1", s)
        c.approve("ica-1", s)
        c.csr("ica-1", outside)  # a key no generate line ever recorded
    scenario("14-R2-key-never-generated", "R2", "the CSR carries a key that no generate line recorded: MISMATCH unknown", r2c,
             ["csr ica-1 MISMATCH unknown"])

    def r2d(c):
        (a, b), _ = keys(2)
        c.generate("sub-a", a)
        c.generate("sub-b", b)
        c.approve("sub-a", a)
        c.approve("sub-b", b)
        c.csr("sub-a", b)  # the two approved keys swapped
        c.csr("sub-b", b)
    scenario("14-R2-two-approved-keys-swapped", "R2",
             "the CSR for sub-a uses sub-b's key: MISMATCH names sub-b, and sub-b's own CSR is still ok", r2d,
             ["csr sub-a MISMATCH sub-b", "csr sub-b ok"])

    # R3 - no current approval for the label.
    def r3(c):
        (a, b), _ = keys(2)
        c.generate("ica-g3b-ev", a)
        c.generate("ica-g3c-ev", b)
        c.approve("ica-g3c-ev", b)
        c.csr("ica-g3b-ev", a)  # never approved
        c.csr("ICA-G3C-EV", b)  # approved under ica-g3c-ev: labels match exactly, letter case included
    scenario("14-R3-no-approval-for-label", "R3",
             "a label never approved, and a label that differs from an approved one only in letter case", r3,
             ["csr ica-g3b-ev NOT-APPROVED", "csr ICA-G3C-EV NOT-APPROVED"])

    def r3b(c):
        (a, b), _ = keys(2)
        c.generate("old-key", a)
        c.generate("new-key", b)
        c.approve("ica", a)
        c.approve("ica", b)  # the witnesses changed their mind: this approval replaces the first
        c.csr("ica", b)
        c.csr("ica", a)
    scenario("14-R3-latest-approval-replaces-earlier", "R3",
             "a label approved twice: only the latest key counts", r3b,
             ["csr ica ok", "csr ica MISMATCH old-key"])

    # R4 - approved deviation clears the approvals.
    def r4(c):
        (a,), _ = keys(1)
        c.generate("k1", a)
        c.approve("k1", a)
        c.deviation("bob")
        c.csr("k1", a)      # approved before the deviation: stale
        c.approve("k1", a)
        c.csr("k1", a)      # re-verified: ok
    scenario("14-R4-approvals-need-redoing", "R4", "an approved deviation clears the approval; approving again restores ok", r4,
             ["deviation bob approved", "csr k1 NOT-APPROVED", "csr k1 ok"])

    def r4b(c):
        (a, b), _ = keys(2)
        c.generate("k1", a)
        c.generate("k2", b)
        c.approve("k1", a)
        c.approve("k2", b)
        c.deviation("carol")
        c.approve("k2", b)  # only k2 is re-approved
        c.csr("k1", a)
        c.csr("k2", b)
        c.deviation("carol")
        c.csr("k2", b)      # a second deviation clears it again
    scenario("14-R4-every-approval-cleared", "R4",
             "two keys approved, a deviation, only one re-approved, then a second deviation clears it again", r4b,
             ["deviation carol approved", "csr k1 NOT-APPROVED", "csr k2 ok", "deviation carol approved",
              "csr k2 NOT-APPROVED"])

    # R5 - unapproved deviation.
    def r5(c):
        (a,), _ = keys(1)
        c.generate("k1", a)
        c.deviation("none")
        c.approve("k1", a)
        c.csr("k1", a)  # everything matches, and it is still unverified
    scenario("14-R5-unapproved-then-everything-matches", "R5",
             "no one approved the deviation: a CSR whose fingerprint matches its approval is UNVERIFIED", r5,
             ["deviation none UNAPPROVED", "csr k1 UNVERIFIED"])

    def r5b(c):
        (a, b), _ = keys(2)
        c.generate("k1", a)
        c.generate("k2", b)
        c.approve("k1", a)
        c.approve("k2", b)
        c.csr("k1", a)      # before the deviation: ok
        c.deviation("none")
        c.csr("k1", a)
        c.csr("k2", b)
    scenario("14-R5-only-later-csrs-affected", "R5",
             "a CSR before the unapproved deviation stays ok; every CSR after it, for any label, is UNVERIFIED", r5b,
             ["csr k1 ok", "deviation none UNAPPROVED", "csr k1 UNVERIFIED", "csr k2 UNVERIFIED"])

    def r5c(c):
        (a,), _ = keys(1)
        c.generate("k1", a)
        c.deviation("none")
        c.deviation("dave")  # a later approved deviation does not undo it
        c.approve("k1", a)
        c.csr("k1", a)
        c.publish("k1")
    scenario("14-R5-later-approval-does-not-restore", "R5",
             "an approved deviation after an unapproved one does not make the ceremony verified again", r5c,
             ["deviation none UNAPPROVED", "deviation dave approved", "csr k1 UNVERIFIED", "publish k1 UNVERIFIED"])

    # R6 - publish.
    def r6(c):
        (a, b), _ = keys(2)
        c.generate("good", a)
        c.generate("bad", b)
        c.approve("good", a)
        c.csr("good", a)
        c.csr("bad", b)
        c.publish("good")
        c.publish("bad")
    scenario("14-R6-publish-ok-and-blocked", "R6", "publish follows its CSR: ok for the good one, BLOCKED for the failed one", r6,
             ["csr good ok", "csr bad NOT-APPROVED", "publish good ok", "publish bad BLOCKED"])

    def r6b(c):
        (a, b), _ = keys(2)
        c.generate("k1", a)
        c.approve("k1", a)
        c.csr("k1", a)
        c.publish("k2")      # no CSR under k2 (and no key either)
        c.publish("k1")
    scenario("14-R6-publish-undefined", "R6", "a publish of a label that has no CSR is undefined", r6b,
             ["csr k1 ok", "publish k2 undefined", "publish k1 ok"])

    def r6c(c):
        (a, b), _ = keys(2)
        c.generate("k1", a)
        c.generate("k2", b)
        c.approve("k1", a)
        c.approve("k2", b)
        c.csr("k1", b)       # k1: wrong key, then the right one
        c.csr("k1", a)
        c.csr("k2", b)       # k2: right key, then the wrong one
        c.csr("k2", a)
        c.publish("k1")
        c.publish("k2")
    scenario("14-R6-latest-csr-decides", "R6", "each publish follows the latest CSR under its label", r6c,
             ["csr k1 MISMATCH k2", "csr k1 ok", "csr k2 ok", "csr k2 MISMATCH k1", "publish k1 ok",
              "publish k2 BLOCKED"])

    def r6d(c):
        (a,), _ = keys(1)
        c.generate("k1", a)
        c.approve("k1", a)
        c.csr("k1", a)       # ok
        c.deviation("none")
        c.publish("k1")
    scenario("14-R6-publish-after-unapproved-deviation", "R6",
             "a CSR that was ok, then an unapproved deviation, then its publish: UNVERIFIED", r6d,
             ["csr k1 ok", "deviation none UNAPPROVED", "publish k1 UNVERIFIED"])

    def r6e(c):
        (a,), _ = keys(1)
        c.generate("k1", a)
        c.approve("k1", a)
        c.csr("k1", a)       # ok
        c.deviation("erin")  # clears approvals, but the CSR was already made
        c.publish("k1")
    scenario("14-R6-publish-ignores-later-approved-deviation", "R6",
             "a CSR that was ok, then an approved deviation, then its publish: still ok", r6e,
             ["csr k1 ok", "deviation erin approved", "publish k1 ok"])

    # R7 - exact duplicate labels.
    def r7(c):
        (a, b), _ = keys(2)
        c.generate("shared", a)
        c.generate("shared", b)
    scenario("14-R7-duplicate-label", "R7", "a label reused by a second generate step", r7, ["duplicate shared"])

    def r7b(c):
        (a, b, d, e), _ = keys(4)
        c.generate("slot", a)
        c.generate("other", b)
        c.generate("slot", d)
        c.generate("slot", e)  # a third use is a duplicate too
    scenario("14-R7-every-reuse-is-flagged", "R7", "a label used three times is flagged at the second and the third use", r7b,
             ["duplicate slot", "duplicate slot"])

    # R8 - similar labels after normalisation.
    def r8(c):
        ks = [strong_key(rng) for _ in range(5)]
        c.generate("ica-g3b-ov", ks[0])
        c.generate("ICA-G3B-OV", ks[1])  # case
        c.generate("ica_g3b_ov", ks[2])  # separator
        c.generate("ica.g3b.ov", ks[3])  # another separator
        c.generate("icag3bov", ks[4])    # no separators
    scenario("14-R8-case-and-separators", "R8", "case, underscore, dot and missing separators all match the first label", r8,
             ["similar ICA-G3B-OV ica-g3b-ov", "similar ica_g3b_ov ica-g3b-ov", "similar ica.g3b.ov ica-g3b-ov",
              "similar icag3bov ica-g3b-ov"])

    def r8b(c):
        ks = [strong_key(rng) for _ in range(6)]
        c.generate("ica-g3b-ov", ks[0])
        c.generate("ica-g3b-ov2", ks[1])  # digits are kept
        c.generate("ica-g3b-0v", ks[2])   # digit 0 is not letter o
        c.generate("ica-g3c-ov", ks[3])   # one letter differs
        c.generate("k1", ks[4])
        c.generate("kl", ks[5])
    scenario("14-R8-not-similar", "R8",
             "labels that differ in a digit or a letter are not similar (no homoglyph rule)", r8b, [])

    def r8c(c):
        ks = [strong_key(rng) for _ in range(5)]
        c.generate("A.b", ks[0])
        c.generate("a-B", ks[1])   # similar to A.b
        c.generate("A_B", ks[2])   # similar to both: the earliest is named
        c.generate("ab", ks[3])
        c.generate("a-b", ks[4])
    scenario("14-R8-names-earliest-match", "R8",
             "a label that matches several earlier labels names the earliest one; earlier labels are never flagged later", r8c,
             ["similar a-B A.b", "similar A_B A.b", "similar ab A.b", "similar a-b A.b"])

    # R9 - priorities.
    def r9(c):
        ks = [strong_key(rng) for _ in range(4)]
        c.generate("Key-A", ks[0])
        c.generate("key_a", ks[1])  # similar to Key-A
        c.generate("key_a", ks[2])  # exact duplicate of key_a, and similar to Key-A too
        c.generate("KEY.A", ks[3])  # similar to both, not an exact duplicate
    scenario("14-R9-duplicate-over-similar", "R9", "an exact duplicate that is also similar to an earlier label shows duplicate", r9,
             ["similar key_a Key-A", "duplicate key_a", "similar KEY.A Key-A"])

    def r9b(c):
        (a, b, d), _ = keys(3)
        c.generate("k1", a)
        c.csr("k1", b)          # no approval and a wrong key: NOT-APPROVED
        c.approve("k1", a)
        c.csr("k1", d)          # MISMATCH
        c.deviation("none")
        c.csr("k1", d)          # unverified, no matter what else is wrong
        c.csr("never-approved", d)
    scenario("14-R9-csr-priority", "R9",
             "UNVERIFIED beats NOT-APPROVED, and NOT-APPROVED beats MISMATCH, when several apply to one CSR", r9b,
             ["csr k1 NOT-APPROVED", "csr k1 MISMATCH unknown", "deviation none UNAPPROVED", "csr k1 UNVERIFIED",
              "csr never-approved UNVERIFIED"])

    def r9c(c):
        (a, b), _ = keys(2)
        c.generate("k1", a)
        c.generate("k2", b)
        c.approve("k1", a)
        c.csr("k1", a)
        c.csr("k2", b)
        c.deviation("none")
        c.publish("k1")       # csr ok but unverified now
        c.publish("k2")       # csr failed and unverified: UNVERIFIED wins over BLOCKED
        c.publish("k3")       # no csr: undefined wins over UNVERIFIED
    scenario("14-R9-publish-priority", "R9",
             "undefined beats UNVERIFIED, and UNVERIFIED beats BLOCKED, when several apply to one publish", r9c,
             ["csr k1 ok", "csr k2 NOT-APPROVED", "deviation none UNAPPROVED", "publish k1 UNVERIFIED",
              "publish k2 UNVERIFIED", "publish k3 undefined"])

    # R10 - output follows log order.
    def r10(c):
        (a, b, d), (w,) = keys(3, (4,))
        c.generate("ica-g3b-dv", a)
        c.approve("ica-g3b-dv", a)
        c.csr("ica-g3b-dv", a)
        c.generate("ICA_G3B_DV", w)
        c.deviation("frank")
        c.generate("ica-g3c-dv", b)
        c.publish("ica-g3b-dv")
        c.approve("ica-g3c-dv", b)
        c.csr("ica-g3c-dv", b)
        c.generate("ica.g3c.dv", d)
        c.publish("ica-g3c-dv")
    scenario("14-R10-log-order", "R10", "findings, deviation, csr and publish lines interleave in log order; approve prints nothing", r10,
             ["csr ica-g3b-dv ok", "similar ICA_G3B_DV ica-g3b-dv", "deviation frank approved", "publish ica-g3b-dv ok",
              "csr ica-g3c-dv ok", "similar ica.g3c.dv ica-g3c-dv", "publish ica-g3c-dv ok"])

    def r10b(c):
        (a, b), _ = keys(2)
        c.generate("k1", a)
        c.deviation("none")
        c.generate("k1", b)      # label findings do not depend on verification
        c.generate("K-1", strong_key(rng))
    scenario("14-R10-generate-findings-after-unapproved-deviation", "R10",
             "duplicate and similar findings still print after an unapproved deviation", r10b,
             ["deviation none UNAPPROVED", "duplicate k1", "similar K-1 k1"])

    # E2E - the failure shape: intended keys, approved deviation, a weak second pair, wrong CSR.
    def incident(c, seed):
        n = 4
        bad = seed % n
        intended = [strong_key(rng) for _ in range(n)]
        weak = weak_key(4)
        names = ["ica-g3b-dv", "ica-g3b-ov", "ica-g3b-ev", "ica-g3c-dv"]
        for name, key in zip(names, intended):
            c.generate(name, key)
        for name, key in zip(names, intended):
            c.approve(name, key)
        c.deviation("grace")                                  # an approved deviation: clears approvals
        c.generate(names[bad].upper().replace("-", "_"), weak)               # the second, weaker pair
        for name, key in zip(names, intended):
            c.approve(name, key)                              # re-verified after the deviation
        for i, name in enumerate(names):
            c.csr(name, weak if i == bad else intended[i])
        for name in names:
            c.publish(name)
        c.deviation("none")                                   # a later, unapproved departure
        c.csr(names[0], intended[0])
        c.publish(names[0])
        c.publish("ica-g3c-ov")
    scenario(f"14-E2E-incident-shape-s{args.seed}", "E2E",
             f"four keys, an approved deviation, a weak pair with a similar label used for one CSR, then an unapproved "
             f"deviation (seed {args.seed})", lambda c: incident(c, args.seed))

    def random_ceremony(r):
        """A random valid log; retried until it shows ok, a finding and a failed CSR."""
        for _ in range(200):
            c = Log()
            strong = [strong_key(r) for _ in range(5)]
            weak = [weak_key(d) for d in r.sample(range(2, 4097), 2)]
            pool = strong + weak
            r.shuffle(pool)
            base = ["ica-g3b-dv", "ica-g3c-ov", "ica-3", "sub.ca.4"]
            variants = []
            for b in base:
                variants += [b, b.upper(), b.replace("-", "_").replace(".", "_"), b.replace("-", "").replace(".", "")]
            labels = r.sample(variants, 7)
            steps = r.randint(14, 30)
            unapproved_at = r.randrange(steps // 2, steps) if r.random() < 0.6 else None
            unused = list(pool)
            made = []  # keys generated so far
            for step in range(steps):
                if step == unapproved_at:
                    c.deviation("none")
                    continue
                kind = r.choices(["generate", "approve", "deviation", "csr", "publish"], [4, 4, 1, 5, 3])[0]
                if kind == "generate" and unused:
                    key = unused.pop()
                    made.append(key)
                    c.generate(r.choice(labels), key)
                elif kind == "approve" and made:
                    c.approve(r.choice(labels), r.choice(made))
                elif kind == "deviation":
                    c.deviation(r.choice(["grace", "heidi", "ivan"]))
                elif kind == "csr" and made:
                    key = r.choice(made + unused[:1])  # sometimes a key no generate line recorded
                    c.csr(r.choice(labels), key)
                elif kind == "publish":
                    c.publish(r.choice(labels))
            text = "\n".join(c.expected)
            if (12 <= len(c.lines) <= 50 and sum(l.startswith("publish ") for l in c.lines) <= 8 and " ok" in text and "MISMATCH" in text and ("similar" in text or "duplicate" in text)
                    and ("NOT-APPROVED" in text or "BLOCKED" in text)):
                return c
        raise AssertionError("no random ceremony met the coverage conditions")

    log = random_ceremony(random.Random(args.seed * 7919 + 14))
    cases.add(f"14-E2E-random-s{args.seed}", "E2E", f"a random valid ceremony of {len(log.lines)} lines (seed {args.seed})",
              log.lines, log.expected)

    cases.save()


if __name__ == "__main__":
    main()
