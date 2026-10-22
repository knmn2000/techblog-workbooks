"""Test cases for checkpoint 11 (draw an outline with curves).

Outlines come from fontTools (JetBrains Mono Bold, including Nerd Font icons whose
contours start off-curve or have no on-curve point at all, and Noto Sans JP) or are
made here. The reference program draws each expected picture. Before a picture is
written, this script checks it against fontTools' own reading of the outline: the
outline goes through fontTools' PointToSegmentPen and BasePen, which split it into
straight lines and quadratic pieces and work out the implied on-curve points. The
picture must have ink along every piece (sampled on the true curve), a red, green or
blue marker on every on-curve, off-curve and implied point, and no ink anywhere else.

It also draws every outline in Python from fontTools' pieces in a few other ways a
correct program may choose (rounding the points to pixels before working out curves
and implied points, more pieces per curve, truncating instead of rounding along a
line) and keeps a case only if each of those passes the checker too.

    py -P tools/gen_p11.py --ref build/ref/assignment_11                        # tests/11 (seed 1)
    py -P tools/gen_p11.py --seed 77 --out build/fresh/11             # what `.\\check 11 -Fresh` runs
"""

import math
import random
import struct
import sys
import tempfile
from pathlib import Path

from fontTools.pens.basePen import BasePen

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inkcheck  # noqa: E402
import wb  # noqa: E402
from imageio import compare_images, write_png  # noqa: E402

REQUIREMENTS = [
    ("R1", "Straight line between two on-curve neighbours"),
    ("R2", "Quadratic curve for an off-curve point between two on-curve points"),
    ("R3", "Two off-curve points in a row: implied on-curve point halfway (blue)"),
    ("R4", "Contours that start off-curve, or have no on-curve point at all"),
    ("R5", "Markers: 2 x thickness squares, red on, green off, blue implied, over the lines"),
    ("R6", "Placement and scale; several outlines on one canvas"),
    ("E2E", "Glyphs from JetBrains Mono Bold and Noto Sans JP, and random outlines"),
]
COMPARE = "image band=1 allow=0"
EXPLAIN = ""  # the checker then names the requirement the failing case targets
SOURCE = "reference drawing, checked against fontTools' pieces and implied points"

RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
WHITE, YELLOW, CYAN, GRAY = (255, 255, 255), (255, 220, 0), (0, 220, 220), (160, 160, 160)

# Hand-made outlines: lists of contours, each a list of (x, y, on).
STAR = [[(250 + round(r * math.sin(k * math.pi / 5)), 250 + round(r * math.cos(k * math.pi / 5)), 1)
         for k, r in enumerate([240, 100] * 5)]]
LENS = [[(0, 0, 1), (250, 300, 0), (500, 0, 1), (250, -300, 0)]]
PILLOW = [[(0, 0, 1), (200, -80, 0), (400, 0, 1), (480, 200, 0), (400, 400, 1), (200, 480, 0), (0, 400, 1),
           (-80, 200, 0)]]
TWO_OFFS = [[(0, 0, 1), (0, 400, 0), (400, 400, 0), (400, 0, 1)]]
RUN_OF_OFFS = [[(0, 0, 1), (-100, 150, 0), (50, 350, 0), (300, 380, 0), (450, 200, 0), (400, 0, 1)]]
CIRCLE4 = [[(0, 0, 0), (0, 400, 0), (400, 400, 0), (400, 0, 0)]]
OFF_FIRST = [[(300, 0, 0), (400, 200, 1), (200, 300, 1), (0, 100, 0)]]
FRACTIONAL = [[(10.5, 0.25, 1), (120.75, -40.5, 0), (230.25, 10.75, 1), (200.5, 150.5, 0), (90.25, 170.125, 0)],
              [(80.5, 50.5, 0), (150.25, 60.75, 0), (110.5, 120.25, 0)]]


def split(contours):
    ends, points = [], []
    for c in contours:
        points += c
        ends.append(len(points) - 1)
    return ends, points


