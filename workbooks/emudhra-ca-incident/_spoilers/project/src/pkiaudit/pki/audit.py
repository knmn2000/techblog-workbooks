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
        lines = [f"key {key_id} {finding or 'ok'}" for key_id, finding in self.keys]
        for chain_id, result in self.chains:
            verdict = "trusted" if result.trusted else f"untrusted {result.reason}"
            lines.append(f"chain {chain_id} {verdict}")
        lines += [f"exposed {key_id} {' '.join(chain_ids)}" for key_id, chain_ids in self.exposed.items()]
        return lines


def read_pki(lines: Iterable[str]) -> Pki:
    """Reads the lines of a PKI file."""
    pki = Pki()
    for line in lines:
        words = line.split()
        if not words:
            continue
        if words[0] == "blocklist":
            pki.blocklist.add((words[1], (int(words[2], 16), int(words[3], 16))))
        elif words[0] == "anchor":
            _, anchor_id, curve_name, x, y = words
            anchor = Anchor(CURVES[curve_name], (int(x, 16), int(y, 16)), anchor_id)
            pki.anchors.append(anchor)
            pki.keys[anchor_id] = (anchor.curve, anchor.public_key)
        elif words[0] == "cert":
            _, cert_id, cert_hex = words
            cert_bytes = bytes.fromhex(cert_hex)
            cert = parse_certificate(cert_bytes)
            pki.certificates[cert_id] = cert_bytes
            pki.keys[cert_id] = (cert.curve, cert.public_key)
        elif words[0] == "chain":
            pki.chains.append((words[1], words[2:]))
    return pki


def blast_radius(chains: Sequence[tuple[str, list[str]]],
                 results: Sequence[ChainResult]) -> dict[str, list[str]]:
    """Maps each key id to the chains that depend on it, in chain order."""
    # A chain depends on every certificate above its leaf, whether or not their signatures
    # verified, and on the anchor that signed its topmost certificate, if one did.
    exposed: dict[str, list[str]] = {}
    for (chain_id, cert_ids), result in zip(chains, results):
        for signer_id in cert_ids[1:]:
            exposed.setdefault(signer_id, []).append(chain_id)
        if result.anchor is not None:
            exposed.setdefault(result.anchor.name, []).append(chain_id)
    return exposed


def audit(pki: Pki) -> AuditReport:
    """Lints every key, validates every chain against every anchor, and works out the blast radius."""
    # The whole blocklist applies to every key, wherever the file declares it.
    keys = [(key_id, lint_key(curve, public_key, pki.blocklist))
            for key_id, (curve, public_key) in pki.keys.items()]
    results = [validate_chain([pki.certificates[cert_id] for cert_id in cert_ids], pki.anchors)
               for _chain_id, cert_ids in pki.chains]
    exposed = blast_radius(pki.chains, results)
    return AuditReport(
        keys=keys,
        chains=[(chain_id, result) for (chain_id, _ids), result in zip(pki.chains, results)],
        exposed={key_id: exposed[key_id] for key_id in pki.keys if key_id in exposed},
    )
