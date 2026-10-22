"""Assignment 14 (ceremony checker): replays the key ceremony log in a test input.

The checker runs `assignment_14_ceremony_checker.py <input-file> <output-file>`.
src/pkiaudit/pki/ceremony.py keeps the ceremony's state and decides each line of output.
"""

import sys

from pkiaudit.pki.ceremony import Ceremony


def main(input_path: str, output_path: str) -> None:
    """Writes the lines each step produces, in log order."""
    ceremony = Ceremony()
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            step = words[0]
            result = None
            if step == "generate":  # generate <label> <fingerprint>
                result = ceremony.generate(words[1], words[2])
            elif step == "approve":  # approve <label> <fingerprint>
                ceremony.approve(words[1], words[2])
            elif step == "deviation":  # deviation <approver>
                result = ceremony.deviation(words[1])
            elif step == "csr":  # csr <label> <fingerprint>
                result = ceremony.csr(words[1], words[2])
            elif step == "publish":  # publish <label>
                result = ceremony.publish(words[1])
            if result is not None:
                lines.append(result)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
