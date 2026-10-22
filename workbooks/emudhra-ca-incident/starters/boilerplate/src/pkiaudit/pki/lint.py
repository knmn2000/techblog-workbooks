# ======================================================================================
# Assignment 13: Lint a public key
# Problem: problems/13-key-linter.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It decides whether a public key is safe to trust: the point is on its curve, it is not
#   on a blocklist of known-compromised keys, and its private key is not small enough to
#   find by search. Assignment 16 lints every key in a PKI with it.
#
# Your job:
#   Write the key linter in `pki/lint.py`: a test that a point satisfies its curve's
#   equation, and a function that runs the three checks in their order and returns the
#   first finding, or None for a good key. For the weak check, call your weak-key search
#   from assignment 10 with the bound of 4096; it finds d*G and -(d*G) alike (see The
#   three checks). The Boilerplate gives you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Linting a public key before a CA trusts or publishes it (assignment 13).

Three checks run from cheapest to most expensive, and the first that fails names the problem:

| Check | Finding |
|---|---|
| The point satisfies the curve's equation | off-curve |
| The key is not on the blocklist of known-compromised keys | known-compromised |
| The private key is not d or n - d for any d up to the bound | weak |

Any one of them, run by the CA, would have caught the incident's keys.
"""

from pkiaudit.attack.weak_key import find_private_key
from pkiaudit.ecc.curve import Curve

WEAK_BOUND = 4096  # how far the weak-key search goes, for both signs (the problem page explains the size)


def on_curve(curve: Curve, point: tuple[int, int]) -> bool:
    """Returns True when the point's coordinates are in [0, p) and satisfy y^2 = x^3 + a*x + b."""
    # TODO: the curve equation, mod p; see "The curves" on the problem page.
    raise NotImplementedError("on_curve")


def lint_key(curve: Curve, public_key: tuple[int, int],
             blocklist: set[tuple[str, tuple[int, int]]]) -> str | None:
    """Returns the first finding ("off-curve", "known-compromised" or "weak"), or None for a good key."""
    # The blocklist holds (curve name, (x, y)) pairs.
    # TODO: run the checks in order and stop at the first that fails; see "The three checks" on
    # the problem page.
    raise NotImplementedError("lint_key")
