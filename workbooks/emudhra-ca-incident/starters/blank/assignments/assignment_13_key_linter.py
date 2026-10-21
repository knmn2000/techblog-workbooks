# ======================================================================================
# Assignment 13: Lint a public key
# Problem: problems/13-key-linter.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 13 as `python -P tools/run_py.py
#   solutions 13 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 13`, or use Run and Submit in the book.
#
# Your job:
#   Read the input line by line (see Input): add each `blocklist` line's curve and point
#   to a blocklist that grows as you read, and lint each `key` line's point, on its curve,
#   against the blocklist so far. Write `ok <label>` or `fail <label> <finding>` for each
#   key, in input order (see Output).
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/lint.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/attack/weak_key.py, src/pkiaudit/ecc/curve.py
#   and src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import lint`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
