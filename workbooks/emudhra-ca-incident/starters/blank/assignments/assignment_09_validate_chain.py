# ======================================================================================
# Assignment 09: Validate a certificate chain
# Problem: problems/09-validate-chain.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 09 as `python -P tools/run_py.py
#   solutions 09 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 09`, or use Run and Submit in the book.
#
# Your job:
#   Write the assignment 09 program, which reads the input's `chain` blocks and writes one
#   verdict line for each. It collects each block's `now`, `anchor` and `cert` lines as
#   the Input section describes, validates the chain with your `pki/chain.py`, and writes
#   `trusted` or `untrusted <reason>` in the Output format.
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/chain.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/x509/certificate.py,
#   src/pkiaudit/x509/signature.py, src/pkiaudit/ecc/curve.py and
#   src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import chain`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
