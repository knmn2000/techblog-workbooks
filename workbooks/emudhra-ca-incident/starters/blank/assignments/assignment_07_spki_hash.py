# ======================================================================================
# Assignment 07: Hash the public key (SPKI)
# Problem: problems/07-spki-hash.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 07 as `python -P tools/run_py.py
#   solutions 07 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 07`, or use Run and Submit in the book.
#
# Your job:
#   Read each `cert` line of the input (see Input) and compute the certificate's SPKI hash
#   with your `x509/spki.py`. Write one `spki` line per certificate, as Output shows.
#
# The other files of this assignment:
#   You also write src/pkiaudit/x509/spki.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/asn1/der.py and
#   src/pkiaudit/x509/certificate.py.
#   Import them as modules of your package, e.g. `from pkiaudit.x509 import spki`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
