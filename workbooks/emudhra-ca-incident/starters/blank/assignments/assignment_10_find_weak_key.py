# ======================================================================================
# Assignment 10: Find a weak private key
# Problem: problems/10-find-weak-key.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 10 as `python -P tools/run_py.py
#   solutions 10 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 10`, or use Run and Submit in the book.
#
# Your job:
#   Write the assignment 10 program, which reads `bound` and `key` lines and writes one
#   verdict per key. It searches each key with the latest bound and the curve named on its
#   line, as the Input section describes, and writes a `weak` line, with `d` or `-d`, or a
#   `none` line in the Output format.
#
# The other files of this assignment:
#   You also write src/pkiaudit/attack/weak_key.py in this assignment; each one gives its
#   job at the top.
#   Earlier files you can use: src/pkiaudit/ecc/curve.py and src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.attack import weak_key`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
