"""Test cases for checkpoint 05 (read the horizontal metrics).

Expected outputs come from fontTools (hhea.ascent, hhea.descent and the decoded
hmtx table), cross-checked against a struct parse of hmtx, so the tests don't
depend on the reference solution.

    py -P tools/gen_p05.py                                  # tests/05 (seed 1)
    py -P tools/gen_p05.py --seed 77 --out build/fresh/05   # what `.\\check 05 -Fresh` runs
"""

import os
import random
import struct
import sys
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "1700000000")  # fontTools timestamps: same bytes every run

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

SOURCE = f"{wb.FT} hhea and hmtx, cross-checked against a struct parse of hmtx"
TAGS = ("hhea", "hmtx", "maxp")

REQUIREMENTS = [
    ("R1", "ascent and descent: the int16 values at hhea + 4 and + 6"),
    ("R2", "Glyphs below numberOfHMetrics: their own advance and lsb"),
    ("R3", "Later glyphs: the last advance, lsb from the array after"),
    ("E2E", "Real fonts and random small fonts"),
]
EXPLAIN = "_lines=R2 ascent=R1 glyph=R2 glyph~missing=R3"


def metrics(font_rel: str):
    """(ascent, descent, numberOfHMetrics, [(advance, lsb) per glyph id], font) from fontTools."""
    font = TTFont(wb.ROOT / font_rel)
    hhea, hmtx, order = font["hhea"], font["hmtx"], font.getGlyphOrder()
    per_glyph = [tuple(hmtx[name]) for name in order]
    # Cross-check: the raw hmtx bytes.
    data = (wb.ROOT / font_rel).read_bytes()
    at, n, long = font.reader.tables["hmtx"].offset, len(order), hhea.numberOfHMetrics
    raw = [struct.unpack_from(">Hh", data, at + 4 * i) for i in range(long)]
    raw += [(raw[-1][0], struct.unpack_from(">h", data, at + 4 * long + 2 * (i - long))[0]) for i in range(long, n)]
    assert raw == per_glyph, f"{font_rel}: fontTools and struct disagree about hmtx"
    assert n == font["maxp"].numGlyphs
    return hhea.ascent, hhea.descent, long, per_glyph, font


def table_lines(font: TTFont):
    return [f'table "{tag}" {e.checkSum} {e.offset} {e.length}'
            for tag, e in sorted(font.reader.tables.items()) if tag in TAGS]


