"""Test cases for checkpoint 12 (intersect two segments).

Expected outputs use exact fractions.Fraction arithmetic. The oracle solves the
two segments' parametric equations for both parameters (s and t) and checks that
both lie in [0, 1]; the script also checks that the problem page's side test
gives the same answer on every line, and that each hand-made line is the kind of
case its requirement promises (a crossing, a touch, a miss, or parallel).

    py -P tools/gen_p12.py                                  # tests/12 (seed 1)
    py -P tools/gen_p12.py --seed 777 --out build/fresh/12  # what `.\\check 12 -Fresh` runs
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402

SOURCE = "exact arithmetic with Python fractions.Fraction (parametric solve, cross-checked)"
FONT_SOURCE = f"outline read by {wb.FT}; intersections with fractions.Fraction"

REQUIREMENTS = [
    ("R1", "Segments that cross give the crossing point"),
    ("R2", "Touching counts: a shared endpoint or a T-junction gives that point"),
    ("R3", "Lines that cross outside either segment -> none"),
    ("R4", "Parallel or collinear segments -> none, even when they overlap"),
    ("R5", "Vertical, horizontal, negative and fractional coordinates"),
    ("E2E", "Scanlines across real glyph edges, and random segments"),
]

# Which requirement a difference most likely comes from. When `none` was expected,
# a point means the side test let it through (R3); nan or inf means a division by
# a zero cross product (R4).
EXPLAIN = ("none=R3 none~nan=R4 none~-nan=R4 none~NaN=R4 none~inf=R4 none~-inf=R4 "
           "none~Infinity=R4 none~-Infinity=R4")


# ---- Exact maths ------------------------------------------------------------------

def dec(v) -> str:
    """An exact decimal string for a number with a short decimal expansion."""
    v = F(v)
    for k in range(12):
        n = v * 10 ** k
        if n.denominator == 1:
            n = n.numerator
            digits = str(abs(n)).rjust(k + 1, "0")
            text = (digits[:-k] + "." + digits[-k:]) if k else digits
            return ("-" if n < 0 else "") + text
    raise ValueError(f"{v} has no short decimal form")


def sub(p, q):
    return (p[0] - q[0], p[1] - q[1])


def cross(u, v):
    return u[0] * v[1] - u[1] * v[0]


def classify(a1, a2, b1, b2):
    """('cross' | 'touch' | 'miss' | 'parallel', point or None), from the parametric form
    a1 + t (a2 - a1) = b1 + s (b2 - b1)."""
    v1, v2 = sub(a2, a1), sub(b2, b1)
    den = cross(v1, v2)
    if den == 0:
        return "parallel", None
    w = sub(b1, a1)
    t, s = cross(w, v2) / den, cross(w, v1) / den
    if not (0 <= t <= 1 and 0 <= s <= 1):
        return "miss", None
    point = (a1[0] + t * v1[0], a1[1] + t * v1[1])
    assert point == (b1[0] + s * v2[0], b1[1] + s * v2[1])
    return ("touch" if t in (0, 1) or s in (0, 1) else "cross"), point


def side_test(a1, a2, b1, b2):
    """The rule as the problem page states it (side test, then t)."""
    def side(p, start, end):
        return cross(sub(end, start), sub(p, start))
    if side(b1, a1, a2) * side(b2, a1, a2) > 0 or side(a1, b1, b2) * side(a2, b1, b2) > 0:
        return None
    v1, v2 = sub(a2, a1), sub(b2, b1)
    den = cross(v1, v2)
    if den == 0:
        return None
    t = cross(sub(b1, a1), v2) / den
    return (a1[0] + t * v1[0], a1[1] + t * v1[1])


def parse(line):
    words = line.split()
    assert words[0] == "segments" and len(words) == 9, line
    v = [F(w) for w in words[1:]]
    # The limits promised on the problem page: |coordinate| <= 1000 in steps of 0.25,
    # so every side test and cross product is exact in double arithmetic.
    assert all(abs(x) <= 1000 and (x * 4).denominator == 1 for x in v), line
    a1, a2, b1, b2 = (v[0], v[1]), (v[2], v[3]), (v[4], v[5]), (v[6], v[7])
    assert a1 != a2 and b1 != b2, f"degenerate segment: {line}"
    return a1, a2, b1, b2


def answer(line, kind=None):
    a1, a2, b1, b2 = parse(line)
    got, point = classify(a1, a2, b1, b2)
    assert point == side_test(a1, a2, b1, b2), line
    assert kind is None or got == kind, f"{line}: meant to be {kind}, is {got}"
    if got != "parallel":
        assert abs(cross(sub(a2, a1), sub(b2, b1))) >= F(1, 4), line
    return "none" if point is None else f"{wb.num(point[0])} {wb.num(point[1])}"


def seg_line(a1, a2, b1, b2):
    return "segments " + " ".join(dec(v) for v in (*a1, *a2, *b1, *b2))


# ---- Cases ------------------------------------------------------------------------------

KIND = {"R1": "cross", "R2": "touch", "R3": "miss", "R4": "parallel"}


def main():
    args = wb.parse_args("12")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "records tolerance=0.001", REQUIREMENTS, EXPLAIN, source=SOURCE)

    def add(case_id, req, title, lines, source=SOURCE):
        cases.add(case_id, req, title, lines, [answer(l, KIND.get(req)) for l in lines], source=source)

    # R1 - proper crossings
    add("12-R1-x-shape", "R1", "the two diagonals of a square cross in its centre",
        ["segments 0 0 10 10 0 10 10 0"])
    add("12-R1-off-center", "R1", "a crossing at t = 0.5 of a slanted segment",
        ["segments 0 0 8 4 2 6 6 -2"])
    add("12-R1-argument-order", "R1", "the same pair given in four orders gives the same point", [
        "segments 0 0 8 4 2 6 6 -2",
        "segments 2 6 6 -2 0 0 8 4",
        "segments 8 4 0 0 2 6 6 -2",
        "segments 6 -2 2 6 8 4 0 0",
    ])
    add("12-R1-thirds", "R1", "crossings at t = 1/3 and t = 5/7 (repeating decimals)", [
        "segments 0 0 200 10 0 5 200 0",
        "segments 0 0 70 0 50 -20 50 8",
    ])
    add("12-R1-several", "R1", "crossings at a range of angles", [
        "segments 0 0 30 10 10 20 20 -10",
        "segments 100 100 300 200 150 250 250 50",
        "segments 0 0 1 100 -50 40 60 60",
        "segments 500 -300 -400 200 -100 -200 100 300",
    ])

    # R2 - touching
    add("12-R2-shared-endpoint", "R2", "two edges of a polygon that meet at a corner", [
        "segments 0 0 10 0 10 0 10 10",
        "segments 0 0 10 0 0 0 -7 3",
        "segments 4 9 0 0 20 1 4 9",
    ])
    add("12-R2-t-junction", "R2", "one segment ends on the middle of the other", [
        "segments 0 0 10 0 5 0 5 8",
        "segments 0 0 10 0 5 -8 5 0",
        "segments 3 -4 3 4 3 0 9 0",
    ])
    add("12-R2-diagonal", "R2", "an endpoint lands exactly on a slanted segment", [
        "segments 0 0 6 3 4 2 4 9",
        "segments 1 1 7 4 -2 10 4 2.5",
    ])
    add("12-R2-scanline-vertex", "R2", "a horizontal line through a corner touches both edges there", [
        "segments -100 5 100 5 3 5 7 12",
        "segments -100 5 100 5 0 0 3 5",
    ])

    # R3 - the lines cross, the segments don't
    add("12-R3-beyond-end", "R3", "the lines cross at (5, 5) but the first segment stops at (4, 4)",
        ["segments 0 0 4 4 0 10 10 0"])
    add("12-R3-falls-short", "R3", "a segment that stops just short of the other", [
        "segments 0 0 10 0 5 1 5 8",
        "segments 0 0 10 0 5 0.5 5 8",
        "segments 0 0 10 0 10.5 -3 10.5 3",
    ])
    add("12-R3-beyond-both", "R3", "the lines cross beyond the ends of both segments", [
        "segments 0 0 1 1 5 0 4 1",
        "segments -10 0 -5 5 10 0 5 5",
    ])

    # R4 - parallel and collinear
    add("12-R4-parallel", "R4", "parallel segments: horizontal, diagonal and vertical", [
        "segments 0 0 10 0 0 5 10 5",
        "segments 0 0 10 10 0 1 10 11",
        "segments 0 0 0 10 3 -5 3 20",
    ])
    add("12-R4-collinear-overlap", "R4", "collinear segments that overlap", [
        "segments 0 0 10 10 5 5 15 15",
        "segments 0 0 10 0 2 0 8 0",
        "segments 0 0 10 0 8 0 2 0",
    ])
    add("12-R4-collinear-touching", "R4", "collinear segments that meet end to end", [
        "segments 0 0 5 0 5 0 10 0",
        "segments 0 0 3 6 3 6 5 10",
    ])
    add("12-R4-identical", "R4", "a segment against itself, both ways round", [
        "segments 1 2 3 4 1 2 3 4",
        "segments 1 2 3 4 3 4 1 2",
    ])
    add("12-R4-collinear-apart", "R4", "collinear segments with a gap between them",
        ["segments 0 0 2 0 5 0 8 0", "segments -1 -2 0 0 2 4 3 6"])

    # R5 - orientation, signs and fractions
    add("12-R5-vertical-horizontal", "R5", "a vertical and a horizontal segment, both orders", [
        "segments 3 -5 3 5 -5 2 5 2",
        "segments -5 2 5 2 3 -5 3 5",
    ])
    add("12-R5-negative", "R5", "everything in the negative quadrant", [
        "segments -10 -10 -2 -6 -8 -2 -4 -10",
        "segments -300 -20 -20 -300 -250 -250 -10 -10",
    ])
    add("12-R5-vertical-slanted", "R5", "a vertical segment against slanted ones", [
        "segments 7 0 7 100 0 3 20 43",
        "segments 7 100 7 0 20 43 0 3",
    ])
    add("12-R5-fractional", "R5", "coordinates in steps of 0.25", [
        "segments -2.5 1.25 7.5 -3.75 0.5 -4 0.5 6",
        "segments 0.25 0.25 10.75 5.5 3.5 -1 2.25 9.75",
    ])
    add("12-R5-large", "R5", "coordinates at the +-1000 limit", [
        "segments -1000 -1000 1000 1000 -1000 1000 1000 -1000",
        "segments -1000 3 1000 3 -999 -1000 997 1000",
    ])
    add("12-R5-scanline", "R5", "a long horizontal line across slanted edges, as a fill would use", [
        "segments 0 7 1000 7 300 0 420 30",
        "segments 0 7 1000 7 420 30 300 0",
        "segments 0 7 1000 7 600 -50 590 50",
    ])

    # Random cases aimed at R1-R4
    def rpt(lo=-100, hi=100):
        return (F(rng.randint(lo, hi)), F(rng.randint(lo, hi)))

    def collect(kind, count, make):
        lines = []
        while len(lines) < count:
            a1, a2, b1, b2 = make()
            if a1 != a2 and b1 != b2 and classify(a1, a2, b1, b2)[0] == kind:
                lines.append(seg_line(a1, a2, b1, b2))
        return lines

    add(f"12-R1-random-s{args.seed}", "R1", f"12 random crossing pairs (seed {args.seed})",
        collect("cross", 12, lambda: (rpt(), rpt(), rpt(), rpt())))

    def touching():
        a1, a2, other = rpt(), rpt(), rpt()
        t = rng.choice([F(0), F(1), F(1, 2), F(1, 4), F(3, 4)])
        p = (a1[0] + t * (a2[0] - a1[0]), a1[1] + t * (a2[1] - a1[1]))
        if p[0].denominator != 1 or p[1].denominator != 1:
            return a1, a1, a1, a1  # rejected: degenerate
        return (a1, a2, p, other) if rng.random() < 0.5 else (a1, a2, other, p)
    add(f"12-R2-random-s{args.seed}", "R2", f"10 random touching pairs (seed {args.seed})",
        collect("touch", 10, touching))
    add(f"12-R3-random-s{args.seed}", "R3", f"10 random pairs whose lines cross outside them (seed {args.seed})",
        collect("miss", 10, lambda: (rpt(), rpt(), rpt(), rpt())))

    def parallel():
        d = (F(rng.randint(-9, 9)), F(rng.randint(-9, 9)))
        a1 = rpt(-50, 50)
        b1 = (a1[0] + rng.randint(-5, 5) * d[0], a1[1] + rng.randint(-5, 5) * d[1]) \
            if rng.random() < 0.5 else rpt(-50, 50)  # collinear half the time
        k1, k2 = rng.choice([-4, -3, -2, -1, 1, 2, 3, 4]), rng.choice([-4, -3, -2, -1, 1, 2, 3, 4])
        return a1, (a1[0] + k1 * d[0], a1[1] + k1 * d[1]), b1, (b1[0] + k2 * d[0], b1[1] + k2 * d[1])
    add(f"12-R4-random-s{args.seed}", "R4", f"10 random parallel or collinear pairs (seed {args.seed})",
        collect("parallel", 10, parallel))

    # End to end: random pairs on a small grid, where touching and collinear pairs are common
    for k in range(3):
        lines = []
        while len(lines) < 20:
            a1, a2, b1, b2 = rpt(-6, 6), rpt(-6, 6), rpt(-6, 6), rpt(-6, 6)
            if a1 != a2 and b1 != b2:
                lines.append(seg_line(a1, a2, b1, b2))
        kinds = [classify(*parse(l))[0] for l in lines]
        summary = ", ".join(f"{kinds.count(x)} {x}" for x in ("cross", "touch", "miss", "parallel"))
        add(f"12-E2E-random-s{args.seed}-{k}", "E2E", f"20 random pairs on a small grid ({summary})", lines)

    # End to end: scanlines across the straight edges of real glyphs
    font = wb.load(wb.JETBRAINS)
    cmap = font.getBestCmap()
    for char in "KZ":
        name = cmap[ord(char)]
        ends, points = wb.outline_of(font, name)
        assert all(on for _, _, on in points), f"{char} has curves"
        edges, start = [], 0
        for end in ends:
            contour = [(F(x), F(y)) for x, y, _ in points[start:end + 1]]
            edges += [(contour[i], contour[(i + 1) % len(contour)]) for i in range(len(contour))]
            start = end + 1
        ys = sorted({p[1] for e in edges for p in e})
        middle = (ys[0] + ys[-1]) // 2 + F(1, 2)
        # A vertex whose two edges both slant, so the scanline touches both of them there.
        corner = next(e[1][1] for i, e in enumerate(edges)
                      if e[0][1] != e[1][1] and edges[(i + 1) % len(edges)][1][1] != e[1][1]
                      and ys[0] < e[1][1] < ys[-1])
        for y, how in ((middle, "between corners"), (corner, "through a corner")):
            lines = [seg_line((-1000, y), (1000, y), p, q) for p, q in edges]
            add(f"12-E2E-scanline-{char}-y{dec(y)}", "E2E",
                f"'{char}' ({name}): a horizontal line at y = {dec(y)} ({how}) against each of its "
                f"{len(edges)} edges", lines, source=FONT_SOURCE)

    cases.save()


if __name__ == "__main__":
    main()
