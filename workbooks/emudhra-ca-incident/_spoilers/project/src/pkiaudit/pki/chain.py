"""Validating a certificate chain (assignment 09).

This is the core of RFC 5280's path validation, cut down to these checks, run in this order:

| Check | Fails with |
|---|---|
| The next certificate up signed each certificate below it | bad-signature |
| A trust anchor signed the topmost certificate | unknown-anchor |
| Every certificate above the leaf is a CA | not-a-ca |
| No signer has more intermediates below it than its pathLenConstraint allows | path-too-long |
| Every certificate's validity window covers the current time | expired |

Assignment 16 runs the same checks over a whole PKI, without a current time.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from pkiaudit.ecc.curve import Curve
from pkiaudit.x509.certificate import parse_certificate
from pkiaudit.x509.signature import SignedData, check_signature, read_signed_data

REASONS = ("bad-signature", "unknown-anchor", "not-a-ca", "path-too-long", "expired")


@dataclass(frozen=True)
class Anchor:
    """A public key the verifier trusts with no certificate; `name` labels it in reports."""

    curve: Curve
    public_key: tuple[int, int]
    name: str = ""


@dataclass(frozen=True)
class ChainResult:
    """A chain's verdict: `reason` is None for a trusted chain, else one of REASONS.

    `anchor` is the anchor that signed the topmost certificate. It stays set when a later check
    fails, and is None when the signature checks failed first.
    """

    reason: str | None = None
    anchor: Anchor | None = None

    @property
    def trusted(self) -> bool:
        """Returns True when the chain passed every check."""
        return self.reason is None


def find_anchor(signed: SignedData, anchors: Sequence[Anchor]) -> Anchor | None:
    """Returns the first anchor whose key verifies the signature, or None."""
    for anchor in anchors:
        if check_signature(signed, anchor.curve, anchor.public_key):
            return anchor
    return None


def validate_chain(chain: Sequence[bytes], anchors: Sequence[Anchor],
                   now: str | None = None) -> ChainResult:
    """Checks DER certificates, leaf first, against the anchors; `now` None skips the validity check."""
    certs = [parse_certificate(cert_bytes) for cert_bytes in chain]
    signed = [read_signed_data(cert_bytes) for cert_bytes in chain]

    # 1. Signatures. The chain holds no root certificate: an anchor's key signs the topmost one.
    for i in range(len(certs) - 1):
        issuer = certs[i + 1]
        if not check_signature(signed[i], issuer.curve, issuer.public_key):
            return ChainResult("bad-signature")
    anchor = find_anchor(signed[-1], anchors)
    if anchor is None:
        return ChainResult("unknown-anchor")

    # 2. Every signer, so every certificate above the leaf, must have cA set.
    if not all(cert.ca for cert in certs[1:]):
        return ChainResult("not-a-ca", anchor)

    # 3. A signer's pathLenConstraint bounds the intermediates between it and the leaf. The
    # certificate at position i (leaf = 0) has i - 1 of them.
    for i in range(1, len(certs)):
        if certs[i].pathlen is not None and i - 1 > certs[i].pathlen:
            return ChainResult("path-too-long", anchor)

    # 4. Validity. Every time here has the same format, so comparing the text compares the times.
    if now is not None and not all(cert.not_before <= now <= cert.not_after for cert in certs):
        return ChainResult("expired", anchor)

    return ChainResult(None, anchor)
