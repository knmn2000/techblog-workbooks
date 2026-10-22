# ======================================================================================
# Assignment 18: Verify a revocation list's signature
# Problem: problems/18-crl-signature.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module reads a certificate revocation list (CRL) and checks its signature against
#   the key its issuer publishes. It keeps one state per issuer: once a list fails, or
#   verifies only under a weak key, that issuer's lists stay halted until its published
#   key changes. It reuses your signature check from assignment 08 and your key linter
#   from assignment 13.
#
# Your job:
#   Write `read_crl`, which finds a CRL's issuer commonName, its signed bytes and its
#   signature, and a `CrlWatch` that remembers each issuer's published key and whether the
#   issuer is halted. Check each CRL by the four rules in their order (see The four
#   rules), with your `check_signature` from assignment 08 and your `lint_key` from
#   assignment 13.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
