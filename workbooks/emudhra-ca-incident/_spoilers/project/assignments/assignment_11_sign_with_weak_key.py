"""Assignment 11 (sign with a weak key): makes the signature each `sign` line of a test input asks for.

The checker runs `assignment_11_sign_with_weak_key.py <input-file> <output-file>`. Signing is in
src/pkiaudit/ecc/ecdsa.py.
"""

import sys

from pkiaudit.ecc.curves import CURVES
from pkiaudit.ecc.ecdsa import sign


def main(input_path: str, output_path: str) -> None:
    """Writes `signature <id> <r> <s>` for each `sign <id> <curve> <d> <z> <k>` line (numbers in hex)."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            _, case_id, curve_name, d, z, k = words
            curve = CURVES[curve_name]
            r, s = sign(curve, int(d, 16), int(z, 16), int(k, 16))
            width = 2 * curve.byte_length
            lines.append(f"signature {case_id} {r:0{width}x} {s:0{width}x}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
