"""Test cases for checkpoint 02 (point addition on a toy curve).

The curve is y^2 = x^3 + 2x + 2 mod 17, with generator G = (5, 1) - the same tiny example used
in checkpoint 10's page. The group it generates has 19 elements (18 affine points plus the point
at infinity); none of them has y = 0, so doubling never produces infinity on this curve.

Independence of the oracle (see `oracle_add` below): the reference solution computes a sum
directly with the textbook slope formulas (one for two distinct points, one for doubling a point
with itself). The oracle below never evaluates either formula. For two distinct points, it
brute-forces the unique slope `m` (trying every value mod 17) for which the straight line through
them is also a line through a candidate `base` point, i.e. a candidate solution; that is a search,
not a direct computation. For doubling, it brute-forces a slope `m` and *proves* the candidate
tangency algebraically: it substitutes the line into the curve equation to get the cubic's actual
coefficients, synthetically divides that cubic by (x - x1), and checks that x1 is *also* a root of
the quotient - i.e. that x1 is a double root, which is the textbook definition of "the line is
tangent there", established by polynomial division rather than by the calculus shortcut
(3x1^2 + a) / (2y1) the reference uses. Both branches then read the third root off Vieta's formula
(sum of the cubic's three roots = m^2), which is arithmetic bookkeeping, not curve-specific
algebra. This was checked, during authoring, against the slope-formula result for all 19 x 19
ordered pairs of points (including infinity): zero disagreements.

    python3 -P tools/gen_p02.py                                  # tests/02 (seed 1)
    python3 -P tools/gen_p02.py --seed 777 --out build/fresh/02  # what `check 02 -Fresh` runs
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import wbcore  # noqa: E402

P = 17
A = 2
B = 2
LIB = "brute-force search over the curve's 19 points, validated by polynomial root-multiplicity (see tools/gen_p02.py)"

REQUIREMENTS = [
    ("R1", "Adding two distinct points with different x, using the chord through them"),
    ("R2", "Doubling a point (P + P), using the tangent at that point"),
    ("R3", "Identity laws: P + inf = P, inf + P = P, inf + inf = inf"),
    ("R4", "Inverse pairs: P + (-P) = inf, where -P is (x, 17 - y)"),
    ("R5", "Every output other than inf is a point actually on the curve"),
    ("E2E", "A full table covering every one of the curve's points at least once"),
]
EXPLAIN = "_lines=R1"

# Every affine point on the curve, found directly from its equation (not from any addition rule).
POINTS = [(x, y) for x in range(P) for y in range(P) if (y * y - (x ** 3 + A * x + B)) % P == 0]
assert len(POINTS) == 18, f"expected 18 affine points on this curve, found {len(POINTS)}"
assert not any(y == 0 for _, y in POINTS), "this curve has no point with y = 0 (no vertical tangent)"

G = (5, 1)


def on_curve(pt):
    if pt is None:
        return True
    x, y = pt
    return (y * y - (x ** 3 + A * x + B)) % P == 0


def negate(pt):
    return None if pt is None else (pt[0], (P - pt[1]) % P)


def oracle_add(p1, p2):
    """Point addition, by brute-force search (see the module docstring for why this is
    independent of the reference's slope formula)."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None  # inverse pair
    if p1 != p2:
        # The unique m for which the line y = y1 + m(x - x1) also passes through p2.
        found = [m for m in range(P) if (y1 + m * (x2 - x1)) % P == y2 % P]
        assert len(found) == 1, (p1, p2, found)
        m = found[0]
    else:
        # The unique m whose tangent line at p1 touches the curve there with multiplicity 2,
        # proved by synthetic division instead of the derivative formula.
        candidates = []
        for m in range(P):
            c3 = (-1) % P
            c2 = (m * m) % P
            c1 = (2 * m * y1 - 2 * m * m * x1 - A) % P
            c0 = (y1 * y1 - 2 * m * y1 * x1 + m * m * x1 * x1 - B) % P
            q2 = c3
            q1 = (c2 + x1 * q2) % P
            q0 = (c1 + x1 * q1) % P
            remainder = (c0 + x1 * q0) % P
            if remainder != 0:
                continue  # x1 isn't even a root of this line's intersection with the curve
            if (q2 * x1 * x1 + q1 * x1 + q0) % P != 0:
                continue  # x1 is a root, but only a single one: this m isn't the tangent
            candidates.append(m)
        assert len(candidates) == 1, (p1, candidates)
        m = candidates[0]
    x3 = (m * m - x1 - x2) % P
    y3 = (m * (x1 - x3) - y1) % P
    result = (x3, y3)
    assert on_curve(result), f"oracle produced an off-curve point: {p1} + {p2} = {result}"
    return result


def fmt(pt):
    return "inf" if pt is None else f"{pt[0]} {pt[1]}"


def parse(text):
    words = text.split()
    return None if words[0] == "inf" else (int(words[0]), int(words[1]))


def line(p1, p2):
    """One `add` input/expected pair, using the brute-force oracle above."""
    result = oracle_add(p1, p2)
    return f"add {fmt(p1)} {fmt(p2)}", fmt(result)


def build(pairs):
    inputs = [l for l, _ in (line(p1, p2) for p1, p2 in pairs)]
    expected = [e for _, e in (line(p1, p2) for p1, p2 in pairs)]
    return inputs, expected


def main():
    args = wbcore.parse_args("02")
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, pairs):
        inputs, expected = build(pairs)
        cases.add(case_id, req, title, inputs, expected)

    # R1 - general addition, two distinct points with different x
    add("02-R1-small", "R1", "1*G + 2*G (the first ordinary addition in the worked table)", [(G, (6, 3))])
    add("02-R1-other-pair", "R1", "two points chosen so neither is a multiple of the other by 1 or 2", [
        ((9, 16), (16, 13))])
    add("02-R1-near-boundary", "R1", "points with x = 0 and x = 16, the ends of the field", [((0, 6), (16, 4))])
    add("02-R1-chord-through-a-point", "R1", "a chord whose third intersection has the same x as one of "
        "the two points added (a tangency coincidence, not a doubling)", [((0, 6), (9, 16))])

    # R2 - doubling
    add("02-R2-g", "R2", "G + G (the doubling the worked table needs for 2*G)", [(G, G)])
    add("02-R2-other", "R2", "doubling a point other than G", [((10, 6), (10, 6))])

    # R3 - identity laws
    add("02-R3-point-plus-inf", "R3", "a point plus infinity, on both sides", [(G, None), (None, G)])
    add("02-R3-inf-plus-inf", "R3", "infinity plus infinity", [(None, None)])
    add("02-R3-several-plus-inf", "R3", "several different points, each plus infinity", [
        ((6, 3), None), ((3, 1), None), ((9, 16), None)])

    # R4 - inverse pairs
    add("02-R4-g-and-negation", "R4", "G plus its own negation", [(G, negate(G))])
    add("02-R4-several", "R4", "three more points, each plus its own negation", [
        ((6, 3), negate((6, 3))), ((10, 6), negate((10, 6))), ((13, 7), negate((13, 7)))])
    add("02-R4-negation-order", "R4", "the negation given first, the point second (same identity, swapped order)", [
        (negate((7, 6)), (7, 6))])

    # R5 - every output other than inf lies on the curve (the oracle already asserts this for
    # every case; these two specifically exercise points near the field's edges, x = 0 and x = 16)
    add("02-R5-edge-x0", "R5", "an addition whose result has x = 0", [((13, 10), (16, 4))])
    add("02-R5-edge-x16", "R5", "an addition whose result has x = 16", [((3, 1), (9, 1))])

    # E2E - the full cycle 1*G, 2*G, ..., 19*G (= inf), covering all 18 affine points and infinity
    table = [G]
    for _ in range(18):
        table.append(oracle_add(table[-1], G))
    pairs = [(table[i], G) for i in range(18)]  # i*G + G = (i+1)*G, for i = 1..18
    add(f"02-E2E-full-table-s{args.seed}", "E2E",
        "the whole cycle 1*G .. 19*G (= inf), each step adding G to the previous multiple", pairs)

    cases.save()


if __name__ == "__main__":
    main()
