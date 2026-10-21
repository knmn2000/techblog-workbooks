# Checkpoint 12 - Generate a key correctly
#
# Problem:  problems/12-generate-key.md (also in the web problem book)
# Check:    ./check.sh 12
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on generate_key().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys

# The curve orders are on the problem page. Fill this in from there.
CURVES = {
    "P-256": {"n": 0, "hexlen": 64},
    "P-384": {"n": 0, "hexlen": 96},
}


def generate_key(curve, blocks):
    """blocks: the candidate byte-blocks already drawn, as hex strings, in the order they were
    drawn. Return the accepted private key d as an int (1 <= d <= n - 1)."""
    # TODO: read each block as a big-endian integer; reject 0 and anything >= n; accept the
    # first candidate that passes. The test data guarantees exactly one block will qualify.
    raise NotImplementedError("generate_key")


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
    except Exception as e:  # report the problem; the checker shows the message
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
