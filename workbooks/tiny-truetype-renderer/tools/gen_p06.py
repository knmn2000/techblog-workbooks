"""Test cases for checkpoint 06 (draw on a framebuffer).

The reference program draws every expected picture. Before a picture is written, this
script checks it against the ideal shapes, independently of the reference code:
points and rectangles must be exactly their pixel sets, lines must have ink along the
true segment (at both edges of their thickness) and no ink further than
thickness/2 + 1.5 pixels from it, and nothing else may be inked.

It also redraws every scene in Python with other ways of turning a line's y (or x) into
a whole pixel - truncating as the blog does, flooring, rounding halves down - and keeps
a scene only if each of those passes the checker too. A missing or extra single pixel
counts (allow=0, so a lost point fails), so scenes where such a choice would decide one
pixel at a clipped or covered end of a line are left out.

    py -P tools/gen_p06.py --ref build/ref/assignment_06                        # tests/06 (seed 1)
    py -P tools/gen_p06.py --seed 77 --out build/fresh/06             # what `.\\check 06 -Fresh` runs
"""

import math
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inkcheck  # noqa: E402
import wb  # noqa: E402
from imageio import compare_images, write_png  # noqa: E402

REQUIREMENTS = [
    ("R1", "Canvas size; black background; (0, 0) top-left, y grows down"),
    ("R2", "point paints a single pixel"),
    ("R3", "rect is centred on (cx, cy): even and odd sizes"),
    ("R4", "line in every direction (shallow, steep, axis-aligned), both ends included"),
    ("R5", "line thickness: a thickness x thickness square at every step"),
    ("R6", "Clipping: shapes that cross the canvas edge or lie outside it"),
    ("R7", "Drawing order: later commands paint over earlier ones"),
    ("E2E", "Whole scenes: the blog's demo and random scenes"),
]
EXPLAIN = "image:size=R1 image:missing=R1 image:format=R1"
COMPARE = "image band=1 allow=0"
SOURCE = "reference drawing, checked against the ideal shapes (exact pixels for point/rect, true segment for line)"

WHITE, RED, GREEN = (255, 255, 255), (200, 0, 0), (0, 200, 0)
PALETTE = [WHITE, RED, GREEN, (60, 120, 255), (255, 220, 0), (0, 220, 220), (230, 0, 230),
           (255, 120, 0), (255, 120, 170), (150, 255, 80), (120, 0, 255), (150, 150, 150)]
BLUE, YELLOW, CYAN, MAGENTA, ORANGE, PINK, LIME, PURPLE, GRAY = PALETTE[3:]

# The checker tells colours apart within 40 per channel, so keep every pair (and black) far apart.
for i, a in enumerate(PALETTE + [inkcheck.BLACK]):
    for b in PALETTE[i + 1:]:
        assert inkcheck.color_distance(a, b) > 80, (a, b)


def point(x, y, c):
    return ("point", x, y, c)


def rect(cx, cy, w, h, c):
    return ("rect", cx, cy, w, h, c)


def line(ax, ay, bx, by, t, c):
    return ("line", ax, ay, bx, by, t, c)


def command_line(cmd) -> str:
    *values, color = cmd
    return " ".join(str(v) for v in [*values, *color])


# ---- Independent check of a drawn picture ----------------------------------------

def rect_box(cx, cy, w, h):
    left, top = cx - w // 2, cy - h // 2
    return left, top, left + w - 1, top + h - 1


def region_of(cmd, w, h) -> inkcheck.Region:
    """Where the command's ink may be: exact for point and rect, near the segment for line."""
    r = inkcheck.Region(w, h)
    if cmd[0] == "point":
        r.box(cmd[1], cmd[2], cmd[1], cmd[2])
    elif cmd[0] == "rect":
        r.box(*rect_box(*cmd[1:5]))
    else:
        _, ax, ay, bx, by, t, _ = cmd
        r.along([(ax, ay), (bx, by)], t / 2 + 1.5)
    return r


