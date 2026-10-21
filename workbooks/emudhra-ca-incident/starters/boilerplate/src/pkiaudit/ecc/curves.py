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
#   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
#   in this assignment's other files.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""The curves the project uses: a toy curve small enough to work by hand (assignment 02), and
the NIST curves P-256 and P-384 (assignment 03).
"""

from pkiaudit.ecc.curve import Curve

# y^2 = x^3 + 2x + 2 mod 17. It has 19 points counting infinity, so G = (5, 1) has order 19.
TOY = Curve(name="toy", p=17, a=2, b=2, g=(5, 1), n=19)


# ---- Assignment 03: the NIST curves ----------------------------------------------------------

# Constants from SEC 2 and NIST SP 800-186. On both curves a = p - 3.
P256 = Curve(
    name="P-256",
    p=0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
    a=0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc,
    b=0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
    g=(0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
       0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5),
    n=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551,
)

P384 = Curve(
    name="P-384",
    p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff,
    a=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000fffffffc,
    b=0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef,
    g=(0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7,
       0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f),
    n=0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973,
)

CURVES = {curve.name: curve for curve in (P256, P384)}  # by the names test inputs use
