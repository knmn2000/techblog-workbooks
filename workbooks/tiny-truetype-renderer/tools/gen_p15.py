"""Test cases for checkpoint 15 (lowest point of a quadratic curve).

Expected outputs use exact fractions.Fraction arithmetic: the minimum of y(t) over
the candidates t = 0, t = 1 and the turning point (when it lies in [0, 1]). Each
answer is also checked independently by evaluating the curve with de Casteljau's
construction at 2001 values of t: no sample may be lower than the answer, and the
lowest sample must be within the largest gap a sample can leave.

    py -P tools/gen_p15.py                                  # tests/15 (seed 1)
    py -P tools/gen_p15.py --seed 777 --out build/fresh/15  # what `.\\check 15 -Fresh` runs
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402
from fontTools.pens.basePen import BasePen  # noqa: E402

SOURCE = "exact arithmetic with Python fractions.Fraction, checked against 2001 samples of the curve"
FONT_SOURCE = f"outline read by {wb.FT}; minimum with fractions.Fraction, checked by sampling"

REQUIREMENTS = [
    ("R1", "Curves that only rise or only fall: the minimum is at an end"),
    ("R2", "A valley inside the curve: the minimum is at the turning point"),
    ("R3", "A turning point outside 0 <= t <= 1 doesn't count"),
    ("R4", "Straight curves (a = 0) and flat ones (a = b = 0)"),
    ("R5", "Curves that bulge upward: the turning point is a maximum"),
    ("E2E", "Every curve of real glyphs (font units and screen coordinates), and random curves"),
]


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


def kind_of(y1, y2, y3):
    a, b = y1 - 2 * y2 + y3, 2 * (y2 - y1)
    if a == 0:
        return ("flat" if b == 0 else "straight"), None
    t = -b / (2 * a)
    if a < 0:
        return "hill", t
    return ("valley-inside" if 0 < t < 1 else "valley-outside"), t


def lowest(y1, y2, y3):
    """The exact minimum of y(t) = (1-t)^2 y1 + 2(1-t)t y2 + t^2 y3 for t in [0, 1]."""
    a, b = y1 - 2 * y2 + y3, 2 * (y2 - y1)
    candidates = [y1, y3]
    if a != 0:
        t = -b / (2 * a)
        if 0 <= t <= 1:
            candidates.append(a * t * t + b * t + y1)
    return min(candidates)


def check_by_sampling(y1, y2, y3, low):
    """Independent check with de Casteljau's construction at t = k / 2000."""
    a = y1 - 2 * y2 + y3
    samples = []
    for k in range(2001):
        t = F(k, 2000)
        p, q = y1 + (y2 - y1) * t, y2 + (y3 - y2) * t
        samples.append(p + (q - p) * t)
    assert min(samples) >= low, "a sample is lower than the answer"
    # Next to the true minimum there is a sample within 1/4000 in t, and y can
    # differ there by at most |a| (1/4000)^2.
    assert min(samples) - low <= abs(a) * F(1, 4000) ** 2, "the answer is lower than the curve gets"


def answer(line, req=None):
    words = line.split()
    assert words[0] == "curve" and len(words) == 7, line
    v = [F(w) for w in words[1:]]
    # The limits promised on the problem page.
    assert all(abs(x) <= 1000 and (x * 10 ** 4).denominator == 1 for x in v), line
    y1, y2, y3 = v[1], v[3], v[5]
    low = lowest(y1, y2, y3)
    check_by_sampling(y1, y2, y3, low)
    kind, t = kind_of(y1, y2, y3)
    monotone = min(y1, y3) <= y2 <= max(y1, y3)
    expect = {
        "R1": kind in ("valley-outside", "hill") and monotone,
        "R2": kind == "valley-inside",
        "R3": kind == "valley-outside" and (t < 0 or t > 1),
        "R4": kind in ("straight", "flat"),
        "R5": kind == "hill" and 0 < t < 1,
    }
    assert req not in expect or expect[req], f"{line}: is {kind}, not an {req} case"
    return wb.num(low)


