# ======================================================================================
# Assignment 02: Add points on a toy curve
# Problem: problems/02-toy-curve.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module holds the elliptic-curve group law: the curve type, points, the point at
#   infinity and the rule that adds two points. Assignment 03 adds scalar multiplication
#   to it, and your ECDSA code from assignment 04 and the weak-key search in assignment 10
#   run on its point addition.
#
# Your job:
#   Declare a curve type and a point type in `ecc/curve.py`, and write the function that
#   adds two points on a curve. A curve holds `p`, `a`, `b`, a generator `G` and its order
#   `n`; a point is an `(x, y)` pair or the point at infinity. Follow "The point at
#   infinity", "Inverse points", "Adding two different points" and "Doubling a point", and
#   divide with your inverse from `ecc/modmath.py`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
