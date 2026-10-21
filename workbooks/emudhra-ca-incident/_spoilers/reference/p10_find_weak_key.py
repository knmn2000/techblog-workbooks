# Reference solution - checkpoint 10 (Find a weak private key). SPOILERS: try it yourself first.
#
# The public key is Q = d*G. If d is small, walking G, 2G, 3G, ... reaches Q after d steps.
# Each step adds G to the previous point, so the whole search costs `bound` point additions
# rather than `bound` full multiplications.

import sys

CURVES = {
    "P-256": {
        "p": 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
        "gx": 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
        "gy": 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5,
    },
    "P-384": {
        "p": 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff,
        "gx": 0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7,
        "gy": 0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f,
    },
}


def add(p, a, point, other):
    """Add two affine points (neither is the point at infinity, and they are not negatives)."""
    x1, y1 = point
    x2, y2 = other
    if (x1, y1) == (x2, y2):
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p  # doubling: the tangent's slope
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, p) % p  # the slope of the line through both points
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def find_private_key(curve, x, y, bound):
    """Return d, with 1 <= d <= bound, if the public key (x, y) on `curve` equals d*G; else None."""
    params = CURVES[curve]
    p, a = params["p"], params["p"] - 3
    g = (params["gx"], params["gy"])
    target = (x, y)
    point = g  # 1*G
    for d in range(1, bound + 1):
        if point == target:
            return d
        point = add(p, a, point, g)
    return None


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    bound = 0
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "bound":  # bound <N>: applies to the key lines after it
                bound = int(words[1])
            elif words[0] == "key":  # key <label> <curve> <x> <y>, coordinates in hex
                label, curve, x, y = words[1], words[2], int(words[3], 16), int(words[4], 16)
                d = find_private_key(curve, x, y, bound)
                lines.append(f"none {label}" if d is None else f"weak {label} {d}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <input-file> <output-file>", file=sys.stderr)
        sys.exit(2)
    try:
        main(sys.argv[1], sys.argv[2])
    except NotImplementedError as e:
        print(f"not implemented: {e}", file=sys.stderr)
        sys.exit(99)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
