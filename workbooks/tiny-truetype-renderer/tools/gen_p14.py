"""Test cases for checkpoint 14 (fill a glyph with the even-odd rule).

    py -P tools/gen_p14.py --ref build/ref/assignment_14.exe                  # tests/14 (seed 1)
    py -P tools/gen_p14.py --seed 7 --out build/fresh/14 --ref ...
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fillgen as fg  # noqa: E402
import wb  # noqa: E402

REQUIREMENTS = [
    ("R1", "Fill each pixel whose centre is inside; the rest stay black"),
    ("R2", "Holes: a contour inside another stays empty"),
    ("R3", "Follow the curves, implied on-curve points included"),
    ("R4", "A vertex on a scanline counts the right number of times"),
    ("R5", "Crossing or overlapping contours: even-odd leaves the overlap empty"),
    ("R6", "Fill several outlines one after another"),
    ("R7", "Placement and scale; clip what falls outside the canvas"),
    ("E2E", "Letters from JetBrains Mono Bold"),
]

SQUARE = [(0, 0), (0, 40), (40, 40), (40, 0)]
TRIANGLE = [(0, 0), (30, 52), (60, 0)]
# A pentagram drawn as one self-crossing contour.
STAR = [(50, 100), (79, 9), (2, 65), (98, 65), (21, 9)]
# A diamond whose vertices sit exactly on pixel-centre rows at scale 0.5.
DIAMOND = [(41, 1), (1, 41), (41, 81), (81, 41)]


def main():
    args = wb.parse_args("14")
    rng = random.Random(args.seed)
    jb, noto = wb.load(wb.JETBRAINS), wb.load(wb.NOTO_JP)
    g = lambda font, ch: fg.glyph(font, ch)
    specs = [
        ("14-R1-square", "R1", "a 40 x 40 square at scale 1", fg.fit([fg.polygon(SQUARE)], 1)),
        ("14-R1-triangle", "R1", "a triangle with sloped sides", fg.fit([fg.polygon(TRIANGLE)], 2)),
        ("14-R1-hyphen", "R1", "'-' hyphen at scale 0.5", fg.fit([g(jb, "-")], 0.5)),
        ("14-R2-o", "R2", "'o': one hole", fg.fit([g(jb, "o")], 0.35)),
        ("14-R2-B", "R2", "'B': two holes", fg.fit([g(jb, "B")], 0.35)),
        ("14-R2-8", "R2", "'8': two holes inside curves", fg.fit([g(jb, "8")], 0.35)),
        ("14-R3-S", "R3", "'S': curves only", fg.fit([g(jb, "S")], 0.35)),
        ("14-R3-e", "R3", "'e'", fg.fit([g(jb, "e")], 0.4)),
        ("14-R3-circle-all-off", "R3", "a contour of 8 off-curve points (every on-curve point implied)",
         fg.fit([([7], fg.circle(60, 60, 55))], 1)),
        ("14-R4-diamond-half", "R4", "a diamond at scale 1.5: its vertices fall exactly on pixel centres",
         fg.fit([fg.polygon(DIAMOND)], 1.5)),
        ("14-R4-diamond-integer", "R4", "the same diamond at scale 1: vertices on pixel boundaries",
         fg.fit([fg.polygon(DIAMOND)], 1)),
        ("14-R4-less-than", "R4", "'<' at scale 0.5: a pointed vertex", fg.fit([g(jb, "<")], 0.5)),
        ("14-R4-W", "R4", "'W' at scale 0.5: vertices sharing a row", fg.fit([g(jb, "W")], 0.5)),
        ("14-R4-E", "R4", "'E' at scale 0.5: horizontal edges", fg.fit([g(jb, "E")], 0.5)),
        ("14-R5-star", "R5", "a pentagram drawn as one crossing contour: the centre stays empty",
         fg.fit([fg.polygon(STAR)], 2)),
        ("14-R5-overlap", "R5", "two overlapping squares in one outline: the overlap stays empty",
         fg.fit([fg.polygon(SQUARE, [(x + 20, y + 20) for x, y in SQUARE])], 2)),
        ("14-R5-ten", "R5", "U+5341 (ten) from Noto Sans JP: two crossing strokes", fg.fit([g(noto, "十")], 0.25)),
        ("14-R6-two-outlines", "R6", "two overlapping squares as two outlines: both filled, no hole",
         fg.fit([fg.polygon(SQUARE), fg.polygon([(x + 20, y + 20) for x, y in SQUARE])], 2)),
        ("14-R6-word", "R6", "three letters as three outlines", None),
    ]
    # Three letters side by side, each its own outline.
    letters = []
    for k, ch in enumerate("Ok8"):
        ends, pts = g(jb, ch)
        letters.append((ends, [(x + 600 * k, y, on) for x, y, on in pts]))
    specs[-1] = ("14-R6-word", "R6", "'O', 'k', '8' as three outlines", fg.fit(letters, 0.22))

    clipped = fg.fit([g(jb, "Q")], 0.4)
    clipped.place = (clipped.place[0] - 40, clipped.place[1] + 30, clipped.place[2])
    specs.append(("14-R7-clipped", "R7", "'Q' placed so it runs off the left and bottom edges", clipped))
    small = fg.fit([g(jb, "g")], 0.15)
    specs.append(("14-R7-small", "R7", "'g' at scale 0.15 (descender below the baseline)", small))
    big = fg.fit([g(jb, "&")], 0.6)
    specs.append(("14-R7-large", "R7", "'&' at scale 0.6", big))

    pool = [chr(c) for c in range(0x21, 0x7F) if not jb["glyf"][jb.getBestCmap()[c]].isComposite()]
    for ch in rng.sample(pool, 6):
        specs.append((f"14-E2E-s{args.seed}-U+{ord(ch):04X}", "E2E",
                      f"U+{ord(ch):04X} ({jb.getBestCmap()[ord(ch)]}), scale 0.3 (seed {args.seed})",
                      fg.fit([g(jb, ch)], 0.3)))

    fg.write_cases("14", True, REQUIREMENTS, specs, args)


if __name__ == "__main__":
    main()
