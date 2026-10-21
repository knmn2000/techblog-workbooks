"""Assignment 10 (find a weak key): searches for the private key of each `key` line of a test input.

The checker runs `assignment_10_find_weak_key.py <input-file> <output-file>`. The search is in
src/pkiaudit/attack/weak_key.py.
"""

import sys

from pkiaudit.attack.weak_key import find_private_key
from pkiaudit.ecc.curves import CURVES


def main(input_path: str, output_path: str) -> None:
    """Writes `weak <label> <d>` or `none <label>` for each key, searching up to the latest bound."""
    bound = 0
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "bound":  # bound <N>: applies to the key lines after it
                bound = int(words[1])
            elif words[0] == "key":  # key <label> <curve> <x> <y>, coordinates in hex
                label, curve = words[1], CURVES[words[2]]
                d = find_private_key(curve, (int(words[3], 16), int(words[4], 16)), bound)
                lines.append(f"none {label}" if d is None else f"weak {label} {d}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
