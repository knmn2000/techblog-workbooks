"""Test cases for checkpoint 04 (locate glyph records with loca).

Expected outputs come from fontTools (maxp.numGlyphs, head.indexToLocFormat, the
decoded loca table and the glyf table's offset in the directory), cross-checked
against a struct parse of the raw loca entries, so the tests don't depend on the
reference solution.

    py -P tools/gen_p04.py                                  # tests/04 (seed 1)
    py -P tools/gen_p04.py --seed 77 --out build/fresh/04   # what `.\\check 04 -Fresh` runs
"""

import logging
import os
import random
import struct
import sys
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "1700000000")  # fontTools timestamps: same bytes every run

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402
from fontTools.ttLib.sfnt import SFNTReader, SFNTWriter  # noqa: E402

logging.getLogger("fontTools").setLevel(logging.ERROR)  # "too much 'glyf' data" is on purpose
SOURCE = f"{wb.FT} maxp, head, loca and the glyf offset, cross-checked against a struct parse of loca"
TAGS = ("glyf", "head", "loca", "maxp")

REQUIREMENTS = [
    ("R1", "numGlyphs = the uint16 at maxp + 4"),
    ("R2", "indexToLocFormat = the int16 at head + 50 (0 short, 1 long)"),
    ("R3", "Short format: each uint16 entry is the offset / 2"),
    ("R4", "Offset = glyf table offset + loca entry (x2 when short)"),
    ("R5", "Length = next entry - this one (x2 if short); numGlyphs + 1 entries"),
    ("E2E", "Real fonts and random small fonts"),
]
EXPLAIN = ("_lines=R1 glyphs:numGlyphs=R1 glyphs:loca=R2 glyphs:format=R2 "
           "glyph:id=R1 glyph:offset=R4 glyph:length=R5")


def locations(font_rel: str):
    """(numGlyphs, 'short'|'long', [(offset, length) per glyph], font) from fontTools."""
    font = TTFont(wb.ROOT / font_rel)
    n = font["maxp"].numGlyphs
    fmt = font["head"].indexToLocFormat
    loca = list(font["loca"])
    glyf = font.reader.tables["glyf"].offset
    # Cross-check: the raw entries, read with struct.
    data = (wb.ROOT / font_rel).read_bytes()
    at = font.reader.tables["loca"].offset
    raw = [2 * v for v in struct.unpack_from(f">{n + 1}H", data, at)] if fmt == 0 else \
        list(struct.unpack_from(f">{n + 1}I", data, at))
    assert len(loca) == n + 1 and raw == loca, f"{font_rel}: fontTools and struct disagree about loca"
    assert fmt in (0, 1)
    return n, ("short" if fmt == 0 else "long"), [(glyf + loca[i], loca[i + 1] - loca[i]) for i in range(n)], font


def table_lines(font: TTFont):
    return [f'table "{tag}" {e.checkSum} {e.offset} {e.length}'
            for tag, e in sorted(font.reader.tables.items()) if tag in TAGS]


def random_outline(rng, points: int):
    pts, x, y = [], 0, 0
    for _ in range(points):
        x = max(-2000, min(2000, x + rng.choice([rng.randint(-255, 255), rng.randint(-1500, 1500), 0])))
        y = max(-2000, min(2000, y + rng.choice([rng.randint(-255, 255), rng.randint(-1500, 1500), 0])))
        pts.append((x, y, int(rng.random() < 0.6)))
    return wb.simple_glyph([pts])


def shapes():
    tri = wb.simple_glyph([[(50, 0, 1), (450, 0, 1), (250, 700, 1)]])
    box = wb.simple_glyph([[(50, 0, 1), (450, 0, 1), (450, 500, 1), (50, 500, 1)]])
    ring = wb.simple_glyph([[(50, 0, 1), (450, 0, 1), (450, 500, 1), (50, 500, 1)],
                            [(150, 100, 1), (150, 400, 1), (350, 400, 1), (350, 100, 1)]])
    curve = wb.simple_glyph([[(0, 0, 1), (250, 0, 0), (500, 0, 1), (500, 250, 0), (500, 500, 1), (0, 500, 1)]],
                            program=b"\xb0\x00")
    return {"tri": tri, "box": box, "ring": ring, "curve": curve}


