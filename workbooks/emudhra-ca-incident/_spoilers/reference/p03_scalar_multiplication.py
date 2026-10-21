# Reference solution - checkpoint 03 (Multiply a point by a number). SPOILERS: try it yourself first.
#
# Double-and-add turns d*G into about log2(d) point operations instead of d of them: walk d's bits
# from the bottom, doubling a running point every step, and adding it into the (separate) result
# whenever that bit is 1. This is the forward direction of checkpoint 10's search: there, d was
# small enough to try every value; here d can be any size, so the public key is built directly.

import sys

# Curve constants, typed from the standard (same values as checkpoint 10's page).
CURVES = {
    "P-256": {
        "p": 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
        "gx": 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
        "gy": 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5,
        "hexlen": 64,
    },
    "P-384": {
        "p": 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff,
        "gx": 0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7,
        "gy": 0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f,
        "hexlen": 96,
    },
}


def add(p, a, point, other):
    """Add two affine points (None means the point at infinity)."""
    if point is None:
        return other
    if other is None:
        return point
    x1, y1 = point
    x2, y2 = other
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if (x1, y1) == (x2, y2):
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p  # doubling: the tangent's slope
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, p) % p  # the slope of the line through both points
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def scalar_multiply(curve, d):
    """Return d*G as an (x, y) pair, by double-and-add. 1 <= d < n (the curve's order)."""
    params = CURVES[curve]
    p, a = params["p"], params["p"] - 3
    addend = (params["gx"], params["gy"])  # doubles every step: G, 2G, 4G, 8G, ...
    result = None  # the point at infinity: the running total
    while d > 0:
        if d & 1:
            result = add(p, a, result, addend)
        addend = add(p, a, addend, addend)
        d >>= 1
    return result


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            # mul <curve> <d>
            curve, d = words[1], int(words[2])
            x, y = scalar_multiply(curve, d)
            hexlen = CURVES[curve]["hexlen"]
            lines.append(f"{x:0{hexlen}x} {y:0{hexlen}x}")
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
    except Exception as e:  # report the problem; the checker shows the message
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
