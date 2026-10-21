# ======================================================================================
# Assignment 07: Hash the public key (SPKI)
# Problem: problems/07-spki-hash.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module computes a key's SPKI hash, the SHA-256 of a certificate's
#   subjectPublicKeyInfo bytes, which is how browsers name a key they block. The hash
#   stays the same in every certificate that carries the key, and assignment 15 blocks
#   whole chains by hashes like these.
#
# Your job:
#   In `x509/spki.py`, find a certificate's subjectPublicKeyInfo field with your
#   `x509/certificate.py` and return the SHA-256 of its original bytes, header included,
#   as lowercase hex. Slice the bytes out of the certificate as they are, as "What gets
#   hashed" describes, without re-encoding the field.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
