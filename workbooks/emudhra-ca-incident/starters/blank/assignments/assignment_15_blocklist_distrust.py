# ======================================================================================
# Assignment 15: Block and distrust
# Problem: problems/15-blocklist-distrust.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 15 as `python -P tools/run_py.py
#   solutions 15 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 15`, or use Run and Submit in the book.
#
# Your job:
#   Read the input line by line (see Input): add `blocked-spki` and `distrusted-root`
#   lines to two growing sets, and gather the `cert` lines of each `chain` block. Check
#   each chain against the two sets with your `check_chain` and write one `chain` line per
#   chain, in input order (see Output).
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/trust.py in this assignment; each one gives its job at
#   the top.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import trust`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
