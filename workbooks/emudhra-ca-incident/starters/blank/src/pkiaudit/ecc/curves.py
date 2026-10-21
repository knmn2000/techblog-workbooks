# ======================================================================================
# Assignment 02: Add points on a toy curve
# Problem: problems/02-toy-curve.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module holds the constants of every curve the project uses: the toy curve now,
#   and P-256 and P-384, which assignment 03 adds. Later assignments look up P-256 and
#   P-384 here, from the certificate reader in assignment 06 to the PKI audit in
#   assignment 16.
#
# Your job:
#   Define the toy curve `y^2 = x^3 + 2x + 2 mod 17` in `ecc/curves.py` as a value of your
#   curve type, with generator `G = (5, 1)` of order 19. Assignment 03 adds P-256 and
#   P-384 to this file.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
