"""Test cases for checkpoint 09 (resolve compound glyphs).

Expected outlines come from fontTools' own compound resolution (Glyph.getCoordinates),
split into one outline per simple component. Hand-made glyphs live in a small font
built with fontTools; the script checks the compiled flags are the ones intended.

    py -P tools/gen_p09.py                          # tests/09 (seed 1)
    py -P tools/gen_p09.py --seed 7 --out build/fresh/09
"""

import random
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import wb  # noqa: E402

REQUIREMENTS = [
    ("R1", "Empty glyph -> 0 components; simple glyph -> 1 component"),
    ("R2", "Component records: flags, glyph id, signed 1- or 2-byte arguments, MORE_COMPONENTS"),
    ("R3", "One scale, separate x and y scales, or a 2x2 matrix (F2Dot14)"),
    ("R4", "x' = a*x + c*y + e and y' = b*x + d*y + f for every point"),
    ("R5", "SCALED_COMPONENT_OFFSET: the offset is transformed too"),
    ("R6", "Nested compound glyphs: transforms compose, inner one first"),
    ("R7", "Components in depth-first order; empty components skipped"),
    ("E2E", "Accented letters from JetBrains Mono Bold"),
]
EXPLAIN = "_lines=R7 glyph=R2 ends=R7 points:count=R7 points:curve=R7 points:x=R4 points:y=R4"

ARG_WORDS, ARGS_XY, SCALE, MORE, XY_SCALE, TWO_BY_TWO, INSTRUCTIONS, SCALED_OFFSET = (
    0x1, 0x2, 0x8, 0x20, 0x40, 0x80, 0x100, 0x800)

BOX = [[(0, 0, 1), (0, 100, 1), (100, 100, 1), (100, 0, 1)]]
TRI = [[(0, 0, 1), (60, 0, 1), (30, 80, 1)]]
BUMP = [[(0, 0, 1), (20, 60, 0), (60, 60, 0), (80, 0, 1)], [(30, 10, 1), (50, 10, 1), (40, 30, 1)]]

# name: (components, extra flags on the first component, instruction bytes, what it tests)
HAND_MADE = {
    "pos_bytes": ([("box", (1, 0, 0, 1, 10, 20))], 0, b"", ("R2", "offset (10, 20) stored as two bytes")),
    "neg_bytes": ([("box", (1, 0, 0, 1, -30, -5))], 0, b"", ("R2", "offset (-30, -5) stored as two signed bytes")),
    "words": ([("box", (1, 0, 0, 1, 300, -200))], 0, b"", ("R2", "offset (300, -200) stored as two int16 words")),
    "three_parts": ([("box", (1, 0, 0, 1, 0, 0)), ("tri", (1, 0, 0, 1, 120, 0)), ("bump", (1, 0, 0, 1, 0, 150))],
                    0, b"", ("R2", "three components chained with MORE_COMPONENTS")),
    "scale": ([("tri", (0.5, 0, 0, 0.5, 0, 0))], 0, b"", ("R3", "WE_HAVE_A_SCALE 0.5")),
    "xy_scale": ([("tri", (1.5, 0, 0, 0.25, 5, 5))], 0, b"", ("R3", "WE_HAVE_AN_X_AND_Y_SCALE 1.5 and 0.25")),
    "rotate": ([("box", (0, 1, -1, 0, 100, 0))], 0, b"", ("R3", "WE_HAVE_A_TWO_BY_TWO: a 90-degree rotation")),
    "shear": ([("tri", (1, 0, 0.5, 1, 0, 0))], 0, b"", ("R4", "2x2 with c = 0.5: x' = x + 0.5*y (a shear)")),
    "mirror": ([("bump", (-1, 0, 0, 1, 200, 0))], 0, b"", ("R4", "2x2-free mirror: x scale -1, offset 200")),
    "scaled_offset": ([("box", (0.5, 0, 0, 0.5, 40, 40))], SCALED_OFFSET, b"",
                      ("R5", "scale 0.5 with SCALED_COMPONENT_OFFSET: offset (40, 40) becomes (20, 20)")),
    "scaled_offset_rot": ([("tri", (0, 1, -1, 0, 50, 10))], SCALED_OFFSET, b"",
                          ("R5", "rotation with SCALED_COMPONENT_OFFSET: the offset is rotated too")),
    "nested": ([("rotate", (0.5, 0, 0, 0.5, 10, 10)), ("tri", (1, 0, 0, 1, 200, 0))], 0, b"",
               ("R6", "a compound inside a compound, scaled 0.5 and moved")),
    "nested2": ([("nested", (1, 0, 0, 1, -50, 30))], 0, b"", ("R6", "three levels deep")),
    "with_empty": ([("box", (1, 0, 0, 1, 0, 0)), ("space", (1, 0, 0, 1, 50, 50)), ("tri", (1, 0, 0, 1, 0, 200))],
                   0, b"", ("R7", "an empty glyph in the middle is skipped")),
    "with_instructions": ([("box", (1, 0, 0, 1, 5, 5)), ("tri", (1, 0, 0, 1, 150, 0))], 0, b"\xb0\x01\x2c",
                          ("R7", "WE_HAVE_INSTRUCTIONS: hinting bytes after the last component")),
}


