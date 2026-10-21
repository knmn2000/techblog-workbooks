# ======================================================================================
# Assignment 13: Lint a public key
# Problem: problems/13-key-linter.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It decides whether a public key is safe to trust: the point is on its curve, it is not
#   on a blocklist of known-compromised keys, and its private key is not small enough to
#   find by search. Assignment 16 lints every key in a PKI with it.
#
# Your job:
#   Write the key linter in `pki/lint.py`: a test that a point satisfies its curve's
#   equation, and a function that runs the three checks in their order and returns the
#   first finding, or None for a good key. For the weak check, call your weak-key search
#   from assignment 10 with the bound of 4096 (see The three checks).
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
