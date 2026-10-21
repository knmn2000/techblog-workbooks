# ======================================================================================
# Assignment 10: Find a weak private key
# Problem: problems/10-find-weak-key.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module recovers a private key from its public key when the private key is small,
#   by trying every value up to a bound. Assignment 13's linter calls it to flag a weak
#   key before a CA trusts or publishes it.
#
# Your job:
#   Implement the small-key search in `attack/weak_key.py`: given a curve, a public key
#   and a bound, find the private key from 1 to the bound whose multiple of the generator
#   equals the key, or report that there is none. Step through the multiples with your
#   point addition from `ecc/curve.py`, one addition per step. The Boilerplate gives you
#   the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Recovering a private key that is too small (assignment 10).

A public key is Q = d*G. When d is small, walking G, 2G, 3G, ... reaches Q after d steps. Each
step adds G to the point before it, so a search up to `bound` costs `bound` point additions. The
incident's intermediate keys fell to this search.
"""

from pkiaudit.ecc.curve import Curve, add_points


def find_private_key(curve: Curve, public_key: tuple[int, int], bound: int) -> int | None:
    """Returns the d in [1, bound] with d*G == public_key, or None if there is none."""
    # TODO: step from 1*G up to bound*G, one addition of G per step, and compare each point with
    # the key; see "How a public key relates to its private key" on the problem page.
    raise NotImplementedError("find_private_key")
