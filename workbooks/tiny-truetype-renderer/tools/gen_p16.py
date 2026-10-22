"""Test cases for checkpoint 16 (fill a polygon with the non-zero rule).

Every outline here has only on-curve points (straight lines).

    py -P tools/gen_p16.py --ref build/ref/assignment_16                      # tests/16 (seed 1)
    py -P tools/gen_p16.py --seed 7 --out build/fresh/16 --ref ...
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fillgen as fg  # noqa: E402
import wb  # noqa: E402

REQUIREMENTS = [
    ("R1", "Fill each pixel whose centre is inside; the rest stay black"),
    ("R2", "Overlaps going the same way stay filled (winding 2)"),
    ("R3", "A contour going the opposite way cuts a hole (winding 0)"),
    ("R4", "A lone counter-clockwise contour fills too (winding -1)"),
    ("R5", "A vertex on a scanline counts the right number of times"),
    ("R6", "Fill several outlines one after another"),
    ("R7", "Placement and scale; clip what falls outside the canvas"),
    ("E2E", "Straight-line glyphs from JetBrains Mono Bold and Noto Sans JP"),
]

SQUARE = [(0, 0), (0, 40), (40, 40), (40, 0)]  # clockwise in y-up glyph space
STAR = [(50, 100), (79, 9), (2, 65), (98, 65), (21, 9)]
DIAMOND = [(41, 1), (1, 41), (41, 81), (81, 41)]
BOWTIE = [(0, 0), (60, 60), (60, 0), (0, 60)]


def moved(points, dx, dy):
    return [(x + dx, y + dy) for x, y in points]


def all_on(font, ch):
    ends, pts = fg.glyph(font, ch)
    return all(on for _, _, on in pts)


def main():
    args = wb.parse_args("16")
    rng = random.Random(args.seed)
    jb, noto = wb.load(wb.JETBRAINS), wb.load(wb.NOTO_JP)
    g = fg.glyph
    frame = fg.polygon([(0, 0), (0, 90), (90, 90), (90, 0)], list(reversed([(20, 20), (20, 70), (70, 70), (70, 20)])))
    specs = [
        ("16-R1-square", "R1", "a 40 x 40 square at scale 1", fg.fit([fg.polygon(SQUARE)], 1)),
        ("16-R1-triangle", "R1", "a triangle with sloped sides", fg.fit([fg.polygon([(0, 0), (30, 52), (60, 0)])], 2)),
        ("16-R2-star", "R2", "a pentagram as one crossing contour: the centre is filled (winding 2)",
         fg.fit([fg.polygon(STAR)], 2)),
        ("16-R2-overlap", "R2", "two overlapping squares going the same way, one outline: no hole",
         fg.fit([fg.polygon(SQUARE, moved(SQUARE, 20, 20))], 2)),
        ("16-R2-ten", "R2", "U+5341 (ten) from Noto Sans JP: crossing strokes, no hole", fg.fit([g(noto, "十")], 0.25)),
        ("16-R3-frame", "R3", "a square with a reversed square inside: a hole", fg.fit([frame], 2)),
        ("16-R3-opposite-overlap", "R3", "two overlapping squares going opposite ways: the overlap is empty",
         fg.fit([fg.polygon(SQUARE, list(reversed(moved(SQUARE, 20, 20))))], 2)),
        ("16-R3-hash", "R3", "'#' from JetBrains Mono Bold: a counter in the middle", fg.fit([g(jb, "#")], 0.4)),
        ("16-R4-reversed", "R4", "a square drawn counter-clockwise, alone: filled", fg.fit([fg.polygon(list(reversed(SQUARE)))], 2)),
        ("16-R4-bowtie", "R4", "a bow tie: one contour whose halves wind opposite ways", fg.fit([fg.polygon(BOWTIE)], 2)),
        ("16-R5-diamond-half", "R5", "a diamond at scale 1.5: vertices exactly on pixel centres",
         fg.fit([fg.polygon(DIAMOND)], 1.5)),
        ("16-R5-diamond-integer", "R5", "the same diamond at scale 1: vertices on pixel boundaries",
         fg.fit([fg.polygon(DIAMOND)], 1)),
        ("16-R5-W", "R5", "'W' at scale 0.5", fg.fit([g(jb, "W")], 0.5)),
        ("16-R5-M", "R5", "'M' at scale 0.5", fg.fit([g(jb, "M")], 0.5)),
        ("16-R6-two-outlines", "R6", "two overlapping squares as two outlines going opposite ways: both filled",
         fg.fit([fg.polygon(SQUARE), fg.polygon(list(reversed(moved(SQUARE, 20, 20))))], 2)),
    ]
    clipped = fg.fit([g(jb, "Z")], 0.4)
    clipped.place = (clipped.place[0] - 30, clipped.place[1] + 25, clipped.place[2])
    specs.append(("16-R7-clipped", "R7", "'Z' running off the left and bottom edges", clipped))
    specs.append(("16-R7-small", "R7", "'4' at scale 0.15", fg.fit([g(jb, "4")], 0.15)))

    # The overlap cases must give a different picture under even-odd, or they test nothing.
    for case_id in ("16-R2-star", "16-R2-overlap", "16-R2-ten"):
        scene = next(s for c, _, _, s in specs if c == case_id)
        assert fg.differs_by_rule(scene, rng), f"{case_id} looks the same under even-odd"

    pool = [chr(c) for c in range(0x21, 0x7F) if all_on(jb, chr(c))]
    for ch in rng.sample(pool, min(4, len(pool))):
        specs.append((f"16-E2E-s{args.seed}-U+{ord(ch):04X}", "E2E",
                      f"U+{ord(ch):04X} ({jb.getBestCmap()[ord(ch)]}), scale 0.3 (seed {args.seed})",
                      fg.fit([g(jb, ch)], 0.3)))
    cjk = [ch for ch in "世王田五工山上下土口" if all_on(noto, ch)]
    for ch in rng.sample(cjk, min(3, len(cjk))):
        specs.append((f"16-E2E-s{args.seed}-U+{ord(ch):04X}", "E2E",
                      f"U+{ord(ch):04X} from Noto Sans JP, scale 0.25 (seed {args.seed})", fg.fit([g(noto, ch)], 0.25)))

    fg.write_cases("16", False, REQUIREMENTS, specs, args)


if __name__ == "__main__":
    main()
