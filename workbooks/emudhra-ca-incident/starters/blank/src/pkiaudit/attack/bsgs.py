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
#   table limit, in exact integers (see The search).
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
