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
    if p1 is INFINITY:
        return p2
    if p2 is INFINITY:
        return p1
    p = curve.p
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % p == 0:  # p2 is -p1: the line through them is vertical
        return INFINITY
    if p1 == p2:
        slope = (3 * x1 * x1 + curve.a) * modinv(2 * y1, p) % p  # the tangent at p1
    else:
        slope = (y2 - y1) * modinv(x2 - x1, p) % p  # the line through p1 and p2
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return (x3, y3)


# ---- Assignment 03: scalar multiplication ----------------------------------------------------


def scalar_multiply(curve: Curve, k: int, point: Point) -> Point:
    """Returns k * point on `curve`, by double-and-add (k >= 0)."""
    # Walk k's bits from the lowest: `addend` runs through point, 2*point, 4*point, ... and each
    # 1 bit adds its multiple into the result. That costs about 2 * log2(k) point additions.
    result = INFINITY
    addend = point
    while k > 0:
        if k & 1:
            result = add_points(curve, result, addend)
        addend = add_points(curve, addend, addend)
        k >>= 1
    return result
