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
#   hashed" describes, without re-encoding the field. The Boilerplate gives you the
#   declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""The SPKI hash: SHA-256 of a certificate's subjectPublicKeyInfo (assignment 07).

Browsers and CAs name a key by this hash when they block it. The hash covers the whole
SubjectPublicKeyInfo SEQUENCE (the algorithm identifier and the BIT STRING), in its original bytes,
so a key keeps its hash in every certificate that carries it.
"""

import hashlib

from pkiaudit.asn1 import der
from pkiaudit.x509.certificate import PUBLIC_KEY_INFO, tbs_fields


def find_spki(cert_bytes: bytes) -> der.Node:
    """Returns the subjectPublicKeyInfo node of a DER certificate."""
    # TODO: the same field your certificate.py reads the key from; see "What gets hashed" on the
    # problem page.
    raise NotImplementedError("find_spki")


def spki_hash(cert_bytes: bytes) -> str:
    """Returns the SHA-256 of a certificate's subjectPublicKeyInfo bytes, as lowercase hex."""
    # TODO: hash the node's original bytes, header included; see "What gets hashed" on the
    # problem page.
    raise NotImplementedError("spki_hash")
