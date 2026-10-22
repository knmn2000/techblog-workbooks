"""Test cases for assignment 10 (find a weak private key).

Every case starts from a private key k that the generator chooses, so it knows the right
answer. The public key written into the input is computed from k by OpenSSL (through the
`cryptography` library), which is independent of the reference solution. A key is `weak <d>` when
k = d for some d from 1 to the bound, and `weak -<d>` when k = n - d for such a d (its public key
is -(d*G), the point (x, p - y)). For every negated key the generator also checks with OpenSSL that
the public key of n - d is d*G with y replaced by p - y.

    python3 -P tools/gen_p10.py                                  # tests/10 (seed 1)
    python3 -P tools/gen_p10.py --seed 777 --out build/fresh/10  # what `check 10 -Fresh` runs
"""

import random
import sys
from pathlib import Path

import cryptography

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = f"cryptography {cryptography.__version__} (OpenSSL): the public key is computed from the chosen private key, d or n - d"

REQUIREMENTS = [
    ("R1", "One output line per key, in input order: `weak <label> <d>`, `weak <label> -<d>` or `none <label>`"),
    ("R2", "A key whose d is between 1 and the bound is reported with that d (d = 1 means the key is G itself; d = 2 needs doubling)"),
    ("R3", "Only d from 1 to the bound counts, in either sign: the bound is inclusive, so d = bound + 1 and -(bound + 1) give `none`"),
    ("R4", "Both curves work: P-256 and P-384 each use their own prime and generator"),
    ("R5", "A bound of 1000 with several keys finishes in time, including keys that are not weak"),
    ("R6", "A key equal to -(d*G), the point (x, p - y), with d from 1 to the bound gives `weak <label> -<d>`: its private key is n - d"),
    ("E2E", "The weak values reported for the real incident, mixed with strong keys"),
]
# An expected `weak` line can belong to R2 or R6, so a difference there falls back to the
# requirement the case targets.
EXPLAIN = "_lines=R1 none=R3"

INCIDENT_D = [4, 56, 115, 66, 155, 156, 230, 237]  # values reported in the press for the eight P-384 keys


def key_line(label, curve, k):
    """The `key` line for private key k, its public key computed by OpenSSL."""
    x, y = curves.public_point(curve, k)
    c = curves.CURVES[curve]
    return f"key {label} {curve} {x:0{c['hexlen']}x} {y:0{c['hexlen']}x}"


def verdict(label, curve, k, bound):
    """The expected line for private key k: weak d for k = d, weak -d for k = n - d, else none."""
    n = curves.CURVES[curve]["n"]
    small, mirrored = 1 <= k <= bound, 1 <= n - k <= bound
    assert not (small and mirrored), "k and n - k are both within the bound only when the bound is near n/2"
    if small:
        return f"weak {label} {k}"
    if mirrored:
        return f"weak {label} -{n - k}"
    return f"none {label}"


def negated_key(curve, d):
    """n - d, after OpenSSL confirms that its public key is d*G with y replaced by p - y."""
    c = curves.CURVES[curve]
    x, y = curves.public_point(curve, d)
    assert curves.public_point(curve, c["n"] - d) == (x, c["p"] - y), "the key n - d must give -(d*G)"
    return c["n"] - d


def build(items):
    """items: a bound (int) or a key (label, curve, d[, 'neg']); 'neg' means the private key n - d.
    Returns (input lines, expected lines)."""
    lines, expected, bound = [], [], None
    for item in items:
        if isinstance(item, int):
            bound = item
            lines.append(f"bound {bound}")
            continue
        label, curve, d, *rest = item
        n = curves.CURVES[curve]["n"]
        assert 1 <= d < n
        k = negated_key(curve, d) if rest == ["neg"] else d
        lines.append(key_line(label, curve, k))
        expected.append(verdict(label, curve, k, bound))
    return lines, expected


def strong(rng, curve, bound):
    d = rng.randrange(2 ** 64, curves.CURVES[curve]["n"] - 1)  # far above any bound, like a real key
    assert d > bound
    return d


