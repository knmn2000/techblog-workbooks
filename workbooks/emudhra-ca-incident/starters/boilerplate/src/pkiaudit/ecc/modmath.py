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
#   mod)` isn't 1. Handle `mod = 1` and `exp = 0` as "Special cases" describes. The
#   Boilerplate gives you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Arithmetic modulo a number: powers and inverses (assignment 01).

Every curve operation in the project divides by a number mod p, and ECDSA divides mod n. Both
divisions are a multiplication by the inverse that `modinv` finds.
"""


def modexp(base: int, exp: int, mod: int) -> int:
    """Returns base ** exp mod `mod`, by square-and-multiply (mod >= 1, exp >= 0, base >= 0)."""
    # TODO: square-and-multiply; see "Modular exponentiation" and "Special cases" on the problem page.
    raise NotImplementedError("modexp")


def modinv(a: int, mod: int) -> int | None:
    """Returns the x in [0, mod) with a * x = 1 mod `mod`, or None when gcd(a, mod) is not 1."""
    # TODO: the extended Euclidean algorithm; see "Modular inverse" and "Special cases" on the
    # problem page.
    raise NotImplementedError("modinv")
