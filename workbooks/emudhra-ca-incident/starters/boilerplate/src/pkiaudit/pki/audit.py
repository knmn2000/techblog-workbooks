# ======================================================================================
# Assignment 16: Audit a PKI
# Problem: problems/16-audit-pki.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It audits a whole PKI file: a lint finding for every key, a verdict for every chain,
#   and the chains each signing key would break if it leaked. The checker's program and
#   the `pkiaudit audit` command both print its report.
#
# Your job:
#   Write the PKI audit in `pki/audit.py`, from reading a PKI file to the lines of its
#   report. Read the `blocklist`, `anchor`, `cert` and `chain` lines (see Input), then
#   lint every key with your `lint_key` from assignment 13 against the whole blocklist,
#   wherever its lines appear in the file, and validate every chain against all the
#   anchors with your `validate_chain` from assignment 09, with no current time. Work out
#   which chains depend on each signing key (see The three things you report), then write
#   the report's `key`, `chain` and `exposed` lines (see Output). The Boilerplate gives
#   you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Auditing a whole PKI (assignment 16).

The audit makes the findings eMudhra, Mozilla and Chrome needed after the disclosure, for every
key and chain in a PKI file:

| Finding | How the audit finds it |
|---|---|
| bad keys | assignment 13's lint, anchors included |
| the chains a verifier trusts | assignment 09's checks, with no current time |
| each signing key's blast radius | the chains that depend on the key, and would break if it leaked |

A PKI file declares one thing per line, and the audit reads it in this format:

| Line | Declares |
|---|---|
| blocklist <curve> <x> <y> | a known-compromised public key |
| anchor <id> <curve> <x> <y> | a trust anchor, a public key with no certificate |
| cert <id> <hex> | a DER certificate |
| chain <chain-id> <id> <id> ... | a chain of certificate ids, leaf first |

The report has a `key` line per anchor and certificate, a `chain` line per chain, and an
`exposed` line per key that some chain depends on.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from pkiaudit.ecc.curve import Curve
from pkiaudit.ecc.curves import CURVES
from pkiaudit.pki.chain import Anchor, ChainResult, validate_chain
from pkiaudit.pki.lint import lint_key
from pkiaudit.x509.certificate import parse_certificate


@dataclass
class Pki:
    """The declarations of a PKI file, each kind in file order."""

    blocklist: set[tuple[str, tuple[int, int]]] = field(default_factory=set)  # (curve name, (x, y))
    keys: dict[str, tuple[Curve, tuple[int, int]]] = field(default_factory=dict)  # anchor and cert ids
    anchors: list[Anchor] = field(default_factory=list)
    certificates: dict[str, bytes] = field(default_factory=dict)  # cert id -> DER
    chains: list[tuple[str, list[str]]] = field(default_factory=list)  # (chain id, cert ids leaf first)


@dataclass
class AuditReport:
    """The audit's findings, in the order the report lists them."""

    keys: list[tuple[str, str | None]]  # (key id, lint finding or None)
    chains: list[tuple[str, ChainResult]]  # (chain id, verdict)
    exposed: dict[str, list[str]]  # key id -> the chains that depend on it

    def lines(self) -> list[str]:
        """Returns the report as text, one finding per line."""
        # TODO: the `key`, `chain` and `exposed` lines, in that order; see "Output" on the
        # problem page.
        raise NotImplementedError("AuditReport.lines")


def read_pki(lines: Iterable[str]) -> Pki:
    """Reads the lines of a PKI file."""
    # TODO: one declaration per line; a `cert` line's key comes from your parse_certificate. See
    # "Input" on the problem page.
    raise NotImplementedError("read_pki")


def blast_radius(chains: Sequence[tuple[str, list[str]]],
                 results: Sequence[ChainResult]) -> dict[str, list[str]]:
    """Maps each key id to the chains that depend on it, in chain order."""
    # TODO: the signers each chain depends on; see "Report blast radius" under "The three things
    # you report" on the problem page.
    raise NotImplementedError("blast_radius")


def audit(pki: Pki) -> AuditReport:
    """Lints every key, validates every chain against every anchor, and works out the blast radius."""
    # The whole blocklist applies to every key, wherever the file declares it.
    # TODO: your lint_key on every key, your validate_chain on every chain with no current time,
    # then blast_radius; see "The three things you report" on the problem page.
    raise NotImplementedError("audit")