def leaves(glyf, name, out):
    """Simple glyphs reached from `name`, depth first, empty ones skipped."""
    g = glyf[name]
    if g.isComposite():
        for c in g.components:
            leaves(glyf, c.glyphName, out)
    elif g.numberOfContours > 0:
        out.append(g)
    return out


def needed(glyf, name, out):
    """`name` and every glyph its components reach."""
    if name not in out:
        out.append(name)
        if glyf[name].isComposite():
            for c in glyf[name].components:
                needed(glyf, c.glyphName, out)
    return out


def expected_for(font, gid):
    glyf, name = font["glyf"], font.getGlyphOrder()[gid]
    g = glyf[name]
    if not g.isComposite() and g.numberOfContours <= 0:
        return f"glyph {gid} components 0"
    coords, _, flags = g.getCoordinates(glyf)
    parts = leaves(glyf, name, [])
    lines, at = [f"glyph {gid} components {len(parts)}"], 0
    for leaf in parts:
        n = len(leaf.coordinates)
        pts = [(x, y, f & 1) for (x, y), f in zip(coords[at:at + n], flags[at:at + n])]
        lines += wb.outline_lines(list(leaf.endPtsOfContours), pts, keyword=None)
        at += n
    assert at == len(coords), "split by leaves doesn't cover every point"
    return "\n".join(lines)


def raw_component_flags(font_path: Path, font, gid):
    """Component flags as stored in the file (fontTools hides some bits after reading)."""
    data = font_path.read_bytes()
    offset, _ = wb.glyph_record(font, gid)
    pos, flags = offset + 10, []
    while True:
        f = struct.unpack(">H", data[pos:pos + 2])[0]
        flags.append(f)
        pos += 4 + (4 if f & ARG_WORDS else 2)
        pos += 2 if f & SCALE else 4 if f & XY_SCALE else 8 if f & TWO_BY_TWO else 0
        if not f & MORE:
            return flags


def input_for(font_rel, font, names):
    order = font.getGlyphOrder()
    lines = [f"font {font_rel}"]
    for n in names:
        gid = order.index(n)
        offset, length = wb.glyph_record(font, gid)
        lines.append(f"glyph {gid} {offset} {length}")
    return lines


def random_font(rng, path: Path):
    """Random compound glyphs (offsets, scales, 2x2, nesting) built by fontTools."""
    quarter = [v / 4 for v in range(-6, 7)]  # dyadic, exact in F2Dot14
    glyphs = {"box": wb.simple_glyph(BOX), "tri": wb.simple_glyph(TRI), "bump": wb.simple_glyph(BUMP)}
    names = []
    for k in range(6):
        comps = []
        for _ in range(rng.randint(1, 3)):
            base = rng.choice(["box", "tri", "bump"] + names[-2:])
            a, d = rng.choice(quarter) or 1, rng.choice(quarter) or 1
            b, c = (rng.choice(quarter), rng.choice(quarter)) if rng.random() < 0.4 else (0, 0)
            e = rng.choice([rng.randint(-120, 120), rng.randint(-900, 900)])
            f = rng.choice([rng.randint(-120, 120), rng.randint(-900, 900)])
            flags = SCALED_OFFSET if rng.random() < 0.25 and (a, b, c, d) != (1, 0, 0, 1) else 0
            comps.append((base, (a, b, c, d, e, f), flags))
        name = f"rnd{k}"
        glyphs[name] = wb.compound_glyph(comps)
        names.append(name)
    order = [".notdef", "box", "tri", "bump", *names]
    return wb.build_font(path, glyphs, order, {}, {}), names


