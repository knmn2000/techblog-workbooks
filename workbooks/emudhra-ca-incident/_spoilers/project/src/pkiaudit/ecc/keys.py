"""Generating a private key the way FIPS 186-5 and SEC 1 describe (assignment 12).

Rejection sampling: draw as many random bytes as the order n takes, read them as a big-endian
number, and keep it only if it lies in [1, n - 1]. Otherwise draw again. Reducing an
out-of-range draw mod n would make small keys more likely; rejecting it keeps every key in range
equally likely.
"""

import os
from collections.abc import Callable

from pkiaudit.ecc.curve import Curve


def generate_private_key(curve: Curve, random_bytes: Callable[[int], bytes] = os.urandom) -> int:
    """Returns a private key d in [1, n - 1], drawing candidates from random_bytes(count)."""
    size = (curve.n.bit_length() + 7) // 8  # 32 bytes for P-256, 48 for P-384
    while True:
        candidate = int.from_bytes(random_bytes(size), "big")
        if 1 <= candidate <= curve.n - 1:
            return candidate
