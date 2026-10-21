# ======================================================================================
# Assignment 09: Validate a certificate chain
# Problem: problems/09-validate-chain.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 09 as `python -P tools/run_py.py
#   solutions 09 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 09`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/chain.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/x509/certificate.py,
#   src/pkiaudit/x509/signature.py, src/pkiaudit/ecc/curve.py and
#   src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import chain`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 09 (validate a chain): gives a verdict on each `chain` block of a test input.

The checker runs `assignment_09_validate_chain.py <input-file> <output-file>`. The checks are in
src/pkiaudit/pki/chain.py.
"""

import sys

from pkiaudit.ecc.curves import CURVES
from pkiaudit.pki.chain import Anchor, validate_chain


def main(input_path: str, output_path: str) -> None:
    """Writes `chain <label> trusted` or `chain <label> untrusted <reason>` for each chain block."""
    lines = []
    label, now, anchors, certs = None, None, [], []

    def finish() -> None:
        if label is None:
            return
        result = validate_chain(certs, anchors, now)
        verdict = "trusted" if result.trusted else f"untrusted {result.reason}"
        lines.append(f"chain {label} {verdict}")

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "chain":  # chain <label>: starts a new chain
                finish()
                label, now, anchors, certs = words[1], None, [], []
            elif words[0] == "now":  # now <time>
                now = words[1]
            elif words[0] == "anchor":  # anchor <curve> <x> <y>: a trusted root public key
                anchors.append(Anchor(CURVES[words[1]], (int(words[2], 16), int(words[3], 16))))
            elif words[0] == "cert":  # cert <hex>: leaf first, most senior intermediate last
                certs.append(bytes.fromhex(words[1]))
    finish()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
