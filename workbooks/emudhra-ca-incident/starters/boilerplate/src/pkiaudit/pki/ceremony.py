# ======================================================================================
# Assignment 14: Check a key ceremony
# Problem: problems/14-ceremony-checker.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It replays the log of a key generation ceremony and checks that each CSR carries the
#   public key the witnesses approved, identifying keys by fingerprint and never by label.
#   It flags labels that collide and deviations from the script. It needs none of your
#   earlier modules, and no later assignment uses it.
#
# Your job:
#   Write the ceremony state in `pki/ceremony.py`, which replays a key ceremony log one
#   step at a time: generate, approve, deviation, csr and publish. Identify each key by
#   its public-key fingerprint and never by its label, and let the priorities under Output
#   decide the line when several findings apply (see Identifying a key and Deviations).
#   The Boilerplate gives you the declarations; fill in each TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Checking the log of a key ceremony (assignment 14).

A ceremony log is a list of steps. `Ceremony` replays them one at a time and returns the line the
step writes to the output, or None when the step writes nothing:

| Step | What the ceremony does | Output |
|---|---|---|
| generate <label> <fp> | the HSM makes a key pair named `label` | `duplicate` or `similar` finding, if any |
| approve <label> <fp> | the witnesses approve the key behind `label` | none |
| deviation <approver> | the ceremony departs from its script | one line |
| csr <label> <fp> | the operator makes a CSR; `fp` names the public key it carries | one line |
| publish <label> | the ceremony publishes the certificate for the latest CSR of `label` | one line |

A key is identified by the fingerprint of its public key, never by its label. Labels are only
compared to find collisions: exact reuse (`duplicate`) and reuse after normalising case and
separators (`similar`). A CSR is checked against the fingerprint approved for its label. An
approved deviation clears every approval, so the keys need approving again. An unapproved one
makes every later CSR and publish unverified.
"""

from dataclasses import dataclass, field


def normalise(label: str) -> str:
    """Lowercases a label and removes `-`, `_` and `.`, so labels that look alike compare equal."""
    # TODO: the rule under "Label collisions" on the problem page.
    raise NotImplementedError("normalise")


@dataclass
class Ceremony:
    """The state of a key ceremony, replayed one step at a time."""

    generated: list[tuple[str, str]] = field(default_factory=list)  # (label, fingerprint), in log order
    approved: dict[str, str] = field(default_factory=dict)  # label -> the fingerprint approved for it
    csr_passed: dict[str, bool] = field(default_factory=dict)  # label -> was its latest CSR ok
    unverified: bool = False  # set for good by a deviation nobody approved

    def generate(self, label: str, fingerprint: str) -> str | None:
        """Records a new key; returns the finding for its label, if it collides with an earlier one."""
        # TODO: `duplicate` or `similar`, never both; see "Label collisions" and the priorities
        # under "Output" on the problem page.
        raise NotImplementedError("Ceremony.generate")

    def approve(self, label: str, fingerprint: str) -> None:
        """The witnesses approve the key with this fingerprint under `label`, replacing any earlier approval."""
        # TODO: see the `approve` row under "Input" on the problem page.
        raise NotImplementedError("Ceremony.approve")

    def deviation(self, approver: str) -> str:
        """A departure from the script. Without an approver, the ceremony cannot verify anything after it."""
        # TODO: see "Deviations" on the problem page.
        raise NotImplementedError("Ceremony.deviation")

    def csr(self, label: str, fingerprint: str) -> str:
        """Checks the key a CSR carries against the key approved for `label`."""
        # TODO: pick the status by priority, and remember whether this CSR passed; see
        # "Identifying a key" and "Output" on the problem page.
        raise NotImplementedError("Ceremony.csr")

    def publish(self, label: str) -> str:
        """Publishes the latest CSR under `label` only if it passed and the ceremony is still verified."""
        # TODO: see the `publish` lines under "Output" on the problem page.
        raise NotImplementedError("Ceremony.publish")
