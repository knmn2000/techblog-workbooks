"""Test cases for assignment 15 (block and distrust).

Expected values are mechanically derivable from the blocklist/distrust-set definitions: for every
case, this generator computes the expected verdict TWO ways, structurally differently, and
asserts they agree before writing the case. `classify_scan` mirrors how a checker would naturally
scan a chain leaf-to-root with an early-exit loop; `classify_sets` is a one-line, set-based
re-statement of the same policy, using `any()`/list comprehensions instead of a loop with a break.
Agreement between the two is the oracle; there is no third-party library for "chain blocking
policy", since this is a policy this workbook defines, not a format anyone parses.

    python3 -P tools/gen_p15.py                                  # tests/15 (seed 1)
    python3 -P tools/gen_p15.py --seed 777 --out build/fresh/15  # what `check 15 -Fresh` runs
"""

import hashlib
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import wbcore  # noqa: E402

LIB = "definitional: two structurally different restatements of the blocking policy, cross-checked before each case is written"

REQUIREMENTS = [
    ("R1", "A clean chain, with nothing blocklisted or distrusted anywhere in it, is `trusted`"),
    ("R2", "A cert whose SPKI hash is directly blocklisted blocks the chain: `blocked spki <role>`, naming that cert"),
    ("R3", "A chain anchored at a distrusted root, with no SPKI hit anywhere in it, is `blocked root <root-id>`"),
    ("R4", "When both could apply to the same chain, the SPKI block is reported, not the root distrust"),
    ("R5", "A blocklist or distrust entry for other chains' certificates does not block this one, and an entry affects only chains after it"),
    ("R6", "A blocked key blocks every chain it appears in, including a cross-signed chain to a root that is not distrusted, where root distrust alone leaves the chain trusted"),
    ("E2E", "Several chains in one input, covering every verdict, judged independently"),
]
EXPLAIN = "_lines=R1"


def spki_hash(tag: str) -> str:
    return hashlib.sha256(f"spki:{tag}".encode()).hexdigest()


def classify_scan(certs, blocked_spki, distrusted_roots):
    """How a checker would naturally scan a chain: leaf to root, stopping at the first hit."""
    for cert in certs:
        if cert["spki"] in blocked_spki:
            return ("blocked", "spki", cert["role"])
    for cert in certs:
        if cert["role"] == "root" and cert["id"] in distrusted_roots:
            return ("blocked", "root", cert["id"])
    return ("trusted",)


def classify_sets(certs, blocked_spki, distrusted_roots):
    """The same policy, restated with set membership and comprehensions instead of a loop."""
    hit_roles = [c["role"] for c in certs if c["spki"] in blocked_spki]
    if hit_roles:
        return ("blocked", "spki", hit_roles[0])
    root_ids = [c["id"] for c in certs if c["role"] == "root"]
    if root_ids and root_ids[0] in distrusted_roots:
        return ("blocked", "root", root_ids[0])
    return ("trusted",)


class World:
    """Accumulates `blocked-spki` and `distrusted-root` lines and the `chain` blocks that follow
    them, exactly as the input format lays them out, and derives each chain's expected verdict."""

    def __init__(self):
        self.lines = []
        self.blocked_spki = set()
        self.distrusted_roots = set()

    def block_spki(self, tag):
        h = spki_hash(tag)
        self.blocked_spki.add(h)
        self.lines.append(f"blocked-spki {h}")

    def distrust_root(self, root_id):
        self.distrusted_roots.add(root_id)
        self.lines.append(f"distrusted-root {root_id}")

    def chain(self, chain_id, certs):
        """certs: list of (role, spki-tag, root-id-or-None). Appends the `chain`/`cert` lines and
        returns the expected output line."""
        self.lines.append(f"chain {chain_id}")
        resolved = []
        for role, tag, root_id in certs:
            h = spki_hash(tag)
            rid = root_id if root_id is not None else "-"
            self.lines.append(f"cert {role} {h} {rid}")
            resolved.append({"role": role, "spki": h, "id": rid})
        a = classify_scan(resolved, self.blocked_spki, self.distrusted_roots)
        b = classify_sets(resolved, self.blocked_spki, self.distrusted_roots)
        assert a == b, f"the two independent classifiers disagree for chain {chain_id}: {a} vs {b}"
        if a[0] == "trusted":
            return f"chain {chain_id} trusted"
        return f"chain {chain_id} blocked {a[1]} {a[2]}"