def tiny_font(path: Path, glyphs, padding=None, spare=b""):
    """glyphs: [(name, Glyph or None)], glyph 0 first. None means an empty glyph.
    padding=0 stores glyphs unpadded (odd lengths, so fontTools writes a long loca).
    spare: bytes appended to the glyf table after the last glyph."""
    order = [name for name, _ in glyphs]
    outlines = {name: g for name, g in glyphs if g is not None}
    cmap = {0x41 + i: name for i, name in enumerate(order[1:])}
    wb.build_font(path, outlines, order, cmap, {})
    if padding is not None:
        font = TTFont(path)
        font["glyf"].padding = padding
        font.save(path)
    if spare:
        with open(path, "rb") as f:
            reader = SFNTReader(f, checkChecksums=0)
            version, tables = reader.sfntVersion, {tag: reader[tag] for tag in reader.tables}
        tables["glyf"] += spare
        with open(path, "wb") as f:
            writer = SFNTWriter(f, len(tables), version)
            for tag, data in tables.items():
                writer[tag] = data
            writer.close()
    return wb.rel(path)


def main():
    args = wb.parse_args("04")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "records glyphs=numGlyphs,loca,format glyph=id,offset,length",
                     REQUIREMENTS, EXPLAIN, source=SOURCE)
    data_dir = args.out / "data"
    s = shapes()

    def case(case_id, req, title, font_rel, ids, expect_format=None):
        n, fmt, where, font = locations(font_rel)
        if expect_format:
            assert fmt == expect_format, f"{case_id}: loca is {fmt}, expected {expect_format}"
        expected = [f"glyphs {n} loca {fmt}"] + [f"glyph {i} {where[i][0]} {where[i][1]}" for i in ids]
        cases.add(case_id, req, title, [f"font {font_rel}", *table_lines(font), *[f"glyph {i}" for i in ids]],
                  expected, source=SOURCE)
        return where

    jb_n, _, jb_where, jb = locations(wb.JETBRAINS)
    noto_n, _, noto_where, noto = locations(wb.NOTO_JP)

    # R1 - numGlyphs
    case("04-R1-jetbrains-header", "R1", "JetBrains Mono with no glyph lines: just the header line", wb.JETBRAINS, [],
         expect_format="long")
    seven = [(".notdef", s["box"]), ("space", None), ("A", s["tri"]), ("B", s["box"]), ("C", s["ring"]),
             ("D", s["curve"]), ("E", s["tri"])]
    case("04-R1-tiny-seven", "R1", "a 7-glyph font: first and last glyph",
         tiny_font(data_dir / "04-R1-tiny-seven.ttf", seven), [0, 6], expect_format="short")

    # R2 - the loca format
    case("04-R2-noto", "R2", "Noto Sans JP: long loca, and odd offsets (no padding)", wb.NOTO_JP, [0, 1, 2, 3, 100, 5000],
         expect_format="long")
    mixed = [(".notdef", s["box"]), ("A", s["tri"]), ("B", s["curve"]), ("C", s["ring"]), ("D", s["tri"])]
    case("04-R2-tiny-long", "R2", "5 small glyphs stored unpadded, so fontTools wrote a long loca",
         tiny_font(data_dir / "04-R2-tiny-long.ttf", mixed, padding=0), range(5), expect_format="long")
    case("04-R2-tiny-short", "R2", "the same 5 glyphs padded to even lengths: a short loca",
         tiny_font(data_dir / "04-R2-tiny-short.ttf", mixed), range(5), expect_format="short")

    # R3 - short entries are halved offsets
    eight = [(".notdef", s["box"]), ("A", s["ring"]), ("B", s["tri"]), ("C", s["curve"]), ("D", s["ring"]),
             ("E", s["box"]), ("F", s["curve"]), ("G", s["tri"])]
    case("04-R3-short-x2", "R3", "8 glyphs in a short loca: every offset is twice the stored value",
         tiny_font(data_dir / "04-R3-short-x2.ttf", eight), range(8), expect_format="short")
    big_rng = random.Random(4)  # fixed: this font is the same for every seed
    big = [(".notdef", s["box"])] + [(f"g{i:03d}", random_outline(big_rng, 300)) for i in range(1, 100)]
    rel = tiny_font(data_dir / "04-R3-short-past-64k.ttf", big)
    where = case("04-R3-short-past-64k", "R3", "100 glyphs, about 80 KB of glyf, still short: offsets pass 65535",
                 rel, [0, 1, 50, 97, 98, 99], expect_format="short")
    assert where[-1][0] - TTFont(wb.ROOT / rel).reader.tables["glyf"].offset > 65535, "glyf too small"

    # R4 - absolute offsets
    jb_cmap = jb.getBestCmap()
    ids = [jb.getGlyphID(jb_cmap[ord(c)]) for c in "- iA"]
    case("04-R4-jetbrains-07", "R4", "JetBrains Mono: '-', ' ', 'i', 'A', the glyphs of checkpoint 7's example",
         wb.JETBRAINS, ids)
    noto_cmap = noto.getBestCmap()
    case("04-R4-noto-kanji", "R4", "Noto Sans JP: the glyphs for 'A', 'a', kana and kanji",
         wb.NOTO_JP, [noto.getGlyphID(noto_cmap[ord(c)]) for c in "Aaあア漢字"])

    # R5 - lengths, including the last glyph
    empty_last = [(".notdef", s["box"]), ("A", s["tri"]), ("B", s["ring"]), ("space", None)]
    rel = tiny_font(data_dir / "04-R5-empty-last-spare.ttf", empty_last, spare=b"\0\0\0\0")
    font = TTFont(wb.ROOT / rel)
    assert font.reader.tables["glyf"].length == font["loca"][-1] + 4
    case("04-R5-empty-last-spare", "R5",
         "the last glyph is empty, and glyf has 4 spare bytes after it (glyf length isn't loca's last entry)",
         rel, range(4))
    case("04-R5-outline-last", "R5", "the last glyph has an outline: its length needs loca's extra entry",
         tiny_font(data_dir / "04-R5-outline-last.ttf", [(".notdef", None), ("A", s["box"]), ("B", s["curve"])]),
         range(3))
    runs = [(".notdef", None), ("space", None), ("nbsp", None), ("A", s["tri"]), ("cr", None), ("B", s["ring"]),
            ("tab", None), ("zw", None)]
    case("04-R5-empty-runs", "R5", "an empty .notdef, empty glyphs in a row, and an empty last glyph",
         tiny_font(data_dir / "04-R5-empty-runs.ttf", runs), range(8))
    case("04-R5-jetbrains-ends", "R5", f"JetBrains Mono: glyphs 0-5 (1-4 are empty) and the last two "
         f"({jb_n - 1} is empty)", wb.JETBRAINS, [0, 1, 2, 3, 4, 5, jb_n - 2, jb_n - 1])
    assert jb_where[-1][1] == 0 and noto_where[-1][1] > 0
    case("04-R5-noto-ends", "R5", f"Noto Sans JP: the first and last glyphs ({noto_n - 1} has an outline)",
         wb.NOTO_JP, [0, 1, noto_n - 2, noto_n - 1])

    # End to end - random glyphs of the real fonts, then random small fonts
    for label, font_rel, n in (("jetbrains", wb.JETBRAINS, jb_n), ("noto", wb.NOTO_JP, noto_n)):
        case(f"04-E2E-{label}-random-s{args.seed}", "E2E", f"{Path(font_rel).stem}: 30 random glyphs (seed {args.seed})",
             font_rel, sorted(rng.sample(range(n), 30)))
    for k in range(2):
        glyphs = [(".notdef", rng.choice([None, s["box"]]))]
        for i in range(1, rng.randint(5, 20)):
            glyphs.append((f"g{i:02d}", rng.choice([None, s["tri"], s["box"], s["ring"], s["curve"],
                                                    random_outline(rng, rng.randint(3, 40))])))
        padding = rng.choice([None, 0])
        spare = rng.choice([b"", b"\0\0"])
        case_id = f"04-E2E-random-s{args.seed}-{k}"
        rel = tiny_font(data_dir / f"{case_id}.ttf", glyphs, padding=padding, spare=spare)
        empties = sum(g is None for _, g in glyphs)
        case(case_id, "E2E", f"random font: {len(glyphs)} glyphs, {empties} empty, "
             f"{'unpadded' if padding == 0 else 'padded'} (seed {args.seed})", rel, range(len(glyphs)))

    cases.save()


if __name__ == "__main__":
    main()
