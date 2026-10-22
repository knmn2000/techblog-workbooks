# ======================================================================================
# Assignment 19: Decide what each client accepts
# Problem: problems/19-client-policy.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module decides, for one certificate chain and one client, whether the client
#   accepts it. A client is four switches: whether it holds the SPKI blocklist, whether
#   its root bundle is updated, how much of the chain it checks for revocation and whether
#   it requires Certificate Transparency. It reuses your `check_chain` from assignment 15
#   for the blocklist and the root distrust, and no later assignment uses it.
#
# Your job:
#   Write `decide` in `pki/client_policy.py`: given a chain with its certificate names,
#   one client's four switches and the facts read so far, return why the client rejects
#   the chain, or None when it accepts it. Call your `check_chain` from assignment 15
#   first, with only the sets this client holds, then check revocation and Certificate
#   Transparency (see The order of the checks). The Boilerplate gives you the
#   declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
    # TODO: look up the certificates `mode` covers; see "What the switches mean" on the problem page.
    raise NotImplementedError("first_revoked")


def decide(chain: Sequence[ChainCert], names: Sequence[str], client: ClientPolicy,
           facts: Facts) -> Reject | None:
    """Why `client` rejects the chain, or None when it accepts it. `names[i]` is the name of
    `chain[i]`, and both run leaf first."""
    # TODO: your check_chain with this client's sets, then revocation, then CT; see "The order of
    # the checks" on the problem page.
    raise NotImplementedError("decide")
