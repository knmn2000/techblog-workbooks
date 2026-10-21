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
#   divide with your inverse from `ecc/modmath.py`. The Boilerplate gives you the
#   declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Points on an elliptic curve and the group law (assignment 02, scalar multiplication in 03).

A curve here is y^2 = x^3 + a*x + b over the integers mod a prime p. A point is an (x, y) pair,
and None stands for the point at infinity, the identity of point addition.
"""

from dataclasses import dataclass

from pkiaudit.ecc.modmath import modinv

Point = tuple[int, int] | None  # an affine point, or None for the point at infinity
INFINITY: Point = None


@dataclass(frozen=True)
class Curve:
    """The curve y^2 = x^3 + a*x + b mod p, with a generator g whose order is n."""

    name: str
    p: int
    a: int
    b: int
    g: tuple[int, int]
    n: int

    @property
    def byte_length(self) -> int:
        """Returns how many bytes one coordinate takes: 32 for P-256, 48 for P-384."""
        return (self.p.bit_length() + 7) // 8


def add_points(curve: Curve, p1: Point, p2: Point) -> Point:
    """Returns p1 + p2 on `curve`, by the chord rule for two points or the tangent rule for one."""
    # TODO: the chord-and-tangent rule; see "The point at infinity", "Inverse points", "Adding two
    # different points" and "Doubling a point" on the problem page.
    raise NotImplementedError("add_points")


# ---- Assignment 03: scalar multiplication ----------------------------------------------------


def scalar_multiply(curve: Curve, k: int, point: Point) -> Point:
    """Returns k * point on `curve`, by double-and-add (k >= 0)."""
    # TODO (assignment 03): double-and-add over the bits of k; see "Double-and-add" on assignment
    # 03's problem page.
    raise NotImplementedError("scalar_multiply")
