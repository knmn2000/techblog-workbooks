"""Test cases for checkpoint 08 (draw an outline with straight lines).

Outlines come from fontTools (JetBrains Mono Bold and Noto Sans JP) or are made here.
The reference program draws each expected picture. Before a picture is written, this
script checks it against the ideal drawing worked out here from the spec: every
segment between consecutive (rounded) points, the closing one included, must have ink
along it at both edges of its thickness; every point must have its full marker; and
no ink may lie further than half a line or marker (+1.5 px) from those shapes.

    py -P tools/gen_p08.py --ref build/ref/assignment_08                        # tests/08 (seed 1)
    py -P tools/gen_p08.py --seed 77 --out build/fresh/08             # what `.\\check 08 -Fresh` runs
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inkcheck  # noqa: E402
import wb  # noqa: E402

REQUIREMENTS = [
    ("R1", "Placement: pixel = (x0 + scale*x, baseline - scale*y), rounded; y grows up"),
    ("R2", "Every contour is closed: its last point joins its first"),
    ("R3", "Contours are separate: no line from one contour to the next"),
    ("R4", "A markerSize square on every point, on- and off-curve alike"),
    ("R5", "Several outlines, each with its own place, style and color"),
    ("R6", "Scale, including coordinates that aren't whole numbers"),
    ("E2E", "Glyphs from JetBrains Mono Bold and Noto Sans JP, and random outlines"),
]
EXPLAIN = ""  # the checker then names the requirement the failing case targets
SOURCE = "reference drawing, checked against the ideal segments and markers worked out from the spec"

WHITE, YELLOW, CYAN, PINK, LIME = (255, 255, 255), (255, 220, 0), (0, 220, 220), (255, 120, 170), (150, 255, 80)

# Hand-made outlines: lists of contours, each a list of (x, y, on).
FLAG = [[(0, -150, 1), (0, 450, 1), (300, 360, 1), (60, 270, 1), (60, -150, 1)]]  # points up and right
TRIANGLE = [[(0, 0, 1), (500, 0, 1), (130, 400, 0)]]
FRACTIONAL = [[(10.25, 0.5, 1), (200.75, 20.25, 1), (180.5, 150.75, 0), (40.125, 170.5, 1)],
              [(90.5, 60.25, 1), (130.75, 70.5, 1), (110.25, 110.125, 1)]]


def split(contours):
    """(ends, points) for a list of contours."""
    ends, points = [], []
    for c in contours:
        points += c
        ends.append(len(points) - 1)
    return ends, points


class Item:
    """One outline as the input describes it: placement, style, colour and points."""

    def __init__(self, ends, points, x0, baseline, scale, thickness, marker, color):
        # Through the same text the program reads, so both sides use identical numbers.
        self.x0, self.baseline, self.scale = (float(wb.num(v)) for v in (x0, baseline, scale))
        self.ends, self.points = list(ends), [(float(wb.num(x)), float(wb.num(y)), on) for x, y, on in points]
        self.thickness, self.marker, self.color = thickness, marker, color

    def lines(self):
        return [f"place {wb.num(self.x0)} {wb.num(self.baseline)} {wb.num(self.scale)}",
                f"style {self.thickness} {self.marker}", "color {} {} {}".format(*self.color),
                *wb.outline_lines(self.ends, self.points)]

    def pixels(self):
        """Every point's pixel, rounded to the nearest as the spec says."""
        return [(inkcheck.rounded(self.x0 + self.scale * x), inkcheck.rounded(self.baseline - self.scale * y))
                for x, y, _ in self.points]

    def contours(self):
        px, start = self.pixels(), 0
        for end in self.ends:
            yield px[start:end + 1]
            start = end + 1

    def box(self):
        px = self.pixels()
        pad = max(self.thickness, self.marker) // 2 + 2
        return (min(x for x, _ in px) - pad, min(y for _, y in px) - pad,
                max(x for x, _ in px) + pad, max(y for _, y in px) + pad)


