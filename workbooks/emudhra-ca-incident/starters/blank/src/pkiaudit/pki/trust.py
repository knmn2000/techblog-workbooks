# ======================================================================================
# Assignment 15: Block and distrust
# Problem: problems/15-blocklist-distrust.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It decides whether a browser still trusts a certificate chain once some keys are
#   blocked by their SPKI hash and some roots are distrusted, the two ways a browser
#   withdraws trust after an incident. It needs none of your earlier modules, and no later
#   assignment uses it.
#
# Your job:
#   Write the browser's verdict on one chain in `pki/trust.py`: given the chain's
#   certificates (role, SPKI hash and root id, leaf first), the blocked SPKI hashes and
#   the distrusted root ids, return what blocks the chain, or None when the browser trusts
#   it. Check the SPKI blocks first, leaf to root, and the root distrust only when no SPKI
#   block matches (see Two ways to block a chain).
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