def must_have_ink(cmd):
    """(x, y, radius): spots that must have the command's colour within radius pixels."""
    if cmd[0] == "point":
        yield cmd[1], cmd[2], 0
    elif cmd[0] == "rect":
        x0, y0, x1, y1 = rect_box(*cmd[1:5])
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                yield x, y, 0
    else:
        _, ax, ay, bx, by, t, _ = cmd
        lo, hi = -(t // 2), t - 1 - t // 2  # the square's extent around its centre
        for sx, sy in inkcheck.segment_samples((ax, ay), (bx, by)):
            for ox in {lo, 0, hi}:
                for oy in {lo, 0, hi}:
                    yield sx + ox, sy + oy, 1


def check_picture(pic, w, h, commands):
    """None if the picture shows exactly the commands, else what is wrong."""
    if (pic.w, pic.h) != (w, h):
        return f"picture is {pic.w}x{pic.h}, expected {w}x{h}"
    regions = [region_of(cmd, w, h) for cmd in commands]
    by_color = {}
    for cmd, region in zip(commands, regions):
        c = cmd[-1]
        by_color[c] = by_color[c].union(region) if c in by_color else region
    stray = inkcheck.stray_ink(pic, by_color)
    if stray:
        return f"ink at ({stray[0]}, {stray[1]}) in {stray[2]} that no command explains"
    covered_later = inkcheck.Region(w, h)  # pixels a later command may have painted over
    for k in range(len(commands) - 1, -1, -1):
        cmd = commands[k]
        for x, y, radius in must_have_ink(cmd):
            px, py = inkcheck.rounded(x), inkcheck.rounded(y)
            if not pic.inside(px, py) or covered_later.touches(px, py, radius):
                continue
            if not pic.near(x, y, cmd[-1], radius):
                return f"command {k + 1} `{command_line(cmd)}` has no ink near ({x:g}, {y:g})"
        covered_later = covered_later.union(regions[k])
    return None


# Other ways a correct program may turn the line's minor coordinate into a pixel.
VARIANTS = {"truncate": int, "floor": math.floor, "round half down": lambda v: math.ceil(v - 0.5)}


def draw_variant(w, h, commands, minor) -> bytes:
    """The scene drawn in Python, with `minor` placing each step of a line. Used only to
    confirm that these variants pass; the expected picture comes from the reference."""
    buf = bytearray(3 * w * h)

    def box(left, top, bw, bh, c):
        x0, x1 = max(left, 0), min(left + bw, w)
        if x0 < x1:
            for y in range(max(top, 0), min(top + bh, h)):
                buf[3 * (y * w + x0):3 * (y * w + x1)] = bytes(c) * (x1 - x0)

    for cmd in commands:
        c = cmd[-1]
        if cmd[0] == "point":
            box(cmd[1], cmd[2], 1, 1, c)
        elif cmd[0] == "rect":
            box(cmd[1] - cmd[3] // 2, cmd[2] - cmd[4] // 2, cmd[3], cmd[4], c)
        else:
            _, ax, ay, bx, by, t, _ = cmd
            steep = abs(by - ay) > abs(bx - ax)
            if steep:
                ax, ay, bx, by = ay, ax, by, bx
            if ax > bx:
                ax, ay, bx, by = bx, by, ax, ay
            slope = 0 if bx == ax else (by - ay) / (bx - ax)
            for x in range(ax, bx + 1):
                y = minor(ay + slope * (x - ax))
                cx, cy = (y, x) if steep else (x, y)
                box(cx - t // 2, cy - t // 2, t, t, c)
    return bytes(buf)


def failing_variant(expected: Path, w, h, commands):
    """The name of the first variant that the checker would reject, or None."""
    band, allow = (float(part.split("=")[1]) for part in COMPARE.split()[1:])
    with tempfile.TemporaryDirectory() as tmp:
        actual = Path(tmp) / "variant.png"
        for name, minor in VARIANTS.items():
            write_png(actual, w, h, draw_variant(w, h, commands, minor))
            problem, _ = compare_images(expected, actual, Path(tmp) / "diff.png", band=int(band), allow=allow)
            if problem:
                return name
    return None


# ---- Cases ----------------------------------------------------------------------

def main():
    args = wb.parse_args("06")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, EXPLAIN, source="reference drawing + ideal shapes")

    def scene(case_id, req, title, w, h, commands, retry=False):
        """Adds the case and returns True; with retry=True, returns False instead of
        stopping when one of the VARIANTS wouldn't pass (the caller picks another scene)."""
        lines = [f"canvas {w} {h}", *map(command_line, commands)]
        path = cases.image_path(case_id)
        wb.run_reference(args.ref, lines, path)
        pic = inkcheck.Picture(path)
        problem = check_picture(pic, w, h, commands)
        assert problem is None, f"{case_id}: the reference picture is wrong: {problem}"
        assert len(pic.colors()) <= 16, f"{case_id}: too many colours for the checker"
        pic.save(path)
        variant = failing_variant(path, w, h, commands)
        if variant:
            assert retry, f"{case_id}: a line drawn with '{variant}' instead of rounding would fail"
            path.unlink()
            return False
        cases.add(case_id, req, title, lines, expected_file=path, source=SOURCE)
        return True

    # E2E - the blog's demo scene
    scene("06-E2E-blog-demo", "E2E", "the blog's demo: two lines and a 50x50 square on 500x500", 500, 500,
          [line(100, 100, 300, 400, 5, WHITE), line(400, 200, 50, 300, 2, RED), rect(200, 400, 50, 50, GREEN)])

    # R1 - canvas size, background, orientation
    scene("06-R1-empty", "R1", "nothing drawn: a black 123x45 picture", 123, 45, [])
    scene("06-R1-corners", "R1", "one point in each corner of a 320x180 canvas (top-left red)", 320, 180,
          [point(0, 0, RED), point(319, 0, GREEN), point(0, 179, BLUE), point(319, 179, YELLOW),
           rect(40, 20, 21, 11, RED), rect(280, 160, 21, 11, YELLOW)])
    scene("06-R1-tall", "R1", "a tall 90x240 canvas: a bar near the top, a dot near the bottom", 90, 240,
          [rect(45, 20, 70, 10, CYAN), rect(45, 220, 9, 9, ORANGE)])

    # R2 - points
    scene("06-R2-points", "R2", "a 10x6 grid of single points, every 13 pixels", 140, 90,
          [point(5 + 13 * i, 6 + 13 * j, PALETTE[(i + j) % len(PALETTE)]) for j in range(6) for i in range(10)])
    scene("06-R2-diagonal", "R2", "points on a diagonal, every third pixel, plus isolated points", 100, 100,
          [point(i, i, WHITE) for i in range(2, 98, 3)] + [point(90, 10, RED), point(10, 90, GREEN), point(50, 20, BLUE)])

    # R3 - rectangles
    scene("06-R3-odd", "R3", "odd sizes (25x15, 7x31, 1x1): centred exactly; a dot marks each centre", 200, 120,
          [rect(50, 40, 25, 15, BLUE), rect(120, 60, 7, 31, ORANGE), rect(170, 30, 1, 1, WHITE),
           point(50, 40, WHITE), point(120, 60, WHITE)])
    scene("06-R3-even", "R3", "even sizes (50x50, 20x8, 2x2): left/top get the extra pixel", 220, 140,
          [rect(60, 70, 50, 50, GREEN), rect(160, 40, 20, 8, PINK), rect(160, 100, 2, 2, WHITE),
           point(60, 70, WHITE), point(160, 40, BLUE)])
    scene("06-R3-thin", "R3", "long thin rectangles: 1x60, 60x1, 3x40, 40x4", 200, 160,
          [rect(30, 80, 1, 60, WHITE), rect(110, 20, 60, 1, YELLOW), rect(70, 100, 3, 40, CYAN),
           rect(150, 120, 40, 4, MAGENTA)])

    # R4 - lines in every direction
    cx, cy, rad = 150, 150, 125
    fan = []
    for k in range(16):
        angle = 2 * math.pi * k / 16 + 0.13
        fan.append(line(cx, cy, cx + round(rad * math.cos(angle)), cy + round(rad * math.sin(angle)), 1,
                        PALETTE[k % 8]))
    scene("06-R4-fan", "R4", "16 one-pixel lines from the centre, every direction (all 8 octants)", 300, 300, fan)
    scene("06-R4-shallow", "R4", "shallow lines (|slope| < 1) drawn left-to-right and right-to-left", 260, 200,
          [line(10, 20, 250, 70, 1, WHITE), line(250, 110, 10, 60, 1, RED), line(20, 190, 240, 130, 1, GREEN),
           line(240, 150, 30, 195, 1, YELLOW)])
    scene("06-R4-steep", "R4", "steep lines (|slope| > 1) going up and down: no gaps allowed", 200, 260,
          [line(20, 10, 60, 250, 1, WHITE), line(110, 250, 80, 10, 1, RED), line(130, 15, 120, 245, 1, GREEN),
           line(190, 240, 150, 20, 1, YELLOW)])
    scene("06-R4-axis", "R4", "horizontal, vertical and 45-degree lines in both directions", 220, 220,
          [line(10, 10, 210, 10, 1, WHITE), line(210, 30, 10, 30, 1, RED), line(20, 50, 20, 210, 1, GREEN),
           line(40, 210, 40, 50, 1, YELLOW), line(60, 60, 210, 210, 1, CYAN), line(210, 60, 60, 210, 1, PINK)])
    scene("06-R4-single-point", "R4", "zero-length lines: one square each (sizes 1, 4 and 9)", 120, 80,
          [line(20, 40, 20, 40, 1, WHITE), line(60, 40, 60, 40, 4, RED), line(95, 40, 95, 40, 9, GREEN)])
    scene("06-R4-short", "R4", "very short lines: 1 to 3 pixels long, both ends drawn", 120, 80,
          [line(10, 10, 11, 10, 1, WHITE), line(30, 10, 30, 12, 1, RED), line(50, 10, 52, 13, 1, GREEN),
           line(80, 13, 77, 10, 1, YELLOW), line(10, 50, 13, 49, 1, CYAN), line(60, 60, 59, 57, 1, PINK)])

    # R5 - thickness
    scene("06-R5-thick", "R5", "thick lines (4, 5, 7, 10, 15 px) in several directions", 300, 260,
          [line(20, 20, 280, 40, 4, WHITE), line(30, 80, 270, 60, 5, RED), line(40, 120, 200, 250, 7, GREEN),
           line(280, 100, 220, 240, 10, YELLOW), line(80, 230, 140, 140, 15, CYAN)])
    scene("06-R5-steep-thick", "R5", "steep thick lines (6 and 9 px) and a thick vertical one (12 px)", 220, 240,
          [line(30, 20, 60, 220, 6, PINK), line(120, 220, 100, 20, 9, LIME), line(180, 30, 180, 210, 12, BLUE)])
    scene("06-R5-even-odd", "R5", "the same diagonal at thickness 1, 2, 3, 4, 5 and 8", 320, 120,
          [line(10 + 50 * k, 10, 50 + 50 * k, 110, t, PALETTE[k]) for k, t in enumerate([1, 2, 3, 4, 5, 8])])

    # R6 - clipping
    scene("06-R6-partly", "R6", "shapes crossing every edge of the canvas", 200, 150,
          [rect(0, 75, 40, 30, RED), rect(200, 75, 41, 31, GREEN), rect(100, 0, 60, 20, BLUE),
           rect(100, 150, 61, 21, YELLOW), line(-50, 30, 250, 60, 3, WHITE), line(30, -40, 70, 200, 5, CYAN),
           point(-1, 10, PINK), point(10, -1, PINK), point(200, 10, PINK), point(10, 150, PINK)])
    scene("06-R6-outside", "R6", "shapes entirely outside the canvas draw nothing; one point inside", 150, 100,
          [rect(-100, -100, 50, 50, RED), rect(400, 50, 30, 30, GREEN), rect(75, 300, 30, 30, BLUE),
           line(-80, -10, -10, -90, 4, WHITE), line(160, 120, 300, 400, 6, YELLOW), line(-20, 50, -20, 90, 3, CYAN),
           point(150, 50, PINK), point(75, 100, PINK), point(-5, -5, PINK), point(75, 50, WHITE)])
    scene("06-R6-huge", "R6", "a rectangle much larger than the canvas covers all of it; a line across", 160, 120,
          [rect(80, 60, 1000, 800, GRAY), line(-500, 10, 700, 110, 7, RED)])
    scene("06-R6-corner-lines", "R6", "thick lines that start outside a corner and end inside", 160, 160,
          [line(-30, -30, 60, 60, 9, WHITE), line(190, -10, 110, 70, 6, ORANGE), line(-20, 170, 40, 120, 5, LIME),
           line(170, 150, 120, 120, 8, PURPLE)])

    # R7 - drawing order
    scene("06-R7-overlap", "R7", "a rect, a thick line across it, a smaller rect, then a point on top", 200, 160,
          [rect(100, 80, 120, 90, BLUE), line(20, 20, 180, 140, 9, YELLOW), rect(100, 80, 30, 30, RED),
           point(100, 80, WHITE)])
    scene("06-R7-repaint", "R7", "the same rect twice: the second colour wins; then lines cross over", 180, 120,
          [rect(90, 60, 100, 60, GREEN), rect(90, 60, 100, 60, MAGENTA), line(10, 60, 170, 60, 6, WHITE),
           line(90, 10, 90, 110, 6, ORANGE)])
    scene("06-R7-stack", "R7", "five overlapping squares, each drawn over the one before", 220, 160,
          [rect(50 + 30 * k, 50 + 15 * k, 60, 60, PALETTE[k + 3]) for k in range(5)])

    # E2E - random scenes
    k = rejected = 0
    while k < 5:
        w, h = rng.randint(120, 360), rng.randint(100, 300)
        cmds = []
        colors = rng.sample(PALETTE, rng.randint(3, 8))
        for _ in range(rng.randint(5, 16)):
            kind = rng.choice(["point", "rect", "line", "line"])
            c = rng.choice(colors)
            if kind == "point":
                cmds.append(point(rng.randint(-5, w + 4), rng.randint(-5, h + 4), c))
            elif kind == "rect":
                cmds.append(rect(rng.randint(-20, w + 20), rng.randint(-20, h + 20),
                                 rng.randint(1, 90), rng.randint(1, 90), c))
            else:
                cmds.append(line(rng.randint(-60, w + 60), rng.randint(-60, h + 60), rng.randint(-60, w + 60),
                                 rng.randint(-60, h + 60), rng.choice([1, 1, 2, 3, 5, 8]), c))
        if scene(f"06-E2E-random-s{args.seed}-{k}", "E2E",
                 f"random scene #{k} (seed {args.seed}): {len(cmds)} commands on {w}x{h}", w, h, cmds, retry=True):
            k += 1
        else:
            rejected += 1
    if rejected:
        print(f"skipped {rejected} random scene(s) that a rounding variant would fail", file=sys.stderr)

    cases.save()


if __name__ == "__main__":
    main()
