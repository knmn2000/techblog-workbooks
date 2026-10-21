# Reference solution - checkpoint 11 (Sign a certificate with a recovered key). SPOILERS: try
# it yourself first.
#
# ECDSA signing is the mirror of checkpoint 04's verification equation: given d, a message hash
# z, and a one-time random number k (given here so the answer is reproducible, instead of drawn
# by the program):
#   R = k*G, r = R.x mod n
#   s = k^-1 * (z + r*d) mod n
# k must never be reused across two different messages signed with the same key: reusing it
# leaks d directly (not exercised here; see the problem page's "After you pass").

import sys

CURVES = {
    "P-256": {
        "p": 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
        "gx": 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
        "gy": 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5,
        "n": 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551,
    },
    "P-384": {
        "p": 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff,
        "gx": 0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7,
        "gy": 0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f,
        "n": 0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973,
    },
}


def add(p, a, point, other):
    """Add two affine points (neither is the point at infinity)."""
    x1, y1 = point
    x2, y2 = other
    if (x1, y1) == (x2, y2):
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def multiply(p, a, g, k):
    """k*G by double-and-add: O(log k) additions, unlike checkpoint 10's O(k) search."""
    result, base = None, g
    while k:
        if k & 1:
            result = base if result is None else add(p, a, result, base)
        base = add(p, a, base, base)
        k >>= 1
    return result


def sign(curve, d, z, k):
    """Returns (r, s), the ECDSA signature for private key d, hash z, nonce k."""
    c = CURVES[curve]
    p, a, n = c["p"], c["p"] - 3, c["n"]
    g = (c["gx"], c["gy"])
    r = multiply(p, a, g, k)[0] % n
    s = pow(k, -1, n) * (z + r * d) % n
    return r, s


# ---- Input/output (provided) -------------------------------------------------


HEXLEN = {"P-256": 64, "P-384": 96}  # zero-padded width: bytes in the field size, times 2


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            # sign <id> <curve> <d> <z> <k>: d, z, k in hex
            _, case_id, curve, d, z, k = words
            r, s = sign(curve, int(d, 16), int(z, 16), int(k, 16))
            w = HEXLEN[curve]
            lines.append(f"signature {case_id} {r:0{w}x} {s:0{w}x}")
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
