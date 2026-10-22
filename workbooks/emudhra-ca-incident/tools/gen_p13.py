"""Test cases for assignment 13 (lint a public key).

Expected reasons come straight from how each test key is built, not from any search the
reference solution performs:
  - off-curve points are perturbed from a real point and confirmed off-curve by
    tools/curves.py's `on_curve` (OpenSSL), independent of anything the reference computes;
  - weak keys are built from a small, explicit d using `curves.public_point` (OpenSSL), so the
    generator knows for a fact that d <= WEAK_BOUND is the true private key. A negated weak key
    is the public key of n - d, also from OpenSSL, and the generator checks that it equals d*G with
    y replaced by p - y;
  - known-compromised keys are exact copies of coordinates the test itself puts on the
    blocklist, so the match is definitional: string/tuple equality, not a computation.
A key's final expected reason, when more than one could apply, follows the priority this
assignment documents: off-curve, then known-compromised, then weak.

    python3 -P tools/gen_p13.py                                  # tests/13 (seed 1)
    python3 -P tools/gen_p13.py --seed 777 --out build/fresh/13  # what `check 13 -Fresh` runs
"""

import random
import sys
from pathlib import Path

import cryptography

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = (f"cryptography {cryptography.__version__} (OpenSSL) for curve membership and the public keys of d and n - d; "
       "exact coordinate match for the blocklist")

WEAK_BOUND = 4096  # see the problem page for why a toy linter uses a bound this small

REQUIREMENTS = [
    ("R1", "A strong, valid key that is not blocklisted passes every check: `ok`"),
    ("R2", "An off-curve point fails with `off-curve`, checked before anything else"),
    ("R3", "A key equal to d*G or -(d*G) with 1 <= d <= 4096 fails with `weak`; 4097*G and -(4097*G) do not"),
    ("R4", "A key that is not weak but matches a `blocklist` entry declared earlier fails with `known-compromised`; an entry for another point, the key's negation included, does not affect it"),
    ("R5", "Priority: off-curve is reported before known-compromised, and known-compromised before weak"),
    ("E2E", "Several keys and a growing blocklist in one input, each key getting its own verdict"),
]
EXPLAIN = "_lines=R1"


def fmt(curve, value):
    return f"{value:0{curves.CURVES[curve]['hexlen']}x}"


def strong_point(rng, curve):
    """A real key point far above the weak-key bound: d is a plausible real private key."""
    n = curves.CURVES[curve]["n"]
    d = rng.randrange(WEAK_BOUND + 2 ** 32, n - 2 ** 32)
    return curves.public_point(curve, d), d


def weak_point(curve, d):
    assert 1 <= d <= WEAK_BOUND
    return curves.public_point(curve, d)


def negated_point(curve, d):
    """-(d*G), as OpenSSL's public key for the private key n - d."""
    c = curves.CURVES[curve]
    x, y = curves.public_point(curve, d)
    nx, ny = curves.public_point(curve, c["n"] - d)
    assert (nx, ny) == (x, c["p"] - y), "the key n - d must give -(d*G)"
    return nx, ny


def off_curve_point(curve, x, y):
    y2 = y + 1
    assert curves.on_curve(curve, x, y)
    assert not curves.on_curve(curve, x, y2), "perturbing y by 1 must leave the point off the curve"
    return x, y2


def key_line(label, curve, x, y):
    return f"key {label} {curve} {fmt(curve, x)} {fmt(curve, y)}"


def blocklist_line(curve, x, y):
    return f"blocklist {curve} {fmt(curve, x)} {fmt(curve, y)}"


def tag(curve):
    return curve.lower().replace("-", "")


