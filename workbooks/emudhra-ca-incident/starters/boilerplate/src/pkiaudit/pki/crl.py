# ======================================================================================
# Assignment 18: Verify a revocation list's signature
# Problem: problems/18-crl-signature.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module reads a certificate revocation list (CRL) and checks its signature against
#   the key its issuer publishes. It keeps one state per issuer: once a list fails, or
#   verifies only under a weak key, that issuer's lists stay halted until its published
#   key changes. It reuses your signature check from assignment 08 and your key linter
#   from assignment 13.
#
# Your job:
#   Write `read_crl`, which finds a CRL's issuer commonName, its signed bytes and its
#   signature, and a `CrlWatch` that remembers each issuer's published key and whether the
#   issuer is halted. Check each CRL by the four rules in their order (see The four
#   rules), with your `check_signature` from assignment 08 and your `lint_key` from
#   assignment 13. The Boilerplate gives you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
    # TODO: find the issuer Name in tbsCertList, skipping the version when it is there, and read
    # its commonName; see "Where the issuer is" on the problem page. Your read_signed_data from
    # assignment 08 gives the signed bytes and (r, s).
    raise NotImplementedError("read_crl")


class CrlWatch:
    """Each issuer's published key, and the set of issuers whose CRLs are halted."""

    def __init__(self) -> None:
        self.keys: dict[str, tuple[Curve, tuple[int, int]]] = {}
        self.halted: set[str] = set()

    def set_key(self, issuer: str, curve: Curve, public_key: tuple[int, int]) -> None:
        """Records the key the issuer's certificate publishes. A different key releases a halt."""
        # TODO: see the `key` line in Input on the problem page.
        raise NotImplementedError("CrlWatch.set_key")

    def check(self, crl: Crl) -> str | None:
        """Returns why the CRL is halted ("issuer-halted", "signature-failed" or "weak-key"), or None."""
        # TODO: the four rules, in their order; see "The four rules" on the problem page.
        raise NotImplementedError("CrlWatch.check")
