# ======================================================================================
# Assignment 16: Audit a PKI
# Problem: problems/16-audit-pki.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   It audits a whole PKI file: a lint finding for every key, a verdict for every chain,
#   and the chains each signing key would break if it leaked. The checker's program and
#   the `pkiaudit audit` command both print its report.
#
# Your job:
#   Write the PKI audit in `pki/audit.py`, from reading a PKI file to the lines of its
#   report. Read the `blocklist`, `anchor`, `cert` and `chain` lines (see Input), then
#   lint every key with your `lint_key` from assignment 13 against the whole blocklist,
#   wherever its lines appear in the file, and validate every chain against all the
#   anchors with your `validate_chain` from assignment 09, with no current time. Work out
#   which chains depend on each signing key (see The three things you report), then write
#   the report's `key`, `chain` and `exposed` lines (see Output).
#
# How to start:
#   Write it yourself from here, or press Boilerplate in the book's editor to get the
#   input/output code and the declarations (the same files are in starters/boilerplate/).
# ======================================================================================
