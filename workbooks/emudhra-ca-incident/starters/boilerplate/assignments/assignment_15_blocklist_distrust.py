# ======================================================================================
# Assignment 15: Block and distrust
# Problem: problems/15-blocklist-distrust.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 15 as `python -P tools/run_py.py
#   solutions 15 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 15`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished: it reads the input, calls your code
#   and writes the answer. You fill in the TODOs in this assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/pki/trust.py in this assignment; each one gives its job at
#   the top.
#   Import them as modules of your package, e.g. `from pkiaudit.pki import trust`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 15 (blocklist and distrust): gives a verdict on each `chain` block of a test input.

The checker runs `assignment_15_blocklist_distrust.py <input-file> <output-file>`. The rules are in
src/pkiaudit/pki/trust.py.
"""

import sys

from pkiaudit.pki.trust import ChainCert, check_chain


def main(input_path: str, output_path: str) -> None:
    """Writes `chain <id> trusted` or `chain <id> blocked <spki|root> <what>` for each chain."""
    blocked_spki: set[str] = set()
    distrusted_roots: set[str] = set()
    lines = []
    chain_id, certs = None, []

    def finish() -> None:
        if chain_id is None:
            return
        block = check_chain(certs, blocked_spki, distrusted_roots)
        lines.append(f"chain {chain_id} trusted" if block is None
                     else f"chain {chain_id} blocked {block.mechanism} {block.what}")

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "blocked-spki":  # blocked-spki <hash>
                blocked_spki.add(words[1])
            elif words[0] == "distrusted-root":  # distrusted-root <root-id>
                distrusted_roots.add(words[1])
            elif words[0] == "chain":  # chain <id>: starts a new chain
                finish()
                chain_id, certs = words[1], []
            elif words[0] == "cert":  # cert <role> <spki-hash> <root-id>, leaf first
                certs.append(ChainCert(words[1], words[2], words[3]))
    finish()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
