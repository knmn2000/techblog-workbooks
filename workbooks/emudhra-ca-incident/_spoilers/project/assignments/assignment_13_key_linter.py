"""Assignment 13 (lint a public key): lints each `key` line of a test input.

The checker runs `assignment_13_key_linter.py <input-file> <output-file>`. The checks are in
src/pkiaudit/pki/lint.py.
"""

import sys

from pkiaudit.ecc.curves import CURVES
from pkiaudit.pki.lint import lint_key


def main(input_path: str, output_path: str) -> None:
    """Writes `ok <label>` or `fail <label> <finding>` for each key, against the blocklist so far."""
    blocklist = set()
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "blocklist":  # blocklist <curve> <x> <y>: applies to the key lines after it
                blocklist.add((words[1], (int(words[2], 16), int(words[3], 16))))
            elif words[0] == "key":  # key <label> <curve> <x> <y>
                label, curve = words[1], CURVES[words[2]]
                finding = lint_key(curve, (int(words[3], 16), int(words[4], 16)), blocklist)
                lines.append(f"ok {label}" if finding is None else f"fail {label} {finding}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
