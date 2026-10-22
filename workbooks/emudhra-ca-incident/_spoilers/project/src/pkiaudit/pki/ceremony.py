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

_SEPARATORS = str.maketrans("", "", "-_.")


def normalise(label: str) -> str:
    """Lowercases a label and removes `-`, `_` and `.`, so labels that look alike compare equal."""
    return label.lower().translate(_SEPARATORS)


@dataclass
class Ceremony:
    """The state of a key ceremony, replayed one step at a time."""

    generated: list[tuple[str, str]] = field(default_factory=list)  # (label, fingerprint), in log order
    approved: dict[str, str] = field(default_factory=dict)  # label -> the fingerprint approved for it
    csr_passed: dict[str, bool] = field(default_factory=dict)  # label -> was its latest CSR ok
    unverified: bool = False  # set for good by a deviation nobody approved

    def generate(self, label: str, fingerprint: str) -> str | None:
        """Records a new key; returns the finding for its label, if it collides with an earlier one."""
        finding = None
        if any(earlier == label for earlier, _ in self.generated):
            finding = f"duplicate {label}"
        else:
            for earlier, _ in self.generated:
                if normalise(earlier) == normalise(label):
                    finding = f"similar {label} {earlier}"  # the earliest label that matches
                    break
        self.generated.append((label, fingerprint))
        return finding

    def approve(self, label: str, fingerprint: str) -> None:
        """The witnesses approve the key with this fingerprint under `label`, replacing any earlier approval."""
        self.approved[label] = fingerprint

    def deviation(self, approver: str) -> str:
        """A departure from the script. Without an approver, the ceremony cannot verify anything after it."""
        if approver == "none":
            self.unverified = True
            return "deviation none UNAPPROVED"
        self.approved.clear()  # the keys have to be verified again after the change
        return f"deviation {approver} approved"

    def csr(self, label: str, fingerprint: str) -> str:
        """Checks the key a CSR carries against the key approved for `label`."""
        if self.unverified:
            status = "UNVERIFIED"
        elif label not in self.approved:
            status = "NOT-APPROVED"
        elif self.approved[label] != fingerprint:
            status = f"MISMATCH {self._generated_as(fingerprint)}"
        else:
            status = "ok"
        self.csr_passed[label] = status == "ok"
        return f"csr {label} {status}"

    def publish(self, label: str) -> str:
        """Publishes the latest CSR under `label` only if it passed and the ceremony is still verified."""
        if label not in self.csr_passed:
            status = "undefined"
        elif self.unverified:
            status = "UNVERIFIED"
        elif not self.csr_passed[label]:
            status = "BLOCKED"
        else:
            status = "ok"
        return f"publish {label} {status}"

    def _generated_as(self, fingerprint: str) -> str:
        """The label of the earliest `generate` line with this fingerprint, or `unknown`."""
        for label, generated in self.generated:
            if generated == fingerprint:
                return label
        return "unknown"
