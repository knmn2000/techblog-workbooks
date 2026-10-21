"""Assignment 04 (ECDSA verify): checks the P-384 signature on each `verify` line of a test input.

The checker runs `assignment_04_ecdsa_verify.py <input-file> <output-file>`. Verification is in
src/pkiaudit/ecc/ecdsa.py.
"""

import sys

from pkiaudit.ecc.curves import P384
from pkiaudit.ecc.ecdsa import verify


def main(input_path: str, output_path: str) -> None:
    """Writes `valid` or `invalid` for each `verify <pubx> <puby> <hash> <r> <s>` line (all hex)."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            pubx, puby, z, r, s = (int(w, 16) for w in words[1:6])
            lines.append("valid" if verify(P384, (pubx, puby), z, r, s) else "invalid")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
