# ======================================================================================
# Assignment 07: Hash the public key (SPKI)
# Problem: problems/07-spki-hash.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 07 as `python -P tools/run_py.py
#   solutions 07 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 07`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished: it reads the input, calls your code
#   and writes the answer. You fill in the TODOs in this assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/x509/spki.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/asn1/der.py and
#   src/pkiaudit/x509/certificate.py.
#   Import them as modules of your package, e.g. `from pkiaudit.x509 import spki`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 07 (SPKI hash): prints the SPKI hash of each `cert` line of a test input.

The checker runs `assignment_07_spki_hash.py <input-file> <output-file>`.
src/pkiaudit/x509/spki.py computes the hash.
"""

import sys

from pkiaudit.x509.spki import spki_hash


def main(input_path: str, output_path: str) -> None:
    """Writes `spki <label> <sha256-hex>` for each `cert <label> <hex>` line."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if words and words[0] == "cert":
                lines.append(f"spki {words[1]} {spki_hash(bytes.fromhex(words[2]))}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
