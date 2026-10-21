# ======================================================================================
# Assignment 15: Block and distrust
# Problem: problems/15-blocklist-distrust.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It decides whether a browser still trusts a certificate chain once some keys are
#   blocked by their SPKI hash and some roots are distrusted, the two ways a browser
#   withdraws trust after an incident. It needs none of your earlier modules, and no later
#   assignment uses it.
#
# Your job:
#   Write the browser's verdict on one chain in `pki/trust.py`: given the chain's
#   certificates (role, SPKI hash and root id, leaf first), the blocked SPKI hashes and
#   the distrusted root ids, return what blocks the chain, or None when the browser trusts
#   it. Check the SPKI blocks first, leaf to root, and the root distrust only when no SPKI
#   block matches (see Two ways to block a chain). The Boilerplate gives you the
#   declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
    # TODO: the SPKI blocks first, then the root distrust; see "Two ways to block a chain" on the
    # problem page.
    raise NotImplementedError("check_chain")
