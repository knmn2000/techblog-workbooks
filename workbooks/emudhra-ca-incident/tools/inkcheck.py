"""Independent checks for pictures drawn by a reference program (drawing checkpoints).

A picture generator draws each expected image with the reference program, then checks
it against the ideal geometry with these helpers before writing it: ink must lie near
an ideal shape of the same colour, and every ideal shape must have ink. Nothing here
shares code with the reference solutions.
"""

import math

from imageio import read_image, write_png

BLACK = (0, 0, 0)


def rounded(v: float) -> int:
    """Nearest whole number, halves away from zero (like C's lround)."""
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


class Picture:
    def __init__(self, path):
        self.w, self.h, self.rgb = read_image(path)

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def at(self, x: int, y: int):
        i = 3 * (y * self.w + x)
        return tuple(self.rgb[i:i + 3])

    def near(self, x: float, y: float, color, radius: int = 1) -> bool:
        """Is there a pixel of `color` within `radius` pixels (both axes) of (x, y)?"""
        cx, cy = rounded(x), rounded(y)
        for yy in range(cy - radius, cy + radius + 1):
            for xx in range(cx - radius, cx + radius + 1):
                if self.inside(xx, yy) and self.at(xx, yy) == color:
                    return True
        return False

    def count(self, x0: int, y0: int, x1: int, y1: int, color) -> int:
        """How many pixels of the box x0..x1, y0..y1 (inclusive) have `color`."""
        return sum(self.at(x, y) == color for y in range(max(y0, 0), min(y1, self.h - 1) + 1)
                   for x in range(max(x0, 0), min(x1, self.w - 1) + 1))

    def colors(self) -> set:
        return {self.rgb[i:i + 3] for i in range(0, len(self.rgb), 3)}

    def inked(self):
        """(x, y, color) of every pixel that isn't black."""
        rgb, w = self.rgb, self.w
        for i in range(self.w * self.h):
            c = rgb[3 * i:3 * i + 3]
            if c != b"\x00\x00\x00":
                yield i % w, i // w, tuple(c)

    def save(self, path):
        """The same pixels as a PNG without row filters, which the checker reads fastest."""
        write_png(path, self.w, self.h, self.rgb)


class Region:
    """A set of pixels on a w x h canvas, built from boxes and thick paths."""

    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.bits = bytearray(w * h)

    def box(self, x0: int, y0: int, x1: int, y1: int):
        """Adds the pixels x0..x1, y0..y1 (inclusive), clipped to the canvas."""
        x0, x1 = max(x0, 0), min(x1, self.w - 1)
        if x0 > x1:
            return
        run = b"\x01" * (x1 - x0 + 1)
        for y in range(max(y0, 0), min(y1, self.h - 1) + 1):
            self.bits[y * self.w + x0:y * self.w + x1 + 1] = run

    def around(self, x: float, y: float, r: float):
        """Adds every pixel within r of (x, y) along both axes (a square)."""
        self.box(math.ceil(x - r), math.ceil(y - r), math.floor(x + r), math.floor(y + r))

    def along(self, points, r: float):
        """Adds every pixel within about r (both axes) of the path through `points`."""
        for a, b in zip(points, points[1:]):
            for x, y in segment_samples(a, b):
                self.around(x, y, r)
        if len(points) == 1:
            self.around(*points[0], r)

    def has(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h and self.bits[y * self.w + x] != 0

    def touches(self, x: int, y: int, radius: int) -> bool:
        """Does the region contain any pixel within `radius` (both axes) of (x, y)?"""
        return any(self.has(xx, yy) for yy in range(y - radius, y + radius + 1)
                   for xx in range(x - radius, x + radius + 1))

    def union(self, other: "Region") -> "Region":
        out = Region(self.w, self.h)
        n = self.w * self.h
        out.bits = bytearray((int.from_bytes(self.bits, "little") | int.from_bytes(other.bits, "little"))
                             .to_bytes(n, "little"))
        return out


def segment_samples(a, b, step: float = 0.5):
    """Points along the segment a-b, both ends included, at most `step` apart."""
    (ax, ay), (bx, by) = a, b
    n = max(1, math.ceil(math.hypot(bx - ax, by - ay) / step))
    return [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n + 1)]


def quad_samples(p0, p1, p2, step: float = 0.5):
    """Points on the quadratic Bezier curve p0-p1-p2, at most about `step` apart."""
    length = math.dist(p0, p1) + math.dist(p1, p2)  # never shorter than the curve
    n = max(1, math.ceil(length / step))
    out = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        out.append((u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
                    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1]))
    return out


def stray_ink(pic: Picture, allowed: dict):
    """The first inked pixel whose colour may not be there, as (x, y, color), or None.
    `allowed` maps a colour to the Region where that colour may appear."""
    for x, y, c in pic.inked():
        region = allowed.get(c)
        if region is None or not region.has(x, y):
            return x, y, c
    return None


def color_distance(a, b) -> int:
    return max(abs(p - q) for p, q in zip(a, b))
