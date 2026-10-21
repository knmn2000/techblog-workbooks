"""Test cases for checkpoint 17 (fill a glyph with the non-zero rule, curves included).

    py -P tools/gen_p17.py --ref build/ref/p17.exe                  # tests/17 (seed 1)
    py -P tools/gen_p17.py --seed 7 --out build/fresh/17 --ref ...
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fillgen as fg  # noqa: E402
import wb  # noqa: E402

REQUIREMENTS = [
    ("R1", "Curved outlines fill exactly the pixels whose centre is inside"),
    ("R2", "Implied on-curve points; contours that start or stay off-curve"),
    ("R3", "Overlapping curved contours going the same way stay filled"),
    ("R4", "Contours going the opposite way cut holes"),
    ("R5", "Scanlines that cross one curve twice or just touch it"),
    ("R6", "Several outlines; compound glyphs given as one outline"),
    ("R7", "Placement and scale; parts outside the canvas are clipped"),
    ("E2E", "Glyphs from JetBrains Mono Bold and Noto Sans JP"),
]


def rotate_start(points, k):
    return points[k:] + points[:k]


def main():
    args = wb.parse_args("17")
    rng = random.Random(args.seed)
    jb, noto = wb.load(wb.JETBRAINS), wb.load(wb.NOTO_JP)
    g = fg.glyph
    ring = ([7, 15], fg.circle(60, 60, 55, all_off=False) + fg.circle(60, 60, 30, clockwise=False, all_off=False))
    two_circles = ([7, 15], fg.circle(50, 50, 45, all_off=False) + fg.circle(100, 50, 45, all_off=False))
    two_circles_opposite = ([7, 15], fg.circle(50, 50, 45, all_off=False) + fg.circle(100, 50, 45, clockwise=False, all_off=False))
    off_first = fg.circle(60, 60, 55, all_off=False)
    off_first = ([7], rotate_start(off_first, 1))  # starts at an off-curve point
    # A circle whose top and bottom land exactly on pixel centres at scale 1.5 (odd y).
    tangent = ([7], fg.circle(61, 61, 40, all_off=False))  # extremes at y = 21 and 101
    specs = [
        ("17-R1-o", "R1", "'o'", fg.fit([g(jb, "o")], 0.35)),
        ("17-R1-S", "R1", "'S'", fg.fit([g(jb, "S")], 0.35)),
        ("17-R1-a", "R1", "'a' (the glyph the blog renders)", fg.fit([g(jb, "a")], 0.4)),
        ("17-R2-all-off", "R2", "a contour of 8 off-curve points: every on-curve point is implied",
         fg.fit([([7], fg.circle(60, 60, 55))], 1)),
        ("17-R2-off-first", "R2", "a contour whose first point is off-curve", fg.fit([off_first], 1)),
        ("17-R3-two-circles", "R3", "two overlapping circles going the same way: no hole", fg.fit([two_circles], 1.5)),
        ("17-R3-a-hiragana", "R3", "U+3042 from Noto Sans JP: curved strokes that overlap", fg.fit([g(noto, "あ")], 0.25)),
        ("17-R4-ring", "R4", "a circle with a reversed circle inside: a ring", fg.fit([ring], 1.5)),
        ("17-R4-opposite-circles", "R4", "two overlapping circles going opposite ways: the overlap is empty",
         fg.fit([two_circles_opposite], 1.5)),
        ("17-R4-B", "R4", "'B': two counters", fg.fit([g(jb, "B")], 0.35)),
        ("17-R5-U", "R5", "'U': each scanline crosses the bottom curve twice", fg.fit([g(jb, "U")], 0.4)),
        ("17-R5-tangent", "R5", "a circle whose top and bottom touch pixel-centre scanlines", fg.fit([tangent], 1.5)),
        ("17-R5-c", "R5", "'c' at scale 0.5 (vertices on pixel centres)", fg.fit([g(jb, "c")], 0.5)),
        ("17-R6-e-acute", "R6", "U+00E9 from JetBrains Mono Bold: a compound glyph as one outline",
         fg.fit([g(jb, "é")], 0.35)),
        ("17-R6-word", "R6", "'a', 'g', '&' as three outlines", None),
    ]
    letters = []
    for k, ch in enumerate("ag&"):
        ends, pts = g(jb, ch)
        letters.append((ends, [(x + 600 * k, y, on) for x, y, on in pts]))
    specs[-1] = ("17-R6-word", "R6", "'a', 'g', '&' as three outlines", fg.fit(letters, 0.22))
    clipped = fg.fit([g(jb, "@")], 0.4)
    clipped.place = (clipped.place[0] + 30, clipped.place[1] - 40, clipped.place[2])
    specs.append(("17-R7-clipped", "R7", "'@' running off the right and top edges", clipped))
    specs.append(("17-R7-large", "R7", "U+6F22 from Noto Sans JP at scale 0.45", fg.fit([g(noto, "漢")], 0.45)))

    for case_id in ("17-R3-two-circles", "17-R3-a-hiragana"):
        scene = next(s for c, _, _, s in specs if c == case_id)
        assert fg.differs_by_rule(scene, rng), f"{case_id} looks the same under even-odd"

    jb_pool = [chr(c) for c in range(0x21, 0x7F) if any(not on for _, _, on in g(jb, chr(c))[1])]
    for ch in rng.sample(jb_pool, 4):
        specs.append((f"17-E2E-s{args.seed}-U+{ord(ch):04X}", "E2E",
                      f"U+{ord(ch):04X} ({jb.getBestCmap()[ord(ch)]}), scale 0.3 (seed {args.seed})",
                      fg.fit([g(jb, ch)], 0.3)))
    for ch in rng.sample("あいのめる字界漢花水", 3):
        specs.append((f"17-E2E-s{args.seed}-U+{ord(ch):04X}", "E2E",
                      f"U+{ord(ch):04X} from Noto Sans JP, scale 0.25 (seed {args.seed})", fg.fit([g(noto, ch)], 0.25)))

    fg.write_cases("17", False, REQUIREMENTS, specs, args)


if __name__ == "__main__":
    main()
