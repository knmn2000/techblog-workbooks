"""Blocking keys and distrusting roots (assignment 15).

A browser has two ways to stop trusting certificates after an incident. An SPKI block names one
key by its SPKI hash (assignment 07) and stops it wherever it appears. A root distrust stops the
whole hierarchy under a root. `check_chain` tries the finer SPKI block first, leaf to root, and
falls back to the root distrust only when the blocklist names no key in the chain.
"""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ChainCert:
    """One certificate of a chain as the browser sees it: its role, SPKI hash and root id."""

    role: str  # "leaf", "intermediate" or "root"
    spki: str
    root_id: str


@dataclass(frozen=True)
class Block:
    """What stops a chain: "spki" with the blocked certificate's role, or "root" with the root id."""

    mechanism: str
    what: str


def check_chain(chain: Sequence[ChainCert], blocked_spki: set[str],
                distrusted_roots: set[str]) -> Block | None:
    """Returns the Block that stops a chain, leaf first, or None when the browser trusts it."""
    for cert in chain:
        if cert.spki in blocked_spki:
            return Block("spki", cert.role)
    for cert in chain:
        if cert.role == "root" and cert.root_id in distrusted_roots:
            return Block("root", cert.root_id)
    return None
