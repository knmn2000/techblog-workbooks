# ======================================================================================
# Assignment 05: Read DER
# Problem: problems/05-der-reader.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 05 as `python -P tools/run_py.py
#   solutions 05 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 05`, or use Run and Submit in the book.
#
# Your job:
#   Read each `der` line of the input (see Input) and parse its bytes with your DER reader
#   from `asn1/der.py`. Walk every node depth first and write one `node` line for each,
#   with its value decoded by type, as Output and "Decoding each type's content" describe.
#
# The other files of this assignment:
#   You also write src/pkiaudit/asn1/der.py in this assignment; each one gives its job at
#   the top.
#   Import them as modules of your package, e.g. `from pkiaudit.asn1 import der`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
