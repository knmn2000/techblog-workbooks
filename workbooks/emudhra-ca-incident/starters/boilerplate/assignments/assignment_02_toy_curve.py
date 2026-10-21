# ======================================================================================
# Assignment 02: Add points on a toy curve
# Problem: problems/02-toy-curve.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 02 as `python -P tools/run_py.py
#   solutions 02 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 02`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/ecc/curve.py and src/pkiaudit/ecc/curves.py in this
#   assignment; each one gives its job at the top.
#   Earlier files you can use: src/pkiaudit/ecc/modmath.py.
#   Import them as modules of your package, e.g. `from pkiaudit.ecc import curve`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
