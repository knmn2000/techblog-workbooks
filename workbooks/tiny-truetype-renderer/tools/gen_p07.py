"""Test cases for checkpoint 07 (decode simple glyphs).

Every expected output comes from fontTools, an independent TrueType
implementation, so the tests don't depend on the reference solution being right.

    py -P tools/gen_p07.py                                  # tests/07 (seed 1)
    py -P tools/gen_p07.py --seed 777 --out build/fresh/07  # what `.\\check 07 -Fresh` runs
    py -P tools/gen_p07.py --all --out build/verify/07      # every simple glyph (verification)
"""

import argparse
import random
import struct
import sys
from array import array
from pathlib import Path

import fontTools
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram
from fontTools.ttLib.tables._g_l_y_f import Glyph, GlyphCoordinates

ROOT = Path(__file__).resolve().parent.parent
FONT_REL = "fonts/JetBrainsMonoNerdFont-Bold.ttf"
FT = f"fontTools {fontTools.version}"
HAND = f"hand-encoded bytes, decoded independently by {FT}"

REQUIREMENTS = [
    ("R1", "One record per input glyph, in input order"),
    ("R2", "Empty glyph (length 0) -> `glyph <id> empty`"),
    ("R3", "Compound glyph (contours < 0) -> `glyph <id> compound`"),
    ("R4", "Header: number of contours and bounding box"),
    ("R5", "Contour end indices in file order; point count = last + 1"),
    ("R6", "Hinting instructions are skipped"),
    ("R7", "REPEAT expanded; on/off for every point, repeats included"),
    ("R8", "1-byte, 2-byte and 'same' deltas -> absolute coordinates"),
    ("E2E", "Real glyphs from JetBrains Mono Bold"),
]

# Hand-made glyph records. `points` is what each byte string is meant to encode;
# the script decodes the bytes with fontTools and stops if the two disagree.
HAND_MADE = [
    dict(id="07-R8-int16", req="R8",
         title="hand-made triangle where every delta is a full int16 (flags 01 01 01)",
         hex="0001 0064 0000 01f4 02bc 0002 0000 01 01 01 0064 0190 ff38 0000 0000 02bc",
         points=[(100, 0, 1), (500, 0, 1), (300, 700, 1)], endPts=[2]),
    dict(id="07-R8-short", req="R8",
         title="hand-made: 1-byte deltas whose sign comes from bits 4/5 (flags 37 26 33 07)",
         hex="0001 0000 0000 00ff 0028 0003 0000 37 26 33 07 0a 05 fa ff 14 14 28",
         points=[(10, 20, 1), (5, 40, 0), (255, 40, 1), (0, 0, 1)], endPts=[3]),
    dict(id="07-R8-negative", req="R8",
         title="hand-made: negative int16 deltas and 'same' on both axes (flags 01 11 20)",
         hex="0001 fed4 ff38 00c8 01f4 0002 0000 01 11 20 fed4 01f4 ff38 02bc",
         points=[(-300, -200, 1), (-300, 500, 1), (200, 500, 0)], endPts=[2]),
    dict(id="07-R7-repeat", req="R7",
         title="hand-made: flag 0x3b with REPEAT count 3 covers points 0-3 (all on-curve)",
         hex="0001 000a 0000 0028 0032 0005 0000 3b 03 35 22 0a 0a 0a 0a 1e 32",
         points=[(10, 0, 1), (20, 0, 1), (30, 0, 1), (40, 0, 1), (40, 50, 1), (10, 50, 0)],
         endPts=[5]),
    dict(id="07-R6-instructions", req="R6",
         title="hand-made: two contours, and 5 instruction bytes that look like flags (all 01)",
         hex="0002 0000 0000 0064 0064 0002 0005 0005 01 01 01 01 01 01 01 01 01 01 01 "
             "0000 0064 ffce ffe2 003c ffe2 0000 0000 0064 ffa6 0000 0046",
         points=[(0, 0, 1), (100, 0, 1), (50, 100, 1), (20, 10, 1), (80, 10, 1), (50, 80, 1)],
         endPts=[2, 5]),
]


def decode(data: bytes, glyf):
    g = Glyph(data)
    g.expand(glyf)
    return g


def points_of(g):
    return [(int(x), int(y), int(f & 1)) for (x, y), f in zip(g.coordinates, g.flags)]


def expected_record(glyph_id, g):
    """The exact text a correct program writes for one glyph."""
    if g is None:
        return f"glyph {glyph_id} empty"
    if g.isComposite():
        return f"glyph {glyph_id} compound"
    ends = "".join(f" {e}" for e in g.endPtsOfContours)
    pts = "".join(f" {x} {y} {'on' if on else 'off'}" for x, y, on in points_of(g))
    return (f"glyph {glyph_id} contours {g.numberOfContours} bbox {g.xMin} {g.yMin} {g.xMax} {g.yMax}\n"
            f"ends{ends}\npoints{pts}")


