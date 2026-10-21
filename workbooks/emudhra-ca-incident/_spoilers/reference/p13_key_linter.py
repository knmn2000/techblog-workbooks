# Reference solution - checkpoint 13 (Lint a public key). SPOILERS: try it yourself first.
#
# Three independent checks, run in order from cheapest to most expensive, stopping at the first
# that fails: is the point even on the curve, is it on a blocklist of known-bad keys, and only
# then, is its private key small enough to find by brute force. Any one of these, run by a CA
# before it trusts or publishes a key, would have caught this incident immediately.

import sys

WEAK_BOUND = 4096  # see the problem page for why a toy linter uses a bound this small

CURVES = {
    "P-256": {
        "p": 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
        "b": 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
        "gx": 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
        "gy": 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5,
    },
    "P-384": {
        "p": 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff,
        "b": 0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef,
        "gx": 0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7,
        "gy": 0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f,
    },
}
for _c in CURVES.values():
    _c["a"] = _c["p"] - 3


def on_curve(curve, x, y):
    c = CURVES[curve]
    p, a, b = c["p"], c["a"], c["b"]
    if not (0 <= x < p and 0 <= y < p):
        return False
    return (y * y - (x ** 3 + a * x + b)) % p == 0


def add(p, a, point, other):
    """Add two affine points (same point-doubling trick as checkpoint 10)."""
    x1, y1 = point
    x2, y2 = other
    if (x1, y1) == (x2, y2):
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def find_small_private_key(curve, x, y, bound):
    """Same search as checkpoint 10, with this checkpoint's own (larger) bound."""
    c = CURVES[curve]
    p, a = c["p"], c["a"]
    g = (c["gx"], c["gy"])
    target = (x, y)
    point = g
    for d in range(1, bound + 1):
        if point == target:
            return d
        point = add(p, a, point, g)
    return None


def lint_key(curve, x, y, blocklist):
    """blocklist: a set of (curve, x, y) tuples declared so far. Return None if the key passes
    every check, or one of "off-curve", "known-compromised", "weak" (first failing reason, in
    that priority order)."""
    if not on_curve(curve, x, y):
        return "off-curve"
    if (curve, x, y) in blocklist:
        return "known-compromised"
    if find_small_private_key(curve, x, y, WEAK_BOUND) is not None:
        return "weak"
    return None


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    blocklist = set()
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "blocklist":  # blocklist <curve> <x> <y>: applies to key lines after it
                curve, x, y = words[1], int(words[2], 16), int(words[3], 16)
                blocklist.add((curve, x, y))
            elif words[0] == "key":  # key <label> <curve> <x> <y>
                label, curve, x, y = words[1], words[2], int(words[3], 16), int(words[4], 16)
                reason = lint_key(curve, x, y, blocklist)
                lines.append(f"ok {label}" if reason is None else f"fail {label} {reason}")
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
