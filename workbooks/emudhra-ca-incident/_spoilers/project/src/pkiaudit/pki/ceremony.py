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
        duplicate = label in self.known
        self.identities += 1
        self.points_at[label] = self.identities
        self.generated_as[self.identities] = label
        self.unattested.add(self.identities)
        self.known.add(label)
        return duplicate

    def wrap(self, label: str, wrapped_label: str) -> None:
        """Exports the key `label` names as `wrapped_label`."""
        self._carry(label, wrapped_label)

    def unwrap(self, wrapped_label: str, label: str) -> None:
        """Imports the key `wrapped_label` names back under `label`."""
        self._carry(wrapped_label, label)

    def _carry(self, source: str, target: str) -> None:
        # An undefined source leaves the target naming no identity.
        self.points_at[target] = self.points_at.get(source)
        self.known.add(target)

    def fingerprint(self, label: str, value: str) -> None:
        """Records the fingerprint of the key `label` names."""
        self.latest[label] = value
        identity = self.points_at.get(label)
        if identity in self.unattested:
            self.attested[identity] = value
            self.unattested.discard(identity)

    def publish(self, label: str) -> Publication:
        """Checks the key `label` names against the fingerprint attested at its generation."""
        if label not in self.known:
            return Publication("undefined")
        identity = self.points_at[label]
        if self.latest.get(label) == self.attested.get(identity):
            return Publication("ok")
        return Publication("MISMATCH", self.generated_as.get(identity))
