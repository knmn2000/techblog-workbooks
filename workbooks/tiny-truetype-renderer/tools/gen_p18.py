"""Test cases for checkpoint 18 (render a line of text).

The reference program draws each expected picture. It is then checked pixel by pixel
against fontTools: its own cmap, advance widths and (compound-resolved) outlines, with
PointInsidePen deciding which glyph, if any, covers each pixel centre.

    py -P tools/gen_p18.py --ref build/ref/assignment_18                      # tests/18 (seed 1)
    py -P tools/gen_p18.py --seed 7 --out build/fresh/18 --ref ...
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import imageio  # noqa: E402
import wb  # noqa: E402

REQUIREMENTS = [
    ("R1", "Decode UTF-8 text into code points (1- to 4-byte characters)"),
    ("R2", "Map characters to glyphs with cmap; an unmapped one draws glyph 0"),
    ("R3", "Each glyph moves the pen by its advance width times the scale"),
    ("R4", "Draw compound glyphs"),
    ("R5", "Fill glyphs by the non-zero rule (curves and overlaps)"),
    ("R6", "Several pen positions, colours and text lines"),
    ("R7", "Scale; clip text that runs off the canvas"),
    ("E2E", "Whole phrases"),
]
COMPARE = "image band=1 allow=0.0002"
WORDS_EN = ["glyph", "kerning", "baseline", "outline", "bezier", "contour", "pixel", "render", "font", "vector"]
WORDS_JA = ["文字", "書体", "曲線", "画素", "輪郭", "日本語"]


class Run:
    """One `pen` + `color` + `text` group."""

    def __init__(self, x, baseline, scale, color, text):
        self.x, self.baseline, self.scale, self.color, self.text = x, baseline, scale, color, text


class Scene:
    def __init__(self, font_rel, width, height, runs):
        self.font_rel, self.width, self.height, self.runs = font_rel, width, height, runs

    def input_lines(self):
        lines = [f"font {self.font_rel}", f"canvas {self.width} {self.height}"]
        for r in self.runs:
            lines += [f"pen {wb.num(r.x)} {wb.num(r.baseline)} {wb.num(r.scale)}", "color %d %d %d" % r.color,
                      f"text {r.text}"]
        return lines


class Shaper:
    """Glyphs, advances and outlines from fontTools."""

    def __init__(self, font_rel):
        self.font = wb.load(font_rel)
        self.cmap = self.font["cmap"].getcmap(0, 4).cmap
        self.order = self.font.getGlyphOrder()
        self.outlines = {}

    def name(self, ch):
        return self.cmap.get(ord(ch), self.order[0])

    def advance(self, name):
        return self.font["hmtx"][name][0]

    def outline(self, name):
        if name not in self.outlines:
            g = self.font["glyf"][name]
            if g.isComposite() or g.numberOfContours > 0:
                ends, pts = wb.outline_of(self.font, name)
                xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                self.outlines[name] = (ends, pts, (min(xs), min(ys), max(xs), max(ys)))
            else:
                self.outlines[name] = None
        return self.outlines[name]

    def placed(self, scene):
        """[(colour, ends, points, bbox, x, baseline, scale)] in drawing order."""
        out = []
        for r in scene.runs:
            x = r.x
            for ch in r.text:
                name = self.name(ch)
                o = self.outline(name)
                if o:
                    out.append((r.color, o[0], o[1], o[2], x, r.baseline, r.scale))
                x += self.advance(name) * r.scale
        return out


def expected_colour(placed, px, py, boundary):
    colour = (0, 0, 0)
    for c, ends, pts, (x0, y0, x1, y1), ox, base, s in placed:
        gx, gy = (px + 0.5 - ox) / s, (base - py - 0.5) / s
        if x0 <= gx <= x1 and y0 <= gy <= y1:
            answers = {wb.inside(ends, pts, gx + dx, gy + dy, False)
                       for dx, dy in ((0, 0), (1e-6, 0), (-1e-6, 0), (0, 1e-6), (0, -1e-6))}
            if len(answers) > 1:
                boundary[0] = True
            if wb.inside(ends, pts, gx, gy, False):
                colour = c
    return colour


def validate(scene, shaper, image_path, rng, samples=4000):
    w, h, rgb = imageio.read_image(image_path)
    assert (w, h) == (scene.width, scene.height)
    placed = shaper.placed(scene)
    bad = []
    for _ in range(samples):
        px, py = rng.randrange(w), rng.randrange(h)
        boundary = [False]
        want = expected_colour(placed, px, py, boundary)
        got = tuple(rgb[3 * (py * w + px):3 * (py * w + px) + 3])
        if want != got and not boundary[0]:
            bad.append((px, py, want, got))
    assert len(bad) <= 2, f"{image_path.name}: reference disagrees with fontTools at {bad[:4]}"


def layout(shaper, font_rel, lines, scale, color=(255, 255, 255), margin=8, max_width=600):
    """A scene with one run per line of text, sized to fit."""
    hhea = shaper.font["hhea"]
    line_height = math.ceil((hhea.ascent - hhea.descent) * scale) + 4
    width = 2 * margin + math.ceil(max(sum(shaper.advance(shaper.name(ch)) for ch in t) * scale for t in lines))
    width = min(width, max_width)
    runs = [Run(margin, margin + math.ceil(hhea.ascent * scale) + k * line_height, scale, color, t)
            for k, t in enumerate(lines)]
    return Scene(font_rel, width, 2 * margin + line_height * len(lines), runs)


def main():
    args = wb.parse_args("18")
    rng = random.Random(args.seed)
    jb, noto = Shaper(wb.JETBRAINS), Shaper(wb.NOTO_JP)
    unmapped = next(chr(cp) for cp in range(0x0378, 0x0400) if cp not in jb.cmap)
    icons = "".join(chr(cp) for cp in sorted(cp for cp in jb.cmap if cp >= 0xF0000)[:3])

    specs = [
        ("18-R1-latin1", "R1", "'naive cafe' with i-diaeresis and e-acute (2-byte UTF-8)",
         jb, layout(jb, wb.JETBRAINS, ["naïve café"], 0.06)),
        ("18-R1-japanese", "R1", "three kanji (3-byte UTF-8) in Noto Sans JP",
         noto, layout(noto, wb.NOTO_JP, ["日本語"], 0.14)),
        ("18-R1-four-byte", "R1", "three Nerd Font icons above U+F0000 (4-byte UTF-8)",
         jb, layout(jb, wb.JETBRAINS, [icons], 0.08)),
        ("18-R2-unmapped", "R2", f"'A', U+{ord(unmapped):04X} (not in the font: glyph 0), 'B'",
         jb, layout(jb, wb.JETBRAINS, [f"A{unmapped}B"], 0.1)),
        ("18-R3-monospace", "R3", "'iiiWWW' in a monospaced font: equal advances",
         jb, layout(jb, wb.JETBRAINS, ["iiiWWW"], 0.08)),
        ("18-R3-proportional", "R3", "'Hamburg' in Noto Sans JP: different advances, fractional pen",
         noto, layout(noto, wb.NOTO_JP, ["Hamburg"], 0.123)),
        ("18-R4-compounds", "R4", "accented capitals, all compound glyphs",
         jb, layout(jb, wb.JETBRAINS, ["ÜÉÑÅŐ"], 0.09)),
        ("18-R5-hiragana", "R5", "five hiragana with overlapping strokes",
         noto, layout(noto, wb.NOTO_JP, ["あいうえお"], 0.11)),
        ("18-R5-symbols", "R5", "'@&8%' : curves and counters",
         jb, layout(jb, wb.JETBRAINS, ["@&8%"], 0.1)),
    ]
    two = layout(jb, wb.JETBRAINS, ["first line", "second line"], 0.06)
    two.runs[1].color = (255, 170, 40)
    specs.append(("18-R6-two-lines", "R6", "two lines of text in two colours", jb, two))
    over = layout(noto, wb.NOTO_JP, ["十字"], 0.16)
    over.runs.append(Run(over.runs[0].x + 40, over.runs[0].baseline + 12, 0.16, (80, 160, 255), "十"))
    specs.append(("18-R6-overdraw", "R6", "a second, blue run drawn over the first", noto, over))
    clip = layout(jb, wb.JETBRAINS, ["this sentence is too long for its canvas"], 0.06, max_width=300)
    specs.append(("18-R7-clipped", "R7", "a sentence running off the right edge", jb, clip))
    specs.append(("18-R7-tiny", "R7", "'tiny text' at scale 0.025", jb, layout(jb, wb.JETBRAINS, ["tiny text"], 0.025)))
    specs.append(("18-R7-large", "R7", "'g' at scale 0.4", jb, layout(jb, wb.JETBRAINS, ["g"], 0.4)))
    specs.append(("18-E2E-hello", "E2E", "'Hello, World!'", jb, layout(jb, wb.JETBRAINS, ["Hello, World!"], 0.07)))
    specs.append(("18-E2E-font-ja", "E2E", "the Japanese word for font", noto,
                  layout(noto, wb.NOTO_JP, ["フォント"], 0.13)))
    en = " ".join(rng.sample(WORDS_EN, 3))
    specs.append((f"18-E2E-s{args.seed}-en", "E2E", f"three random words (seed {args.seed})", jb,
                  layout(jb, wb.JETBRAINS, [en], 0.06)))
    ja = "".join(rng.sample(WORDS_JA, 2))
    specs.append((f"18-E2E-s{args.seed}-ja", "E2E", f"two random Japanese words (seed {args.seed})", noto,
                  layout(noto, wb.NOTO_JP, [ja], 0.09)))

    source = f"reference picture, checked pixel by pixel against {wb.FT} (cmap, hmtx, outlines, PointInsidePen)"
    cases = wb.Cases(args.out, args.seed, COMPARE, REQUIREMENTS, source=source)
    for case_id, req, title, shaper, scene in specs:
        image = cases.image_path(case_id)
        wb.run_reference(args.ref, scene.input_lines(), image)
        validate(scene, shaper, image, rng)
        cases.add(case_id, req, title, scene.input_lines(), expected_file=image)
    cases.save()


if __name__ == "__main__":
    main()
