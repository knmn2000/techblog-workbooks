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
#   own: assignments 07 and 08 reuse them. The Boilerplate gives you the declarations;
#   fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Reading an X.509 certificate's fields out of its DER (assignment 06).

    Certificate    ::= SEQUENCE { tbsCertificate, signatureAlgorithm, signatureValue }
    TBSCertificate ::= SEQUENCE { version [0], serialNumber, signature, issuer, validity,
                                  subject, subjectPublicKeyInfo, ..., extensions [3] }

This module reads tbsCertificate: the names, the validity window, the elliptic-curve public key
and the BasicConstraints extension. Assignment 08 reads the signature around it.
"""

from dataclasses import dataclass

from pkiaudit.asn1 import der
from pkiaudit.ecc.curve import Curve
from pkiaudit.ecc.curves import P256, P384

ID_EC_PUBLIC_KEY = "1.2.840.10045.2.1"
CURVE_OIDS = {"1.2.840.10045.3.1.7": P256, "1.3.132.0.34": P384}
COMMON_NAME_OID = "2.5.4.3"
BASIC_CONSTRAINTS_OID = "2.5.29.19"

# Positions in the list tbs_fields returns: tbsCertificate's fields after the version.
SERIAL, SIGNATURE, ISSUER, VALIDITY, SUBJECT, PUBLIC_KEY_INFO = range(6)


@dataclass(frozen=True)
class Certificate:
    """The fields of a certificate's tbsCertificate that the project uses."""

    serial: int
    issuer_cn: str | None
    subject_cn: str | None
    not_before: str
    not_after: str
    curve: Curve
    public_key: tuple[int, int]
    ca: bool
    pathlen: int | None  # None when there is no path length constraint


def certificate_node(cert_bytes: bytes) -> der.Node:
    """Returns the top-level Certificate SEQUENCE, after checking it has its three fields."""
    # TODO: parse the bytes with your DER reader and check for one SEQUENCE with three
    # children; see "The shape of a certificate" on the problem page.
    raise NotImplementedError("certificate_node")


def tbs_fields(cert_bytes: bytes) -> list[der.Node]:
    """Returns tbsCertificate's fields after the version, so SERIAL to PUBLIC_KEY_INFO index it."""
    # TODO: tbsCertificate is the first field; skip its `[0]` version. See the table under "The
    # shape of a certificate" on the problem page.
    raise NotImplementedError("tbs_fields")


def read_name_cn(name: der.Node) -> str | None:
    """Returns a Name's commonName as text, or None if it has none."""
    # TODO: see "Reading a Name's common name" on the problem page.
    raise NotImplementedError("read_name_cn")


def read_validity(validity: der.Node) -> tuple[str, str]:
    """Returns (notBefore, notAfter) as the text the certificate stores, UTCTime or GeneralizedTime."""
    # TODO: see "Reading validity" on the problem page.
    raise NotImplementedError("read_validity")


def read_public_key(spki: der.Node) -> tuple[Curve, tuple[int, int]]:
    """Returns (curve, (x, y)) from a SubjectPublicKeyInfo that holds an uncompressed EC point."""
    # TODO: check the algorithm, look the curve up in CURVE_OIDS and split the point; see
    # "Reading the public key" on the problem page.
    raise NotImplementedError("read_public_key")


def read_basic_constraints(extensions: der.Node) -> tuple[bool, int | None]:
    """Returns (cA, pathLenConstraint) from the [3] extensions field, or (False, None) if absent."""
    # TODO: find the extension with BASIC_CONSTRAINTS_OID and parse its extnValue as DER again;
    # see "Reading BasicConstraints" on the problem page.
    raise NotImplementedError("read_basic_constraints")


def parse_certificate(cert_bytes: bytes) -> Certificate:
    """Reads the fields of a DER certificate."""
    # TODO: read each field from tbs_fields with the functions above. Extensions, if present,
    # are the `[3]` field right after subjectPublicKeyInfo; without them the certificate is not
    # a CA and has no path length. See "The shape of a certificate" and "Reading
    # BasicConstraints" on the problem page.
    raise NotImplementedError("parse_certificate")
