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
