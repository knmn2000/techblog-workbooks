# ======================================================================================
# Assignment 09: Validate a certificate chain
# Problem: problems/09-validate-chain.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module decides whether a verifier should trust a chain of certificates, leaf
#   first, that ends at one of its trust anchors, and names the first check that fails if
#   not. Assignment 16 runs it over every chain in a PKI to find the chains a bad key
#   breaks.
#
# Your job:
#   Implement chain validation in `pki/chain.py`: given DER certificates, leaf first, and
#   a list of trust anchors, run the four checks in the page's order and report the first
#   one that fails. Define the trust anchor and the verdict the program uses, and read
#   each certificate and its signature with your code from assignments 06 and 08. The
#   Boilerplate gives you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
    # TODO: try each anchor's key in turn; see check 1 under "The four checks, in order" on the
    # problem page.
    raise NotImplementedError("find_anchor")


def validate_chain(chain: Sequence[bytes], anchors: Sequence[Anchor],
                   now: str | None = None) -> ChainResult:
    """Checks DER certificates, leaf first, against the anchors; `now` None skips the validity check."""
    # TODO: parse each certificate and its signature, then run the checks in order and return at
    # the first failure; see "The four checks, in order" on the problem page.
    raise NotImplementedError("validate_chain")
