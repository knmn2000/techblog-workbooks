"""Test cases for assignment 17 (find a weak key in square-root time: baby-step giant-step).

Every key starts from a signed private value e that the generator chooses, so it knows the right
answer: `weak <label> <e>` when 1 <= |e| <= bound, else `none <label>`. OpenSSL (through the
`cryptography` library) computes the public key d*G for d = |e|. For a negative e the generator
writes (x, p - y) and checks that OpenSSL gives the same point for the private key n - d.

`plan` lines are integer arithmetic from the page's definitions, computed here a second way: the
square root by brute force (small bounds) or exactly (an even power of two) or with
`math.isqrt` checked against its definition, and the giant points as the smallest count whose
centres reach the bound. The answers never depend on the search the reference runs.

    python3 -P tools/gen_p17.py                                  # tests/17 (seed 1)
    python3 -P tools/gen_p17.py --seed 777 --out build/fresh/17  # what `check 17 -Fresh` runs
"""

import math
import random
import sys
from pathlib import Path

import cryptography

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = (f"cryptography {cryptography.__version__} (OpenSSL): each public key is computed from the chosen "
       "private value; plan lines from the page's formulas in exact integers")

REQUIREMENTS = [
    ("R1", "One output line per `key` and `plan` line, in input order, each key searched on its own curve; a later `bound` or `table` line replaces the earlier one"),
    ("R2", "A key d*G with d from 1 to the bound gives `weak <label> <d>`, including d at the edges of the table and of the giant steps"),
    ("R3", "A key -(d*G), which is (x, p - y), with d from 1 to the bound gives `weak <label> -<d>`"),
    ("R4", "A key whose private value is outside -bound .. bound gives `none`, including values the last giant step reaches past the bound"),
    ("R5", "Bounds up to 2^28 on P-256 and 2^26 on P-384 finish in time, where a scan of every value would take minutes or hours"),
    ("R6", "`plan` gives the table size m and the number of giant points, computed in exact integers, with the `table` limit applied"),
    ("E2E", "The incident's values, one key at two bounds, near misses and a random mix of keys and plans"),
]
EXPLAIN = "_lines=R1 plan=R6 none~weak=R4"

INCIDENT_D = [4, 56, 115, 66, 155, 156, 230, 237]  # the eight P-384 values reported for the incident
P384_MAX_BOUND = 2 ** 26  # largest bound an input with a P-384 key uses (see the page's Constraints)
P256_MAX_BOUND = 2 ** 28
LINEAR_SECONDS = {"P-256": 49e-6, "P-384": 83e-6}  # one point addition with the reference's arithmetic
TIME_LIMIT = 10


def tag(curve):
    return curve.lower().replace("-", "")


