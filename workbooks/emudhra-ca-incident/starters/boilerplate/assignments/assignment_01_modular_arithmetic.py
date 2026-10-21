# ======================================================================================
# Assignment 01: Modular arithmetic
# Problem: problems/01-modular-arithmetic.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 01 as `python -P tools/run_py.py
#   solutions 01 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 01`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/ecc/modmath.py in this assignment; each one gives its job
#   at the top.
#   Import them as modules of your package, e.g. `from pkiaudit.ecc import modmath`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 01 (modular arithmetic): answers each `modexp` and `modinv` line of a test input.

The checker runs `assignment_01_modular_arithmetic.py <input-file> <output-file>`. The arithmetic
is in src/pkiaudit/ecc/modmath.py.
"""

import sys

from pkiaudit.ecc.modmath import modexp, modinv


def main(input_path: str, output_path: str) -> None:
    """Writes one answer line per question line of the input."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "modexp":  # modexp <base> <exp> <mod>
                base, exp, mod = int(words[1]), int(words[2]), int(words[3])
                lines.append(f"modexp {modexp(base, exp, mod)}")
            elif words[0] == "modinv":  # modinv <a> <mod>
                inverse = modinv(int(words[1]), int(words[2]))
                lines.append("modinv none" if inverse is None else f"modinv {inverse}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
