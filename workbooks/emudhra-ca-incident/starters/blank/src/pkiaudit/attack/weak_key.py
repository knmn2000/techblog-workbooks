# ======================================================================================
# Assignment 10: Find a weak private key
# Problem: problems/10-find-weak-key.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module recovers a private key from its public key when the private key is a small
#   d or n - d, by trying every d up to a bound. Assignment 13's linter calls it to flag a
#   weak key before a CA trusts or publishes it.
#
# Your job:
#   Implement the small-key search in `attack/weak_key.py`: given a curve, a public key
#   and a bound, find the d from 1 to the bound whose multiple of the generator equals the
#   key (answer d) or the key's negation (answer -d), or report that there is none. Step
#   through the multiples with your point addition from `ecc/curve.py`, one addition per
#   step, and compare each with both points.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
