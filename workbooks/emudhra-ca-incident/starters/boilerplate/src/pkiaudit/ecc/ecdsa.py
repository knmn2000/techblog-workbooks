# ======================================================================================
# Assignment 04: Verify an ECDSA signature
# Problem: problems/04-ecdsa-verify.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module holds ECDSA: checking a signature now, and making one in assignment 11.
#   Your certificate-signature check in assignment 08 calls this verification, and through
#   it so do the chain validation in assignment 09 and the PKI audit in assignment 16.
#
# Your job:
#   Write ECDSA signature verification in `ecc/ecdsa.py`: given a curve, a public key
#   point, a hash read as a number and a signature `(r, s)`, decide whether the signature
#   is valid. Follow the four steps of "The verification equation", with your inverse from
#   `ecc/modmath.py` and your scalar multiplication and point addition from
#   `ecc/curve.py`. The Boilerplate gives you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""ECDSA: checking a signature (assignment 04) and making one (assignment 11).

A public key is a point Q = d*G, where the private key d is a number in [1, n - 1]. A signature on
a message hash z is a pair (r, s) of numbers in the same range.
"""

from pkiaudit.ecc.curve import Curve, add_points, scalar_multiply
from pkiaudit.ecc.modmath import modinv


def verify(curve: Curve, public_key: tuple[int, int], z: int, r: int, s: int) -> bool:
    """Returns True when (r, s) is a valid signature on hash z by the holder of `public_key`."""
    # TODO: the range check, then u1*G + u2*Q; see "The verification equation" on the problem page.
    raise NotImplementedError("verify")


# ---- Assignment 11: signing ------------------------------------------------------------------


def sign(curve: Curve, d: int, z: int, k: int) -> tuple[int, int]:
    """Returns the signature (r, s) on hash z with private key d and one-time number k."""
    # TODO (assignment 11): r from k*G, then s; see "The signing equation" on assignment 11's
    # problem page.
    raise NotImplementedError("sign")
