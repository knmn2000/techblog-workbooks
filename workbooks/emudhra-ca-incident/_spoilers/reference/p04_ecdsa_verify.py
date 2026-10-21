# Reference solution - checkpoint 04 (Verify an ECDSA signature). SPOILERS: try it yourself first.
#
# The verification equation: reject out-of-range r or s immediately (no point computation needed).
# Otherwise compute w = s^-1 mod n, u1 = z*w mod n, u2 = r*w mod n, and the point u1*G + u2*Q. The
# signature is valid exactly when that point isn't infinity and its x, reduced mod n, equals r.

import sys

P = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff
A = P - 3
GX = 0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7
GY = 0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f
N = 0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973
G = (GX, GY)


def add(point, other):
    """Add two affine points (None means the point at infinity)."""
    if point is None:
        return other
    if other is None:
        return point
    x1, y1 = point
    x2, y2 = other
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if (x1, y1) == (x2, y2):
        slope = (3 * x1 * x1 + A) * pow(2 * y1, -1, P) % P
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (slope * slope - x1 - x2) % P
    return x3, (slope * (x1 - x3) - y1) % P


def scalar_multiply(d, point):
    """d*point, by double-and-add (same as checkpoint 3)."""
    result = None
    addend = point
    while d > 0:
        if d & 1:
            result = add(result, addend)
        addend = add(addend, addend)
        d >>= 1
    return result


def verify(pubx, puby, zhash, r, s):
    """True if (pubx, puby) validly signed the 48-byte hash zhash with signature (r, s)."""
    if not (1 <= r <= N - 1 and 1 <= s <= N - 1):
        return False
    w = pow(s, -1, N)
    u1 = (zhash * w) % N
    u2 = (r * w) % N
    point = add(scalar_multiply(u1, G), scalar_multiply(u2, (pubx, puby)))
    if point is None:
        return False
    return point[0] % N == r


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            # verify <pubx> <puby> <hash> <r> <s>, all hex
            pubx, puby, zhash, r, s = (int(w, 16) for w in words[1:6])
            lines.append("valid" if verify(pubx, puby, zhash, r, s) else "invalid")
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
