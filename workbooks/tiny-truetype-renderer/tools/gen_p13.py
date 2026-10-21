"""Test cases for checkpoint 13 (intersect a line and a quadratic curve).

Expected outputs use exact arithmetic: fractions.Fraction throughout, and a
60-digit decimal square root when a root is irrational. Each line is also checked
independently: the curve is evaluated by de Casteljau's construction at 400+
values of t, and the number of times it meets the line (sign changes and exact
zeros of the side test) must equal the number of points in the answer. Lines are
kept away from numerically fragile spots: every root that isn't exactly 0 or 1
is at least 0.01 away from 0 and 1, and two distinct roots are at least 0.01 apart.

    py -P tools/gen_p13.py                                  # tests/13 (seed 1)
    py -P tools/gen_p13.py --seed 777 --out build/fresh/13  # what `.\\check 13 -Fresh` runs
"""

import random
import sys
from decimal import Decimal, getcontext
from fractions import Fraction as F
from math import isqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402
from fontTools.pens.basePen import BasePen  # noqa: E402

getcontext().prec = 60
SOURCE = "exact arithmetic (fractions.Fraction, 60-digit decimal square roots), root count cross-checked"
FONT_SOURCE = f"outline read by {wb.FT}; exact arithmetic (Fraction, 60-digit decimal square roots)"

REQUIREMENTS = [
    ("R1", "A line that crosses the curve twice gives both points (the line is infinite)"),
    ("R2", "Only crossings with 0 <= t <= 1 count: one inside, one beyond an end"),
    ("R3", "No crossing with 0 <= t <= 1 -> none"),
    ("R4", "A tangent line gives its touching point once"),
    ("R5", "K.A = 0: the equation is linear (or has no solution)"),
    ("R6", "Points are ordered by t, whichever way the line points"),
    ("R7", "Crossings at the ends, t = 0 and t = 1, count"),
    ("E2E", "Horizontal scanlines across every curve of real glyphs, and random lines"),
]

# When `none` was expected but points were written, the filter on t (or the
# discriminant) let something through.
EXPLAIN = "none=R3"


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


def to_dec(f) -> Decimal:
    f = F(f)
    return Decimal(f.numerator) / Decimal(f.denominator)


def sub(p, q):
    return (p[0] - q[0], p[1] - q[1])


def dot(u, v):
    return u[0] * v[0] + u[1] * v[1]


def cross(u, v):
    return u[0] * v[1] - u[1] * v[0]


def exact_sqrt(f: F):
    if f.numerator < 0:
        return None
    n, d = isqrt(f.numerator), isqrt(f.denominator)
    return F(n, d) if n * n == f.numerator and d * d == f.denominator else None


def analyse(p1, p2, p3, l1, l2):
    """Every real root of K.(P(t) - l1) = 0, exactly, and what kind of case it is."""
    d = sub(l2, l1)
    k = (d[1], -d[0])
    A = (p1[0] - 2 * p2[0] + p3[0], p1[1] - 2 * p2[1] + p3[1])
    B = (2 * (p2[0] - p1[0]), 2 * (p2[1] - p1[1]))
    qa, qb, qc = dot(k, A), dot(k, B), dot(k, sub(p1, l1))
    if qa == 0:
        if qb == 0:
            assert qc != 0, "the curve lies along the line (every t is a root); the tests exclude this"
            return "parallel", []
        return "linear", [-qc / qb]
    disc = qb * qb - 4 * qa * qc
    if disc < 0:
        return "miss", []
    if disc == 0:
        return "tangent", [-qb / (2 * qa)]
    r = exact_sqrt(disc)
    if r is not None:
        return "two-roots", sorted([(-qb - r) / (2 * qa), (-qb + r) / (2 * qa)])
    s = to_dec(disc).sqrt()
    return "two-roots", sorted([(to_dec(-qb) - s) / to_dec(2 * qa), (to_dec(-qb) + s) / to_dec(2 * qa)])


def de_casteljau(p1, p2, p3, t):
    def lerp(a, b):
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
    return lerp(lerp(p1, p2), lerp(p2, p3))


def sign(v):
    return (v > 0) - (v < 0)


