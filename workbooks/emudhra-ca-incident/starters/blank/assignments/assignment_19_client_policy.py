# ======================================================================================
# Assignment 19: Decide what each client accepts
# Problem: problems/19-client-policy.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 19 as `python -P tools/run_py.py
#   solutions 19 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 19`, or use Run and Submit in the book.
#
# Your job:
#   Read the input line by line (see Input): keep the `client` lines in order, add
#   `blocked-spki`, `distrusted-root`, `revoked` and `logged` lines to four growing sets,
#   and gather the `cert` lines of each `chain` block. Decide each chain once its last
#   `cert` line is read, before a later fact line can reach it, and write one `verdict`
#   line for each chain and client, in the order Output gives.
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/client_policy.py in this assignment; each one gives
#   its job at the top.
#   Earlier files you can use: src/pkiaudit/pki/trust.py.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import client_policy`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================

def main():
    pass


if __name__ == "__main__":
    main()
