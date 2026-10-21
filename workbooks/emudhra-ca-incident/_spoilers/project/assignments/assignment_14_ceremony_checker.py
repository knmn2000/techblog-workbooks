"""Assignment 14 (ceremony checker): replays the key ceremony log in a test input.

The checker runs `assignment_14_ceremony_checker.py <input-file> <output-file>`.
src/pkiaudit/pki/ceremony.py keeps the ceremony's state.
"""

import sys

from pkiaudit.pki.ceremony import Ceremony


def main(input_path: str, output_path: str) -> None:
    """Writes a `duplicate` line for each reused label and a `publish` line for each publish step."""
    ceremony = Ceremony()
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            step = words[0]
            if step == "generate":  # generate <label> <curve>
                if ceremony.generate(words[1]):
                    lines.append(f"duplicate {words[1]}")
            elif step == "wrap":  # wrap <label> <wrapped-label>
                ceremony.wrap(words[1], words[2])
            elif step == "unwrap":  # unwrap <wrapped-label> <label>
                ceremony.unwrap(words[1], words[2])
            elif step == "fingerprint":  # fingerprint <label> <hex>
                ceremony.fingerprint(words[1], words[2])
            elif step == "publish":  # publish <label>
                result = ceremony.publish(words[1])
                if result.status == "MISMATCH":
                    lines.append(f"publish {words[1]} MISMATCH {result.generated_as}")
                else:
                    lines.append(f"publish {words[1]} {result.status}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
