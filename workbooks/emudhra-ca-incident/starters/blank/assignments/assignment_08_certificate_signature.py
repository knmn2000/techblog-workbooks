# ======================================================================================
# Assignment 08: Check a certificate's signature
# Problem: problems/08-certificate-signature.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 08 as `python -P tools/run_py.py
#   solutions 08 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 08`, or use Run and Submit in the book.
#
# Your job:
#   Read the input's `cert` and `issuer_pubkey` line pairs (see Input) and check each
#   certificate's signature against the issuer key with your `x509/signature.py`. Write
#   one `signature <label> valid` or `invalid` line per pair, as Output shows.
#
# The other files of this assignment:
#   You also write src/pkiaudit/x509/signature.py in this assignment; each one gives its
#   job at the top.
#   Earlier files you can use: src/pkiaudit/asn1/der.py, src/pkiaudit/x509/certificate.py,
#   src/pkiaudit/ecc/ecdsa.py, src/pkiaudit/ecc/curve.py and src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.x509 import signature`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
