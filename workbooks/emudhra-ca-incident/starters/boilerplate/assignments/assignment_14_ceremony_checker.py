# ======================================================================================
# Assignment 14: Check a key ceremony
# Problem: problems/14-ceremony-checker.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 14 as `python -P tools/run_py.py
#   solutions 14 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 14`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/ceremony.py in this assignment; each one gives its job
#   at the top.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import ceremony`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
