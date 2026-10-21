# ======================================================================================
# Assignment 01: Modular arithmetic
# Problem: problems/01-modular-arithmetic.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module holds the project's arithmetic mod a number: powers by
#   square-and-multiply, and inverses by the extended Euclidean algorithm. Your
#   `ecc/curve.py` from assignment 02 divides mod p with the inverse, and your
#   `ecc/ecdsa.py` divides mod n with it in assignments 04 and 11.
#
# Your job:
#   Write modular exponentiation and the modular inverse in `ecc/modmath.py`. Raise a
#   number to a power mod `mod` by square-and-multiply, and find an inverse with the
#   extended Euclidean algorithm, returning a value that means "no inverse" when `gcd(a,
#   mod)` isn't 1. Handle `mod = 1` and `exp = 0` as "Special cases" describes.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