def ceil_sqrt(N):
    """The smallest r with r*r >= N, found without the formula the page suggests where possible."""
    if N <= 2 ** 20:
        r = 1
        while r * r < N:
            r += 1
        return r
    if N & (N - 1) == 0 and (N.bit_length() - 1) % 2 == 0:
        return 1 << ((N.bit_length() - 1) // 2)  # an even power of two has an exact root
    r = math.isqrt(N - 1) + 1
    assert (r - 1) * (r - 1) < N <= r * r
    return r


def plan_numbers(N, limit):
    """(m, giant points) by the page's definitions: m = min(ceil(sqrt(N)), limit), and g giant
    points on each side of Q (Q counted once), the fewest whose last centre 2m*(g - 1) is within m
    of N."""
    m = ceil_sqrt(N) if limit is None else min(ceil_sqrt(N), limit)
    g = 1 if N <= m else -(-(N - m) // (2 * m)) + 1
    assert 2 * m * (g - 1) + m >= N and (g == 1 or 2 * m * (g - 2) + m < N)
    return m, 2 * g - 1


def float_plan(N, limit):
    """What a program that uses floating point gets, for checking that a case catches it."""
    m = math.ceil(math.sqrt(N))
    if limit is not None:
        m = min(m, limit)
    return m, 2 * math.ceil((N + m) / (2 * m)) - 1


def key_point(curve, e):
    """(x, y) of e*G by OpenSSL; a negative e is the negation (x, p - y) of |e|*G."""
    c = curves.CURVES[curve]
    d = abs(e)
    assert 1 <= d < c["n"]
    x, y = curves.public_point(curve, d)
    if e < 0:
        y = c["p"] - y
        assert (x, y) == curves.public_point(curve, c["n"] - d), "-(d*G) must be (n - d)*G"
    return x, y


def build(items):
    """items, in input order: ("bound", N), ("table", M or None), ("key", label, curve, e) and
    ("plan", label, bits). Returns (input lines, expected lines)."""
    lines, expected = [], []
    bound, limit, curves_seen = None, None, set()
    for item in items:
        kind = item[0]
        if kind == "bound":
            bound = item[1]
            assert 1 <= bound <= P256_MAX_BOUND
            lines.append(f"bound {bound}")
        elif kind == "table":
            limit = item[1]
            assert limit is None or limit >= 1
            lines.append(f"table {'none' if limit is None else limit}")
        elif kind == "key":
            _, label, curve, e = item
            assert bound is not None, "every key needs a bound line before it"
            curves_seen.add(curve)
            x, y = key_point(curve, e)
            hexlen = curves.CURVES[curve]["hexlen"]
            lines.append(f"key {label} {curve} {x:0{hexlen}x} {y:0{hexlen}x}")
            expected.append(f"weak {label} {e}" if 1 <= abs(e) <= bound else f"none {label}")
        elif kind == "plan":
            _, label, bits = item
            assert 1 <= bits <= 400
            m, giant = plan_numbers(2 ** bits, limit)
            lines.append(f"plan {label} {bits}")
            expected.append(f"plan {label} baby {m} giant {giant}")
    if "P-384" in curves_seen:
        assert all(int(l.split()[1]) <= P384_MAX_BOUND for l in lines if l.startswith("bound ")), \
            "an input with a P-384 key keeps every bound at 2^26 or below"
    return lines, expected


def strong(rng, curve, sign=1):
    """A private value far above any bound, like a real key."""
    return sign * rng.randrange(2 ** 64, curves.CURVES[curve]["n"] - 2 ** 64)


def keys(curve, values, prefix="k"):
    return [("key", f"{prefix}{'m' if e < 0 else ''}{abs(e) if abs(e) < 10 ** 9 else i}", curve, e)
            for i, e in enumerate(values)]


def main():
    args = wbcore.parse_args("17")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, items):
        lines, expected = build(items)
        cases.add(case_id, req, title, lines, expected)
        return lines, expected

    # With bound 1000: m = 32, so the giant points sit at centres 0, 64, 128, ... and -64, -128, ...
    assert plan_numbers(1000, None) == (32, 33)

    # R1 - order, formats, and later bound and table lines replacing earlier ones. The keys sit
    # in the table's own range (d < m), so a failure here points at the input handling. R3 covers
    # the output of a negated key.
    add("17-R1-mixed", "R1", "bound 1000: weak, strong and plan lines interleaved on both curves", [
        ("bound", 1000), ("key", "a", "P-256", 9), ("plan", "p1", 20), ("key", "b", "P-384", 20),
        ("key", "c", "P-256", strong(rng, "P-256")), ("key", "d", "P-384", 23), ("plan", "p2", 10)])
    add("17-R1-later-lines-replace", "R1", "a second bound line changes the verdicts; a table line changes the next plan", [
        ("bound", 2), ("key", "low-3", "P-256", 3), ("key", "low-2", "P-256", 2),
        ("bound", 20), ("key", "high-3", "P-256", 3), ("key", "high-21", "P-256", 21),
        ("plan", "free", 16), ("table", 3), ("plan", "three", 16), ("table", None), ("plan", "free-again", 16)])
    add("17-R1-curves-share-a-bound", "R1", "one bound, P-256 and P-384 keys in turn: each curve needs its own table", [
        ("bound", 5000), ("key", "a", "P-256", 50), ("key", "b", "P-384", 50), ("key", "c", "P-256", 61),
        ("key", "d", "P-384", 61), ("key", "e", "P-384", 17)])

    # R2 - positive keys at every edge of the walk
    for curve in curves.CURVES:
        t = tag(curve)
        add(f"17-R2-first-keys-{t}", "R2", f"{curve}, bound 1000: d = 1, 2 and 3",
            [("bound", 1000)] + keys(curve, [1, 2, 3]))
        add(f"17-R2-table-edge-{t}", "R2", f"{curve}, bound 1000 (m = 32): d = 31, 32 and 33 around the last baby step",
            [("bound", 1000)] + keys(curve, [31, 32, 33]))
        add(f"17-R2-giant-centres-{t}", "R2", f"{curve}, bound 1000 (m = 32): d = 64, 128 and 640, where Q - c*G is the point at infinity",
            [("bound", 1000)] + keys(curve, [64, 128, 640]))
        add(f"17-R2-block-edges-{t}", "R2", f"{curve}, bound 1000 (m = 32): d = 63, 65, 95, 96, 97 and 159 at the edges of a giant step's range",
            [("bound", 1000)] + keys(curve, [63, 65, 95, 96, 97, 159]))
        add(f"17-R2-last-{t}", "R2", f"{curve}, bound 1000: d = 999 and d = 1000",
            [("bound", 1000)] + keys(curve, [999, 1000]))
    add("17-R2-tiny-bounds", "R2", "P-256: bounds 1, 2 and 3, each with d equal to the bound", [
        ("bound", 1), ("key", "one", "P-256", 1), ("bound", 2), ("key", "two", "P-256", 2),
        ("bound", 3), ("key", "three", "P-256", 3)])
    add("17-R2-not-square", "R2", "P-384: bound 10 (m = 4) with d = 8, 9, 10 and bound 17 (m = 5) with d = 10, 16, 17", [
        ("bound", 10)] + keys("P-384", [8, 9, 10], "a") + [("bound", 17)] + keys("P-384", [10, 16, 17], "b"))
    add("17-R2-table-1", "R2", "P-256, table 1, bound 50: one baby step, so every even d is a giant centre", [
        ("table", 1), ("bound", 50)] + keys("P-256", [1, 2, 25, 49, 50]))
    add("17-R2-table-7", "R2", "P-384, table 7, bound 1000: m = 7 below sqrt(1000), d = 7, 8, 14, 15, 993 and 1000", [
        ("table", 7), ("bound", 1000)] + keys("P-384", [7, 8, 14, 15, 993, 1000]))
    add(f"17-R2-random-s{args.seed}", "R2", f"P-256, bound 1000000: five random d (seed {args.seed})", [
        ("bound", 10 ** 6)] + keys("P-256", sorted(rng.sample(range(1, 10 ** 6 + 1), 5))))

    # R3 - negated keys, found on the walk up from Q
    for curve in curves.CURVES:
        t = tag(curve)
        add(f"17-R3-neg-small-{t}", "R3", f"{curve}, bound 1000: -(d*G) for d = 1, 2, 31, 32 and 33",
            [("bound", 1000)] + keys(curve, [-1, -2, -31, -32, -33]))
        add(f"17-R3-neg-centres-{t}", "R3", f"{curve}, bound 1000 (m = 32): -(d*G) for d = 64, 65, 96, 97 and 128",
            [("bound", 1000)] + keys(curve, [-64, -65, -96, -97, -128]))
        add(f"17-R3-neg-last-{t}", "R3", f"{curve}, bound 1000: -(d*G) for d = 999 and 1000",
            [("bound", 1000)] + keys(curve, [-999, -1000]))
    add("17-R3-pair", "R3", "P-256, bound 1000000: 654321*G and its negation side by side", [
        ("bound", 10 ** 6), ("key", "k1", "P-256", 654321), ("key", "k2", "P-256", -654321)])
    add("17-R3-neg-table-1", "R3", "P-384, table 1, bound 50: -(d*G) for d = 1, 2, 3 and 50", [
        ("table", 1), ("bound", 50)] + keys("P-384", [-1, -2, -3, -50]))

    # R4 - out of range, including what the last giant point reaches past the bound
    for curve in curves.CURVES:
        t = tag(curve)
        add(f"17-R4-one-past-{t}", "R4", f"{curve}, bound 1000: d = 1001 and -1001, next to d = 1000",
            [("bound", 1000)] + keys(curve, [1001, -1001, 1000]))
        add(f"17-R4-strong-{t}", "R4", f"{curve}, bound 1000: three strong keys",
            [("bound", 1000)] + [("key", f"s{i}", curve, strong(rng, curve, (-1) ** i)) for i in range(3)])
    assert plan_numbers(10, None) == (4, 3)  # centres -8, 0, 8 reach -12 .. 12
    add("17-R4-past-the-bound", "R4", "P-256, bound 10 (m = 4): d = 11, 12, -11, -12 lie inside the last giant step's range", [
        ("bound", 10)] + keys("P-256", [11, 12, -11, -12, 10]))
    assert plan_numbers(1000, None) == (32, 33)  # last centres +-1024 reach -1056 .. 1056
    add("17-R4-last-centre", "R4", "P-384, bound 1000 (m = 32): d = 1024 and 1056 sit on and at the edge of the last centre", [
        ("bound", 1000)] + keys("P-384", [1024, -1024, 1056, -1056, 1025]))
    add("17-R4-bound-1", "R4", "P-256, bound 1: only d = 1 and -1 are in range", [
        ("bound", 1)] + keys("P-256", [2, -2, -1]))

    # R5 - big bounds; a scan of every value would take far longer than the limit
    def big(case_id, title, bound, curve, values, limit=None):
        assert bound * LINEAR_SECONDS[curve] > 20 * TIME_LIMIT
        items = ([("table", limit)] if limit else []) + [("bound", bound)]
        add(case_id, "R5", title, items + [("key", f"k{i}", curve, e) for i, e in enumerate(values)])

    big("17-R5-p256-2e28-edge", "P-256, bound 2^28: d = -2^28, the last value of the walk up", 2 ** 28, "P-256", [-(2 ** 28)])
    big(f"17-R5-p256-2e28-strong-s{args.seed}", f"P-256, bound 2^28: a strong key, so every giant point runs (seed {args.seed})",
        2 ** 28, "P-256", [strong(rng, "P-256")])
    big("17-R5-p384-2e26-edge", "P-384, bound 2^26: d = 2^26 and d = -2^26", 2 ** 26, "P-384", [2 ** 26, -(2 ** 26)])
    big(f"17-R5-p384-2e26-strong-s{args.seed}", f"P-384, bound 2^26: a strong key (seed {args.seed})",
        2 ** 26, "P-384", [strong(rng, "P-384", -1)])
    for curve in curves.CURVES:
        values = [rng.randint(2 ** 21, 2 ** 22), -rng.randint(2 ** 21, 2 ** 22), strong(rng, curve),
                  -rng.randint(1, 2 ** 22), strong(rng, curve, -1)]
        big(f"17-R5-five-keys-{tag(curve)}-s{args.seed}", f"{curve}, bound 2^22: five keys share one bound (seed {args.seed})",
            2 ** 22, curve, values)
    big(f"17-R5-table-1024-s{args.seed}", f"P-256, table 1024, bound 2^22: a smaller table and 4097 giant points (seed {args.seed})",
        2 ** 22, "P-256", [-(2 ** 22), rng.randint(1, 2 ** 22), strong(rng, "P-256")], limit=1024)

    # R6 - plan lines
    add("17-R6-small", "R6", "plan for bits 1, 2, 3, 8, 12 and 13 with no table limit",
        [("plan", f"b{b}", b) for b in (1, 2, 3, 8, 12, 13)])
    lines, expected = add("17-R6-float-traps", "R6", "plan for bits 54, 63, 109 and 127, where floating-point square roots go wrong",
                          [("plan", f"b{b}", b) for b in (54, 63, 109, 127)])
    assert any(float_plan(2 ** b, None) != plan_numbers(2 ** b, None) for b in (54, 63, 109, 127))
    add("17-R6-huge", "R6", "plan for bits 255, 256, 257, 383, 384 and 400",
        [("plan", f"b{b}", b) for b in (255, 256, 257, 383, 384, 400)])
    add("17-R6-table-limits", "R6", "plan with table 1, 1000 and 2^40, then no limit again", [
        ("table", 1), ("plan", "t1-8", 8), ("plan", "t1-32", 32), ("table", 1000), ("plan", "t1000-32", 32),
        ("plan", "t1000-64", 64), ("table", 2 ** 40), ("plan", "big-64", 64), ("plan", "big-100", 100),
        ("plan", "big-384", 384), ("table", None), ("plan", "free-100", 100)])
    for b, limit in ((100, 1000), (384, 2 ** 40)):
        assert float_plan(2 ** b, limit) != plan_numbers(2 ** b, limit)

    # E2E
    add("17-E2E-incident-values", "E2E", "P-384, bound 255: the eight reported values, 256, and two strong keys", [
        ("bound", 255)] + [("key", f"intermediate-{i + 1}", "P-384", d) for i, d in enumerate(INCIDENT_D)] + [
        ("key", "just-over", "P-384", 256), ("key", "strong-1", "P-384", strong(rng, "P-384")),
        ("key", "strong-2", "P-384", strong(rng, "P-384", -1))])
    add("17-E2E-bound-gap", "E2E", "P-256: d = 3000000 is none at bound 4096 and weak at bound 2^22; plans for 2^32 and 2^384", [
        ("bound", 4096), ("key", "k1", "P-256", 3000000), ("bound", 2 ** 22), ("key", "k2", "P-256", 3000000),
        ("table", 1024), ("plan", "p1", 32), ("table", None), ("plan", "p2", 32), ("plan", "p3", 384)])
    near = [rng.choice((1, -1)) * rng.randint(5000, 2 ** 24) for _ in range(4)]
    add(f"17-E2E-near-misses-s{args.seed}", "E2E", f"P-256: four keys with |d| from 5000 to 2^24, at bounds 4096 and 2^24 (seed {args.seed})", [
        ("bound", 4096)] + keys("P-256", near, "a") + [("bound", 2 ** 24)] + keys("P-256", near, "b"))
    items = []
    for i in range(12):
        if i % 4 == 0:
            items.append(("bound", rng.choice((255, 1000, 4096, 10 ** 5, 2 ** 20))))
            if rng.random() < 0.3:
                items.append(("table", rng.choice((None, 300, 1000))))
        bound = next(it[1] for it in reversed(items) if it[0] == "bound")
        curve = rng.choice(list(curves.CURVES))
        r = rng.random()
        e = strong(rng, curve) if r < 0.2 else rng.randint(1, bound + bound // 4 + 2)
        items.append(("key", f"r{i}", curve, e * rng.choice((1, -1))))
        if rng.random() < 0.25:
            items.append(("plan", f"q{i}", rng.randint(1, 400)))
    # A small table and a big bound make the walk long; every random key stays quick.
    limit = None
    for it in items:
        if it[0] == "table":
            limit = it[1]
        if it[0] == "bound":
            assert plan_numbers(it[1], limit)[1] <= 2 ** 12
    add(f"17-E2E-random-s{args.seed}", "E2E", f"twelve random keys on both curves, random bounds, tables and plans (seed {args.seed})", items)

    cases.save()


if __name__ == "__main__":
    main()