def main():
    args = wbcore.parse_args("13")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    # R1 - a strong, unremarkable key: ok.
    for curve in curves.CURVES:
        (x, y), d = strong_point(rng, curve)
        cases.add(f"13-R1-ok-{tag(curve)}", "R1", f"{curve}: a strong key (d far above the bound), not blocklisted",
                   [key_line("a", curve, x, y)], [f"ok a"])

    # R2 - off-curve: perturb a real point's y by one.
    for curve in curves.CURVES:
        (x, y), d = strong_point(rng, curve)
        xo, yo = off_curve_point(curve, x, y)
        cases.add(f"13-R2-offcurve-{tag(curve)}", "R2", f"{curve}: a valid point with y perturbed by 1, off the curve",
                   [key_line("a", curve, xo, yo)], ["fail a off-curve"])

    # R3 - weak: small d, well inside the bound.
    for curve in curves.CURVES:
        for d in (1, 4, 56, WEAK_BOUND):
            x, y = weak_point(curve, d)
            cases.add(f"13-R3-weak-d{d}-{tag(curve)}", "R3", f"{curve}: d = {d} (at or inside the bound {WEAK_BOUND})",
                       [key_line("a", curve, x, y)], ["fail a weak"])
    # d one past the bound must NOT be weak: it's ok (not blocklisted, on curve).
    for curve in curves.CURVES:
        x, y = curves.public_point(curve, WEAK_BOUND + 1)
        cases.add(f"13-R3-just-over-bound-{tag(curve)}", "R3",
                   f"{curve}: d = {WEAK_BOUND + 1}, one past the weak-key bound: ok",
                   [key_line("a", curve, x, y)], ["ok a"])
    # The negated key -(d*G) belongs to n - d, which the same search finds: weak up to the bound.
    for curve in curves.CURVES:
        for d in (1, 56, WEAK_BOUND):
            x, y = negated_point(curve, d)
            cases.add(f"13-R3-weak-neg-d{d}-{tag(curve)}", "R3",
                       f"{curve}: -(d*G) for d = {d}, the private key n - {d} (at or inside the bound {WEAK_BOUND})",
                       [key_line("a", curve, x, y)], ["fail a weak"])
    for curve in curves.CURVES:
        x, y = negated_point(curve, WEAK_BOUND + 1)
        cases.add(f"13-R3-neg-just-over-bound-{tag(curve)}", "R3",
                   f"{curve}: -(d*G) for d = {WEAK_BOUND + 1}, one past the weak-key bound: ok",
                   [key_line("a", curve, x, y)], ["ok a"])

    # R4 - known-compromised: a strong key whose exact coordinates are on an earlier blocklist line.
    for curve in curves.CURVES:
        (x, y), d = strong_point(rng, curve)
        cases.add(f"13-R4-known-compromised-{tag(curve)}", "R4",
                   f"{curve}: a strong key (not weak) whose coordinates are blocklisted",
                   [blocklist_line(curve, x, y), key_line("a", curve, x, y)], ["fail a known-compromised"])
    # a blocklist entry that does NOT apply to a different, strong key: must not be falsely flagged.
    for curve in curves.CURVES:
        (bx, by), _ = strong_point(rng, curve)
        (x, y), _ = strong_point(rng, curve)
        cases.add(f"13-R4-blocklist-does-not-apply-{tag(curve)}", "R4",
                   f"{curve}: a blocklist entry for a different key must not flag this one",
                   [blocklist_line(curve, bx, by), key_line("a", curve, x, y)], ["ok a"])

    # a blocklist entry for Q does not block -Q, which is a different key (both strong here).
    for curve in curves.CURVES:
        (x, y), _ = strong_point(rng, curve)
        p = curves.CURVES[curve]["p"]
        assert curves.on_curve(curve, x, p - y)
        cases.add(f"13-R4-negation-not-blocklisted-{tag(curve)}", "R4",
                   f"{curve}: the blocklist holds a strong key Q, and the key is -Q (same x, y replaced by p - y)",
                   [blocklist_line(curve, x, y), key_line("a", curve, x, p - y)], ["ok a"])

    # R5 - priority: off-curve wins over known-compromised (same invalid coordinates, blocklisted anyway).
    for curve in curves.CURVES:
        (x, y), d = strong_point(rng, curve)
        xo, yo = off_curve_point(curve, x, y)
        cases.add(f"13-R5-offcurve-beats-blocklist-{tag(curve)}", "R5",
                   f"{curve}: an off-curve point whose exact (invalid) coordinates are also blocklisted",
                   [blocklist_line(curve, xo, yo), key_line("a", curve, xo, yo)], ["fail a off-curve"])
    # known-compromised wins over weak (small d, and also blocklisted).
    for curve in curves.CURVES:
        x, y = weak_point(curve, 4)
        cases.add(f"13-R5-blocklist-beats-weak-{tag(curve)}", "R5",
                   f"{curve}: d = 4 (weak) whose coordinates are also blocklisted: known-compromised wins",
                   [blocklist_line(curve, x, y), key_line("a", curve, x, y)], ["fail a known-compromised"])

    # known-compromised wins over weak for a negated weak key too.
    for curve in curves.CURVES:
        x, y = negated_point(curve, 4)
        cases.add(f"13-R5-blocklist-beats-weak-neg-{tag(curve)}", "R5",
                   f"{curve}: -(4*G) (weak, private key n - 4) whose coordinates are also blocklisted: known-compromised wins",
                   [blocklist_line(curve, x, y), key_line("a", curve, x, y)], ["fail a known-compromised"])

    # E2E - several keys, a growing blocklist, every reason mixed, each key judged on its own.
    for curve in ("P-256", "P-384"):
        lines, expected = [], []
        (bx1, by1), _ = strong_point(rng, curve)
        lines.append(blocklist_line(curve, bx1, by1))
        # a strong, clean key: ok
        (x, y), _ = strong_point(rng, curve)
        lines.append(key_line("clean", curve, x, y))
        expected.append("ok clean")
        # off-curve key
        (x, y), _ = strong_point(rng, curve)
        xo, yo = off_curve_point(curve, x, y)
        lines.append(key_line("bent", curve, xo, yo))
        expected.append("fail bent off-curve")
        # weak key
        x, y = weak_point(curve, 56)
        lines.append(key_line("tiny", curve, x, y))
        expected.append("fail tiny weak")
        # negated weak key: private key n - 115
        x, y = negated_point(curve, 115)
        lines.append(key_line("mirror", curve, x, y))
        expected.append("fail mirror weak")
        # a second blocklist entry added mid-stream; a key matching it, declared after
        (bx2, by2), _ = strong_point(rng, curve)
        lines.append(blocklist_line(curve, bx2, by2))
        lines.append(key_line("flagged", curve, bx2, by2))
        expected.append("fail flagged known-compromised")
        # the FIRST blocklist entry still applies to a key declared later
        lines.append(key_line("alsoflagged", curve, bx1, by1))
        expected.append("fail alsoflagged known-compromised")
        # one more clean key at the end
        (x, y), _ = strong_point(rng, curve)
        lines.append(key_line("last", curve, x, y))
        expected.append("ok last")
        cases.add(f"13-E2E-mixed-{tag(curve)}-s{args.seed}", "E2E",
                   f"{curve}: seven keys (clean, off-curve, weak, negated weak, blocklisted now, blocklisted earlier, clean), seed {args.seed}",
                   lines, expected)

    cases.save()


if __name__ == "__main__":
    main()