def outline(x_min: int, width: int = 300):
    return wb.simple_glyph([[(x_min, 0, 1), (x_min + width, 0, 1), (x_min + width // 2, 600, 1)]])


def tiny_font(path: Path, spec, ascent=800, descent=-200):
    """spec: [(name, advance, xMin or None for an empty glyph)], glyph 0 first."""
    order = [name for name, _, _ in spec]
    glyphs = {name: outline(x) for name, _, x in spec if x is not None}
    advances = {name: adv for name, adv, _ in spec}
    cmap = {0x41 + i: name for i, name in enumerate(order[1:])}
    wb.build_font(path, glyphs, order, cmap, advances, ascent=ascent, descent=descent)
    return wb.rel(path)


def main():
    args = wb.parse_args("05")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, source=SOURCE)
    data_dir = args.out / "data"

    def case(case_id, req, title, font_rel, queries, check=None):
        ascent, descent, long, per_glyph, font = metrics(font_rel)
        if check:
            assert check(long, len(per_glyph)), f"{case_id}: numberOfHMetrics {long} of {len(per_glyph)} glyphs"
        expected = []
        for q in queries:
            if q == "font-metrics":
                expected.append(f"ascent {ascent} descent {descent}")
            else:
                gid = int(q.split()[1])
                expected.append(f"glyph {gid} advance {per_glyph[gid][0]} lsb {per_glyph[gid][1]}")
        cases.add(case_id, req, title, [f"font {font_rel}", *table_lines(font), *queries], expected, source=SOURCE)
        return long, len(per_glyph)

    def glyphs(ids):
        return [f"glyph {i}" for i in ids]

    every = lambda long, n: long == n  # noqa: E731
    fewer = lambda long, n: long < n   # noqa: E731

    # R1 - ascent and descent
    case("05-R1-jetbrains", "R1", "JetBrains Mono: ascent 1020, descent -300", wb.JETBRAINS, ["font-metrics"])
    case("05-R1-noto", "R1", "Noto Sans JP: ascent and descent", wb.NOTO_JP, ["font-metrics", "glyph 0"])
    rel = tiny_font(data_dir / "05-R1-extremes.ttf", [(".notdef", 500, 50), ("A", 600, 20)],
                    ascent=32767, descent=-32768)
    case("05-R1-extremes", "R1", "a small font with ascent 32767 and descent -32768 (the int16 limits)",
         rel, ["font-metrics"])
    rel = tiny_font(data_dir / "05-R1-small-descent.ttf", [(".notdef", 500, 50), ("A", 600, 20)],
                    ascent=1, descent=-1)
    case("05-R1-small-descent", "R1", "a small font with ascent 1 and descent -1 (ffff)", rel, ["font-metrics"])

    # R2 - glyphs that have their own longHorMetric
    jb_ascii = [0, 1, 2, 3, 4, 5, 17, 37, 69, 77]
    case("05-R2-jetbrains", "R2", "JetBrains Mono (monospaced, numberOfHMetrics = numGlyphs): a few glyphs",
         wb.JETBRAINS, glyphs(jb_ascii), check=every)
    noto = TTFont(wb.ROOT / wb.NOTO_JP)
    cmap = noto.getBestCmap()
    noto_ids = [0, 1] + [noto.getGlyphID(cmap[ord(c)]) for c in "AWij.,あア漢字"]
    case("05-R2-noto", "R2", "Noto Sans JP (proportional): Latin letters, punctuation, kana and kanji",
         wb.NOTO_JP, glyphs(noto_ids), check=every)
    spec = [(".notdef", 500, 50), ("space", 250, None), ("A", 620, -40), ("B", 580, 0), ("C", 410, -125),
            ("D", 700, 35), ("E", 520, -3)]
    rel = tiny_font(data_dir / "05-R2-negative-lsb.ttf", spec)
    case("05-R2-negative-lsb", "R2", "7 glyphs, all different advances; some outlines start left of 0 (negative lsb)",
         rel, glyphs(range(len(spec))), check=every)

    # R3 - glyphs past numberOfHMetrics
    spec = [(".notdef", 500, 50), ("A", 620, 30), ("B", 580, 10), ("C", 600, 70), ("D", 600, 5), ("E", 600, 140)]
    rel = tiny_font(data_dir / "05-R3-shared-advance.ttf", spec)
    long, n = case("05-R3-shared-advance", "R3",
                   "the last 3 glyphs share advance 600, so only 4 long metrics are stored",
                   rel, glyphs(range(len(spec))), check=fewer)
    assert long == 4 and n == 6
    spec = [(".notdef", 500, 50), ("A", 640, 20), ("B", 500, -60), ("C", 500, -5), ("D", 500, None), ("E", 500, -230)]
    rel = tiny_font(data_dir / "05-R3-negative-tail.ttf", spec)
    case("05-R3-negative-tail", "R3", "trailing glyphs with negative lsb values in the lsb-only array",
         rel, ["font-metrics"] + glyphs(range(len(spec))), check=fewer)
    spec = [(".notdef", 600, 50)] + [(f"g{i}", 600, rng.randint(-50, 150)) for i in range(1, 9)]
    rel = tiny_font(data_dir / "05-R3-one-metric.ttf", spec)
    long, n = case("05-R3-one-metric", "R3", "every glyph has advance 600, so numberOfHMetrics is 1",
                   rel, glyphs(range(len(spec))))
    assert long == 1

    # End to end - random glyphs of the real fonts, then random small fonts
    for label, font_rel in (("jetbrains", wb.JETBRAINS), ("noto", wb.NOTO_JP)):
        n = TTFont(wb.ROOT / font_rel)["maxp"].numGlyphs
        case(f"05-E2E-{label}-random-s{args.seed}", "E2E", f"{Path(font_rel).stem}: 25 random glyphs (seed {args.seed})",
             font_rel, ["font-metrics"] + glyphs(sorted(rng.sample(range(n), 25))))
    for k in range(2):
        count = rng.randint(4, 30)
        tail = rng.randint(0, count - 2)  # how many glyphs at the end share one advance
        shared = rng.choice([500, 600, 1000])
        spec = []
        for i in range(count):
            advance = shared if i >= count - tail else rng.randint(100, 1200)
            spec.append((".notdef" if i == 0 else f"g{i:02d}", advance,
                         None if rng.random() < 0.15 else rng.randint(-300, 300)))
        case_id = f"05-E2E-random-s{args.seed}-{k}"
        rel = tiny_font(data_dir / f"{case_id}.ttf", spec, ascent=rng.randint(500, 2000), descent=-rng.randint(0, 800))
        long, _ = metrics(rel)[2:4]
        case(case_id, "E2E", f"random font: {count} glyphs, {count - long} after numberOfHMetrics (seed {args.seed})",
             rel, ["font-metrics"] + glyphs(range(count)))

    cases.save()


if __name__ == "__main__":
    main()
