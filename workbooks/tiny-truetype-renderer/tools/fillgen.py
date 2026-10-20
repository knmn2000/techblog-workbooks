"""Shared machinery for the fill checkpoints' generators (gen_p14, gen_p16, gen_p17).

The reference program draws each expected image. Before a case is written, the
image is checked pixel by pixel against fontTools' PointInsidePen (an independent
inside test) at the pixel centres: a pixel must be inked exactly when its centre is
inside one of the outlines by the checkpoint's rule.
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import imageio  # noqa: E402
import wb  # noqa: E402

COMPARE = "image band=1 allow=0.0002"
# Any difference in a fill picture can come from any requirement, so no "likely cause".
EXPLAIN = ""


class Scene:
    def __init__(self, width, height, place, outlines, color=(255, 255, 255)):
        self.width, self.height, self.place, self.outlines, self.color = width, height, place, outlines, color

    def input_lines(self):
        x0, baseline, scale = self.place
        lines = [f"canvas {self.width} {self.height}", f"place {wb.num(x0)} {wb.num(baseline)} {wb.num(scale)}",
                 "color %d %d %d" % self.color]
        for ends, points in self.outlines:
            lines += wb.outline_lines(ends, points)
        return lines


def fit(outlines, scale, margin=6, max_side=560):
    """A scene that fits the outlines at `scale`, with integer placement."""
    xs = [p[0] for _, pts in outlines for p in pts]
    ys = [p[1] for _, pts in outlines for p in pts]
    x0 = margin - math.floor(min(xs) * scale)
    baseline = margin + math.ceil(max(ys) * scale)
    width = math.ceil((max(xs) - min(xs)) * scale) + 2 * margin + 1
    height = math.ceil((max(ys) - min(ys)) * scale) + 2 * margin + 1
    assert width <= max_side and height <= max_side, f"scene too big: {width}x{height}"
    return Scene(width, height, (x0, baseline, scale), outlines)


def glyph(font, ch_or_name):
    name = ch_or_name if len(ch_or_name) > 1 else font.getBestCmap()[ord(ch_or_name)]
    return wb.outline_of(font, name)


def polygon(*contours):
    """One outline from contours given as lists of (x, y) on-curve points."""
    ends, points = [], []
    for c in contours:
        points += [(x, y, 1) for x, y in c]
        ends.append(len(points) - 1)
    return ends, points


def circle(cx, cy, r, clockwise=True, all_off=True):
    """A circle-like contour of 8 points (clockwise in y-up glyph space by default).
    all_off: 8 off-curve control points, so every on-curve point is implied.
    Otherwise on-curve points alternate with off-curve ones, starting on-curve."""
    pts = []
    for k in range(8):
        a = (-1 if clockwise else 1) * k * math.pi / 4
        on = 0 if all_off else int(k % 2 == 0)
        # Off-curve points sit where the tangents of their neighbouring curve points
        # meet: 22.5 degrees away (all off) or 45 degrees away (alternating).
        rr = r if on else r / math.cos(math.pi / 8 if all_off else math.pi / 4)
        pts.append((round(cx + rr * math.cos(a), 2), round(cy + rr * math.sin(a), 2), on))
    return pts


def is_inside(scene, gx, gy, even_odd):
    return any(wb.inside(ends, pts, gx, gy, even_odd) for ends, pts in scene.outlines)


def on_boundary(scene, gx, gy, even_odd, eps=1e-6):
    """A pixel centre exactly on an edge: whether it counts as inside is a tie-break
    convention, so either answer is right. Detected by nudging the point."""
    answers = {is_inside(scene, gx + dx, gy + dy, even_odd) for dx, dy in ((eps, 0), (-eps, 0), (0, eps), (0, -eps))}
    return len(answers) > 1


def validate(scene, image_path, even_odd, rng, samples=5000):
    """Every sampled pixel is inked exactly when its centre is inside (PointInsidePen)."""
    w, h, rgb = imageio.read_image(image_path)
    assert (w, h) == (scene.width, scene.height)
    x0, baseline, scale = scene.place
    pixels = [(rng.randrange(w), rng.randrange(h)) for _ in range(samples)]
    pixels += [(x, h // 2) for x in range(w)] + [(w // 2, y) for y in range(h)]
    bad = []
    for px, py in pixels:
        gx, gy = (px + 0.5 - x0) / scale, (baseline - (py + 0.5)) / scale
        want = is_inside(scene, gx, gy, even_odd)
        got = rgb[3 * (py * w + px)] != 0 or rgb[3 * (py * w + px) + 1] != 0 or rgb[3 * (py * w + px) + 2] != 0
        if want != got and not on_boundary(scene, gx, gy, even_odd):
            bad.append((px, py, want))
    assert len(bad) <= 2, f"{image_path.name}: reference disagrees with PointInsidePen at {bad[:5]}"
    return len(pixels)


def differs_by_rule(scene, rng, step=2):
    """Do even-odd and non-zero give different pictures? (Overlap tests must.)
    Checks every `step`-th pixel, so a small overlap isn't missed."""
    x0, baseline, scale = scene.place
    for py in range(0, scene.height, step):
        for px in range(0, scene.width, step):
            gx, gy = (px + 0.5 - x0) / scale, (baseline - (py + 0.5)) / scale
            if is_inside(scene, gx, gy, True) != is_inside(scene, gx, gy, False):
                return True
    return False


def write_cases(checkpoint, even_odd, requirements, specs, args):
    """specs: [(case id, requirement, title, Scene)]"""
    rng = random.Random(args.seed * 7919 + int(checkpoint))
    source = f"reference picture, checked pixel by pixel against {wb.FT} PointInsidePen"
    cases = wb.Cases(args.out, args.seed, COMPARE, requirements, EXPLAIN, source=source)
    for case_id, req, title, scene in specs:
        image = cases.image_path(case_id)
        wb.run_reference(args.ref, scene.input_lines(), image)
        validate(scene, image, even_odd, rng)
        cases.add(case_id, req, title, scene.input_lines(), expected_file=image)
    cases.save()
