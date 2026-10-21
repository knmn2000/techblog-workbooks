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
#   Write the assignment 11 program, which reads `sign` lines and writes one `signature`
#   line for each. It reads the curve name and the hex values of d, z and k as the Input
#   section describes, signs with your `ecc/ecdsa.py`, and writes r and s in zero-padded
#   lowercase hex in the Output format.
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
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
