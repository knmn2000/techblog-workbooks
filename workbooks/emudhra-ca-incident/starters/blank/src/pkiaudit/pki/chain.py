# ======================================================================================
# Assignment 09: Validate a certificate chain
# Problem: problems/09-validate-chain.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module decides whether a verifier should trust a chain of certificates, leaf
#   first, that ends at one of its trust anchors, and names the first check that fails if
#   not. Assignment 16 runs it over every chain in a PKI to find the chains a bad key
#   breaks.
#
# Your job:
#   Implement chain validation in `pki/chain.py`: given DER certificates, leaf first, and
#   a list of trust anchors, run the four checks in the page's order and report the first
#   one that fails. Define the trust anchor and the verdict the program uses, and read
#   each certificate and its signature with your code from assignments 06 and 08.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
