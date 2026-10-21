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
    tbs, _algorithm, signature_value = certificate_node(cert_bytes).children
    _unused, signature = der.decode_bit_string(signature_value.content)
    r, s = der.parse_all(signature)[0].children[:2]
    return SignedData(tbs.encoding(cert_bytes), der.decode_integer(r.content), der.decode_integer(s.content))


def tbs_hash(tbs: bytes, curve: Curve) -> int:
    """Returns ECDSA's z for the signed bytes: SHA-384, cut to as many leading bits as the curve's n has."""
    digest = hashlib.sha384(tbs).digest()
    z = int.from_bytes(digest, "big")
    excess = 8 * len(digest) - curve.n.bit_length()
    return z >> excess if excess > 0 else z


def check_signature(signed: SignedData, issuer_curve: Curve, issuer_key: tuple[int, int]) -> bool:
    """Returns True when the issuer's public key verifies the certificate's signature."""
    return ecdsa.verify(issuer_curve, issuer_key, tbs_hash(signed.tbs, issuer_curve), signed.r, signed.s)
