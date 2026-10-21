"""Small, dependency-free image reading/writing and the checker's image comparison.

read_image() accepts PNG (8-bit gray, gray+alpha, RGB, RGBA or palette; not
interlaced) and binary PPM (P6). Alpha is ignored. Everything becomes RGB bytes.
"""

import struct
import zlib
from pathlib import Path


class ImageError(Exception):
    pass


def _unfilter(raw: bytes, width: int, height: int, bpp: int) -> bytearray:
    stride = width * bpp
    out = bytearray(stride * height)
    prev = bytearray(stride)
    pos = 0
    for y in range(height):
        kind = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        if kind == 1:
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif kind == 2:
            line = bytearray((a + b) & 0xFF for a, b in zip(line, prev))
        elif kind == 3:
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif kind == 4:
            for i in range(stride):
                a = line[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[i] = (line[i] + pred) & 0xFF
        elif kind != 0:
            raise ImageError(f"PNG row {y} uses unknown filter type {kind}")
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return out


def _read_png(data: bytes):
    pos, idat, palette = 8, [], None
    width = height = depth = color = interlace = None
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if kind == b"IHDR":
            width, height, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif kind == b"PLTE":
            palette = body
        elif kind == b"IDAT":
            idat.append(body)
        elif kind == b"IEND":
            break
    if width is None:
        raise ImageError("PNG has no IHDR chunk")
    if depth != 8:
        raise ImageError(f"PNG bit depth {depth} isn't supported - write 8 bits per channel")
    if interlace:
        raise ImageError("interlaced PNG isn't supported - write a non-interlaced PNG")
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
    if channels is None:
        raise ImageError(f"PNG color type {color} isn't supported")
    pixels = _unfilter(zlib.decompress(b"".join(idat)), width, height, channels)
    if color == 2:
        rgb = bytes(pixels)
    elif color == 6:
        rgb = bytes(b for i, b in enumerate(pixels) if i % 4 != 3)
    elif color == 0:
        rgb = bytes(v for g in pixels for v in (g, g, g))
    elif color == 4:
        rgb = bytes(v for g in pixels[0::2] for v in (g, g, g))
    else:
        if palette is None:
            raise ImageError("palette PNG without a PLTE chunk")
        rgb = bytes(c for i in pixels for c in palette[3 * i:3 * i + 3])
    return width, height, rgb


def _read_ppm(data: bytes):
    fields, pos = [], 2
    while len(fields) < 3:
        while data[pos:pos + 1].isspace():
            pos += 1
        if data[pos:pos + 1] == b"#":
            while data[pos:pos + 1] not in (b"\n", b""):
                pos += 1
            continue
        start = pos
        while not data[pos:pos + 1].isspace():
            pos += 1
        fields.append(int(data[start:pos]))
    width, height, maxval = fields
    if maxval != 255:
        raise ImageError("PPM must use maxval 255")
    pos += 1
    return width, height, bytes(data[pos:pos + width * height * 3])


def read_image(path: Path):
    """(width, height, rgb bytes)."""
    data = Path(path).read_bytes()
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return _read_png(data)
    if data[:2] == b"P6":
        return _read_ppm(data)
    raise ImageError("not a PNG or binary PPM (P6) file")


def png_bytes(width: int, height: int, rgb: bytes, level: int = 9) -> bytes:
    rows = b"".join(b"\x00" + rgb[y * width * 3:(y + 1) * width * 3] for y in range(height))

    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))

    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, level)) + chunk(b"IEND", b""))


def write_png(path: Path, width: int, height: int, rgb: bytes):
    Path(path).write_bytes(png_bytes(width, height, rgb))


# ---- Comparison -------------------------------------------------------------------

BACKGROUND = (0, 0, 0)


def _name(color):
    names = {(0, 0, 0): "black", (255, 255, 255): "white", (255, 0, 0): "red",
             (0, 255, 0): "green", (0, 0, 255): "blue"}
    return names.get(color, "rgb(%d, %d, %d)" % color)


