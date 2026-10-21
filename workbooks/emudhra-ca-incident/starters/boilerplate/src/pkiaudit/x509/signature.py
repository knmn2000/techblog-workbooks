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
#   (assignment 04). The Boilerplate gives you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Checking a certificate's signature (assignment 08).

The issuer signs tbsCertificate's original DER bytes. The signatureValue BIT STRING holds the
signature as DER again: ECDSA-Sig-Value ::= SEQUENCE { r INTEGER, s INTEGER }. Every issuer in
this project signs with ecdsa-with-SHA384.
"""

import hashlib
from dataclasses import dataclass

from pkiaudit.asn1 import der
from pkiaudit.ecc import ecdsa
from pkiaudit.ecc.curve import Curve
from pkiaudit.x509.certificate import certificate_node


@dataclass(frozen=True)
class SignedData:
    """What a certificate's issuer signed, and the signature: the TBS bytes and (r, s)."""

    tbs: bytes  # tbsCertificate's original bytes, header included
    r: int
    s: int


def read_signed_data(cert_bytes: bytes) -> SignedData:
    """Reads the signed bytes and the signature out of a DER certificate."""
    # TODO: tbsCertificate's original bytes, and r and s from the signatureValue BIT STRING;
    # see "What the issuer signs" and step 2 of "The equation" on the problem page.
    raise NotImplementedError("read_signed_data")


def tbs_hash(tbs: bytes, curve: Curve) -> int:
    """Returns ECDSA's z for the signed bytes: SHA-384, cut to as many leading bits as the curve's n has."""
    # TODO: SHA-384 of `tbs`, read as a big-endian number; see step 1 of "The equation" on the
    # problem page. P-384's n has 384 bits, as many as the digest, so nothing gets cut there.
    raise NotImplementedError("tbs_hash")


def check_signature(signed: SignedData, issuer_curve: Curve, issuer_key: tuple[int, int]) -> bool:
    """Returns True when the issuer's public key verifies the certificate's signature."""
    # TODO: your ECDSA verify from assignment 04, with z from tbs_hash; see step 3 of "The
    # equation" on the problem page.
    raise NotImplementedError("check_signature")
