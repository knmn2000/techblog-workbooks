# Checkpoint 02 - Add points on a toy curve
#
# Problem:  problems/02-toy-curve.md (also in the web problem book)
# Check:    ./check.sh 02
#
# Only your program's output is checked, so you can structure it however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you can
# focus on add_points().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys

P = 17  # the field: all arithmetic below is mod 17
A = 2  # the curve is y^2 = x^3 + 2x + 2 mod 17
B = 2


def add_points(p1, p2):
    """p1, p2: each either None (the point at infinity) or an (x, y) pair. Return the sum,
    in the same representation (None, or an (x, y) tuple)."""
    # TODO: handle infinity on either side, the inverse-pair case (sum is infinity), doubling
    # (p1 == p2, use the tangent slope), and the ordinary case (the chord's slope).
    raise NotImplementedError("add_points")


# ---- Input/output (provided) -------------------------------------------------


def parse_point(words, i):
    """Reads one point starting at words[i] (`inf`, or two integers). Returns (point, next index)."""
    if words[i] == "inf":
        return None, i + 1
    return (int(words[i]), int(words[i + 1])), i + 2


def format_point(pt):
    return "inf" if pt is None else f"{pt[0]} {pt[1]}"


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            # add <P1> <P2>, each P either `inf` or two mod-17 integers
            p1, i = parse_point(words, 1)
            p2, _ = parse_point(words, i)
            lines.append(format_point(add_points(p1, p2)))
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
