# ======================================================================================
# Assignment 08: Check a certificate's signature
# Problem: problems/08-certificate-signature.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module checks that an issuer's public key signed a certificate: it reads the
#   signed tbsCertificate bytes and the signature, hashes the bytes with SHA-384 and runs
#   your ECDSA verify. Assignment 09 checks every link of a chain with it, and assignment
#   16 does the same across a whole PKI.
#
# Your job:
#   In `x509/signature.py`, read a certificate's signed bytes (tbsCertificate's original
#   DER, header included) and its signature values `r` and `s` from the signatureValue BIT
#   STRING. Hash the signed bytes with SHA-384 into ECDSA's `z`, and check the signature
#   against an issuer's curve and public key with your verify from `ecc/ecdsa.py`
#   (assignment 04).
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
