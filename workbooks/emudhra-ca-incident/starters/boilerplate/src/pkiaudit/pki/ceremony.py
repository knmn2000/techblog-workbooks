# ======================================================================================
# Assignment 14: Check a key ceremony
# Problem: problems/14-ceremony-checker.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It replays the log of a key generation ceremony and follows each key from the step
#   that made it to the step that publishes it, so a reused label or a key that changed on
#   the way gets flagged. It needs none of your earlier modules, and no later assignment
#   uses it.
#
# Your job:
#   Write the ceremony state in `pki/ceremony.py`, which replays a key ceremony log one
#   step at a time: generate, wrap, unwrap, fingerprint and publish. Give every generate
#   step a new key identity, even when it reuses a label, and let wrap and unwrap pass the
#   identity a label names on to another label. A publish reports `ok`, `undefined`, or a
#   mismatch with the label the key was generated under (see Chains of custody). The
#   Boilerplate gives you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Checking the log of a key ceremony (assignment 14).

A ceremony log is a list of steps. `Ceremony` replays them one at a time:

| Step | What the ceremony does |
|---|---|
| generate <label> <curve> | makes a new key and names it `label` |
| wrap <label> <wrapped> | exports the key `label` names, encrypted, as `wrapped` |
| unwrap <wrapped> <label> | imports `wrapped` back under `label` |
| fingerprint <label> <hex> | records the fingerprint of the key `label` names |
| publish <label> | publishes the key `label` names |

Each generate makes a new key identity, even when it reuses a label. A label names one identity
at a time, and wrap and unwrap pass the identity on to another label. The ceremony tracks
identities by number, so reusing a label for a new key leaves earlier wraps pointing at the old
key. The first fingerprint recorded after a key's generation attests that key. A publish is ok
only when the label's latest fingerprint matches its identity's attested one.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Publication:
    """The result of a publish step: "ok", "undefined" or "MISMATCH".

    For a mismatch, `generated_as` is the label the key's generate step used, where an auditor
    starts looking.
    """

    status: str
    generated_as: str | None = None


@dataclass
class Ceremony:
    """The state of a key ceremony, replayed one step at a time."""

    known: set[str] = field(default_factory=set)  # every label a step has defined
    points_at: dict[str, int | None] = field(default_factory=dict)  # label -> the identity it names
    generated_as: dict[int, str] = field(default_factory=dict)  # identity -> its generate label
    attested: dict[int, str] = field(default_factory=dict)  # identity -> its first fingerprint
    latest: dict[str, str] = field(default_factory=dict)  # label -> the last fingerprint recorded for it
    unattested: set[int] = field(default_factory=set)  # identities with no fingerprint yet
    identities: int = 0  # how many keys the ceremony has generated

    def generate(self, label: str) -> bool:
        """Makes a new key named `label`; returns True when the label was already in use."""
        # TODO: a new identity, even for a reused label; see the `generate` row under "Input" on
        # the problem page.
        raise NotImplementedError("Ceremony.generate")

    def wrap(self, label: str, wrapped_label: str) -> None:
        """Exports the key `label` names as `wrapped_label`."""
        self._carry(label, wrapped_label)

    def unwrap(self, wrapped_label: str, label: str) -> None:
        """Imports the key `wrapped_label` names back under `label`."""
        self._carry(wrapped_label, label)

    def _carry(self, source: str, target: str) -> None:
        """Passes the identity `source` names on to `target`, for wrap and unwrap."""
        # TODO: `target` names whatever identity `source` names now (none, when `source` is
        # undefined); see the `wrap` and `unwrap` rows under "Input" on the problem page.
        raise NotImplementedError("Ceremony._carry")

    def fingerprint(self, label: str, value: str) -> None:
        """Records the fingerprint of the key `label` names."""
        # TODO: the label's latest fingerprint, and the attested one for a new identity; see
        # "Chains of custody" on the problem page.
        raise NotImplementedError("Ceremony.fingerprint")

    def publish(self, label: str) -> Publication:
        """Checks the key `label` names against the fingerprint attested at its generation."""
        # TODO: undefined, ok or MISMATCH; see "Output" and "Chains of custody" on the problem
        # page.
        raise NotImplementedError("Ceremony.publish")