def compare_images(expected_path: Path, actual_path: Path, diff_path: Path, band: int = 1,
                   allow: float = 0.0, tolerance: int = 40, label: str = ""):
    """Compares two images, forgiving differences that are only a shifted edge.

    Every pixel is classified as the nearest colour of the expected image's palette
    (within `tolerance` per channel) or as "other". A differing pixel is forgiven when
    it is only an edge that moved by up to `band` pixels:
      - extra ink (expected background) if the expected image has that ink within `band`;
      - missing ink (actual background) if the actual image has that ink within `band`;
      - a different colour if either image has the other's colour within `band`.
    So anti-aliasing, a shifted edge or a closed sliver thinner than `band` pass, while
    a stray line or a missing shape fails. Up to `allow` (a fraction of all pixels) may count.
    Returns (None, []) on a match, otherwise (message, where) like compare().
    """
    ew, eh, exp = read_image(expected_path)
    if not Path(actual_path).exists():
        return "your program didn't write an image to the output path", ["image:missing"]
    try:
        aw, ah, act = read_image(actual_path)
    except ImageError as e:
        return f"couldn't read your image: {e}", ["image:format"]
    if (aw, ah) != (ew, eh):
        return f"image is {aw}x{ah} pixels, expected {ew}x{eh}", ["image:size"]

    palette = sorted({tuple(exp[i:i + 3]) for i in range(0, len(exp), 3)})
    if len(palette) > 16:
        raise ImageError("expected image has more than 16 colours")
    index = {c: k for k, c in enumerate(palette)}

    def classify(buf, i):
        r, g, b = buf[i], buf[i + 1], buf[i + 2]
        c = (r, g, b)
        if c in index:
            return index[c]
        best = min(palette, key=lambda p: max(abs(p[0] - r), abs(p[1] - g), abs(p[2] - b)))
        if max(abs(best[0] - r), abs(best[1] - g), abs(best[2] - b)) <= tolerance:
            return index[best]
        return -1

    n = ew * eh
    e_cls = [index[(exp[3 * i], exp[3 * i + 1], exp[3 * i + 2])] for i in range(n)]
    a_cls = [classify(act, 3 * i) for i in range(n)]
    bg = index.get(BACKGROUND, -2)

    def near(cls_list, x, y, wanted):
        for dy in range(-band, band + 1):
            yy = y + dy
            if 0 <= yy < eh:
                row = yy * ew
                for dx in range(-band, band + 1):
                    xx = x + dx
                    if 0 <= xx < ew:
                        c = cls_list[row + xx]
                        if c == wanted or (wanted == -1 and c != bg):
                            return True
        return False

    diff = bytearray(n * 3)
    bad_extra, bad_missing, bad_color, forgiven = [], [], [], 0
    for i in range(n):
        e, a = e_cls[i], a_cls[i]
        if e == a:
            v = 40 if e == bg else 110
            diff[3 * i:3 * i + 3] = bytes((v, v, v))
            continue
        x, y = i % ew, i // ew
        if (near(e_cls, x, y, a) if e == bg else near(a_cls, x, y, e) if a == bg
                else near(e_cls, x, y, a) or near(a_cls, x, y, e)):
            forgiven += 1
            diff[3 * i:3 * i + 3] = b"\x8c\x78\x00"
        elif e == bg:
            bad_extra.append((x, y))
            diff[3 * i:3 * i + 3] = b"\xff\x30\x30"
        elif a == bg:
            bad_missing.append((x, y))
            diff[3 * i:3 * i + 3] = b"\x30\x90\xff"
        else:
            bad_color.append((x, y))
            diff[3 * i:3 * i + 3] = b"\xff\x30\xff"

    bad = len(bad_extra) + len(bad_missing) + len(bad_color)
    if bad <= allow * n:
        return None, []
    write_png(diff_path, ew, eh, bytes(diff))
    parts, where = [], []
    if bad_missing:
        x, y = bad_missing[0]
        parts.append(f"{len(bad_missing)} pixels missing, e.g. ({x}, {y}) should be {_name(palette[e_cls[y * ew + x]])}")
        where.append("image:missing-ink")
    if bad_extra:
        x, y = bad_extra[0]
        parts.append(f"{len(bad_extra)} extra pixels, e.g. ({x}, {y}) should be {_name(palette[bg]) if bg >= 0 else 'background'}")
        where.append("image:extra-ink")
    if bad_color:
        x, y = bad_color[0]
        parts.append(f"{len(bad_color)} pixels in the wrong colour, e.g. ({x}, {y}) should be {_name(palette[e_cls[y * ew + x]])}")
        where.append("image:wrong-color")
    rel = label or Path(diff_path).as_posix()
    return ("; ".join(parts) + f" (beyond the {band}-pixel edge tolerance). "
            f"Diff: {rel} - red extra, blue missing, magenta wrong colour, yellow forgiven"), where
