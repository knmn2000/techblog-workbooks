"""ECDSA: checking a signature (assignment 04) and making one (assignment 11).

A public key is a point Q = d*G, where the private key d is a number in [1, n - 1]. A signature on
a message hash z is a pair (r, s) of numbers in the same range.
"""

from pkiaudit.ecc.curve import Curve, add_points, scalar_multiply
from pkiaudit.ecc.modmath import modinv


def verify(curve: Curve, public_key: tuple[int, int], z: int, r: int, s: int) -> bool:
    """Returns True when (r, s) is a valid signature on hash z by the holder of `public_key`."""
    n = curve.n
    if not (1 <= r <= n - 1 and 1 <= s <= n - 1):
        return False
    w = modinv(s, n)
    u1 = (z * w) % n
    u2 = (r * w) % n
    # u1*G + u2*Q lands on the signer's point k*G when the signer made s from this z and Q's d.
    point = add_points(curve, scalar_multiply(curve, u1, curve.g), scalar_multiply(curve, u2, public_key))
    if point is None:
        return False
    return point[0] % n == r


# ---- Assignment 11: signing ------------------------------------------------------------------


def sign(curve: Curve, d: int, z: int, k: int) -> tuple[int, int]:
    """Returns the signature (r, s) on hash z with private key d and one-time number k."""
    # k must be secret and used once: two signatures with the same k and key give away d.
    n = curve.n
    r = scalar_multiply(curve, k, curve.g)[0] % n
    s = modinv(k, n) * (z + r * d) % n
    return r, s
