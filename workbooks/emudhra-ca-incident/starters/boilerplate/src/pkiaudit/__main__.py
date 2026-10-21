# ======================================================================================
# Assignment 16: Audit a PKI
# Problem: problems/16-audit-pki.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This is the finished command-line program. `pkiaudit audit <pki-file>`, or `python -m
#   pkiaudit audit <pki-file>`, prints the audit report for a PKI file, using your
#   `pki/audit.py`.
#
# Your job:
#   The Boilerplate gives you this file finished: the declarations. You fill in the TODOs
#   in this assignment's other files.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""The pkiaudit command (assignment 16).

    pkiaudit audit <pki-file>        prints the audit report for a PKI file
    python -m pkiaudit audit <pki-file>

pki/audit.py describes the file format and the report.
"""

import argparse
import sys

from pkiaudit.pki.audit import audit, read_pki


def main(argv: list[str] | None = None) -> int:
    """Runs the command with `argv` (sys.argv[1:] when None) and returns its exit code."""
    parser = argparse.ArgumentParser(prog="pkiaudit", description="Audit a small public-key infrastructure.")
    commands = parser.add_subparsers(dest="command", required=True)
    audit_command = commands.add_parser(
        "audit", help="lint every key, validate every chain and report each signing key's blast radius")
    audit_command.add_argument("pki_file", help="a file of blocklist, anchor, cert and chain lines")
    args = parser.parse_args(argv)

    with open(args.pki_file, encoding="utf-8") as f:
        report = audit(read_pki(f))
    for line in report.lines():
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