def square_offsets(size):
    """Offsets of a size x size square's first, middle and last pixels from its centre."""
    lo, hi = -(size // 2), size - 1 - size // 2
    return [(ox, oy) for ox in {lo, 0, hi} for oy in {lo, 0, hi}]


def check_picture(pic, w, h, items):
    """None if the picture is exactly the ideal drawing (within a pixel), else what is wrong."""
    if (pic.w, pic.h) != (w, h):
        return f"picture is {pic.w}x{pic.h}, expected {w}x{h}"
    for i, a in enumerate(items):  # different colours never overlap, so drawing order can't matter
        for b in items[i + 1:]:
            ba, bb = a.box(), b.box()
            if a.color != b.color and ba[0] <= bb[2] and bb[0] <= ba[2] and ba[1] <= bb[3] and bb[1] <= ba[3]:
                return "two outlines of different colours overlap; move them apart"
    allowed, musts = {}, []
    for it in items:
        region = allowed.setdefault(it.color, inkcheck.Region(w, h))
        for contour in it.contours():
            closed = contour + contour[:1]
            region.along(closed, it.thickness / 2 + 1.5)
            for a, b in zip(closed, closed[1:]):
                for sx, sy in inkcheck.segment_samples(a, b):
                    musts += [(sx + ox, sy + oy, it.color, f"segment {a}-{b}") for ox, oy in square_offsets(it.thickness)]
        for x, y in it.pixels():
            region.around(x, y, it.marker / 2 + 1.5)
            musts += [(x + ox, y + oy, it.color, f"marker at {(x, y)}") for ox, oy in square_offsets(it.marker)]
    stray = inkcheck.stray_ink(pic, allowed)
    if stray:
        return f"ink at ({stray[0]}, {stray[1]}) in {stray[2]} that no segment or marker explains"
    for x, y, color, what in musts:
        if pic.inside(inkcheck.rounded(x), inkcheck.rounded(y)) and not pic.near(x, y, color, 1):
            return f"no ink near ({x:g}, {y:g}) for the {what}"
    return None


def fit(contours_or_outline, scale, margin):
    """(ends, points, x0, baseline, width, height) so the outline sits `margin` px inside."""
    ends, points = contours_or_outline if isinstance(contours_or_outline, tuple) else split(contours_or_outline)
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    x0 = round(margin - scale * min(xs))
    baseline = round(margin + scale * max(ys))
    w = math.ceil(x0 + scale * max(xs) + margin)
    h = math.ceil(baseline - scale * min(ys) + margin)
    return ends, points, x0, baseline, w, h


def random_outline(rng):
    contours = []
    for _ in range(rng.randint(1, 3)):
        cx, cy, r = rng.randint(150, 850), rng.randint(150, 850), rng.randint(80, 300)
        n = rng.randint(3, 9)
        pts = []
        for k in range(n):  # roughly around a circle, so contours look like shapes
            a = 2 * math.pi * k / n + rng.uniform(-0.3, 0.3)
            rr = r * rng.uniform(0.4, 1.1)
            pts.append((round(cx + rr * math.cos(a)), round(cy + rr * math.sin(a)), int(rng.random() < 0.6)))
        contours.append(pts)
    return split(contours)


def main():
    args = wb.parse_args("08")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "image band=1 allow=0", REQUIREMENTS, EXPLAIN)
    jb, noto = wb.load(wb.JETBRAINS), wb.load(wb.NOTO_JP)

    def glyph(font, ch):
        return wb.outline_of(font, font.getBestCmap()[ord(ch)])

    def picture(case_id, req, title, w, h, items, source=SOURCE):
        assert w <= 620 and h <= 620, f"{case_id}: canvas {w}x{h} is too big for the checker"
        lines = [f"canvas {w} {h}"] + [line for it in items for line in it.lines()]
        path = cases.image_path(case_id)
        wb.run_reference(args.ref, lines, path)
        pic = inkcheck.Picture(path)
        problem = check_picture(pic, w, h, items)
        assert problem is None, f"{case_id}: the reference picture is wrong: {problem}"
        pic.save(path)
        cases.add(case_id, req, title, lines, expected_file=path, source=source)

    def single(case_id, req, title, outline, scale, thickness, marker, color=WHITE, margin=None, source=SOURCE):
        margin = margin if margin is not None else marker + 6
        ends, points, x0, baseline, w, h = fit(outline, scale, margin)
        picture(case_id, req, title, w, h, [Item(ends, points, x0, baseline, scale, thickness, marker, color)],
                source=source)

    hand = "hand-made outline; picture checked against the ideal segments and markers"

    # R1 - placement, y up
    single("08-R1-hyphen", "R1", "'-' (JetBrains Mono Bold) at scale 1: four points, one contour",
           glyph(jb, "-"), 1, 3, 10)
    ends, points = split(FLAG)
    picture("08-R1-flag", "R1", "hand-made flag pointing up and right; its pole goes below the baseline",
            260, 330, [Item(ends, points, 70, 240, 0.5, 2, 8, YELLOW)], source=hand)
    ends, points = glyph(jb, "g")
    picture("08-R1-g-offset", "R1", "'g' with x0 = 140 and the baseline at 250: the descender hangs below it",
            420, 360, [Item(ends, points, 140, 250, 0.4, 2, 6, CYAN)])

    # R2 - closed contours
    single("08-R2-triangle", "R2", "hand-made triangle: the third side is the closing line", TRIANGLE, 0.8, 3, 9,
           source=hand)
    single("08-R2-A", "R2", "'A': both contours end with a closing line", glyph(jb, "A"), 0.6, 3, 9)

    # R3 - separate contours
    single("08-R3-B", "R3", "'B': three contours, no line between them", glyph(jb, "B"), 0.6, 2, 8)
    single("08-R3-o", "R3", "'o': an outer and an inner contour", glyph(jb, "o"), 0.7, 2, 8, PINK)
    single("08-R3-ten", "R3", "U+5341 (CJK 'ten', Noto Sans JP): two overlapping bars", glyph(noto, "十"), 0.45, 2, 8)
    single("08-R3-a-hiragana", "R3", "U+3042 (hiragana 'a', Noto Sans JP): three contours, 106 points", glyph(noto, "あ"),
           0.55, 2, 6, LIME)

    # R4 - markers on every point
    single("08-R4-big-markers", "R4", "'o' with 16 px markers and 1 px lines: off-curve points get markers too",
           glyph(jb, "o"), 0.6, 1, 16, YELLOW)
    single("08-R4-odd-even", "R4", "'D' with 7 px markers (odd size) and 4 px lines", glyph(jb, "D"), 0.6, 4, 7)

    # R5 - several outlines
    (ea, pa), (eb, pb) = glyph(jb, "A"), glyph(jb, "B")
    picture("08-R5-two", "R5", "'A' then 'B' side by side, each with its own place and colour", 470, 300,
            [Item(ea, pa, 0, 260, 0.35, 2, 7, YELLOW), Item(eb, pb, 230, 280, 0.3, 3, 9, CYAN)])
    (e1, p1), (e2, p2), (e3, p3) = glyph(jb, "-"), glyph(noto, "十"), glyph(noto, "あ")
    picture("08-R5-three", "R5", "'-', U+5341 and U+3042: three outlines with different place, style and colour",
            590, 260, [Item(e1, p1, -40, 220, 0.4, 1, 5, PINK), Item(e2, p2, 160, 230, 0.22, 3, 6, LIME),
                       Item(e3, p3, 355, 225, 0.25, 2, 4, WHITE)])

    # R6 - scale
    single("08-R6-a-small", "R6", "'a' at scale 0.3", glyph(jb, "a"), 0.3, 1, 5)
    single("08-R6-a-large", "R6", "'a' at scale 0.75", glyph(jb, "a"), 0.75, 3, 10, CYAN)
    single("08-R6-hyphen-tiny", "R6", "'-' at scale 0.15: markers almost touch", glyph(jb, "-"), 0.15, 1, 4)
    single("08-R6-fractional", "R6", "hand-made outline whose coordinates aren't whole numbers, at scale 1.5",
           FRACTIONAL, 1.5, 2, 6, source=hand)

    # E2E - the blog's demo (halved to fit) and random outlines
    ends, points = glyph(jb, "a")
    picture("08-E2E-blog-a", "E2E", "the blog's demo, at half size: 'a' on 600x600, 3 px lines, 10 px markers",
            600, 600, [Item(ends, points, 150, 450, 0.5, 3, 10, WHITE)])
    single("08-E2E-S", "E2E", "'S' (JetBrains Mono Bold): one long contour", glyph(jb, "S"), 0.5, 2, 6)
    for k in range(3):
        ends, points = random_outline(rng)
        scale = rng.choice([0.25, 0.3, 0.4, 0.5])
        single(f"08-E2E-random-s{args.seed}-{k}", "E2E",
               f"random outline #{k} (seed {args.seed}): {len(ends)} contours, {len(points)} points, scale {scale}",
               (ends, points), scale, rng.choice([1, 2, 3]), rng.choice([4, 6, 9]),
               rng.choice([WHITE, YELLOW, CYAN, PINK, LIME]), source="random outline; " + SOURCE)

    cases.save()


if __name__ == "__main__":
    main()
