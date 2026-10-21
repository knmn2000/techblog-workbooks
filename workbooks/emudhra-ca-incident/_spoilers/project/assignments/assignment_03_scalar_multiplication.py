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
