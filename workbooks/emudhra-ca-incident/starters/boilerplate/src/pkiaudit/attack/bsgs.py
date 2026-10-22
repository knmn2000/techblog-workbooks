# ======================================================================================
# Assignment 17: Find a weak key in square-root time
# Problem: problems/17-baby-step-giant-step.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module finds a small private key with about 2 * sqrt(bound) point additions,
#   where assignment 10's loop spends one per candidate. It stores a table of baby steps,
#   walks giant steps from the public key in both directions, and its `plan` function says
#   what a table size costs in steps. No later assignment uses it.
#
# Your job:
#   Implement baby-step giant-step in `attack/bsgs.py`: a table from the x of each `j*G`,
#   for `j` from 1 to `m`, to `j` and y, and a walk from the public key in steps of
#   `2m*G`, down and then up, that looks up each point's x and compares y. Write `plan`
#   too, which returns the table size and the number of giant points for a bound and a
#   table limit, in exact integers (see The search). The Boilerplate gives you the
#   declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Finding a small private key in square-root time: baby-step giant-step (assignment 17).

Assignment 10's search spends one point addition per candidate. This one stores the m baby
steps 1*G .. m*G in a table keyed by x, then visits giant points Q - c*G for centres c that are
2m apart. A giant point with the x of j*G is j*G or -(j*G), so it gives e = c + j or e = c - j
for Q = e*G, and its y says which. Each giant point therefore covers the 2m + 1 keys from c - m
to c + m, and walking both ways from Q covers every key from -bound to bound with about
bound / m giant points.
"""

from math import isqrt

from pkiaudit.ecc.curve import Curve, Point, add_points, scalar_multiply


def plan(bound: int, table_limit: int | None = None) -> tuple[int, int]:
    """Returns (m, giant points) for a search of keys -bound .. bound with at most table_limit
    baby steps: m = min(ceil(sqrt(bound)), table_limit), and 2*g - 1 giant points, Q and g - 1
    on each side of it, with g = ceil((bound + m) / (2m))."""
    # TODO: compute m and the giant points in exact integers (isqrt, and // to round up); see
    # "The search" on the problem page.
    raise NotImplementedError("plan")


def build_baby_table(curve: Curve, m: int) -> dict[int, tuple[int, int]]:
    """Returns {x of j*G: (j, y of j*G)} for j = 1 .. m."""
    # TODO: step from 1*G to m*G, one addition of G per step, storing each point's x with j and
    # y; see "The baby steps" on the problem page.
    raise NotImplementedError("build_baby_table")


def find_private_key_bsgs(curve: Curve, public_key: tuple[int, int], bound: int,
                          table: dict[int, tuple[int, int]]) -> int | None:
    """Returns the e with 1 <= |e| <= bound and e*G == public_key, or None if there is none.
    `table` comes from build_baby_table(curve, m); a negative e means the key is -(|e|*G)."""
    # TODO: walk down from Q by -(2m*G), then up from Q by 2m*G, and look up each point's x in
    # the table, as "The giant steps" on the problem page describes. Handle the point at
    # infinity, and keep only an e with 1 <= |e| <= bound.
    raise NotImplementedError("find_private_key_bsgs")
