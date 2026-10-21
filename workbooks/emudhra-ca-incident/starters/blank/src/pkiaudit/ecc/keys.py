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
#   the operating system's random source when the caller passes none.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
