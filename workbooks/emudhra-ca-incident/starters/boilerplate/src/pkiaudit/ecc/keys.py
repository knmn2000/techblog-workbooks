# ======================================================================================
# Assignment 12: Generate a key correctly
# Problem: problems/12-generate-key.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module turns random bytes into a private key the way FIPS 186-5 and SEC 1
#   describe, so that every key from 1 to n - 1 is equally likely. It takes the random
#   source as an argument, so the tests can replay recorded draws through it.
#
# Your job:
#   Implement private-key generation by rejection sampling in `ecc/keys.py`: draw
#   candidates from the random source you are given until one lies in the valid range for
#   the curve's order, and return it. Ask for as many bytes as the order needs, and use
#   the operating system's random source when the caller passes none. The Boilerplate
#   gives you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
    # TODO: draw, check the range, draw again until a candidate is accepted; see "Rejection
    # sampling" on the problem page.
    raise NotImplementedError("generate_private_key")
