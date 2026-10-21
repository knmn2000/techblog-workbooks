# ======================================================================================
# Assignment 04: Verify an ECDSA signature
# Problem: problems/04-ecdsa-verify.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 04 as `python -P tools/run_py.py
#   solutions 04 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 04`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished: it reads the input, calls your code
#   and writes the answer. You fill in the TODOs in this assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/ecc/ecdsa.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/ecc/modmath.py, src/pkiaudit/ecc/curve.py and
#   src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.ecc import ecdsa`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
