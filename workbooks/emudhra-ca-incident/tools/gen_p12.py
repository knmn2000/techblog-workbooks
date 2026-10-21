"""Test cases for checkpoint 12 (generate a key correctly).

Every case supplies the exact sequence of candidate byte-blocks a key generator would have
drawn from its random source, so the test is reproducible without calling a real RNG. The
expected value is the direct FIPS 186-5 / SEC1 rule applied by hand: the candidate is read as a
big-endian unsigned integer and accepted only if 1 <= candidate <= n - 1 (n = the curve's real
order, from tools/curves.py); every earlier block in a `draw` line is checked here to make sure
it truly deserves rejection, so a mistake in the test data stops the generator, not the learner.

    python3 -P tools/gen_p12.py                                  # tests/12 (seed 1)
    python3 -P tools/gen_p12.py --seed 777 --out build/fresh/12  # what `check 12 -Fresh` runs
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = "FIPS 186-5 / SEC1 rejection sampling: accept iff 1 <= candidate <= n - 1 (n from tools/curves.py)"

REQUIREMENTS = [
    ("R1", "A single accepted draw with no rejections is reported with that d"),
    ("R2", "A draw of exactly 0 is rejected, and the generator moves on to the next draw"),
    ("R3", "A draw of exactly n (or any value at or above it) is rejected; a draw of n - 1 is accepted (the largest valid key)"),
    ("R4", "Several draws in a row are rejected before the one that is finally accepted"),
    ("R5", "Both curves work, each using its own order n and its own byte length"),
    ("E2E", "A ceremony's worth of draws in one input, mixing both curves and every kind of rejection"),
]
EXPLAIN = "_lines=R1"


def block(curve, value):
    """A candidate byte-block, as hex text, for `curve` (zero-padded to its fixed length)."""
    c = curves.CURVES[curve]
    bits = c["bits"]
    assert 0 <= value < (1 << bits), f"{value:#x} does not fit in {bits} bits"
    return f"{value:0{c['hexlen']}x}"


def must_reject(curve, value):
    """Checks (independently of any generator code) that `value` is not a valid private key."""
    n = curves.CURVES[curve]["n"]
    assert not (1 <= value <= n - 1), f"{value:#x} is actually a valid key on {curve}; it would be accepted"
    return block(curve, value)


def must_accept(curve, value):
    n = curves.CURVES[curve]["n"]
    assert 1 <= value <= n - 1, f"{value:#x} is out of range for {curve} (n = {n:#x})"
    return block(curve, value)


def build(curve, rejects, accept):
    """rejects: values that must each be rejected, in order. accept: the value finally accepted.
    Returns (draw-line-blocks, expected-d)."""
    blocks = [must_reject(curve, r) for r in rejects] + [must_accept(curve, accept)]
    return blocks, accept


def add_case(cases, case_id, req, title, label, curve, rejects, accept):
    blocks, d = build(curve, rejects, accept)
    hexlen = curves.CURVES[curve]["hexlen"]
    line = f"draw {label} {curve} " + " ".join(blocks)
    expected = f"key {label} {d:0{hexlen}x}"
    cases.add(case_id, req, title, [line], expected)


def strong(rng, curve):
    """A plausible real private key: nowhere near the small or boundary values this checkpoint
    is built around, so these cases don't accidentally double as weak-key cases."""
    n = curves.CURVES[curve]["n"]
    return rng.randrange(2 ** 64, n - 2 ** 64)


def random_reject_above_n(rng, curve):
    """A value that is >= n but still fits in the fixed byte length: n plus a bit more."""
    n = curves.CURVES[curve]["n"]
    bits = curves.CURVES[curve]["bits"]
    top = (1 << bits) - 1
    return rng.randint(n, top)


def tag(curve):
    return curve.lower().replace("-", "")


def main():
    args = wbcore.parse_args("12")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    # R1 - one draw, no rejections at all.
    for curve in curves.CURVES:
        add_case(cases, f"12-R1-single-{tag(curve)}", "R1",
                  f"{curve}: a single draw, already in range, accepted with no rejections",
                  "k", curve, [], strong(rng, curve))

    # R2 - the all-zero candidate must be rejected (the one value no real key can ever be).
    for curve in curves.CURVES:
        add_case(cases, f"12-R2-zero-{tag(curve)}", "R2",
                  f"{curve}: the first draw is all-zero and must be rejected",
                  "k", curve, [0], strong(rng, curve))

    # R3 - both boundaries: n itself must be rejected, n - 1 must be accepted.
    for curve in curves.CURVES:
        n = curves.CURVES[curve]["n"]
        add_case(cases, f"12-R3-n-exact-{tag(curve)}", "R3",
                  f"{curve}: a draw of exactly n (the order) must be rejected",
                  "k", curve, [n], strong(rng, curve))
        add_case(cases, f"12-R3-n-minus-1-{tag(curve)}", "R3",
                  f"{curve}: a draw of n - 1 is the largest valid key and must be accepted",
                  "k", curve, [], n - 1)
        add_case(cases, f"12-R3-huge-{tag(curve)}", "R3",
                  f"{curve}: a draw of all-FF bits (far above n) must be rejected",
                  "k", curve, [(1 << curves.CURVES[curve]["bits"]) - 1], strong(rng, curve))

    # R4 - several rejections in a row before the accepted draw.
    for curve in curves.CURVES:
        n = curves.CURVES[curve]["n"]
        rejects = [0, n, random_reject_above_n(rng, curve), (1 << curves.CURVES[curve]["bits"]) - 1]
        add_case(cases, f"12-R4-many-rejects-{tag(curve)}", "R4",
                  f"{curve}: four rejected draws (0, n, a value above n, all-FF) before acceptance",
                  "k", curve, rejects, strong(rng, curve))

    # R5 - both curves side by side in one input, each using its own n and byte length.
    lines, expected = [], []
    for curve in curves.CURVES:
        n = curves.CURVES[curve]["n"]
        hexlen = curves.CURVES[curve]["hexlen"]
        label = f"k-{tag(curve)}"
        blocks, d = build(curve, [0, n], strong(rng, curve))
        lines.append(f"draw {label} {curve} " + " ".join(blocks))
        expected.append(f"key {label} {d:0{hexlen}x}")
    cases.add("12-R5-both-curves", "R5", "one input with a draw for each curve, each with its own n and byte length",
               lines, expected)

    # E2E - a ceremony's worth of draws: several keys, mixed curves, mixed rejection patterns.
    lines, expected = [], []
    patterns = [
        lambda curve: ([], strong(rng, curve)),
        lambda curve: ([0], strong(rng, curve)),
        lambda curve: ([curves.CURVES[curve]["n"]], strong(rng, curve)),
        lambda curve: ([0, curves.CURVES[curve]["n"], (1 << curves.CURVES[curve]["bits"]) - 1], strong(rng, curve)),
        lambda curve: ([], curves.CURVES[curve]["n"] - 1),
    ]
    curve_list = list(curves.CURVES)
    for i in range(8):
        curve = curve_list[i % len(curve_list)]
        rejects, accept = rng.choice(patterns)(curve)
        label = f"k{i}"
        blocks, d = build(curve, rejects, accept)
        hexlen = curves.CURVES[curve]["hexlen"]
        lines.append(f"draw {label} {curve} " + " ".join(blocks))
        expected.append(f"key {label} {d:0{hexlen}x}")
    cases.add(f"12-E2E-ceremony-s{args.seed}", "E2E",
               f"eight draws across both curves, every rejection pattern mixed together (seed {args.seed})",
               lines, expected)

    cases.save()


if __name__ == "__main__":
    main()
