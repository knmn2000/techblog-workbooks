# ======================================================================================
# Assignment 04: Verify an ECDSA signature
# Problem: problems/04-ecdsa-verify.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module holds ECDSA: checking a signature now, and making one in assignment 11.
#   Your certificate-signature check in assignment 08 calls this verification, and through
#   it so do the chain validation in assignment 09 and the PKI audit in assignment 16.
#
# Your job:
#   Write ECDSA signature verification in `ecc/ecdsa.py`: given a curve, a public key
#   point, a hash read as a number and a signature `(r, s)`, decide whether the signature
#   is valid. Follow the four steps of "The verification equation", with your inverse from
#   `ecc/modmath.py` and your scalar multiplication and point addition from
#   `ecc/curve.py`.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
