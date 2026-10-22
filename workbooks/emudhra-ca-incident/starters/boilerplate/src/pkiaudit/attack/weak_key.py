# ======================================================================================
# Assignment 10: Find a weak private key
# Problem: problems/10-find-weak-key.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module recovers a private key from its public key when the private key is a small
#   d or n - d, by trying every d up to a bound. Assignment 13's linter calls it to flag a
#   weak key before a CA trusts or publishes it.
#
# Your job:
#   Implement the small-key search in `attack/weak_key.py`: given a curve, a public key
#   and a bound, find the d from 1 to the bound whose multiple of the generator equals the
#   key (answer d) or the key's negation (answer -d), or report that there is none. Step
#   through the multiples with your point addition from `ecc/curve.py`, one addition per
#   step, and compare each with both points. The Boilerplate gives you the declarations;
#   fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Recovering a private key that is too small (assignment 10).

A public key is Q = d*G. When d is small, walking G, 2G, 3G, ... reaches Q after d steps. Each
step adds G to the point before it, so a search up to `bound` costs `bound` point additions. The
incident's intermediate keys fell to this search.

The private key n - d gives -(d*G), the point d*G with y replaced by p - y. Comparing each step's
point with -Q as well as Q finds that key in the same walk, with no extra additions.
"""

from pkiaudit.ecc.curve import Curve, add_points


def find_private_key(curve: Curve, public_key: tuple[int, int], bound: int) -> int | None:
    """Returns d when public_key == d*G, or -d when public_key == -(d*G), for d in [1, bound].

    -d stands for the private key n - d, which equals -d mod n. Returns None if neither matches.
    """
    # TODO: step from 1*G up to bound*G, one addition of G per step, and compare each point with
    # the key and with its negation; see "How a public key relates to its private key" and
    # "The negated key" on the problem page.
    raise NotImplementedError("find_private_key")
