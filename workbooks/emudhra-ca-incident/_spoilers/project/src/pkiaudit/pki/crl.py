"""Checking a certificate revocation list's signature, and halting an issuer whose list fails (assignment 18).

    CertificateList ::= SEQUENCE { tbsCertList, signatureAlgorithm, signatureValue }
    TBSCertList     ::= SEQUENCE { version INTEGER OPTIONAL, signature, issuer, thisUpdate, ... }

A CRL carries its signature the way a certificate does, so `read_signed_data` and
`check_signature` from assignment 08 work on it unchanged. The new parsing is the issuer, whose
position depends on whether the optional version is there.

`CrlWatch` keeps one state per issuer. Its checks run in this order, and the first that applies
gives the verdict:

| Check | Verdict |
|---|---|
| The issuer is halted | issuer-halted |
| The signature does not verify under the issuer's published key | signature-failed (halts) |
| `lint_key` has a finding for the published key | weak-key (halts) |

Only a `set_key` with a different key releases a halted issuer.
"""

from dataclasses import dataclass

from pkiaudit.asn1 import der
from pkiaudit.ecc.curve import Curve
from pkiaudit.pki.lint import lint_key
from pkiaudit.x509.certificate import certificate_node, read_name_cn
from pkiaudit.x509.signature import SignedData, check_signature, read_signed_data


@dataclass(frozen=True)
class Crl:
    """The parts of a CRL the watch needs: who issued it, and what was signed with which signature."""

    issuer_cn: str
    signed: SignedData


def read_crl(crl_bytes: bytes) -> Crl:
    """Reads a DER CRL's issuer commonName, its signed tbsCertList bytes and its signature."""
    fields = certificate_node(crl_bytes).children[0].children
    if fields[0].tag == der.INTEGER:  # version: v2 CRLs carry it, v1 CRLs leave it out
        fields = fields[1:]
    issuer_cn = read_name_cn(fields[1])  # fields[0] is the signature AlgorithmIdentifier
    if issuer_cn is None:
        raise ValueError("the CRL's issuer has no commonName")
    return Crl(issuer_cn, read_signed_data(crl_bytes))


class CrlWatch:
    """Each issuer's published key, and the set of issuers whose CRLs are halted."""

    def __init__(self) -> None:
        self.keys: dict[str, tuple[Curve, tuple[int, int]]] = {}
        self.halted: set[str] = set()

    def set_key(self, issuer: str, curve: Curve, public_key: tuple[int, int]) -> None:
        """Records the key the issuer's certificate publishes. A different key releases a halt."""
        if self.keys.get(issuer) != (curve, public_key):
            self.halted.discard(issuer)
        self.keys[issuer] = (curve, public_key)

    def check(self, crl: Crl) -> str | None:
        """Returns why the CRL is halted ("issuer-halted", "signature-failed" or "weak-key"), or None."""
        issuer = crl.issuer_cn
        if issuer in self.halted:
            return "issuer-halted"  # a list that verifies after a failure proves nothing yet
        curve, public_key = self.keys[issuer]
        if not check_signature(crl.signed, curve, public_key):
            self.halted.add(issuer)
            return "signature-failed"
        # Every published key is on its curve and the blocklist is empty, so a finding means weak.
        if lint_key(curve, public_key, set()) is not None:
            self.halted.add(issuer)
            return "weak-key"
        return None
