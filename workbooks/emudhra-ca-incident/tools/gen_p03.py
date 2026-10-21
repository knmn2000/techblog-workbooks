"""Test cases for assignment 03 (scalar multiplication by double-and-add).

Expected public keys come from `curves.public_point`, which computes d*G through the
`cryptography` library (OpenSSL) - independent of the reference solution, which must implement
its own point doubling and addition (in the same style as assignment 10's reference) and its own
double-and-add loop, not call the library.

    python3 -P tools/gen_p03.py                                  # tests/03 (seed 1)
    python3 -P tools/gen_p03.py --seed 777 --out build/fresh/03  # what `check 03 -Fresh` runs
"""

import random
import sys
from pathlib import Path

import cryptography

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = f"cryptography {cryptography.__version__} (OpenSSL): d*G computed by deriving a private key with value d"

REQUIREMENTS = [
    ("R1", "Small d (1, 2, 3) matches the curve's own generator table"),
    ("R2", "d with different bit patterns (all ones, a single high bit, alternating bits) exercises every branch of double-and-add"),
    ("R3", "d = n - 1 gives the negation of G"),
    ("R4", "Both curves work: P-256 and P-384 each use their own prime and generator"),
    ("R5", "Large random d finishes well under the time limit (double-and-add, not repeated addition)"),
]
EXPLAIN = "_lines=R1"


def mul_line(curve, d):
    """One `mul` input/expected pair. The oracle is curves.public_point (OpenSSL)."""
    n = curves.CURVES[curve]["n"]
    assert 1 <= d < n
    x, y = curves.public_point(curve, d)
    assert curves.on_curve(curve, x, y)
    hexlen = curves.CURVES[curve]["hexlen"]
    return f"mul {curve} {d}", f"{x:0{hexlen}x} {y:0{hexlen}x}"


def build(items):
    inputs = [l for l, _ in items]
    expected = [e for _, e in items]
    return inputs, expected


def main():
    args = wbcore.parse_args("03")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, items):
        inputs, expected = build(items)
        cases.add(case_id, req, title, inputs, expected)

    # R1 - small d, matching the curve's own small-multiple table
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        add(f"03-R1-small-{tag}", "R1", f"{curve}: d = 1, 2, 3 (G itself, the first doubling, the first addition)",
            [mul_line(curve, 1), mul_line(curve, 2), mul_line(curve, 3)])

    # R2 - bit patterns that exercise every branch of double-and-add
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        bits = curves.CURVES[curve]["bits"]
        n = curves.CURVES[curve]["n"]
        all_ones = min((1 << (bits - 8)) - 1, n - 1)  # a run of 1 bits, short of the curve's own bit length
        high_bit = 1 << (bits - 16)  # a single high bit, otherwise all zero
        alternating = int("10" * ((bits - 16) // 2), 2) + 1  # 0101...01, kept odd and in range
        add(f"03-R2-bitpatterns-{tag}", "R2", f"{curve}: d all 1 bits, d a single high bit, d alternating bits", [
            mul_line(curve, all_ones), mul_line(curve, high_bit), mul_line(curve, alternating)])

    # R3 - d = n - 1: the negation of G
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        n = curves.CURVES[curve]["n"]
        add(f"03-R3-negation-{tag}", "R3", f"{curve}: d = n - 1 (should be G with its y negated)", [mul_line(curve, n - 1)])

    # R4 - both curves, several ordinary d values in one input
    add(f"03-R4-both-curves-s{args.seed}", "R4", f"four ordinary d values, two per curve (seed {args.seed})", [
        mul_line("P-256", rng.randrange(1000, 2 ** 64)), mul_line("P-384", rng.randrange(1000, 2 ** 96)),
        mul_line("P-256", rng.randrange(2 ** 64, 2 ** 128)), mul_line("P-384", rng.randrange(2 ** 96, 2 ** 192))])

    # R5 - large random d, timed: an O(d) loop (assignment 10's approach) could never finish on a
    # d this size, while double-and-add (O(log d)) needs only a few hundred doublings
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        n = curves.CURVES[curve]["n"]
        items = [mul_line(curve, rng.randrange(2 ** (curves.CURVES[curve]["bits"] - 2), n - 1)) for _ in range(3)]
        add(f"03-R5-large-{tag}-s{args.seed}", "R5",
            f"{curve}: three large random d, each nearly the full bit length (seed {args.seed})", items)

    cases.save()


if __name__ == "__main__":
    main()
