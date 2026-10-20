"""Test cases for checkpoint 03 (map characters to glyphs, cmap format 12).

Expected outputs come from fontTools' cmap parser (getcmap(0, 4) and the font's
glyph order), cross-checked against a direct struct parse of the subtable, so the
tests don't depend on the reference solution.

    py -P tools/gen_p03.py                                  # tests/03 (seed 1)
    py -P tools/gen_p03.py --seed 77 --out build/fresh/03   # what `.\\check 03 -Fresh` runs
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

SOURCE = f"{wb.FT} cmap.getcmap(0, 4) and getGlyphID, cross-checked against a struct parse"

REQUIREMENTS = [
    ("R1", "Use the platform 0 / encoding 4 subtable, wherever it is listed"),
    ("R2", "Every group maps startCharCode..endCharCode (both included)"),
    ("R3", "Code points above U+FFFF (32-bit codes)"),
    ("R4", "A code point no group covers -> `none`"),
    ("R5", "count = how many code points the subtable maps"),
    ("R6", "No (0, 4) subtable in format 12 -> the single line `unsupported`"),
    ("E2E", "Real fonts and random character maps"),
]
EXPLAIN = "_lines=R6 count=R5 lookup=R2 unsupported=R6 count~unsupported=R1 lookup~unsupported=R1"


def cp_text(cp: int) -> str:
    return f"U+{cp:04X}"


def raw_mapping(data: bytes, cmap: int):
    """The (0, 4) format 12 mapping straight from the bytes, or None."""
    _, n = struct.unpack_from(">HH", data, cmap)
    for i in range(n):
        platform, encoding, offset = struct.unpack_from(">HHI", data, cmap + 4 + 8 * i)
        if (platform, encoding) == (0, 4):
            pos = cmap + offset
            if struct.unpack_from(">H", data, pos)[0] != 12:
                return None
            (groups,) = struct.unpack_from(">I", data, pos + 12)
            mapping = {}
            for g in range(groups):
                start, end, glyph = struct.unpack_from(">III", data, pos + 16 + 12 * g)
                for c in range(start, end + 1):
                    assert c not in mapping, "overlapping groups"
                    mapping[c] = glyph + c - start
            return mapping
    return None


def font_mapping(font_rel: str):
    """{code point: glyph id} from fontTools, or None when the checkpoint says `unsupported`."""
    font = TTFont(wb.ROOT / font_rel)
    sub = font["cmap"].getcmap(0, 4)
    ours = raw_mapping((wb.ROOT / font_rel).read_bytes(), font.reader.tables["cmap"].offset)
    if sub is None or sub.format != 12:
        assert ours is None, f"{font_rel}: struct parse found a (0, 4) format 12 subtable"
        return None, font
    theirs = {cp: font.getGlyphID(name) for cp, name in sub.cmap.items()}
    assert theirs == ours, f"{font_rel}: fontTools and the struct parse disagree"
    return theirs, font


def expected_lines(mapping, queries):
    if mapping is None:
        return ["unsupported"]
    lines = []
    for q in queries:
        if q == "count":
            lines.append(f"count {len(mapping)}")
        else:
            cp = int(q.split()[1][2:], 16)
            lines.append(f"{q} {mapping.get(cp, 'none')}")
    return lines


def table_line(font: TTFont, tag: str) -> str:
    e = font.reader.tables[tag]
    return f'table "{tag}" {e.checkSum} {e.offset} {e.length}'


def names(n: int):
    return [".notdef"] + [f"g{i:04d}" for i in range(1, n)]


def build(path: Path, num_glyphs: int, subtables, order=None):
    """A font whose glyphs are all empty; subtables = [(platform, encoding, format, {cp: gid})]."""
    order = order or names(num_glyphs)
    tables = [(p, e, f, {cp: order[g] for cp, g in m.items()}) for p, e, f, m in subtables]
    best = next((m for p, e, f, m in tables if f in (4, 12)), {})
    wb.build_font(path, {}, order, best, {}, cmap_subtables=tables)
    return path


def move_record_last(path: Path, platform: int, encoding: int):
    """Rewrites the cmap header so the (platform, encoding) record comes last. Records are
    8 bytes at 4-byte-aligned positions, so the table's checksum doesn't change."""
    data = bytearray(path.read_bytes())
    cmap = TTFont(path).reader.tables["cmap"].offset
    n = struct.unpack_from(">H", data, cmap + 2)[0]
    records = [bytes(data[cmap + 4 + 8 * i: cmap + 12 + 8 * i]) for i in range(n)]
    key = struct.pack(">HH", platform, encoding)
    records.sort(key=lambda r: r[:4] == key)
    data[cmap + 4: cmap + 4 + 8 * n] = b"".join(records)
    path.write_bytes(bytes(data))
    order = [struct.unpack(">HH", r[:4]) for r in records]
    assert order[-1] == (platform, encoding)
    return order


def main():
    args = wb.parse_args("03")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, source=SOURCE)
    data_dir = args.out / "data"

    def case(case_id, req, title, font_rel, queries):
        mapping, font = font_mapping(font_rel)
        cases.add(case_id, req, title, [f"font {font_rel}", table_line(font, "cmap"), *queries],
                  expected_lines(mapping, queries), source=SOURCE)
        return mapping

    def lookups(cps):
        return [f"lookup {cp_text(cp)}" for cp in cps]

    jb_map, jb = font_mapping(wb.JETBRAINS)
    noto_map, noto = font_mapping(wb.NOTO_JP)
    jb_records = [(t.platformID, t.platEncID, t.format) for t in jb["cmap"].tables]
    assert jb_records[0] == (0, 3, 4) and jb_records[1] == (0, 4, 12), jb_records

    # R1 - which subtable
    case("03-R1-jetbrains", "R1", "JetBrains Mono: (0, 4) is the 2nd of 5 subtables; the 1st is (0, 3) format 4",
         wb.JETBRAINS, lookups([0x41, 0x61, 0x30, 0x20AC]) + ["count"])
    decoy = {cp: 40 - (cp - 0x41) for cp in range(0x41, 0x5B)}  # A..Z backwards
    real = {cp: 1 + (cp - 0x41) for cp in range(0x41, 0x5B)}    # A..Z forwards
    build(data_dir / "03-R1-decoy-first.ttf", 64,
          [(0, 3, 12, decoy), (0, 4, 12, real), (3, 10, 12, decoy)])
    case("03-R1-decoy-first", "R1",
         "a (0, 3) format 12 subtable with other mappings comes first; (0, 4) is 2nd",
         wb.rel(data_dir / "03-R1-decoy-first.ttf"), lookups([0x41, 0x42, 0x4D, 0x5A]) + ["count"])
    path = build(data_dir / "03-R1-listed-last.ttf", 64,
                 [(0, 3, 4, decoy), (3, 10, 12, decoy), (0, 4, 12, {**real, 0x1F600: 50})])
    order = move_record_last(path, 0, 4)
    case("03-R1-listed-last", "R1",
         f"(0, 4) is the last of {len(order)} records, after a (3, 10) format 12 subtable with other mappings",
         wb.rel(path), lookups([0x41, 0x5A, 0x1F600, 0x61]) + ["count"])

    # R2 - expanding groups
    runs = {**{cp: 1 + cp - 0x0100 for cp in range(0x0100, 0x0500)},    # 1024 codes, one group
            **{cp: 1100 + cp - 0x3041 for cp in range(0x3041, 0x3097)}}  # hiragana, one group
    build(data_dir / "03-R2-long-runs.ttf", 1200, [(0, 4, 12, runs)])
    case("03-R2-long-runs", "R2", "two long groups: U+0100-U+04FF (1024 codes) and U+3041-U+3096",
         wb.rel(data_dir / "03-R2-long-runs.ttf"),
         lookups([0x0100, 0x0101, 0x0300, 0x04FE, 0x04FF, 0x0500, 0x3041, 0x3070, 0x3096, 0x3097]))
    singles = {cp: 30 - 2 * (cp - 0x41) for cp in range(0x41, 0x4F)}  # each code its own group
    singles[0x7E] = 3
    build(data_dir / "03-R2-single-groups.ttf", 40, [(0, 4, 12, singles)])
    case("03-R2-single-groups", "R2", "15 groups of one code each (glyph ids go down by 2)",
         wb.rel(data_dir / "03-R2-single-groups.ttf"), lookups(sorted(singles)))
    case("03-R2-jetbrains-ascii", "R2", "JetBrains Mono: every printable ASCII character",
         wb.JETBRAINS, lookups(range(0x20, 0x7F)))
    case("03-R2-jetbrains-latin1", "R2", "JetBrains Mono: U+00A0-U+00FF (Latin-1)",
         wb.JETBRAINS, lookups(range(0xA0, 0x100)))

    # R3 - beyond the BMP
    nerd = sorted(cp for cp in jb_map if cp >= 0xF0000)
    case("03-R3-nerd-icons", "R3", f"JetBrains Mono: Nerd Font icons above U+F0000 ({len(nerd)} of them)",
         wb.JETBRAINS, lookups([nerd[0], nerd[1], nerd[-1]] + sorted(rng.sample(nerd, 12))))
    astral = {**{cp: 10 + cp - 0x1F600 for cp in range(0x1F600, 0x1F650)},
              0xF600: 5, 0xF601: 6, 0x20000: 7, 0x10FFFD: 8}
    build(data_dir / "03-R3-astral.ttf", 128, [(0, 4, 12, astral)])
    case("03-R3-astral", "R3",
         "U+1F600-U+1F64F, U+20000 and U+10FFFD; U+F600/U+F601 map elsewhere (catches 16-bit codes)",
         wb.rel(data_dir / "03-R3-astral.ttf"),
         lookups([0x1F600, 0x1F601, 0x1F64F, 0xF600, 0xF601, 0xF64F, 0x20000, 0x10FFFD, 0xFFFD]) + ["count"])
    noto_astral = sorted(cp for cp in noto_map if cp > 0xFFFF)
    case("03-R3-noto-supplementary", "R3",
         f"Noto Sans JP: CJK characters above U+FFFF ({len(noto_astral)} of them)",
         wb.NOTO_JP, lookups([noto_astral[0], noto_astral[-1]] + sorted(rng.sample(noto_astral, 10))))

    # R4 - unmapped
    group_edges = sorted({cp + 1 for cp in jb_map if cp + 1 not in jb_map} |
                         {cp - 1 for cp in jb_map if cp - 1 not in jb_map and cp > 0})
    probes = [0x0000, 0x0378, 0xD800, 0xFFFF, 0x10FFFF] + rng.sample(group_edges, 8)
    assert all(cp not in jb_map for cp in probes)
    case("03-R4-jetbrains-unmapped", "R4",
         "JetBrains Mono: unassigned code points and codes just outside a group", wb.JETBRAINS,
         lookups(sorted(probes)))
    gaps = {**{cp: 1 + cp - 0x30 for cp in range(0x30, 0x3A)}, **{cp: 20 + cp - 0x41 for cp in range(0x41, 0x47)}}
    build(data_dir / "03-R4-gaps.ttf", 40, [(0, 4, 12, gaps)])
    case("03-R4-gaps", "R4", "groups 0-9 and A-F: lookups before, between and after them",
         wb.rel(data_dir / "03-R4-gaps.ttf"), lookups([0x2F, 0x30, 0x39, 0x3A, 0x40, 0x41, 0x46, 0x47, 0x61]))

    # R5 - count
    case("03-R5-count-jetbrains", "R5", f"JetBrains Mono: count ({len(jb_map)})", wb.JETBRAINS, ["count"])
    case("03-R5-count-noto", "R5", f"Noto Sans JP: count ({len(noto_map)}), twice", wb.NOTO_JP, ["count", "count"])
    case("03-R5-count-runs", "R5", f"the long-runs font: count ({len(runs)})",
         wb.rel(data_dir / "03-R2-long-runs.ttf"), ["count", "lookup U+0041"])

    # R6 - unsupported
    bmp = {0x41: 1, 0x42: 2, 0x43: 3}
    for case_id, title, subtables in (
            ("03-R6-format4-only", "only (0, 3) and (3, 1) subtables, both format 4", [(0, 3, 4, bmp), (3, 1, 4, bmp)]),
            ("03-R6-windows-12-only", "a (3, 10) format 12 subtable but no (0, 4)", [(3, 1, 4, bmp), (3, 10, 12, bmp)]),
            ("03-R6-format13", "(0, 4) is format 13, which has the same layout as 12 but means something else",
             [(0, 3, 4, bmp), (0, 4, 13, bmp)]),
            ("03-R6-format4-at-0-4", "(0, 4) is format 4", [(0, 4, 4, bmp), (3, 1, 4, bmp)])):
        build(data_dir / f"{case_id}.ttf", 8, subtables)
        case(case_id, "R6", title, wb.rel(data_dir / f"{case_id}.ttf"), ["count", "lookup U+0041", "lookup U+0042"])

    # End to end - real fonts and random character maps
    kanji = [0x4E00, 0x6F22, 0x5B57, 0x65E5, 0x672C, 0x8A9E, 0x3042, 0x30A2, 0x3002, 0xFF21, 0x0041, 0x00E9]
    case("03-E2E-noto-japanese", "E2E", "Noto Sans JP: kanji, kana, punctuation and full-width letters",
         wb.NOTO_JP, lookups(kanji) + ["count"])
    for label, font_rel, mapping in (("jetbrains", wb.JETBRAINS, jb_map), ("noto", wb.NOTO_JP, noto_map)):
        mapped = rng.sample(sorted(mapping), 25)
        unmapped = []
        while len(unmapped) < 10:
            cp = rng.choice([rng.randrange(0x10000), rng.randrange(0x10000, 0x110000)])
            if cp not in mapping:
                unmapped.append(cp)
        cps = mapped + unmapped
        rng.shuffle(cps)
        case(f"03-E2E-{label}-random-s{args.seed}", "E2E",
             f"{Path(font_rel).stem}: 25 mapped and 10 unmapped code points (seed {args.seed})",
             font_rel, lookups(cps) + ["count"])
    for k in range(2):
        mapping, cp, gid = {}, rng.randrange(0x20, 0x3000), 1
        for _ in range(rng.randint(5, 20)):
            if rng.random() < 0.2:
                cp = rng.randrange(cp, max(cp + 1, 0x100000))
            run = rng.choice([1, 1, 2, 5, rng.randint(10, 200)])
            for i in range(run):
                mapping[cp + i] = gid + i
            cp += run + rng.randint(1, 40)
            gid += run + rng.randint(0, 3)
        case_id = f"03-E2E-random-s{args.seed}-{k}"
        build(data_dir / f"{case_id}.ttf", gid + 1, [(0, 4, 12, mapping)])
        keys = sorted(mapping)
        probes = rng.sample(keys, min(15, len(keys))) + [keys[0] - 1, keys[-1] + 1] + \
            [c + 1 for c in rng.sample(keys, 5)]
        case(case_id, "E2E", f"random character map: {len(mapping)} codes up to {cp_text(keys[-1])} (seed {args.seed})",
             wb.rel(data_dir / f"{case_id}.ttf"), lookups(probes) + ["count"])

    cases.save()


if __name__ == "__main__":
    main()
