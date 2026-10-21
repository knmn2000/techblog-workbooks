# ======================================================================================
# Assignment 03: Multiply a point by a number
# Problem: problems/03-scalar-multiplication.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 03 as `python -P tools/run_py.py
#   solutions 03 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 03`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   It adds to src/pkiaudit/ecc/curve.py, which you started earlier: Add scalar
#   multiplication to `ecc/curve.py`: a function that returns `k` times a point by
#   double-and-add, built on your point addition from assignment 02. It must finish in
#   well under the time limit for a `k` hundreds of bits long, as "Double-and-add"
#   describes. The Boilerplate's `ecc/curve.py` from assignment 02 already declares it as
#   `scalar_multiply`; if you wrote the file your own way, add the function now.
#   It adds to src/pkiaudit/ecc/curves.py, which you started earlier: Add the NIST curves
#   P-256 and P-384 to `ecc/curves.py`, with the constants from "The curves", and a way to
#   look each one up by the name the input uses (`P-256` or `P-384`). The Boilerplate's
#   `ecc/curves.py` from assignment 02 already defines both under its assignment 03
#   marker.
#   Import them as modules of your package, e.g. `from pkiaudit.ecc import curve`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 03 (scalar multiplication): computes d*G for each `mul` line of a test input.

The checker runs `assignment_03_scalar_multiplication.py <input-file> <output-file>`. The
multiplication is in src/pkiaudit/ecc/curve.py, and the curves in src/pkiaudit/ecc/curves.py.
"""

import sys

from pkiaudit.ecc.curve import scalar_multiply
from pkiaudit.ecc.curves import CURVES


def main(input_path: str, output_path: str) -> None:
    """Writes the public point for each `mul <curve> <d>` line, as two hex coordinates."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            curve, d = CURVES[words[1]], int(words[2])
            x, y = scalar_multiply(curve, d, curve.g)
            width = 2 * curve.byte_length
            lines.append(f"{x:0{width}x} {y:0{width}x}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
