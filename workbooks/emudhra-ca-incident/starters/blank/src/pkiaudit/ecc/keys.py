# ======================================================================================
# Assignment 12: Generate and validate a key
# Problem: problems/12-generate-key.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module validates a private key before it is used, and generates one by rejection
#   sampling. A key must lie in 1 to n - 1 and sit at least 2^128 (P-256) or 2^192 (P-384)
#   away from 0 and from n; a uniform draw fails that with probability about 2^-127 or
#   2^-191. The generator takes its random source as an argument, so the tests can replay
#   recorded draws through it.
#
# Your job:
#   Write the private-key checks in `ecc/keys.py`: a function that returns the first
#   reason a key is rejected, `out-of-range` before `weak`, or None for a usable key, with
#   the bound from the Weak keys section of the problem page. Add a generator that draws
#   candidates from the random source it is given, as many bytes as the order needs, and
#   redraws until one passes the checks; it uses the operating system's random source when
#   the caller passes none.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
