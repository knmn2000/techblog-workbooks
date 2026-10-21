# ======================================================================================
# Assignment 11: Sign a certificate with a recovered key
# Problem: problems/11-sign-with-weak-key.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 11 as `python -P tools/run_py.py
#   solutions 11 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 11`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   It adds to src/pkiaudit/ecc/ecdsa.py, which you started earlier: Add ECDSA signing to
#   `ecc/ecdsa.py`, next to the verification you wrote in assignment 04: given a curve, a
#   private key, a message hash and a nonce, compute the signature pair (r, s). Build it
#   from your scalar multiplication in `ecc/curve.py` and your modular inverse in
#   `ecc/modmath.py`. The Boilerplate's `ecc/ecdsa.py` from assignment 04 already declares
#   it as `sign` under its assignment 11 marker; if you wrote the file your own way, add
#   the function now.
#   Earlier files you can use: src/pkiaudit/ecc/modmath.py, src/pkiaudit/ecc/curve.py and
#   src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.ecc import ecdsa`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
