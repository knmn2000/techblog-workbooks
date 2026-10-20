"""Test cases for checkpoint 01 (read big-endian numbers).

Every expected value comes from Python's struct module (exact decimal arithmetic
for F2Dot14), never from the reference solution. Values read from real fonts are
also cross-checked against what fontTools parses for the same fields.

    py -P tools/gen_p01.py                                  # tests/01 (seed 1)
    py -P tools/gen_p01.py --seed 77 --out build/fresh/01   # what `.\\check 01 -Fresh` runs
"""

import random
import struct
import sys
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402

STRUCT = "Python struct (>B >b >H >h >I >i; F2Dot14 = >h / 16384 exactly)"
FONT_SOURCE = f"Python struct at offsets from the table directory, cross-checked against {wb.FT}"

REQUIREMENTS = [
    ("R1", "Unsigned reads (u8, u16, u32), most significant byte first"),
    ("R2", "Signed reads (i8, i16, i32): two's complement"),
    ("R3", "F2Dot14 = signed 16-bit value / 16384"),
    ("R4", "jump moves to an absolute offset; skip moves forward"),
    ("R5", "A read past the end of the file -> `eof`, then stop"),
    ("E2E", "Real font fields and random operation sequences"),
]

FORMATS = {"u8": ">B", "i8": ">b", "u16": ">H", "i16": ">h", "u32": ">I", "i32": ">i", "f2dot14": ">h"}
READS = list(FORMATS)

# Which requirement a difference most likely comes from, by the operation on the line.
EXPLAIN = " ".join(["_lines=R5", "eof=R5", "u8=R1", "u16=R1", "u32=R1", "i8=R2", "i16=R2", "i32=R2",
                    "f2dot14=R3"] + [f"{op}~eof=R5" for op in READS])


def f2dot14_text(raw: int) -> str:
    """raw / 16384 written out exactly (it has at most 14 digits after the point)."""
    return format(Decimal(raw) / Decimal(16384), "f")


def expected_lines(data: bytes, ops) -> list:
    """What a correct program writes for `ops` on a file holding `data`."""
    pos, out = 0, []
    for op in ops:
        name, *arg = op.split()
        if name == "jump":
            pos = int(arg[0])
            continue
        if name == "skip":
            pos += int(arg[0])
            continue
        fmt = FORMATS[name]
        size = struct.calcsize(fmt)
        if pos + size > len(data):
            out.append("eof")
            break
        (value,) = struct.unpack_from(fmt, data, pos)
        pos += size
        out.append(f"{name} {f2dot14_text(value) if name == 'f2dot14' else value}")
    return out


