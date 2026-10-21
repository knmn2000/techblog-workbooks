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
#   Read each `mul <curve> <d>` line, look up the curve by name in your `ecc/curves.py`
#   and compute `d*G` with your scalar multiplication from `ecc/curve.py`. Write the two
#   coordinates in lowercase hex, each zero-padded to the curve's width, as the Output
#   section gives.
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
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