def check_count(p1, p2, p3, l1, l2, kind, inside):
    """Independent check: walk along the curve and count where it meets the line."""
    samples = {F(i, 400) for i in range(401)} | {t for t in inside if isinstance(t, F)}
    side = [sign(cross(sub(l2, l1), sub(de_casteljau(p1, p2, p3, t), l1))) for t in sorted(samples)]
    meets = side.count(0) + sum(1 for a, b in zip(side, side[1:]) if a * b < 0)
    assert meets == len(inside), f"root count {len(inside)} but the curve meets the line {meets} times"
    if kind == "tangent" and inside:
        i = sorted(samples).index(inside[0])
        nearby = [s for s in side[max(0, i - 1):i + 2] if s != 0]
        assert len(set(nearby)) <= 1, "a tangent should touch, not cross"


def answer(line, req=None, verify=True):
    words = line.split()
    assert words[0] == "curve" and words[7] == "line" and len(words) == 12, line
    v = [F(w) for w in words[1:7] + words[8:]]
    # The limits promised on the problem page.
    assert all(abs(x) <= 1000 and (x * 4).denominator == 1 for x in v), line
    p1, p2, p3, l1, l2 = (v[0], v[1]), (v[2], v[3]), (v[4], v[5]), (v[6], v[7]), (v[8], v[9])
    assert l1 != l2, line
    kind, roots = analyse(p1, p2, p3, l1, l2)
    # Keep clear of fragile spots, so any sensible floating-point solution agrees.
    for t in roots:
        if t not in (0, 1):
            assert abs(t) >= F(1, 100) and abs(t - 1) >= F(1, 100), f"{line}: root {float(t):.5f} near an end"
    if len(roots) == 2:
        assert abs(roots[1] - roots[0]) >= Decimal("0.01"), f"{line}: nearly tangent"
    inside = [t for t in roots if 0 <= t <= 1]
    if verify:
        check_count(p1, p2, p3, l1, l2, kind, inside)

    expect = {
        "R1": kind == "two-roots" and len(inside) == 2,
        "R2": kind == "two-roots" and len(inside) == 1,
        "R3": kind in ("miss", "two-roots") and not inside,
        "R4": kind == "tangent",
        "R5": kind in ("linear", "parallel"),
        "R6": len(inside) == 2,
        "R7": any(t in (0, 1) for t in inside),
    }
    assert req not in expect or expect[req], f"{line}: is {kind} with {len(inside)} points, not an {req} case"

    if not inside:
        return "none"
    out = []
    for t in inside:
        if isinstance(t, F):
            x, y = de_casteljau(p1, p2, p3, t)
        else:
            x, y = de_casteljau(tuple(map(to_dec, p1)), tuple(map(to_dec, p2)), tuple(map(to_dec, p3)), t)
            assert abs(cross(tuple(map(to_dec, sub(l2, l1))), (x - to_dec(l1[0]), y - to_dec(l1[1])))) < Decimal("1e-40")
        out.append(f"{wb.num(x)} {wb.num(y)}")
    return " ".join(out)


def curve_line(p1, p2, p3, l1, l2):
    return f"curve {' '.join(dec(v) for v in (*p1, *p2, *p3))} line {' '.join(dec(v) for v in (*l1, *l2))}"


# ---- Font outlines ------------------------------------------------------------------

class CurvePen(BasePen):
    """Collects the single quadratic curves of an outline. fontTools' BasePen
    inserts the implied on-curve point between two off-curve points."""

    def __init__(self):
        super().__init__(None)
        self.curves = []

    def _moveTo(self, pt):
        pass

    def _lineTo(self, pt):
        pass

    def _qCurveToOne(self, pt1, pt2):
        self.curves.append(tuple((F(x), F(y)) for x, y in (self._getCurrentPoint(), pt1, pt2)))

    def _curveToOne(self, pt1, pt2, pt3):
        raise AssertionError("TrueType outlines have no cubic curves")

    def _closePath(self):
        pass


def font_curves(font_rel, char):
    font = wb.load(font_rel)
    name = font.getBestCmap()[ord(char)]
    ends, points = wb.outline_of(font, name)
    pen = CurvePen()
    wb.draw_outline(pen, ends, points)
    return name, pen.curves


# ---- Cases ------------------------------------------------------------------------------

