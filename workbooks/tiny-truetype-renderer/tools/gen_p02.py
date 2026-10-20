"""Test cases for checkpoint 02 (read the table directory).

Expected outputs come from parsing each file's directory with Python's struct
module, cross-checked against fontTools' own directory reader (SFNTReader), so the
tests don't depend on the reference solution.

    py -P tools/gen_p02.py                                  # tests/02 (seed 1)
    py -P tools/gen_p02.py --seed 77 --out build/fresh/02   # what `.\\check 02 -Fresh` runs
"""

import io
import os
import random
import struct
import sys
from array import array
from pathlib import Path

os.environ.setdefault("SOURCE_DATE_EPOCH", "1700000000")  # fontTools timestamps: same bytes every run

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402
from fontTools.ttLib import TTFont, newTable  # noqa: E402
from fontTools.ttLib.sfnt import SFNTReader  # noqa: E402
from fontTools.ttLib.tables import ttProgram  # noqa: E402

SOURCE = f"Python struct, cross-checked against {wb.FT} SFNTReader"

REQUIREMENTS = [
    ("R1", "Header: numTables after the scaler type; search fields skipped"),
    ("R2", "Records: tag, then checkSum, offset, length (big-endian uint32)"),
    ("R3", "Tags exactly as stored: 4 characters, trailing spaces kept"),
    ("E2E", "Real fonts and random directories"),
]


def parse_directory(data: bytes):
    """(numTables, [(tag, checkSum, offset, length)]) straight from the bytes."""
    (num_tables,) = struct.unpack_from(">H", data, 4)
    records = [struct.unpack_from(">4sIII", data, 12 + 16 * i) for i in range(num_tables)]
    return num_tables, [(tag.decode("latin-1"), cs, off, ln) for tag, cs, off, ln in records]


def expected_for(data: bytes) -> list:
    num_tables, records = parse_directory(data)
    reader = SFNTReader(io.BytesIO(data), checkChecksums=0)  # independent check
    assert reader.numTables == num_tables, "struct and fontTools disagree on numTables"
    theirs = {str(tag): (e.checkSum, e.offset, e.length) for tag, e in reader.tables.items()}
    ours = {tag: (cs, off, ln) for tag, cs, off, ln in records}
    assert theirs == ours and len(ours) == num_tables, "struct and fontTools disagree on the records"
    return [f"tables {num_tables}"] + [f'table "{tag}" {cs} {off} {ln}' for tag, cs, off, ln in records]


def directory(records, scaler=b"\x00\x01\x00\x00", search=None, tail=b"") -> bytes:
    """A hand-made file: header, records, then `tail`. records: [(tag, checkSum, offset, length)]."""
    n = len(records)
    if search is None:
        es = n.bit_length() - 1 if n else 0
        sr = 16 << es if n else 0
        search = (sr, es, n * 16 - sr)
    data = scaler + struct.pack(">HHHH", n, *search)
    for tag, cs, off, ln in records:
        assert len(tag) == 4
        data += tag.encode("latin-1") + struct.pack(">III", cs, off, ln)
    return data + tail


def tiny_font(path: Path, extra_tables=(), drop_tables=()) -> Path:
    """A small TrueType font built by fontTools, with tables added or removed."""
    a = wb.simple_glyph([[(50, 0, 1), (450, 0, 1), (250, 700, 1)]])
    o = wb.simple_glyph([[(50, 0, 1), (450, 0, 1), (450, 500, 1), (50, 500, 1)],
                         [(150, 100, 1), (150, 400, 1), (350, 400, 1), (350, 100, 1)]])
    wb.build_font(path, {"A": a, "O": o}, [".notdef", "space", "A", "O"],
                  {0x20: "space", 0x41: "A", 0x4F: "O"}, {"A": 500, "O": 500})
    font = TTFont(path)
    for tag in extra_tables:
        table = newTable(tag)
        if tag == "cvt ":
            table.values = array("h", [0, 20, -40, 700])
        elif tag in ("fpgm", "prep"):
            table.program = ttProgram.Program()
            table.program.fromBytecode(b"\xb0\x01\x1d" if tag == "prep" else b"\xb0\x00\x2c\x2d")
        elif tag == "gasp":
            table.version = 1
            table.gaspRange = {8: 2, 0xFFFF: 15}
        font[tag] = table
    for tag in drop_tables:
        del font[tag]
    font.save(path)
    return path


