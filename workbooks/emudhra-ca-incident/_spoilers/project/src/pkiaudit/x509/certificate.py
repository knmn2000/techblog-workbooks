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
    top = der.parse_all(cert_bytes)
    if len(top) != 1 or top[0].tag != der.SEQUENCE or not top[0].constructed:
        raise ValueError("a certificate is exactly one top-level SEQUENCE")
    if len(top[0].children) != 3:
        raise ValueError("a Certificate has exactly 3 fields: tbsCertificate, "
                         "signatureAlgorithm, signatureValue")
    return top[0]


def tbs_fields(cert_bytes: bytes) -> list[der.Node]:
    """Returns tbsCertificate's fields after the version, so SERIAL to PUBLIC_KEY_INFO index it."""
    fields = certificate_node(cert_bytes).children[0].children
    if fields and fields[0].cls == "context" and fields[0].tag == 0:
        return fields[1:]  # version [0] EXPLICIT: every certificate here is v3
    return fields


def read_name_cn(name: der.Node) -> str | None:
    """Returns a Name's commonName as text, or None if it has none."""
    # Name ::= SEQUENCE OF RelativeDistinguishedName, each a SET OF { type OID, value }.
    for rdn in name.children:
        for attribute in rdn.children:
            attr_type, value = attribute.children
            if der.decode_oid(attr_type.content) == COMMON_NAME_OID:
                return value.content.decode("utf-8")
    return None


def read_validity(validity: der.Node) -> tuple[str, str]:
    """Returns (notBefore, notAfter) as the text the certificate stores, UTCTime or GeneralizedTime."""
    not_before, not_after = validity.children
    return not_before.content.decode("ascii"), not_after.content.decode("ascii")


def read_public_key(spki: der.Node) -> tuple[Curve, tuple[int, int]]:
    """Returns (curve, (x, y)) from a SubjectPublicKeyInfo that holds an uncompressed EC point."""
    # SubjectPublicKeyInfo ::= SEQUENCE { AlgorithmIdentifier { algorithm, curve }, BIT STRING }
    algorithm, public_key_bits = spki.children
    algorithm_oid, parameters = algorithm.children
    if der.decode_oid(algorithm_oid.content) != ID_EC_PUBLIC_KEY:
        raise ValueError("subjectPublicKeyInfo algorithm is not id-ecPublicKey")
    curve_oid = der.decode_oid(parameters.content)
    if curve_oid not in CURVE_OIDS:
        raise ValueError(f"unrecognised curve OID {curve_oid}")
    _unused, point = der.decode_bit_string(public_key_bits.content)
    if not point or point[0] != 0x04:
        raise ValueError("expected an uncompressed EC point (0x04 || x || y)")
    width = (len(point) - 1) // 2
    x = int.from_bytes(point[1:1 + width], "big")
    y = int.from_bytes(point[1 + width:], "big")
    return CURVE_OIDS[curve_oid], (x, y)


def read_basic_constraints(extensions: der.Node) -> tuple[bool, int | None]:
    """Returns (cA, pathLenConstraint) from the [3] extensions field, or (False, None) if absent."""
    # Extension ::= SEQUENCE { extnID, critical BOOLEAN DEFAULT FALSE, extnValue OCTET STRING }:
    # critical may be missing, so extnValue is the last field.
    for extension in extensions.children[0].children:
        if der.decode_oid(extension.children[0].content) != BASIC_CONSTRAINTS_OID:
            continue
        # extnValue's content is DER again: BasicConstraints ::= SEQUENCE { cA, pathLen }.
        constraints = der.parse_all(extension.children[-1].content)[0].children
        ca = False
        if constraints and constraints[0].tag == der.BOOLEAN:
            ca = constraints[0].content[0] != 0
            constraints = constraints[1:]  # cA is DEFAULT FALSE, so DER leaves it out when false
        pathlen = der.decode_integer(constraints[0].content) if constraints else None
        return ca, pathlen
    return False, None  # RFC 5280 4.2.1.9: a certificate without BasicConstraints is not a CA


def parse_certificate(cert_bytes: bytes) -> Certificate:
    """Reads the fields of a DER certificate."""
    fields = tbs_fields(cert_bytes)
    not_before, not_after = read_validity(fields[VALIDITY])
    curve, public_key = read_public_key(fields[PUBLIC_KEY_INFO])
    ca, pathlen = False, None
    # Extensions, when present, come right after the public key: no certificate here has the
    # optional unique IDs [1] and [2] that may sit between them.
    rest = fields[PUBLIC_KEY_INFO + 1:]
    if rest and rest[0].cls == "context" and rest[0].tag == 3:
        ca, pathlen = read_basic_constraints(rest[0])
    return Certificate(
        serial=der.decode_integer(fields[SERIAL].content),
        issuer_cn=read_name_cn(fields[ISSUER]),
        subject_cn=read_name_cn(fields[SUBJECT]),
        not_before=not_before,
        not_after=not_after,
        curve=curve,
        public_key=public_key,
        ca=ca,
        pathlen=pathlen,
    )