def main():
    args = wb.parse_args("01")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "records tolerance=0.000001", REQUIREMENTS, EXPLAIN, source=STRUCT)

    def hand(case_id, req, title, hex_bytes, ops, intended):
        """A hand-made byte file. `intended` is what the bytes are meant to hold;
        the script stops if struct reads something else."""
        data = bytes.fromhex(hex_bytes.replace(" ", ""))
        lines = expected_lines(data, ops)
        assert lines == intended, f"{case_id}: struct reads {lines}, intended {intended}"
        path = cases.data_file(f"{case_id}.bin", data)
        cases.add(case_id, req, title, [f"file {path}", *ops], lines, source=STRUCT)

    def on_font(case_id, req, title, font_rel, ops, cross_check):
        """Reads from a real font; `cross_check` is the values fontTools parses for the same fields."""
        data = (wb.ROOT / font_rel).read_bytes()
        lines = expected_lines(data, ops)
        values = [l.split()[1] if l != "eof" else "eof" for l in lines]
        same = len(values) == len(cross_check) and all(
            v == c if c == "eof" else Decimal(v) == Decimal(c) for v, c in zip(values, cross_check))
        assert same, f"{case_id}: struct {values} vs fontTools {cross_check}"
        cases.add(case_id, req, title, [f"file {font_rel}", *ops], lines, source=FONT_SOURCE)

    # R1 - unsigned
    hand("01-R1-u8", "R1", "u8 at the boundaries: 00 7f 80 ff, then 41",
         "00 7f 80 ff 41", ["u8"] * 5, ["u8 0", "u8 127", "u8 128", "u8 255", "u8 65"])
    hand("01-R1-u16", "R1", "u16: 0000 7fff 8000 ffff 1234 0100 (0x0100 is 256, not 1)",
         "0000 7fff 8000 ffff 1234 0100", ["u16"] * 6,
         ["u16 0", "u16 32767", "u16 32768", "u16 65535", "u16 4660", "u16 256"])
    hand("01-R1-u32", "R1", "u32: 00000000 7fffffff 80000000 ffffffff 12345678 00010000",
         "00000000 7fffffff 80000000 ffffffff 12345678 00010000", ["u32"] * 6,
         ["u32 0", "u32 2147483647", "u32 2147483648", "u32 4294967295", "u32 305419896", "u32 65536"])
    hand("01-R1-sizes", "R1", "u8, u16, u32 one after another: each read moves on by its own size",
         "01 0203 04050607 ff", ["u8", "u16", "u32", "u8"], ["u8 1", "u16 515", "u32 67438087", "u8 255"])

    # R2 - signed
    hand("01-R2-i8", "R2", "i8: 00 7f 80 ff 81 01",
         "00 7f 80 ff 81 01", ["i8"] * 6, ["i8 0", "i8 127", "i8 -128", "i8 -1", "i8 -127", "i8 1"])
    hand("01-R2-i16", "R2", "i16: 0000 7fff 8000 ffff 8001 fed4",
         "0000 7fff 8000 ffff 8001 fed4", ["i16"] * 6,
         ["i16 0", "i16 32767", "i16 -32768", "i16 -1", "i16 -32767", "i16 -300"])
    hand("01-R2-i32", "R2", "i32: 00000000 7fffffff 80000000 ffffffff fffffed4 00010000",
         "00000000 7fffffff 80000000 ffffffff fffffed4 00010000", ["i32"] * 6,
         ["i32 0", "i32 2147483647", "i32 -2147483648", "i32 -1", "i32 -300", "i32 65536"])
    hand("01-R2-same-bytes", "R2", "the same bytes ff fe ff ff read as unsigned and as signed",
         "fffe ffff", ["u16", "jump 0", "i16", "jump 0", "u32", "jump 0", "i32", "jump 0", "u8", "i8"],
         ["u16 65534", "i16 -2", "u32 4294901759", "i32 -65537", "u8 255", "i8 -2"])

    # R3 - F2Dot14
    spec = {"7fff": 1.999939, "7000": 1.75, "0001": 0.000061, "0000": 0.0, "ffff": -0.000061, "8000": -2.0}
    spec_hex = " ".join(spec)
    spec_lines = expected_lines(bytes.fromhex(spec_hex.replace(" ", "")), ["f2dot14"] * 6)
    for line, (raw, shown) in zip(spec_lines, spec.items()):
        assert abs(float(line.split()[1]) - shown) <= 5e-7, f"F2Dot14 {raw}: {line} vs the spec's {shown}"
    hand("01-R3-spec-table", "R3", "the six F2Dot14 examples from the OpenType spec: 7fff 7000 0001 0000 ffff 8000",
         spec_hex, ["f2dot14"] * 6, spec_lines)
    hand("01-R3-halves", "R3", "F2Dot14 +-1, +-0.5, +-1.5 and just below +-1",
         "4000 c000 2000 e000 6000 a000 3fff c001", ["f2dot14"] * 8,
         ["f2dot14 1", "f2dot14 -1", "f2dot14 0.5", "f2dot14 -0.5", "f2dot14 1.5", "f2dot14 -1.5",
          "f2dot14 0.99993896484375", "f2dot14 -0.99993896484375"])

    noto = wb.load(wb.NOTO_JP)
    avar = noto.reader.tables["avar"]
    pairs = sorted(noto["avar"].segments["wght"].items())
    ops = [f"jump {avar.offset}", "skip 6", "u16", "u16"] + ["f2dot14", "f2dot14"] * len(pairs)
    on_font("01-R3-noto-avar", "R3",
            f"Noto Sans JP 'avar' table: axis count, map count, then {len(pairs)} F2Dot14 pairs",
            wb.NOTO_JP, ops, [1, len(pairs)] + [v for p in pairs for v in p])

    # R4 - jump and skip
    counting = " ".join(f"{i:02x}" for i in range(32))
    hand("01-R4-jump", "R4", "jump back and forth in a file whose byte k holds k",
         counting, ["jump 10", "u8", "jump 2", "u16", "jump 0", "u32", "jump 30", "u16", "jump 2", "u8"],
         ["u8 10", "u16 515", "u32 66051", "u16 7711", "u8 2"])
    hand("01-R4-skip", "R4", "skip from wherever the last read stopped (byte k holds k)",
         counting, ["skip 3", "u8", "skip 0", "u8", "skip 4", "u16", "jump 20", "skip 5", "u8", "skip 1", "i16"],
         ["u8 3", "u8 4", "u16 2314", "u8 25", "i16 6940"])
    jb = wb.load(wb.JETBRAINS)
    head = jb.reader.tables["head"].offset
    on_font("01-R4-font-head", "R4", f"JetBrains Mono: jump to 'head' ({head}), skip to unitsPerEm and indexToLocFormat",
            wb.JETBRAINS, [f"jump {head}", "skip 18", "u16", "skip 30", "i16"],
            [jb["head"].unitsPerEm, jb["head"].indexToLocFormat])

    # R5 - end of file
    hand("01-R5-eof-in-u32", "R5", "5-byte file: a u16, then a u32 with only 3 bytes left; the last op is never run",
         "0102 030405", ["u16", "u32", "u8"], ["u16 258", "eof"])
    hand("01-R5-exact-end", "R5", "a u32 that ends exactly at the end of the file is fine; the next read is not",
         "deadbeef", ["u32", "u8", "u8"], ["u32 3735928559", "eof"])
    hand("01-R5-jump-past-end", "R5", "jump past the end of an 8-byte file, then read",
         "0011223344556677", ["u8", "jump 100", "u8", "u16"], ["u8 0", "eof"])
    hand("01-R5-skip-past-end", "R5", "skip to the last two bytes, read them, skip 1 more, then read",
         "0011223344556677", ["skip 6", "u16", "skip 1", "u8"], ["u16 26231", "eof"])
    hand("01-R5-empty-file", "R5", "an empty file: the very first read is past the end", "", ["i8", "u8"], ["eof"])
    size = (wb.ROOT / wb.JETBRAINS).stat().st_size
    last = (wb.ROOT / wb.JETBRAINS).read_bytes()[-2:]
    on_font("01-R5-font-end", "R5", f"JetBrains Mono ({size} bytes): read the last u16, then one more i16",
            wb.JETBRAINS, [f"jump {size - 2}", "u16", "i16", "u8"], [struct.unpack(">H", last)[0], "eof"])

    # End to end - real header fields
    for label, font_rel, font in (("jetbrains", wb.JETBRAINS, jb), ("noto", wb.NOTO_JP, noto)):
        t = font.reader.tables
        h, hh, mx = t["head"].offset, t["hhea"].offset, t["maxp"].offset
        first_tag = min(t)  # the directory is sorted by tag, so its first record is the smallest tag
        e = t[first_tag]
        on_font(f"01-E2E-{label}-directory", "E2E",
                f"{Path(font_rel).stem}: sfnt version, numTables, search fields, first table record ('{first_tag}')",
                font_rel, ["u32", "u16", "u16", "u16", "u16", "u32", "u32", "u32", "u32"],
                [0x00010000, len(t), font.reader.searchRange, font.reader.entrySelector, font.reader.rangeShift,
                 struct.unpack(">I", first_tag.encode("latin-1"))[0], e.checkSum, e.offset, e.length])
        hd, hhea = font["head"], font["hhea"]
        on_font(f"01-E2E-{label}-fields", "E2E",
                f"{Path(font_rel).stem}: head magic, unitsPerEm, bounding box, indexToLocFormat; "
                f"maxp numGlyphs; hhea ascent and descent",
                font_rel, [f"jump {h + 12}", "u32", "skip 2", "u16", "skip 16", "i16", "i16", "i16", "i16", f"jump {h + 50}", "i16",
                           f"jump {mx + 4}", "u16", f"jump {hh + 4}", "i16", "i16"],
                [hd.magicNumber, hd.unitsPerEm, hd.xMin, hd.yMin, hd.xMax, hd.yMax, hd.indexToLocFormat,
                 font["maxp"].numGlyphs, hhea.ascent, hhea.descent])

    # End to end - random files and random operation sequences
    for k in range(4):
        data = bytes(rng.randrange(256) for _ in range(rng.randint(24, 64)))
        ops = []
        for _ in range(rng.randint(15, 30)):
            r = rng.random()
            if r < 0.15:
                ops.append(f"jump {rng.randrange(len(data) + 3)}")
            elif r < 0.25:
                ops.append(f"skip {rng.randrange(6)}")
            else:
                ops.append(rng.choice(READS))
        case_id = f"01-E2E-random-s{args.seed}-{k}"
        lines = expected_lines(data, ops)
        path = cases.data_file(f"{case_id}.bin", data)
        cases.add(case_id, "E2E", f"random file of {len(data)} bytes, {len(ops)} random operations (seed {args.seed})",
                  [f"file {path}", *ops], lines, source=STRUCT)

    cases.save()


if __name__ == "__main__":
    main()
