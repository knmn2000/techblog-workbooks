# ======================================================================================
# Assignment 13: Lint a public key
# Problem: problems/13-key-linter.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 13 as `python -P tools/run_py.py
#   solutions 13 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 13`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/lint.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/attack/weak_key.py, src/pkiaudit/ecc/curve.py
#   and src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import lint`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