def main():
    args = wb.parse_args("02")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "unordered table=tag,checkSum,offset,length", REQUIREMENTS,
                     "tables=R1 table=R2 table:tag=R3", source=SOURCE)
    data_dir = args.out / "data"

    def font_case(case_id, req, title, path):
        rel = wb.rel(path) if isinstance(path, Path) else path
        cases.add(case_id, req, title, [f"font {rel}"], expected_for((wb.ROOT / rel).read_bytes()), source=SOURCE)

    def hand_case(case_id, req, title, data):
        rel = cases.data_file(f"{case_id}.bin", data)
        cases.add(case_id, req, title, [f"font {rel}"], expected_for(data), source=SOURCE)

    # R1 - the header
    hand_case("02-R1-no-tables", "R1", "hand-made: a 12-byte header with numTables 0", directory([]))
    hand_case("02-R1-true-scaler", "R1",
              "hand-made: scaler type 'true' and search fields that are all ffff (skip them, don't use them)",
              directory([("cmap", 0x11111111, 64, 8), ("glyf", 0x22222222, 72, 4), ("head", 0x33333333, 76, 4)],
                        scaler=b"true", search=(0xFFFF, 0xFFFF, 0xFFFF), tail=bytes(16)))
    hand_case("02-R1-one-table", "R1", "hand-made: numTables 1, so the search fields are 16 0 0",
              directory([("name", 0x0A0B0C0D, 28, 6)], tail=b"\x00\x00\x00\x00\x00\x00"))

    # R2 - the record fields
    tiny_font(data_dir / "02-R2-tiny-basic.ttf")
    font_case("02-R2-tiny-basic", "R2", "a 4-glyph font built by fontTools (10 tables)", data_dir / "02-R2-tiny-basic.ttf")
    tiny_font(data_dir / "02-R2-tiny-stripped.ttf", drop_tables=("OS/2", "name", "post"))
    font_case("02-R2-tiny-stripped", "R2", "the same font without OS/2, name and post (7 tables)",
              data_dir / "02-R2-tiny-stripped.ttf")
    hand_case("02-R2-big-values", "R2",
              "hand-made: field values of 2^31 and more, and byte patterns that differ when reversed",
              directory([("BASE", 0xFFFFFFFF, 0x80000000, 0x00000001), ("DSIG", 0x80000001, 0x01020304, 0xFEDCBA98),
                         ("kern", 0x00000000, 0xA0B0C0D0, 0x7FFFFFFF)]))

    # R3 - tags with trailing spaces
    tiny_font(data_dir / "02-R3-tiny-hinted.ttf", extra_tables=("cvt ", "fpgm", "prep", "gasp"))
    font_case("02-R3-tiny-hinted", "R3", "the 4-glyph font plus 'cvt ', fpgm, prep and gasp (14 tables)",
              data_dir / "02-R3-tiny-hinted.ttf")
    hand_case("02-R3-spaces", "R3", "hand-made: tags 'A   ', 'CFF ', 'ab  ', 'cvt ' and 'zzz ' (1 to 3 trailing spaces)",
              directory([("A   ", 1, 108, 4), ("CFF ", 2, 112, 4), ("ab  ", 3, 116, 4), ("cvt ", 4, 120, 4),
                         ("head", 5, 124, 4), ("zzz ", 6, 128, 4)], tail=bytes(24)))

    # End to end - the real fonts, then random directories
    font_case("02-E2E-jetbrains", "E2E", "JetBrains Mono Bold (18 tables, including 'cvt ')", wb.JETBRAINS)
    font_case("02-E2E-noto", "E2E", "Noto Sans JP, a variable font (23 tables)", wb.NOTO_JP)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/2"
    for k in range(3):
        tags = set()
        for _ in range(rng.randint(1, 30)):
            size = rng.choice([4, 4, 4, 3, 2, 1])
            tags.add("".join(rng.choice(letters) for _ in range(size)).ljust(4))
        records = [(tag, rng.randrange(1 << 32), rng.randrange(1 << 32), rng.randrange(1 << 20)) for tag in sorted(tags)]
        case_id = f"02-E2E-random-s{args.seed}-{k}"
        hand_case(case_id, "E2E", f"random directory of {len(records)} records (seed {args.seed})", directory(records))

    cases.save()


if __name__ == "__main__":
    main()
