# ======================================================================================
# Assignment 08: Check a certificate's signature
# Problem: problems/08-certificate-signature.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 08 as `python -P tools/run_py.py
#   solutions 08 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 08`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/x509/signature.py in this assignment; each one gives its
#   job at the top.
#   Earlier files you can use: src/pkiaudit/asn1/der.py, src/pkiaudit/x509/certificate.py,
#   src/pkiaudit/ecc/ecdsa.py, src/pkiaudit/ecc/curve.py and src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.x509 import signature`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 08 (certificate signature): checks each certificate of a test input against the
issuer key on the line after it.

The checker runs `assignment_08_certificate_signature.py <input-file> <output-file>`.
src/pkiaudit/x509/signature.py reads and checks the signature.
"""

import sys

from pkiaudit.ecc.curves import CURVES
from pkiaudit.x509.signature import check_signature, read_signed_data


def main(input_path: str, output_path: str) -> None:
    """Writes `signature <label> valid|invalid` for each `cert` and `issuer_pubkey` pair of lines."""
    lines = []
    pending = None  # (label, certificate bytes) of the `cert` line waiting for its issuer key
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "cert":  # cert <label> <hex>
                pending = (words[1], bytes.fromhex(words[2]))
            elif words[0] == "issuer_pubkey":  # issuer_pubkey <label> <curve> <x> <y>
                label, curve = words[1], CURVES[words[2]]
                if pending is None or pending[0] != label:
                    raise ValueError(f"issuer_pubkey {label} must follow the cert with the same label")
                issuer_key = (int(words[3], 16), int(words[4], 16))
                valid = check_signature(read_signed_data(pending[1]), curve, issuer_key)
                lines.append(f"signature {label} {'valid' if valid else 'invalid'}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
