# Checkpoint 10 - Find a weak private key
#
# Problem:  problems/10-find-weak-key.md (also in the web problem book)
# Check:    ./check.sh 10
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on find_private_key().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys

# The curve constants are on the problem page. Fill this in from there.
CURVES = {
    "P-256": {},
    "P-384": {},
}


def find_private_key(curve, x, y, bound):
    """Return d, with 1 <= d <= bound, if the public key (x, y) on `curve` equals d*G; else None."""
    # TODO: step through G, 2G, 3G, ... up to `bound`, comparing each point with (x, y).
    raise NotImplementedError("find_private_key")


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
    except Exception as e:  # report the problem; the checker shows the message
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
