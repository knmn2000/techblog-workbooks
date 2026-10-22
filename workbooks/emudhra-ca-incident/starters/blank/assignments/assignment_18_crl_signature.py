# ======================================================================================
# Assignment 18: Verify a revocation list's signature
# Problem: problems/18-crl-signature.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 18 as `python -P tools/run_py.py
#   solutions 18 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 18`, or use Run and Submit in the book.
#
# Your job:
#   Read the input's `key` and `crl` lines in order (see Input) and check each CRL with
#   your `pki/crl.py`. Write one `crl <label> ok` or `crl <label> halt <reason>` line per
#   `crl` line, as Output shows.
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/crl.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/asn1/der.py, src/pkiaudit/x509/certificate.py,
#   src/pkiaudit/x509/signature.py, src/pkiaudit/pki/lint.py and
#   src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import crl`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