def curve_line(p1, p2, p3):
    return "curve " + " ".join(dec(v) for v in (*p1, *p2, *p3))


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
    args = wb.parse_args("15")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "records tolerance=0.001", REQUIREMENTS, source=SOURCE)

    def add(case_id, req, title, lines, source=SOURCE):
        cases.add(case_id, req, title, lines, [answer(l, req) for l in lines], source=source)

    # R1 - monotone curves
    add("15-R1-rising", "R1", "curves that only rise: the minimum is p1's y", [
        "curve 0 0 5 2 10 10",
        "curve 0 10 50 30 100 35",
    ])
    add("15-R1-falling", "R1", "curves that only fall: the minimum is p3's y", [
        "curve 0 20 5 4 10 -3",
        "curve 0 100 50 90 100 0",
    ])
    add("15-R1-turning-at-an-end", "R1", "the turning point is exactly at t = 0 or t = 1", [
        "curve 0 0 5 0 10 10",
        "curve 0 10 5 0 10 0",
    ])

    # R2 - a valley inside
    add("15-R2-symmetric", "R2", "a symmetric valley: lowest at t = 0.5", ["curve 0 10 5 -10 10 10"])
    add("15-R2-asymmetric", "R2", "a lopsided valley: lowest at t = 0.625, y = -1.25", ["curve 0 30 40 -20 100 10"])
    add("15-R2-fractional", "R2", "minima that aren't whole numbers", [
        "curve 0 7 3 -4 6 2",
        "curve 152 -180 152 -260 300 -250",
        "curve 0 0 5 -1 10 10",
    ])

    # R3 - turning point outside [0, 1]
    add("15-R3-before-start", "R3", "turning point at t = -0.5 (y = -0.5 there, off the curve)",
        ["curve 0 0 5 1 10 4"])
    add("15-R3-after-end", "R3", "turning point at t = 1.5 (y = -5 there, off the curve)",
        ["curve 0 40 50 10 100 0"])
    add("15-R3-far", "R3", "turning points at t = 2, far beyond the end", [
        "curve 0 300 10 100 20 0",
        "curve 0 -50 10 -70 20 -80",
    ])

    # R4 - straight and flat
    add("15-R4-straight", "R4", "straight curves: the control point's y is halfway (a = 0)", [
        "curve 0 10 5 5 10 0",
        "curve 0 -3 5 2 10 7",
        "curve 0 2.5 4 5 8 7.5",
        "curve 5 0 5 50 5 100",
    ])
    add("15-R4-flat", "R4", "flat curves: all three y equal (a = b = 0)", [
        "curve 0 7 5 7 10 7",
        "curve -20 -3.5 0 -3.5 40 -3.5",
        "curve 0 0 50 0 100 0",
    ])

    # R5 - hills
    add("15-R5-hill", "R5", "curves that bulge upward: the turning point is the highest point", [
        "curve 0 0 5 10 10 4",
        "curve 0 6 5 20 10 2",
    ])
    add("15-R5-symmetric", "R5", "a symmetric arch: highest at t = 0.5, lowest at both ends", ["curve 0 0 50 100 100 0"])
    add("15-R5-negative", "R5", "a hill below zero", ["curve -10 -40 0 -10 10 -30"])

    # Random cases aimed at R2, R3 and R5, then anything
    def rcurve():
        return [(F(rng.randint(-200, 200)), F(rng.randint(-200, 200))) for _ in range(3)]

    def collect(count, want):
        lines = []
        while len(lines) < count:
            c = rcurve()
            kind, t = kind_of(c[0][1], c[1][1], c[2][1])
            if want(kind, t):
                lines.append(curve_line(*c))
        return lines

    add(f"15-R2-random-s{args.seed}", "R2", f"10 random valleys with the turning point inside (seed {args.seed})",
        collect(10, lambda kind, t: kind == "valley-inside"))
    add(f"15-R3-random-s{args.seed}", "R3", f"10 random valleys with the turning point outside (seed {args.seed})",
        collect(10, lambda kind, t: kind == "valley-outside" and (t < 0 or t > 1)))
    add(f"15-R5-random-s{args.seed}", "R5", f"10 random hills (seed {args.seed})",
        collect(10, lambda kind, t: kind == "hill" and 0 < t < 1))
    add(f"15-E2E-random-s{args.seed}", "E2E", f"25 random curves of every kind (seed {args.seed})",
        collect(25, lambda kind, t: True))

    # End to end - every curve of real glyphs
    for font_rel, char, label in ((wb.JETBRAINS, "o", "JetBrains Mono Bold"),
                                  (wb.JETBRAINS, "S", "JetBrains Mono Bold"),
                                  (wb.NOTO_JP, "あ", "Noto Sans JP")):
        name, curves = font_curves(font_rel, char)
        add(f"15-E2E-curves-U+{ord(char):04X}", "E2E",
            f"U+{ord(char):04X} ({name}, {label}): each of its {len(curves)} curves, in font units (y up)",
            [curve_line(*c) for c in curves], source=FONT_SOURCE)
    # The way a renderer sees them: scaled to pixels and flipped so that y points down.
    name, curves = font_curves(wb.JETBRAINS, "S")
    flip = [tuple((x / 8 + 10, (800 - y) / 8) for x, y in c) for c in curves]
    add("15-E2E-screen-S", "E2E", f"'S' ({name}) scaled by 1/8 and flipped so y points down, as on screen",
        [curve_line(*c) for c in flip], source=FONT_SOURCE)

    cases.save()


if __name__ == "__main__":
    main()