def main():
    args = wb.parse_args("09")
    rng = random.Random(args.seed)
    cases = wb.Cases(args.out, args.seed, "records points=x,y,curve tolerance=0.01", REQUIREMENTS, EXPLAIN)

    # The hand-made font: base glyphs, then compounds that each exercise one rule.
    font_path = args.out / "data" / "compound-test.ttf"
    glyphs = {"box": wb.simple_glyph(BOX), "tri": wb.simple_glyph(TRI), "bump": wb.simple_glyph(BUMP)}
    for name, (comps, extra, program, _) in HAND_MADE.items():
        comps = [(*comps[0], extra), *comps[1:]] if extra else comps
        g = wb.compound_glyph(comps)
        if program:
            from fontTools.ttLib.tables import ttProgram
            g.program = ttProgram.Program()
            g.program.fromBytecode(program)
        glyphs[name] = g
    order = [".notdef", "space", "box", "tri", "bump", *HAND_MADE]
    font = wb.build_font(font_path, glyphs, order, {0x20: "space"}, {"space": 300})
    font_rel = wb.rel(font_path)
    glyf = font["glyf"]

    # The compiled flags must be the ones each case claims to test.
    want = {"pos_bytes": ARGS_XY, "neg_bytes": ARGS_XY, "words": ARG_WORDS, "scale": SCALE,
            "xy_scale": XY_SCALE, "rotate": TWO_BY_TWO, "shear": TWO_BY_TWO, "mirror": XY_SCALE,
            "scaled_offset": SCALED_OFFSET, "scaled_offset_rot": SCALED_OFFSET}
    for name, bit in want.items():
        stored = raw_component_flags(font_path, font, order.index(name))[0]
        assert stored & bit and stored & ARGS_XY, f"{name}: flags {stored:#06x} lack {bit:#x}"
    assert not raw_component_flags(font_path, font, order.index("pos_bytes"))[0] & ARG_WORDS
    assert raw_component_flags(font_path, font, order.index("with_instructions"))[-1] & INSTRUCTIONS

    # R1 - empty and simple glyphs
    for name, label in (("space", "an empty glyph"), ("bump", "a simple glyph with off-curve points")):
        gid = order.index(name)
        cases.add(f"09-R1-{name}", "R1", f"{name}: {label}", input_for(font_rel, font, [name]) + [f"decode {gid}"],
                  expected_for(font, gid))

    for name, (_, _, _, (req, label)) in HAND_MADE.items():
        gid = order.index(name)
        cases.add(f"09-{req}-{name.replace('_', '-')}", req, f"{name}: {label}",
                  input_for(font_rel, font, needed(glyf, name, [])) + [f"decode {gid}"], expected_for(font, gid))

    # R7 - several decode lines, and glyph lines in a different order
    names = ["three_parts", "nested", "with_empty"]
    lines = input_for(font_rel, font, sorted({n for x in names for n in needed(glyf, x, [])}, reverse=True))
    cases.add("09-R7-several", "R7", "three decode lines in one input, glyph lines listed in reverse",
              lines + [f"decode {order.index(n)}" for n in names],
              "\n".join(expected_for(font, order.index(n)) for n in names))

    # End to end - JetBrains Mono's accented letters and ASCII compounds
    jb = wb.load(wb.JETBRAINS)
    jb_order, jb_cmap = jb.getGlyphOrder(), jb.getBestCmap()
    for ch in "\"`ijAeuUnO" + "ÀéüÜñŐǘÅ":
        name = jb_cmap[ord(ch)]
        if not jb["glyf"][name].isComposite():
            continue
        gid = jb_order.index(name)
        cases.add(f"09-E2E-U+{ord(ch):04X}", "E2E", f"U+{ord(ch):04X} ({name}) in JetBrains Mono Bold",
                  input_for(wb.JETBRAINS, jb, needed(jb["glyf"], name, [])) + [f"decode {gid}"],
                  expected_for(jb, gid))

    # Random compound glyphs (new ones for every seed)
    rnd_path = args.out / "data" / f"random-s{args.seed}.ttf"
    rnd_font, rnd_names = random_font(rng, rnd_path)
    for name in rnd_names:
        gid = rnd_font.getGlyphOrder().index(name)
        cases.add(f"09-R6-random-s{args.seed}-{name}", "R6", f"random compound {name} (seed {args.seed})",
                  input_for(wb.rel(rnd_path), rnd_font, needed(rnd_font["glyf"], name, [])) + [f"decode {gid}"],
                  expected_for(rnd_font, gid))

    cases.save()


if __name__ == "__main__":
    main()
