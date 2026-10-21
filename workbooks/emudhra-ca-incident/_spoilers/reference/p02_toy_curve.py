# Reference solution - checkpoint 02 (Add points on a toy curve). SPOILERS: try it yourself first.
#
# Two formulas: a chord through two distinct points, or the tangent at a point to double it. Both
# give a slope; squaring the slope and subtracting the two known x's (by the curve's own algebra)
# gives the third point's x, and the slope gives its y. The point at infinity is the identity:
# adding it to anything returns that thing unchanged.

import sys

P = 17  # the field: all arithmetic below is mod 17
A = 2  # the curve is y^2 = x^3 + 2x + 2 mod 17
B = 2


def add_points(p1, p2):
    """p1, p2: each either None (the point at infinity) or an (x, y) pair. Returns the sum,
    in the same representation."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:  # p2 is -p1: the sum is infinity
        return None
    if p1 == p2:
        slope = (3 * x1 * x1 + A) * pow(2 * y1, -1, P) % P  # tangent at p1
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, P) % P  # the line through p1 and p2
    x3 = (slope * slope - x1 - x2) % P
    y3 = (slope * (x1 - x3) - y1) % P
    return (x3, y3)


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