class Pieces(BasePen):
    """Collects the straight lines and quadratic pieces fontTools makes of an outline.
    BasePen splits a run of off-curve points at the implied on-curve points between them,
    including the special case of a contour with no on-curve point."""

    def __init__(self):
        super().__init__(glyphSet=None)
        self.lines, self.quads, self.ends = [], [], []
        self.start = self.cur = None

    def _moveTo(self, p):
        self.start = self.cur = p
        self.ends.append(p)

    def _lineTo(self, p):
        self.lines.append((self.cur, p))
        self.cur = p
        self.ends.append(p)

    def _qCurveToOne(self, c, p):
        self.quads.append((self.cur, c, p))
        self.cur = p
        self.ends.append(p)

    def _curveToOne(self, c1, c2, p):
        raise AssertionError("TrueType outlines have no cubic curves")

    def _closePath(self):
        if self.cur != self.start:
            self.lines.append((self.cur, self.start))


class Item:
    """One outline as the input describes it, and what fontTools says it looks like."""

    def __init__(self, ends, points, x0, baseline, scale, thickness, color):
        self.x0, self.baseline, self.scale = (float(wb.num(v)) for v in (x0, baseline, scale))
        self.ends, self.points = list(ends), [(float(wb.num(x)), float(wb.num(y)), on) for x, y, on in points]
        self.thickness, self.color = thickness, color
        pen = Pieces()
        wb.draw_outline(pen, self.ends, self.points)
        on_points = {(x, y) for x, y, on in self.points if on}
        self.implied = sorted({p for p in pen.ends if p not in on_points})
        self.lines, self.quads = pen.lines, pen.quads

    def lines_in(self):
        return [f"place {wb.num(self.x0)} {wb.num(self.baseline)} {wb.num(self.scale)}",
                f"style {self.thickness}", "color {} {} {}".format(*self.color),
                *wb.outline_lines(self.ends, self.points)]

    def px(self, p):
        return self.x0 + self.scale * p[0], self.baseline - self.scale * p[1]

    def rpx(self, p):
        x, y = self.px(p)
        return inkcheck.rounded(x), inkcheck.rounded(y)

    def markers(self):
        """(centre pixel, colour) of every marker."""
        return ([(self.rpx(p), RED if p[2] else GREEN) for p in self.points]
                + [(self.rpx(p), BLUE) for p in self.implied])

    def box(self):
        cs = [c for c, _ in self.markers()]
        pad = self.thickness + 2
        return (min(x for x, _ in cs) - pad, min(y for _, y in cs) - pad,
                max(x for x, _ in cs) + pad, max(y for _, y in cs) + pad)