def repeats_on_curve(record: bytes) -> bool:
    """True if the raw flags apply REPEAT to an on-curve flag."""
    nc = struct.unpack(">h", record[:2])[0]
    if nc <= 0:
        return False
    pos = 10 + 2 * nc
    n = struct.unpack(">H", record[pos - 2:pos])[0] + 1
    pos += 2 + struct.unpack(">H", record[pos:pos + 2])[0]
    count = 0
    while count < n:
        flag = record[pos]
        pos += 1
        if flag & 0x08:
            times = record[pos]
            pos += 1
            if flag & 0x01 and times:
                return True
            count += 1 + times
        else:
            count += 1
    return False


def random_glyph(rng, glyf):
    """A random simple glyph, encoded by fontTools' own compiler."""
    points, on_curve, ends = [], [], []
    x = y = 0
    for _ in range(rng.randint(1, 4)):
        staircase = rng.random() < 0.4  # identical flags in a row, so the compiler uses REPEAT
        step = rng.choice([7, 40, 300])
        for _ in range(rng.randint(3, 14)):
            if staircase:
                dx, dy, on = step, 0, 1
            else:
                dx = rng.choice([0, rng.randint(-255, 255), rng.randint(-1500, 1500)])
                dy = rng.choice([0, rng.randint(-255, 255), rng.randint(-1500, 1500)])
                on = int(rng.random() < 0.6)
            x = max(-16000, min(16000, x + dx))
            y = max(-16000, min(16000, y + dy))
            points.append((x, y))
            on_curve.append(on)
        ends.append(len(points) - 1)

    g = Glyph()
    g.numberOfContours = len(ends)
    g.endPtsOfContours = ends
    g.coordinates = GlyphCoordinates(points)
    g.flags = array("B", on_curve)
    g.program = ttProgram.Program()
    g.program.fromBytecode(bytes(rng.randrange(256) for _ in range(rng.randint(0, 12))))
    data = g.compile(glyf)
    back = decode(data, glyf)
    assert points_of(back) == [(px, py, on) for (px, py), on in zip(points, on_curve)]
    return data, back


