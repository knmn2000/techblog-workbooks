# Checkpoint 03 - Multiply a point by a number
#
# Problem:  problems/03-scalar-multiplication.md (also in the web problem book)
# Check:    ./check.sh 03
#
# Only your program's output is checked, so you can structure it however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you can
# focus on scalar_multiply().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

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


def scalar_multiply(curve, d):
    """Return d*G as an (x, y) pair, for the named curve. 1 <= d < n (the curve's order)."""
    # TODO: double-and-add. Walk d's bits from the bottom; double a running point every step, and
    # add it into a separate result whenever the current bit is 1. A loop that adds G to itself
    # d times (checkpoint 10's approach) is too slow here - d can be hundreds of bits long.
    raise NotImplementedError("scalar_multiply")


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
