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
#   Read each `verify <pubx> <puby> <hash> <r> <s>` line, parse all five values as hex
#   numbers, and check the signature on P-384 with your verification from `ecc/ecdsa.py`.
#   Write `valid` or `invalid` for each line, in input order, as the Output section shows.
#
# The other files of this assignment:
#   You also write src/pkiaudit/ecc/ecdsa.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/ecc/modmath.py, src/pkiaudit/ecc/curve.py and
#   src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.ecc import ecdsa`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
