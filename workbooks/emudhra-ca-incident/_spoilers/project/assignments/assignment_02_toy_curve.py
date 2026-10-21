"""Assignment 02 (toy curve): adds the two points on each `add` line of a test input.

The checker runs `assignment_02_toy_curve.py <input-file> <output-file>`. src/pkiaudit/ecc/curve.py
adds the points, on the toy curve from src/pkiaudit/ecc/curves.py.
"""

import sys

from pkiaudit.ecc.curve import INFINITY, Point, add_points
from pkiaudit.ecc.curves import TOY


def parse_point(words: list[str], i: int) -> tuple[Point, int]:
    """Reads one point at words[i], `inf` or two numbers; returns (point, index of the next word)."""
    if words[i] == "inf":
        return INFINITY, i + 1
    return (int(words[i]), int(words[i + 1])), i + 2


def format_point(point: Point) -> str:
    """Writes a point the way the output expects: `inf` or `x y`."""
    return "inf" if point is INFINITY else f"{point[0]} {point[1]}"


def main(input_path: str, output_path: str) -> None:
    """Writes the sum for each `add <P1> <P2>` line."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            p1, i = parse_point(words, 1)
            p2, _ = parse_point(words, i)
            lines.append(format_point(add_points(TOY, p1, p2)))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