class Cases:
    def __init__(self, out_dir: Path, seed: int):
        self.out_dir = out_dir
        self.data_dir = out_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.lines = [
            "# Generated by tools/gen_p07.py - do not edit by hand.",
            f"source {FT}",
            f"seed {seed}",
            "compare records points=x,y,curve",
            # Which requirement a difference most likely comes from, by where it is in the output.
            "explain _lines=R1 glyph~empty=R2 glyph~compound=R3 glyph=R4 ends=R5 "
            "points:count=R5 points:curve=R7 points:x=R8 points:y=R8",
        ]
        self.lines += [f"requirement {rid} {text}" for rid, text in REQUIREMENTS]
        self.count = 0

    def add(self, case_id, req, title, input_lines, expected, source=FT):
        self.lines += [f"case {case_id} {req}", f"title {title}", f"source {source}", "input",
                       *input_lines, "expected", *expected.split("\n"), "end"]
        self.count += 1

    def data_file(self, name: str, data: bytes) -> str:
        path = self.data_dir / f"{name}.bin"
        path.write_bytes(data)
        return path.resolve().relative_to(ROOT).as_posix()

    def save(self):
        (self.out_dir / "cases.txt").write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", type=Path, default=ROOT / "tests" / "07")
    ap.add_argument("--all", action="store_true", help="every simple glyph in the font (verification)")
    args = ap.parse_args()
    out_dir = args.out if args.out.is_absolute() else ROOT / args.out

    font = TTFont(ROOT / FONT_REL)
    glyf, order, cmap = font["glyf"], font.getGlyphOrder(), font.getBestCmap()
    loca = font["loca"]
    glyf_offset = font.reader.tables["glyf"].offset
    raw = (ROOT / FONT_REL).read_bytes()
    rng = random.Random(args.seed)
    cases = Cases(out_dir, args.seed)

    def where(gid):
        return glyf_offset + loca[gid], loca[gid + 1] - loca[gid]

    def glyph_line(gid):
        offset, length = where(gid)
        return f"glyph {gid} {offset} {length}"

    def glyph_of(gid):
        g = glyf[order[gid]]
        return None if where(gid)[1] == 0 else g

    def font_case(case_id, req, title, gids):
        cases.add(case_id, req, title, [f"font {FONT_REL}", *map(glyph_line, gids)],
                  "\n".join(expected_record(gid, glyph_of(gid)) for gid in gids))

    def gid_of(ch):
        return order.index(cmap[ord(ch)])

    simple = [i for i, n in enumerate(order) if glyf[n].numberOfContours > 0 and where(i)[1] > 0]

    if args.all:
        for gid in simple:
            font_case(f"all-gid{gid}", "E2E", f"{order[gid]} (glyph {gid})", [gid])
        cases.save()
        print(f"wrote {out_dir / 'cases.txt'}: {cases.count} cases", file=sys.stderr)
        return

    # R1 - several glyphs in one input
    mixed = [gid_of("-"), gid_of(" "), gid_of("i"), gid_of("A")]
    font_case("07-R1-four-glyphs", "R1", "four glyphs in one input: '-', ' ', 'i', 'A' "
              "(simple, empty, compound, simple)", mixed)

    # R2 - empty glyphs
    for cp in (0x20, 0xA0):
        if cp in cmap and where(order.index(cmap[cp]))[1] == 0:
            font_case(f"07-R2-empty-U+{cp:04X}", "R2", f"U+{cp:04X} ({cmap[cp]}): record length 0",
                      [order.index(cmap[cp])])

    # R3 - compound glyphs are reported, not decoded
    for cp in range(0x21, 0x7F):
        if glyf[cmap[cp]].isComposite():
            font_case(f"07-R3-compound-U+{cp:04X}", "R3",
                      f"'{chr(cp)}' U+{cp:04X} ({cmap[cp]}) is compound", [gid_of(chr(cp))])

    # R4 - header
    font_case("07-R4-B", "R4", "'B': three contours", [gid_of("B")])
    font_case("07-R4-g", "R4", "'g': a descender, so yMin is negative", [gid_of("g")])

    # R5 - contour ends
    ascii_simple = [gid_of(chr(cp)) for cp in range(0x21, 0x7F) if gid_of(chr(cp)) in set(simple)]
    for label, pool in (("ASCII", ascii_simple), ("font", simple)):
        gid = max(pool, key=lambda i: (glyf[order[i]].numberOfContours, -i))
        font_case(f"07-R5-most-contours-{label.lower()}", "R5",
                  f"{order[gid]} (glyph {gid}): the {label} glyph with the most contours "
                  f"({glyf[order[gid]].numberOfContours})", [gid])

    # R6-R8 - hand-made records, checked against fontTools before they're written
    for h in HAND_MADE:
        data = bytes.fromhex(h["hex"].replace(" ", ""))
        g = decode(data, glyf)
        assert points_of(g) == h["points"], f"{h['id']}: the bytes don't encode the intended points"
        assert list(g.endPtsOfContours) == h["endPts"], f"{h['id']}: wrong contour ends"
        path = cases.data_file(h["id"], data)
        cases.add(h["id"], h["req"], h["title"], [f"font {path}", f"glyph 0 0 {len(data)}"],
                  expected_record(0, g), source=HAND)

    # R7 - a real glyph that repeats an on-curve flag
    repeaters = [i for i in ascii_simple if repeats_on_curve(raw[slice(where(i)[0], sum(where(i)))])]
    gid = min(repeaters, key=lambda i: len(glyf[order[i]].coordinates))
    font_case("07-R7-real-repeat", "R7", f"{order[gid]} (glyph {gid}): repeats an on-curve flag", [gid])

    # R8 - the hyphen (the worked example) and random glyphs compiled by fontTools
    font_case("07-R8-hyphen", "R8", "'-' hyphen: the worked example on the problem page", [gid_of("-")])
    for k in range(4):
        data, g = random_glyph(rng, glyf)
        name = f"07-R8-random-s{args.seed}-{k}"
        path = cases.data_file(name, data)
        cases.add(name, "R8", f"random glyph #{k} (seed {args.seed}): {g.numberOfContours} contours, "
                  f"{len(g.coordinates)} points", [f"font {path}", f"glyph 0 0 {len(data)}"],
                  expected_record(0, g), source=f"glyph compiled and decoded by {FT}")

    # End to end - every simple ASCII glyph, then a sample of the rest of the font
    for gid in ascii_simple:
        cp = next(c for c in range(0x21, 0x7F) if order.index(cmap[c]) == gid)
        font_case(f"07-E2E-U+{cp:04X}", "E2E", f"'{chr(cp)}' U+{cp:04X} ({order[gid]}, glyph {gid})", [gid])
    rest = [i for i in simple if i not in set(ascii_simple)]
    by_points = sorted(rest, key=lambda i: -len(glyf[order[i]].coordinates))[:5]
    by_contours = sorted(rest, key=lambda i: -glyf[order[i]].numberOfContours)[:5]
    rest_repeaters = [i for i in rest if repeats_on_curve(raw[slice(where(i)[0], sum(where(i)))])]
    picked = list(dict.fromkeys(by_points + by_contours + rng.sample(rest_repeaters, 10) + rng.sample(rest, 20)))
    for gid in picked:
        reason = ("most points" if gid in by_points else "most contours" if gid in by_contours
                  else "repeats an on-curve flag" if gid in rest_repeaters else "random pick")
        font_case(f"07-E2E-gid{gid}", "E2E",
                  f"{order[gid]} (glyph {gid}, {len(glyf[order[gid]].coordinates)} points, {reason})", [gid])

    cases.save()
    print(f"wrote {out_dir / 'cases.txt'}: {cases.count} cases. "
          f"{len(repeaters)}/{len(ascii_simple)} simple ASCII glyphs repeat an on-curve flag.", file=sys.stderr)


if __name__ == "__main__":
    main()
