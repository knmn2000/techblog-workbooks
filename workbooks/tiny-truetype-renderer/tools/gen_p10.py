"""Test cases for checkpoint 10 (lerp and quadratic Bezier curves).

Expected outputs use exact fractions.Fraction arithmetic. Curve points come from
the expanded (Bernstein) formula, which is a different route from the nested
lerps the reference uses; the script also checks that both routes agree exactly.

    py -P tools/gen_p10.py                                  # tests/10 (seed 1)
    py -P tools/gen_p10.py --seed 777 --out build/fresh/10  # what `.\\check 10 -Fresh` runs
"""

import random
import sys
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402
from fontTools.pens.basePen import BasePen  # noqa: E402

SOURCE = "exact arithmetic with Python fractions.Fraction"
FONT_SOURCE = f"outline read by {wb.FT}, points computed with fractions.Fraction"

REQUIREMENTS = [
    ("R1", "lerp: the point a fraction t of the way from a to b"),
    ("R2", "bezier: the point at t on the curve from a to c, which bends toward b"),
    ("R3", "Exact endpoints: t = 0 gives the start, t = 1 the end (not the control point)"),
    ("R4", "Negative and fractional coordinates and t"),
    ("E2E", "Real curves from JetBrains Mono Bold and Noto Sans JP, and random inputs"),
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


def lerp(a, b, t):
    return tuple(p + (q - p) * t for p, q in zip(a, b))


def bernstein(a, b, c, t):
    """(1-t)^2 a + 2(1-t)t b + t^2 c, exactly."""
    s = 1 - t
    return tuple(s * s * p + 2 * s * t * q + t * t * r for p, q, r in zip(a, b, c))


def answer(line: str) -> str:
    """The expected output line for one input line, computed exactly."""
    words = line.split()
    nums = [F(w) for w in words[1:]]  # decimal text -> exact value
    # The limits promised on the problem page.
    assert all(abs(n) <= 1000 and (n * 10 ** 4).denominator == 1 for n in nums), line
    t = nums[-1]
    assert 0 <= t <= 1, line
    if words[0] == "lerp":
        assert len(nums) == 5, line
        x, y = lerp(nums[0:2], nums[2:4], t)
    else:
        assert words[0] == "bezier" and len(nums) == 7, line
        a, b, c = nums[0:2], nums[2:4], nums[4:6]
        x, y = bernstein(a, b, c, t)
        # Same point by de Casteljau's construction (a sanity check of the maths itself).
        assert (x, y) == lerp(lerp(a, b, t), lerp(b, c, t), t)
        if t == 0:
            assert (x, y) == tuple(a)
        if t == 1:
            assert (x, y) == tuple(c)
    return f"{wb.num(x)} {wb.num(y)}"


def lerp_line(a, b, t):
    return "lerp " + " ".join(dec(v) for v in (*a, *b, t))


def bezier_line(a, b, c, t):
    return "bezier " + " ".join(dec(v) for v in (*a, *b, *c, t))


# ---- Font outlines ------------------------------------------------------------------

class SegmentPen(BasePen):
    """Collects an outline as straight lines and single quadratic curves. fontTools'
    BasePen inserts the implied on-curve point between two off-curve points."""

    def __init__(self):
        super().__init__(None)
        self.items = []
        self.start = None

    def _moveTo(self, pt):
        self.start = pt

    def _lineTo(self, pt):
        self.items.append(("line", self._getCurrentPoint(), pt))

    def _qCurveToOne(self, pt1, pt2):
        self.items.append(("curve", self._getCurrentPoint(), pt1, pt2))

    def _curveToOne(self, pt1, pt2, pt3):
        raise AssertionError("TrueType outlines have no cubic curves")

    def _closePath(self):
        if self._getCurrentPoint() != self.start:
            self.items.append(("line", self._getCurrentPoint(), self.start))


def font_segments(font_rel: str, char: str):
    font = wb.load(font_rel)
    name = font.getBestCmap()[ord(char)]
    ends, points = wb.outline_of(font, name)
    pen = SegmentPen()
    wb.draw_outline(pen, ends, points)
    return name, [(kind, *[(F(x), F(y)) for x, y in pts]) for kind, *pts in pen.items]


# ---- Cases ------------------------------------------------------------------------------

def main():
    args = wb.parse_args("10")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "records tolerance=0.001", REQUIREMENTS, source=SOURCE)

    def add(case_id, req, title, lines, source=SOURCE):
        cases.add(case_id, req, title, lines, [answer(l) for l in lines], source=source)

    # R1 - lerp
    add("10-R1-midpoint", "R1", "lerp at t = 0.5 is the midpoint", [
        "lerp 0 0 10 20 0.5",
        "lerp 2 3 8 3 0.5",
        "lerp 100 40 20 0 0.5",
    ])
    add("10-R1-quarters", "R1", "lerp at t = 0.25, 0.5, 0.75 along one segment", [
        "lerp 0 0 100 40 0.25",
        "lerp 0 0 100 40 0.5",
        "lerp 0 0 100 40 0.75",
    ])
    add("10-R1-direction", "R1", "lerp measures t from a, so swapping a and b changes the answer", [
        "lerp 10 20 50 100 0.25",
        "lerp 50 100 10 20 0.25",
        "lerp 10 20 50 100 0.9",
        "lerp 50 100 10 20 0.9",
    ])
    add("10-R1-axis-aligned", "R1", "lerp along horizontal and vertical segments", [
        "lerp 0 7 200 7 0.3",
        "lerp 7 0 7 200 0.3",
        "lerp 300 50 100 50 0.6",
        "lerp 50 300 50 100 0.6",
    ])
    add("10-R1-same-point", "R1", "lerp between a point and itself stays put", [
        "lerp 42 17 42 17 0.4",
        "lerp 42 17 42 17 1",
    ])

    # R2 - quadratic Bezier
    add("10-R2-midpoint", "R2", "an arch from (0,0) to (100,0) pulled toward (50,100): t = 0.5",
        ["bezier 0 0 50 100 100 0 0.5"])
    add("10-R2-quarters", "R2", "the same arch at t = 0.25 and 0.75 (never reaches the control point)", [
        "bezier 0 0 50 100 100 0 0.25",
        "bezier 0 0 50 100 100 0 0.75",
    ])
    add("10-R2-asymmetric", "R2", "a lopsided curve with the control point off to one side", [
        f"bezier 0 0 80 60 20 100 {dec(F(k, 10))}" for k in range(1, 10)
    ])
    add("10-R2-sampled", "R2", "one curve sampled at 11 evenly spaced t, as a drawing loop would", [
        f"bezier 10 200 150 20 300 180 {dec(F(k, 10))}" for k in range(11)
    ])
    add("10-R2-order-matters", "R2", "the same three points with the control point in each position", [
        "bezier 0 0 100 0 100 100 0.5",
        "bezier 100 0 0 0 100 100 0.5",
        "bezier 0 0 100 100 100 0 0.5",
    ])
    add("10-R2-straight", "R2", "a control point on the line between a and c gives a straight curve", [
        "bezier 0 0 50 50 100 100 0.25",
        "bezier 0 0 10 10 100 100 0.25",
    ])

    # R3 - endpoints
    add("10-R3-curve-endpoints", "R3", "bezier at t = 0 and t = 1 returns a and c exactly", [
        "bezier 3 4 50 100 97 8 0",
        "bezier 3 4 50 100 97 8 1",
        "bezier 300 -20 -40 75 12 600 0",
        "bezier 300 -20 -40 75 12 600 1",
    ])
    add("10-R3-control-not-on-curve", "R3", "t = 1 ends at c, not at the control point b", [
        "bezier 0 0 0 100 100 100 1",
        "bezier 0 0 0 100 100 100 0.5",
    ])
    add("10-R3-lerp-endpoints", "R3", "lerp at t = 0 and t = 1 returns a and b exactly", [
        "lerp 12 34 56 78 0",
        "lerp 12 34 56 78 1",
        "lerp -5.5 0.25 9 -3 0",
        "lerp -5.5 0.25 9 -3 1",
    ])

    # R4 - negative and fractional values
    add("10-R4-negative", "R4", "negative coordinates", [
        "lerp -10 -20 -30 -60 0.25",
        "lerp -100 50 100 -50 0.75",
        "bezier -50 -50 0 -150 50 -50 0.5",
        "bezier -200 10 -10 -90 -120 -300 0.3",
    ])
    add("10-R4-fractional", "R4", "fractional coordinates and t", [
        "lerp 0.5 1.25 3.75 -2.5 0.125",
        "lerp 12.5 7.75 -3.25 0.5 0.3",
        "bezier 0.5 0.5 2.25 4.75 6.125 0.375 0.6",
        "bezier 301.5 -76.5 351 -76 399 -29.5 0.05",
    ])
    add("10-R4-crossing-origin", "R4", "a curve that runs from one quadrant into the opposite one", [
        f"bezier -60 40 10 -90 70 -30 {dec(F(k, 8))}" for k in range(0, 9, 2)
    ])
    lines = []
    for _ in range(12):
        a = (F(rng.randint(-4000, 4000), 8), F(rng.randint(-4000, 4000), 8))
        b = (F(rng.randint(-4000, 4000), 8), F(rng.randint(-4000, 4000), 8))
        c = (F(rng.randint(-4000, 4000), 8), F(rng.randint(-4000, 4000), 8))
        t = F(rng.randint(0, 1000), 1000)
        lines.append(lerp_line(a, b, t) if rng.random() < 0.4 else bezier_line(a, b, c, t))
    add(f"10-R4-random-s{args.seed}", "R4", f"random negative and fractional values (seed {args.seed})", lines)

    # Random positive integer inputs for R1 and R2
    lines = [lerp_line((rng.randint(0, 1000), rng.randint(0, 1000)), (rng.randint(0, 1000), rng.randint(0, 1000)),
                       F(rng.randint(0, 100), 100)) for _ in range(15)]
    add(f"10-R1-random-s{args.seed}", "R1", f"15 random lerps (seed {args.seed})", lines)
    lines = [bezier_line(*[(rng.randint(0, 1000), rng.randint(0, 1000)) for _ in range(3)],
                         F(rng.randint(0, 100), 100)) for _ in range(15)]
    add(f"10-R2-random-s{args.seed}", "R2", f"15 random curve points (seed {args.seed})", lines)

    # End to end - the midpoint of every piece of real outlines
    for font_rel, char, label in ((wb.JETBRAINS, "S", "JetBrains Mono Bold"),
                                  (wb.JETBRAINS, "o", "JetBrains Mono Bold"),
                                  (wb.NOTO_JP, "あ", "Noto Sans JP")):
        name, segs = font_segments(font_rel, char)
        lines = [lerp_line(s[1], s[2], F(1, 2)) if s[0] == "line" else bezier_line(s[1], s[2], s[3], F(1, 2))
                 for s in segs]
        curves = sum(s[0] == "curve" for s in segs)
        add(f"10-E2E-midpoints-U+{ord(char):04X}", "E2E",
            f"U+{ord(char):04X} ({name}, {label}): the midpoint of each of its {len(segs) - curves} lines "
            f"and {curves} curves", lines, source=FONT_SOURCE)
    name, segs = font_segments(wb.JETBRAINS, "3")
    curve = next(s for s in segs if s[0] == "curve" and len({s[1][0], s[2][0], s[3][0]}) == 3)
    add("10-E2E-flatten-three", "E2E", f"one curve of '3' ({name}) cut into 16 short steps, as a renderer would",
        [bezier_line(curve[1], curve[2], curve[3], F(k, 16)) for k in range(17)], source=FONT_SOURCE)

    cases.save()


if __name__ == "__main__":
    main()
