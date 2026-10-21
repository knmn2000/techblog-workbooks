# ======================================================================================
# Assignment 06: Read a certificate
# Problem: problems/06-read-certificate.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module reads the fields of an X.509 certificate that the project needs: the
#   subject and issuer names, the validity window, the elliptic-curve public key and
#   whether the certificate is a CA. Assignment 07 finds the public key field through it,
#   08 the signed bytes, and 09 and 16 validate chains with the fields it reads.
#
# Your job:
#   In `x509/certificate.py`, read the fields of a DER certificate's tbsCertificate with
#   your DER reader from assignment 05: the serial number, the issuer's and subject's
#   common names, the two validity times, the curve and public key point, and the
#   BasicConstraints values. Give the curve as your `P256` or `P384` from `ecc/curves.py`,
#   and read a certificate without BasicConstraints as not a CA, with no path length. Keep
#   finding the top-level SEQUENCE and listing tbsCertificate's fields as steps of their
#   own: assignments 07 and 08 reuse them.
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
