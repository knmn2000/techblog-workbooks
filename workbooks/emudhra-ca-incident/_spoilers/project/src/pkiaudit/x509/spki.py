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
    return tbs_fields(cert_bytes)[PUBLIC_KEY_INFO]


def spki_hash(cert_bytes: bytes) -> str:
    """Returns the SHA-256 of a certificate's subjectPublicKeyInfo bytes, as lowercase hex."""
    return hashlib.sha256(find_spki(cert_bytes).encoding(cert_bytes)).hexdigest()
