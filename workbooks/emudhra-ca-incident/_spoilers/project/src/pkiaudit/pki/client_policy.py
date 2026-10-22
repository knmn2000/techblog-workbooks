"""What each client accepts (assignment 19).

A client's decision on a chain depends on which mechanisms it has. This module models a client as
four switches: whether it holds the SPKI blocklist, whether its root bundle has dropped the
distrusted roots, how much of the chain it looks up for revocation, and whether it requires
Certificate Transparency. `decide` runs your `check_chain` from assignment 15 first, with only the
sets this client holds, then revocation, then CT, and returns the first reason it finds.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from pkiaudit.pki.trust import ChainCert, check_chain


@dataclass(frozen=True)
class ClientPolicy:
    """One client's four switches."""

    revocation: str  # "off", "leaf" or "chain"
    blocklist: bool  # holds the SPKI blocklist
    ct_required: bool  # rejects a leaf without CT proofs
    bundle_updated: bool  # its root bundle no longer holds the distrusted roots


@dataclass
class Facts:
    """The facts the input has given so far. The sets grow as the program reads on."""

    blocked_spki: set[str]
    distrusted_roots: set[str]
    revoked: set[str]  # certificate names
    logged: set[str]  # certificate names


@dataclass(frozen=True)
class Reject:
    """Why a client rejects a chain: the reason word and what it names (a role, a root id, or "")."""

    reason: str  # "blocked-spki", "distrusted-root", "revoked" or "missing-ct"
    what: str = ""


def first_revoked(chain: Sequence[ChainCert], names: Sequence[str], mode: str,
                  revoked: set[str]) -> str | None:
    """The role of the first revoked certificate the client looks up, leaf first, or None.
    A certificate the revocation data doesn't list counts as not revoked."""
    looked_up = {"off": 0, "leaf": 1, "chain": len(chain)}[mode]
    for cert, name in zip(chain[:looked_up], names[:looked_up]):
        if name in revoked:
            return cert.role
    return None


def decide(chain: Sequence[ChainCert], names: Sequence[str], client: ClientPolicy,
           facts: Facts) -> Reject | None:
    """Why `client` rejects the chain, or None when it accepts it. `names[i]` is the name of
    `chain[i]`, and both run leaf first."""
    # Stage one is assignment 15's verdict, with only the lists this client holds.
    block = check_chain(chain,
                        facts.blocked_spki if client.blocklist else set(),
                        facts.distrusted_roots if client.bundle_updated else set())
    if block is not None:
        return Reject("blocked-spki" if block.mechanism == "spki" else "distrusted-root", block.what)
    role = first_revoked(chain, names, client.revocation, facts.revoked)
    if role is not None:
        return Reject("revoked", role)
    # Logs issue CT proofs (SCTs) for the leaf, so only the leaf's logging matters.
    if client.ct_required and names[0] not in facts.logged:
        return Reject("missing-ct")
    return None