def square_offsets(size):
    lo, hi = -(size // 2), size - 1 - size // 2
    return [(ox, oy) for ox in {lo, 0, hi} for oy in {lo, 0, hi}]


def boxes_meet(a, b):
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def marker_clash(item):
    """Two markers of different colours that overlap (then their order would matter), or None."""
    t = item.thickness
    ms = item.markers()
    for i, ((ax, ay), ac) in enumerate(ms):
        for (bx, by), bc in ms[i + 1:]:
            if ac != bc and boxes_meet((ax - t, ay - t, ax + t - 1, ay + t - 1), (bx - t, by - t, bx + t - 1, by + t - 1)):
                return (ax, ay), (bx, by)
    return None


def check_picture(pic, w, h, items):
    """None if the picture is exactly fontTools' outline drawn per the spec (within a pixel)."""
    if (pic.w, pic.h) != (w, h):
        return f"picture is {pic.w}x{pic.h}, expected {w}x{h}"
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if boxes_meet(a.box(), b.box()):
                return "two outlines overlap; move them apart"
    allowed, musts = {}, []
    for it in items:
        t = it.thickness
        markers = it.markers()
        line_region = allowed.setdefault(it.color, inkcheck.Region(w, h))
        under_marker = inkcheck.Region(w, h)  # where markers hide the lines
        for (x, y), c in markers:
            allowed.setdefault(c, inkcheck.Region(w, h)).around(x, y, t + 1.5)
            under_marker.around(x, y, t + 1.5)
            musts += [(x + ox, y + oy, c, f"marker at ({x}, {y})") for ox, oy in square_offsets(2 * t)]
        paths = [[it.rpx(a), it.rpx(b)] for a, b in it.lines]
        paths += [inkcheck.quad_samples(it.px(a), it.px(c), it.px(b)) for a, c, b in it.quads]
        for path in paths:
            line_region.along(path, t / 2 + 1.5)
            for a, b in zip(path, path[1:]):
                for sx, sy in inkcheck.segment_samples(a, b):
                    if not under_marker.touches(inkcheck.rounded(sx), inkcheck.rounded(sy), 1):
                        musts += [(sx + ox, sy + oy, it.color, "line or curve") for ox, oy in square_offsets(t)]
    stray = inkcheck.stray_ink(pic, allowed)
    if stray:
        return f"ink at ({stray[0]}, {stray[1]}) in {stray[2]} that no piece or marker explains"
    for x, y, color, what in musts:
        if pic.inside(inkcheck.rounded(x), inkcheck.rounded(y)) and not pic.near(x, y, color, 1):
            return f"no {color} ink near ({x:g}, {y:g}) for the {what}"
    return None


# ---- Other correct drawings, to make sure the tests accept them ------------------

def f32(v: float) -> float:
    """v as a C float (Canvas::drawLine takes floats)."""
    return struct.unpack("f", struct.pack("f", v))[0]


class Raster:
    """Canvas.h's drawRect and drawLine in Python, with a choice of rounding along a line."""

    def __init__(self, w, h, minor):
        self.w, self.h, self.minor = w, h, minor
        self.buf = bytearray(3 * w * h)

    def rect(self, cx, cy, size, c):
        left, top = cx - size // 2, cy - size // 2
        x0, x1 = max(left, 0), min(left + size, self.w)
        if x0 < x1:
            for y in range(max(top, 0), min(top + size, self.h)):
                self.buf[3 * (y * self.w + x0):3 * (y * self.w + x1)] = bytes(c) * (x1 - x0)

    def line(self, a, b, t, c):
        ax, ay, bx, by = (inkcheck.rounded(f32(v)) for v in (*a, *b))
        steep = abs(by - ay) > abs(bx - ax)
        if steep:
            ax, ay, bx, by = ay, ax, by, bx
        if ax > bx:
            ax, ay, bx, by = bx, by, ax, ay
        slope = 0 if bx == ax else (by - ay) / (bx - ax)
        for x in range(ax, bx + 1):
            y = self.minor(ay + slope * (x - ax))
            self.rect(*((y, x) if steep else (x, y)), t, c)


def draw_variant(w, h, items, round_points=False, pieces_per_px=1, minor=inkcheck.rounded) -> bytes:
    raster = Raster(w, h, minor)
    markers = []
    for it in items:
        t = it.thickness
        # The outline in pixels; fontTools splits it into pieces and finds the implied points.
        pts = [(*(it.rpx(p) if round_points else it.px(p)), p[2]) for p in it.points]
        pen = Pieces()
        wb.draw_outline(pen, it.ends, pts)
        for a, b in pen.lines:
            raster.line(a, b, t, it.color)
        for p0, p1, p2 in pen.quads:
            n = max(1, math.ceil(pieces_per_px * (math.dist(p0, p1) + math.dist(p1, p2))))
            prev = p0
            for i in range(1, n + 1):
                u, v = 1 - i / n, i / n
                nxt = (u * u * p0[0] + 2 * u * v * p1[0] + v * v * p2[0], u * u * p0[1] + 2 * u * v * p1[1] + v * v * p2[1])
                raster.line(prev, nxt, t, it.color)
                prev = nxt
        on_points = {(x, y) for x, y, on in pts if on}
        markers += [((x, y), 2 * t, RED if on else GREEN) for x, y, on in pts]
        markers += [(p, 2 * t, BLUE) for p in sorted({e for e in pen.ends if e not in on_points})]
    for (x, y), size, c in markers:
        raster.rect(inkcheck.rounded(x), inkcheck.rounded(y), size, c)
    return bytes(raster.buf)


VARIANTS = {
    "the spec, in Python": {},
    "points rounded to pixels first": {"round_points": True},
    "twice as many pieces per curve": {"pieces_per_px": 2},
    "truncating along a line": {"minor": int},
}


def failing_variant(expected: Path, w, h, items):
    """The first of VARIANTS that the checker would reject, as (name, message), or None."""
    band, allow = (float(part.split("=")[1]) for part in COMPARE.split()[1:])
    with tempfile.TemporaryDirectory() as tmp:
        actual = Path(tmp) / "variant.png"
        for name, options in VARIANTS.items():
            write_png(actual, w, h, draw_variant(w, h, items, **options))
            problem, _ = compare_images(expected, actual, Path(tmp) / "diff.png", band=int(band), allow=allow)
            if problem:
                return name, problem.split(" (beyond")[0]
    return None


def fit(outline, scale, margin):
    ends, points = outline if isinstance(outline, tuple) else split(outline)
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    x0 = round(margin - scale * min(xs))
    baseline = round(margin + scale * max(ys))
    return ends, points, x0, baseline, math.ceil(x0 + scale * max(xs) + margin), math.ceil(baseline - scale * min(ys) + margin)


def random_outline(rng):
    contours = []
    for _ in range(rng.randint(1, 3)):
        cx, cy, r = rng.randint(200, 800), rng.randint(200, 800), rng.randint(120, 320)
        n = rng.randint(3, 9)
        all_off = rng.random() < 0.25
        pts = []
        for k in range(n):
            a = 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
            rr = r * rng.uniform(0.5, 1.1)
            on = 0 if all_off else int(rng.random() < 0.45)
            pts.append((round(cx + rr * math.cos(a)), round(cy + rr * math.sin(a)), on))
        contours.append(pts)
    return split(contours)


def main():
    args = wb.parse_args("11")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, EXPLAIN)
    jb, noto = wb.load(wb.JETBRAINS), wb.load(wb.NOTO_JP)
    fragile = []  # hand-picked cases where one of VARIANTS would fail; pick another scale or thickness

    def glyph(font, ch):
        return wb.outline_of(font, font.getBestCmap()[ord(ch)])

    def picture(case_id, req, title, w, h, items, source=SOURCE, retry=False):
        assert w <= 620 and h <= 620, f"{case_id}: canvas {w}x{h} is too big for the checker"
        for it in items:
            clash = marker_clash(it)
            if clash:
                assert retry, f"{case_id}: markers of different colours overlap at {clash}; change the scale"
                return False
        lines = [f"canvas {w} {h}"] + [line for it in items for line in it.lines_in()]
        path = cases.image_path(case_id)
        wb.run_reference(args.ref, lines, path)
        pic = inkcheck.Picture(path)
        problem = check_picture(pic, w, h, items)
        assert problem is None, f"{case_id}: the reference picture is wrong: {problem}"
        pic.save(path)
        failing = failing_variant(path, w, h, items)
        if failing:
            path.unlink()
            if not retry:  # a hand-picked case: report it with the others, then stop
                fragile.append(f"{case_id}: a correct drawing ({failing[0]}) would fail: {failing[1]}")
            return False
        cases.add(case_id, req, title, lines, expected_file=path, source=source)
        return True

    def single(case_id, req, title, outline, scale, thickness, color=WHITE, source=SOURCE, retry=False):
        ends, points, x0, baseline, w, h = fit(outline, scale, 2 * thickness + 6)
        return picture(case_id, req, title, w, h, [Item(ends, points, x0, baseline, scale, thickness, color)],
                       source=source, retry=retry)

    hand = "hand-made outline; " + SOURCE

    # R1 - straight lines
    single("11-R1-hyphen", "R1", "'-' (JetBrains Mono Bold) at scale 1: four on-curve points, four lines",
           glyph(jb, "-"), 1, 2)
    single("11-R1-star", "R1", "hand-made star: ten on-curve points", STAR, 0.9, 3, YELLOW, source=hand)

    # R2 - curves between on-curve points
    single("11-R2-lens", "R2", "hand-made lens: on, off, on, off - two curves", LENS, 0.8, 2, source=hand)
    single("11-R2-pillow", "R2", "hand-made pillow: every side bulges through one off-curve point", PILLOW, 0.8, 3,
           CYAN, source=hand)
    single("11-R2-D", "R2", "'D' (JetBrains Mono Bold): straight sides and round curves", glyph(jb, "D"), 0.6, 2)

    # R3 - implied on-curve points
    single("11-R3-two-offs", "R3", "hand-made: two off-curve points in a row, implied point between them",
           TWO_OFFS, 0.8, 3, source=hand)
    single("11-R3-run", "R3", "hand-made: four off-curve points in a row, three implied points", RUN_OF_OFFS, 0.8,
           2, YELLOW, source=hand)
    single("11-R3-o", "R3", "'o': both contours are mostly off-curve pairs", glyph(jb, "o"), 0.7, 2)
    single("11-R3-S", "R3", "'S': one contour, many implied points", glyph(jb, "S"), 0.6, 2, CYAN)

    # R4 - contours that start off-curve
    single("11-R4-circle4", "R4", "hand-made: four off-curve points and nothing else make a circle", CIRCLE4, 0.8,
           3, source=hand)
    single("11-R4-off-first", "R4", "hand-made: the contour starts and ends with off-curve points", OFF_FIRST, 0.9,
           3, YELLOW, source=hand)
    icons = [(0xF111, "fa-circle (U+F111): one contour of 8 off-curve points", 0.45, 3),
             (0xF10C, "fa-circle_o (U+F10C): a ring, two contours without on-curve points", 0.45, 2),
             (0xE3A2, "weather-moon_third_quarter (U+E3A2): starts with 4 off-curve points", 0.6, 2),
             (0xF00C, "fa-check (U+F00C): starts with 3 off-curve points", 0.5, 2),
             (0xF042, "fa-circle_half_stroke (U+F042): one contour starts off-curve, one has no on-curve point",
              0.45, 2)]
    for cp, title, scale, t in icons:
        single(f"11-R4-U+{cp:04X}", "R4", title, wb.outline_of(jb, jb.getBestCmap()[cp]), scale, t)

    # R5 - markers
    single("11-R5-big-markers", "R5", "'a' with 5 px lines, so 10 px markers in all three colours", glyph(jb, "a"),
           0.7, 5, GRAY)
    single("11-R5-thin", "R5", "'B' with 1 px lines and 2 px markers", glyph(jb, "B"), 0.5, 1, YELLOW)

    # R6 - placement, scale, several outlines
    single("11-R6-noto-a", "R6", "'a' from Noto Sans JP at scale 0.6: another font's curves", glyph(noto, "a"), 0.6, 2)
    ends, points = glyph(jb, "g")
    picture("11-R6-g-offset", "R6", "'g' with x0 = 120 and the baseline at 240: the descender hangs below it",
            400, 340, [Item(ends, points, 120, 240, 0.4, 2, CYAN)])
    (eo, po), (et, pt) = glyph(jb, "o"), glyph(noto, "十")
    picture("11-R6-two", "R6", "'o' then U+5341 (Noto Sans JP): two outlines, each with its own place and colour",
            520, 300, [Item(eo, po, 0, 230, 0.4, 2, YELLOW), Item(et, pt, 250, 255, 0.27, 3, WHITE)])
    single("11-R6-fractional", "R6", "hand-made curves whose coordinates aren't whole numbers, at scale 1.5",
           FRACTIONAL, 1.5, 2, source=hand)

    # E2E - the blog's demo (halved to fit) and random outlines
    ends, points = glyph(jb, "a")
    picture("11-E2E-blog-a", "E2E", "the blog's demo, at half size: 'a' on 600x600 with 3 px lines", 600, 600,
            [Item(ends, points, 150, 450, 0.5, 3, WHITE)])
    single("11-E2E-A", "E2E", "'A' (JetBrains Mono Bold)", glyph(jb, "A"), 0.5, 2)
    k = 0
    while k < 3:
        ends, points = random_outline(rng)
        scale, t = rng.choice([0.3, 0.4, 0.5]), rng.choice([1, 2, 3])
        if single(f"11-E2E-random-s{args.seed}-{k}", "E2E",
                  f"random outline #{k} (seed {args.seed}): {len(ends)} contours, {len(points)} points",
                  (ends, points), scale, t, rng.choice([WHITE, YELLOW, CYAN, GRAY]),
                  source="random outline; " + SOURCE, retry=True):
            k += 1

    if fragile:
        sys.exit("\n".join(fragile))
    cases.save()


if __name__ == "__main__":
    main()
