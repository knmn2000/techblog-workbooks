# ======================================================================================
# Assignment 16: Audit a PKI
# Problem: problems/16-audit-pki.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 16 as `python -P tools/run_py.py
#   solutions 16 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 16`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished: it reads the input, calls your code
#   and writes the answer. You fill in the TODOs in this assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/audit.py and src/pkiaudit/__main__.py in this
#   assignment; each one gives its job at the top.
#   Earlier files you can use: src/pkiaudit/pki/lint.py, src/pkiaudit/pki/chain.py,
#   src/pkiaudit/x509/certificate.py, src/pkiaudit/ecc/curve.py and
#   src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import audit`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 16 (audit a PKI): audits the PKI in a test input.

The checker runs `assignment_16_audit_pki.py <input-file> <output-file>`. A test input is a PKI
file, and the expected output is the audit report, so this program uses the reader and the report
from src/pkiaudit/pki/audit.py, the same ones the `pkiaudit audit` command uses.
"""

import sys

from pkiaudit.pki.audit import audit, read_pki


def main(input_path: str, output_path: str) -> None:
    """Writes the audit report for the PKI in the input file."""
    with open(input_path, encoding="utf-8") as f:
        report = audit(read_pki(f))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report.lines()) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
