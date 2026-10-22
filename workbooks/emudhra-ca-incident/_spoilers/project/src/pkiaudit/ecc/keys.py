"""Validating and generating private keys (assignment 12).

A private key d is valid when 1 <= d <= n - 1. A valid key is still unusable when it is absurdly
small, or absurdly close to n: d and n - d give public keys that share an x-coordinate, so n - 4
is as easy to find as 4. A uniform draw lands within 2^(L/2) of 0 or n with probability about
2^(1 - L/2), where L is the bit length of n (2^-127 for P-256, 2^-191 for P-384), so a key
that does was not drawn uniformly.

Generation is rejection sampling: draw as many random bytes as n takes, read them as a big-endian
number, and draw again until the candidate passes validation.
"""

import os
from collections.abc import Callable

from pkiaudit.ecc.curve import Curve


def weak_bound(curve: Curve) -> int:
    """Returns 2^(L/2), where L is the bit length of the order: 2^128 for P-256, 2^192 for P-384."""
    return 1 << (curve.n.bit_length() // 2)


def validate_private_key(curve: Curve, d: int) -> str | None:
    """Returns None for a usable private key, or the first reason to reject it."""
    if not 1 <= d <= curve.n - 1:
        return "out-of-range"  # decided first: 0 is also below the weak bound
    bound = weak_bound(curve)
    if d < bound or curve.n - d < bound:
        return "weak"
    return None


def generate_private_key(curve: Curve, random_bytes: Callable[[int], bytes] = os.urandom) -> int:
    """Returns a private key that passes validation, drawing candidates from random_bytes(count)."""
    size = (curve.n.bit_length() + 7) // 8  # 32 bytes for P-256, 48 for P-384
    while True:
        candidate = int.from_bytes(random_bytes(size), "big")
        if validate_private_key(curve, candidate) is None:
            return candidate