def main():
    args = wbcore.parse_args("10")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, items):
        lines, expected = build(items)
        cases.add(case_id, req, title, lines, expected)

    # R1 - several keys in one input, and the bound changing between them
    add("10-R1-mixed", "R1", "five keys on both curves: weak, strong, weak, strong, weak", [
        255, ("a", "P-384", 4), ("b", "P-256", strong(rng, "P-256", 255)), ("c", "P-256", 200),
        ("d", "P-384", strong(rng, "P-384", 255)), ("e", "P-384", 255)])
    add("10-R1-two-bounds", "R1", "a second `bound` line replaces the first for the keys after it", [
        10, ("low-1", "P-256", 7), ("low-2", "P-256", 12), 20, ("high-1", "P-256", 12), ("high-2", "P-256", 21)])
    add("10-R1-one-key", "R1", "a single strong key", [255, ("only", "P-384", strong(rng, "P-384", 255))])

    # R2 - d = 1 (the key is G), d = 2 (the first doubling), small values, the last value in range
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        add(f"10-R2-d1-{tag}", "R2", f"{curve}: d = 1, so the public key is G itself", [255, ("g", curve, 1)])
        add(f"10-R2-d2-{tag}", "R2", f"{curve}: d = 2, the one step that needs point doubling", [255, ("two", curve, 2)])
        add(f"10-R2-d3-{tag}", "R2", f"{curve}: d = 3, the first step that adds two different points", [255, ("three", curve, 3)])
        add(f"10-R2-last-{tag}", "R2", f"{curve}: d equal to the bound (255)", [255, ("last", curve, 255)])
    add("10-R2-bound-1", "R2", "bound 1: only d = 1 can be found", [1, ("one", "P-256", 1), ("two", "P-256", 2)])
    add("10-R2-small-bound", "R2", "bound 10 with d = 7 and d = 10", [10, ("seven", "P-384", 7), ("ten", "P-384", 10)])

    # R3 - one past the bound, in both signs
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        add(f"10-R3-256-{tag}", "R3", f"{curve}: d = 256 with bound 255 (the first value out of range)",
            [255, ("out", curve, 256), ("in", curve, 255)])
    add("10-R3-bound-11", "R3", "bound 10, d = 11", [10, ("eleven", "P-256", 11)])
    add("10-R3-bound-1", "R3", "bound 1, d = 2 (G + G is out of range)", [1, ("two", "P-384", 2)])
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        add(f"10-R3-neg-256-{tag}", "R3", f"{curve}: -(256*G) with bound 255 (the negation of the first value out of range)",
            [255, ("out", curve, 256, "neg")])
    add("10-R3-neg-bound-10", "R3", "bound 10: 11*G and -(11*G)", [10, ("eleven", "P-256", 11), ("minus-eleven", "P-256", 11, "neg")])

    # R4 - both curves, every key weak, in one input
    for k in range(2):
        ds = sorted(rng.sample(range(1, 256), 6))
        add(f"10-R4-both-curves-s{args.seed}-{k}", "R4", f"six random d in 1..255 (seed {args.seed}), alternating P-256 and P-384",
            [255] + [(f"k{i}", "P-256" if i % 2 == 0 else "P-384", d) for i, d in enumerate(ds)])

    # R5 - a bigger bound and several keys
    add("10-R5-edge-1000", "R5", "bound 1000: d = 1000 on both curves, d = 999 and d = 1001", [
        1000, ("max-256", "P-256", 1000), ("max-384", "P-384", 1000), ("over", "P-384", 1001),
        ("near", "P-256", 999)])
    for k in range(2):
        curve = ("P-256", "P-384")[k]
        items = [1000] + [(f"w{i}", curve, rng.randint(500, 1000)) for i in range(2)] + \
                [(f"s{i}", curve, strong(rng, curve, 1000)) for i in range(2)]
        add(f"10-R5-four-keys-{curve.lower().replace('-', '')}-s{args.seed}", "R5",
            f"four {curve} keys, bound 1000: two weak (d in 500..1000) and two strong (seed {args.seed})", items)
    add(f"10-R5-all-strong-s{args.seed}", "R5",
        f"four strong P-384 keys, bound 1000: nothing is found, so every step runs (seed {args.seed})",
        [1000] + [(f"s{i}", "P-384", strong(rng, "P-384", 1000)) for i in range(4)])

    # R6 - the negated key -(d*G) = (x, p - y), whose private key is n - d
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        add(f"10-R6-neg-{tag}", "R6", f"{curve}: -(d*G) for d = 1, 2, 56 and 255, then 4*G",
            [255, ("n1", curve, 1, "neg"), ("n2", curve, 2, "neg"), ("n56", curve, 56, "neg"),
             ("n255", curve, 255, "neg"), ("p4", curve, 4)])
    add("10-R6-neg-and-plain", "R6", "42*G and -(42*G) side by side", [
        100, ("plain", "P-384", 42), ("flipped", "P-384", 42, "neg")])
    add("10-R6-neg-bound-1", "R6", "bound 1: -G is weak, -(2*G) is not", [
        1, ("minus-g", "P-384", 1, "neg"), ("minus-two", "P-384", 2, "neg")])
    ds = sorted(rng.sample(range(1, 256), 6))
    add(f"10-R6-random-s{args.seed}", "R6", f"six random d in 1..255, each as d*G or -(d*G) at random (seed {args.seed})",
        [255] + [(f"k{i}", "P-256" if i % 2 == 0 else "P-384", d, *(["neg"] if rng.random() < 0.5 else []))
                 for i, d in enumerate(ds)])

    # E2E - the values reported for the real incident
    add("10-E2E-incident-values", "E2E", "P-384, bound 255: the eight reported values, a key with d = 256 and two strong keys", [
        255] + [(f"intermediate-{i + 1}", "P-384", d) for i, d in enumerate(INCIDENT_D)] + [
        ("just-over", "P-384", 256), ("strong-1", "P-384", strong(rng, "P-384", 255)),
        ("strong-2", "P-384", strong(rng, "P-384", 255))])
    for i, d in enumerate(INCIDENT_D):
        add(f"10-E2E-incident-d{d}", "E2E", f"P-384, bound 255: d = {d}", [255, (f"intermediate-{i + 1}", "P-384", d)])
    add("10-E2E-incident-negated", "E2E", "P-384, bound 255: the eight reported values negated (private keys n - d), and -(256*G)",
        [255] + [(f"mirror-{i + 1}", "P-384", d, "neg") for i, d in enumerate(INCIDENT_D)] + [("mirror-over", "P-384", 256, "neg")])
    items = [255]
    for i in range(15):
        curve = rng.choice(list(curves.CURVES))
        if rng.random() < 0.3:
            items.append((f"r{i}", curve, strong(rng, curve, 255)))
        else:
            items.append((f"r{i}", curve, rng.randint(1, 400), *(["neg"] if rng.random() < 0.3 else [])))
    add(f"10-E2E-random-s{args.seed}", "E2E",
        f"fifteen random keys, bound 255: d*G or -(d*G) with d in 1..400 (so some are out of range), or strong (seed {args.seed})", items)

    cases.save()


if __name__ == "__main__":
    main()