def tag(n, s=""):
    return f"t{n}{s}"


def main():
    args = wbcore.parse_args("15")
    rng = random.Random(args.seed)

    def new_case(case_id, req, title):
        w = World()
        expected = []

        def chain(chain_id, certs):
            expected.append(w.chain(chain_id, certs))

        return w, chain, expected, lambda: cases.add(case_id, req, title, w.lines, expected)

    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    # R1 - a clean, unremarkable chain.
    w, chain, expected, save = new_case("15-R1-trusted", "R1", "a leaf, intermediate and root with nothing blocked or distrusted")
    chain("c1", [("leaf", "leaf-1", None), ("intermediate", "int-1", None), ("root", "root-1", "root-alpha")])
    save()

    # R2 - each cert role individually SPKI-blocklisted, one chain at a time.
    for role, idx in (("leaf", 1), ("intermediate", 2), ("root", 3)):
        w, chain, expected, save = new_case(
            f"15-R2-spki-blocked-{role}", "R2", f"the {role}'s own SPKI hash is directly blocklisted")
        w.block_spki(f"blocked-{role}-{idx}")
        certs = [("leaf", "leaf-x", None), ("intermediate", "int-x", None), ("root", "root-x", "root-beta")]
        certs = [(r, (f"blocked-{role}-{idx}" if r == role else t), rid) for r, t, rid in certs]
        chain("c1", certs)
        save()

    # R3 - the root is distrusted; nothing in the chain is individually SPKI-blocked.
    w, chain, expected, save = new_case(
        "15-R3-distrusted-root", "R3", "the root is on the distrust list; no SPKI hash in the chain is blocklisted")
    w.distrust_root("root-legacy")
    chain("c1", [("leaf", "leaf-2", None), ("intermediate", "int-2", None), ("root", "root-2", "root-legacy")])
    save()

    # R4 - both could apply: the SPKI block wins (checked first; it's the finer-grained, faster response).
    w, chain, expected, save = new_case(
        "15-R4-spki-wins-over-root", "R4",
        "the intermediate is SPKI-blocklisted AND the root is distrusted: the SPKI block is reported")
    w.block_spki("both-int")
    w.distrust_root("root-both")
    chain("c1", [("leaf", "leaf-3", None), ("intermediate", "both-int", None), ("root", "root-3", "root-both")])
    save()

    # R5 - a blocklist/distrust set that exists for OTHER chains must not leak onto an unrelated one.
    w, chain, expected, save = new_case(
        "15-R5-unrelated-chain-not-blocked", "R5",
        "blocklist and distrust entries for a different chain's certs/root do not affect this one")
    w.block_spki("other-chain-int")
    w.distrust_root("totally-unrelated-root")  # never the root of any chain below: pure noise data
    chain("blocked-one", [("leaf", "leaf-4", None), ("intermediate", "other-chain-int", None), ("root", "root-4", "some-other-root")])
    chain("unrelated", [("leaf", "leaf-5", None), ("intermediate", "int-5", None), ("root", "root-5", "root-gamma")])
    save()

    # R5 - an entry affects only the chains after it, even when it comes before the next `chain` line.
    w, chain, expected, save = new_case(
        "15-R5-entry-after-chain", "R5",
        "a blocklist entry and a distrust entry come after the first chain's certs: they block only the second chain")
    chain("before", [("leaf", "leaf-6", None), ("intermediate", "late-int", None), ("root", "root-6", "late-root")])
    w.block_spki("late-int")
    w.distrust_root("late-root")
    chain("after", [("leaf", "leaf-7", None), ("intermediate", "late-int", None), ("root", "root-7", "late-root")])
    save()

    # R6 - cross-signing: the same intermediate key certified under a second root. In the incident,
    # Sectigo cross-signed the eight weak keys under another root, so a chain through the
    # cross-certificate never reaches the distrusted root. Only the SPKI block stops it. Synthetic ids.
    w, chain, expected, save = new_case(
        "15-R6-cross-signed-key-blocked", "R6",
        "one blocked intermediate key in two chains, one to the distrusted root and one through a cross-certificate to another root")
    w.block_spki("cross-int")
    w.distrust_root("root-issuer")
    chain("own-root", [("leaf", "leaf-8", None), ("intermediate", "cross-int", None), ("root", "root-8", "root-issuer")])
    chain("cross-signed", [("leaf", "leaf-9", None), ("intermediate", "cross-int", None), ("root", "root-9", "root-cross-signer")])
    save()

    w, chain, expected, save = new_case(
        "15-R6-distrust-alone-misses-cross-sign", "R6",
        "root distrust stops the chain to its own root and leaves the cross-signed chain trusted, until the key is blocked")
    w.distrust_root("root-home")
    chain("own-root", [("leaf", "leaf-10", None), ("intermediate", "shared-int", None), ("root", "root-10", "root-home")])
    chain("cross-before", [("leaf", "leaf-11", None), ("intermediate", "shared-int", None), ("root", "root-11", "root-other")])
    w.block_spki("shared-int")
    chain("cross-after", [("leaf", "leaf-11", None), ("intermediate", "shared-int", None), ("root", "root-11", "root-other")])
    save()

    # E2E - several chains in one input: every verdict kind, judged independently.
    w, chain, expected, save = new_case(
        f"15-E2E-several-chains-s{args.seed}", "E2E",
        f"five chains in one input: trusted, SPKI-blocked, root-distrusted, both apply, and an unrelated trusted chain (seed {args.seed})")
    w.block_spki("e2e-blocked-int")
    w.distrust_root("e2e-distrusted-root")
    w.distrust_root("e2e-both-root")
    w.block_spki("e2e-both-int")
    chain("clean", [("leaf", f"e2e-leaf-{rng.randint(0, 9999)}", None),
                     ("intermediate", f"e2e-int-{rng.randint(0, 9999)}", None),
                     ("root", f"e2e-root-{rng.randint(0, 9999)}", "e2e-untouched-root")])
    chain("spki-hit", [("leaf", f"e2e-leaf-{rng.randint(0, 9999)}", None),
                        ("intermediate", "e2e-blocked-int", None),
                        ("root", f"e2e-root-{rng.randint(0, 9999)}", "e2e-untouched-root")])
    chain("root-hit", [("leaf", f"e2e-leaf-{rng.randint(0, 9999)}", None),
                        ("intermediate", f"e2e-int-{rng.randint(0, 9999)}", None),
                        ("root", f"e2e-root-{rng.randint(0, 9999)}", "e2e-distrusted-root")])
    chain("both-hit", [("leaf", f"e2e-leaf-{rng.randint(0, 9999)}", None),
                        ("intermediate", "e2e-both-int", None),
                        ("root", f"e2e-root-{rng.randint(0, 9999)}", "e2e-both-root")])
    chain("still-unrelated", [("leaf", f"e2e-leaf-{rng.randint(0, 9999)}", None),
                               ("intermediate", f"e2e-int-{rng.randint(0, 9999)}", None),
                               ("root", f"e2e-root-{rng.randint(0, 9999)}", "e2e-fine-root")])
    save()

    cases.save()


if __name__ == "__main__":
    main()
