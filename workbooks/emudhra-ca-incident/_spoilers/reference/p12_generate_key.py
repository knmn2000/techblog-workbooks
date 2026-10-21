# Reference solution - checkpoint 12 (Generate a key correctly). SPOILERS: try it yourself first.
#
# FIPS 186-5 / SEC1 rejection sampling: read each candidate as a big-endian unsigned integer and
# accept it only if it is strictly between 0 and n (the curve's order). Reject everything else
# and draw again. This is the step that, done correctly, can never produce a key like the ones in
# the incident: it either returns a uniformly random d in [1, n-1], or it draws again.

import sys

CURVES = {
    "P-256": {"n": 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551, "hexlen": 64},
    "P-384": {"n": 0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973,
              "hexlen": 96},
}


def generate_key(curve, blocks):
    """blocks: the candidate byte-blocks already drawn, as hex strings, in the order they were
    drawn. Return the accepted private key d as an int (1 <= d <= n - 1)."""
    n = CURVES[curve]["n"]
    for hexblock in blocks:
        candidate = int(hexblock, 16)  # big-endian: hex text already reads most-significant byte first
        if 1 <= candidate <= n - 1:
            return candidate
    raise ValueError(f"no accepted draw for {curve} among {len(blocks)} candidates")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "draw":  # draw <label> <curve> <hex-block> [<hex-block> ...]
                label, curve, *blocks = words[1:]
                d = generate_key(curve, blocks)
                hexlen = CURVES[curve]["hexlen"]
                lines.append(f"key {label} {d:0{hexlen}x}")
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