def main():
    args = wb.parse_args("13")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "records tolerance=0.001", REQUIREMENTS, EXPLAIN, source=SOURCE)

    def add(case_id, req, title, lines, source=SOURCE):
        cases.add(case_id, req, title, lines, [answer(l, req) for l in lines], source=source)

    arch = "curve 0 0 50 100 100 0"
    # R1 - two crossings
    add("13-R1-arch", "R1", "a horizontal line crosses an arch twice, at t = 0.2 and 0.8",
        [f"{arch} line 0 32 100 32"])
    add("13-R1-far-points", "R1", "the same line given by two points far from the curve (the line is infinite)", [
        f"{arch} line -1000 32 -999 32",
        f"{arch} line 500 32 900 32",
    ])
    add("13-R1-irrational", "R1", "crossings where t is irrational", [
        f"{arch} line 0 20 100 20",
        f"{arch} line 0 45 1 45",
    ])
    add("13-R1-slanted", "R1", "slanted lines crossing twice", [
        f"{arch} line 0 10 200 90",
        "curve -40 -30 60 80 120 -20 line -50 -10 150 30",
    ])
    add("13-R1-vertical", "R1", "a vertical line across a curve that bulges sideways",
        ["curve 0 0 100 50 0 100 line 30 -500 30 500"])

    # R2 - one crossing inside, the other beyond an end
    add("13-R2-rising", "R2", "y = 100 t^2 meets y = 25 at t = 0.5; the root t = -0.5 is off the curve",
        ["curve 0 0 50 0 100 100 line 0 25 100 25"])
    add("13-R2-short-line", "R2", "the same, with the line given by two points far to the left",
        ["curve 0 0 50 0 100 100 line -300 25 -200 25"])
    add("13-R2-slanted", "R2", "a slanted line: one root at 0.905, the other at -0.055", [
        f"{arch} line 0 -10 100 20",
        "curve 0 0 50 0 100 100 line 0 50 100 70",
    ])

    # R3 - nothing on the curve
    add("13-R3-above", "R3", "a line above the arch: no real roots", [
        f"{arch} line 0 60 100 60",
        f"{arch} line 0 51 100 51",
    ])
    add("13-R3-beyond-ends", "R3", "the line crosses the curve's extension at t = -0.09 and 1.09", [
        f"{arch} line 0 -20 100 -20",
        f"{arch} line -50 -20 150 -20",
    ])
    add("13-R3-slanted-miss", "R3", "slanted lines that pass the curve by", [
        "curve 0 0 50 0 100 100 line -10 0 90 110",
        "curve 0 0 100 50 0 100 line 60 0 80 100",
    ])

    # R4 - tangents (whole numbers, so the discriminant is exactly 0)
    add("13-R4-arch-top", "R4", "a horizontal line touching the top of an arch at t = 0.5",
        ["curve 0 0 5 10 10 0 line 0 5 10 5"])
    add("13-R4-slanted", "R4", "a slanted line touching the curve at t = 0.25",
        ["curve 0 0 16 32 32 0 line 8 12 40 44"])
    add("13-R4-sideways", "R4", "a vertical line touching a sideways curve at its leftmost point",
        ["curve 0 0 -20 20 0 40 line -10 -100 -10 100"])
    add("13-R4-outside", "R4", "the line touches the curve's extension at t = 1.5 -> none",
        ["curve 0 40 50 10 100 0 line 0 -5 100 -5"])

    # R5 - the linear case
    add("13-R5-scanline", "R5", "a horizontal line across a curve whose y changes linearly", [
        "curve 0 0 10 5 0 10 line -10 5 10 5",
        "curve 100 0 160 50 100 100 line 0 30 1 30",
    ])
    add("13-R5-slanted", "R5", "a line parallel to A = p1 - 2 p2 + p3, which is (20, 20)",
        ["curve 0 0 0 -10 20 0 line 0 -5 10 5"])
    add("13-R5-straight-curve", "R5", "a straight 'curve' (control point halfway) has A = 0", [
        "curve 0 0 5 5 10 10 line 0 8 10 8",
        "curve 0 0 5 5 10 10 line 8 0 9 -1",
    ])
    add("13-R5-no-crossing", "R5", "linear but off the curve (t = 1.2), and a straight curve parallel to the line", [
        f"{arch} line 120 0 120 50",
        "curve 0 0 5 0 10 0 line 0 3 10 3",
    ])

    # R6 - order by t
    add("13-R6-line-direction", "R6", "the same line pointing both ways gives the same order", [
        f"{arch} line 0 32 100 32",
        f"{arch} line 100 32 0 32",
    ])
    add("13-R6-curve-direction", "R6", "the curve run backwards gives the points in reverse order", [
        "curve 100 0 50 100 0 0 line 0 32 100 32",
        "curve 100 0 50 100 0 0 line 100 32 0 32",
    ])
    add("13-R6-falling", "R6", "order by t, not by x or y", [
        "curve 0 100 100 50 0 0 line 30 -500 30 500",
        "curve 0 100 100 50 0 0 line 30 500 30 -500",
        "curve 100 100 0 100 0 0 line 0 32 100 132",
    ])

    # R7 - roots exactly at the ends
    add("13-R7-start", "R7", "the line passes through p1 (t = 0) and crosses again at t = 0.75",
        [f"{arch} line 0 0 100 50"])
    add("13-R7-end", "R7", "the line passes through p3 (t = 1) and crosses again at t = 0.25",
        [f"{arch} line 100 0 0 50"])
    add("13-R7-chord", "R7", "the line through p1 and p3 meets the curve at t = 0 and t = 1",
        [f"{arch} line 0 0 100 0", f"{arch} line 300 0 -40 0"])
    add("13-R7-scanline-at-end", "R7", "a horizontal line at the height of p3: t = 1 (and -1, off the curve)",
        ["curve 0 0 50 0 100 100 line 0 100 1 100"])
    add("13-R7-tangent-at-start", "R7", "a line along p1 -> p2 touches the curve at t = 0",
        ["curve 0 0 50 0 100 100 line 0 0 10 0"])

    # Random cases
    def rpt(lo=-100, hi=100):
        return (F(rng.randint(lo, hi)), F(rng.randint(lo, hi)))

    def random_lines(count, want):
        lines = []
        for _ in range(100000):
            p1, p2, p3, l1, l2 = rpt(), rpt(), rpt(), rpt(), rpt()
            if l1 == l2:
                continue
            text = curve_line(p1, p2, p3, l1, l2)
            try:
                answer(text, verify=False)  # robust? (add() verifies the ones kept)
            except AssertionError:
                continue
            kind, roots = analyse(p1, p2, p3, l1, l2)
            n = sum(1 for t in roots if 0 <= t <= 1)
            if want is None or want(kind, n):
                lines.append(text)
                if len(lines) == count:
                    return lines
        raise RuntimeError("couldn't find enough random lines")

    add(f"13-R1-random-s{args.seed}", "R1", f"10 random lines that cross a random curve twice (seed {args.seed})",
        random_lines(10, lambda kind, n: kind == "two-roots" and n == 2))
    add(f"13-R2-random-s{args.seed}", "R2", f"10 random lines that cross once (seed {args.seed})",
        random_lines(10, lambda kind, n: kind == "two-roots" and n == 1))
    add(f"13-R3-random-s{args.seed}", "R3", f"10 random lines that miss the curve (seed {args.seed})",
        random_lines(10, lambda kind, n: kind in ("miss", "two-roots") and n == 0))
    for k in range(2):
        lines = random_lines(15, None)
        add(f"13-E2E-random-s{args.seed}-{k}", "E2E", f"15 random curves and lines, set {k} (seed {args.seed})", lines)

    # End to end: one horizontal scanline against every curve of a glyph
    for font_rel, char, label in ((wb.JETBRAINS, "o", "JetBrains Mono Bold"),
                                  (wb.JETBRAINS, "S", "JetBrains Mono Bold"),
                                  (wb.NOTO_JP, "あ", "Noto Sans JP")):
        name, curves = font_curves(font_rel, char)
        ys = sorted(y for c in curves for _, y in c)
        best = None
        for k in range(1, 32):  # the robust height that crosses the most curves
            y = ys[0] + (ys[-1] - ys[0]) * k // 32 + F(1, 4)
            lines = [curve_line(*c, (0, y), (1000, y)) for c in curves]
            try:
                expected = [answer(l, verify=False) for l in lines]
            except AssertionError:
                continue  # a curve too close to tangent or to an end at this height
            hits = sum(e != "none" for e in expected)
            if best is None or hits > best[0]:
                best = (hits, y, lines, expected)
        assert best is not None, f"no robust scanline height for {char}"
        hits, y, lines, expected = best
        assert expected == [answer(l) for l in lines]  # now with the independent check
        linear = sum(c[0][1] - 2 * c[1][1] + c[2][1] == 0 for c in curves)
        cases.add(f"13-E2E-scanline-U+{ord(char):04X}", "E2E",
                  f"U+{ord(char):04X} ({name}, {label}): y = {dec(y)} against each of its {len(curves)} curves "
                  f"({hits} crossed; {linear} curves have K.A = 0)", lines, expected, source=FONT_SOURCE)

    cases.save()


if __name__ == "__main__":
    main()
