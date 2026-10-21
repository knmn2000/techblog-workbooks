# ======================================================================================
# Assignment 06: Read a certificate
# Problem: problems/06-read-certificate.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 06 as `python -P tools/run_py.py
#   solutions 06 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 06`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/x509/certificate.py in this assignment; each one gives its
#   job at the top.
#   Earlier files you can use: src/pkiaudit/asn1/der.py, src/pkiaudit/ecc/curve.py and
#   src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.x509 import certificate`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 06 (read a certificate): prints the fields of each `cert` line of a test input.

The checker runs `assignment_06_read_certificate.py <input-file> <output-file>`. The fields are
read by src/pkiaudit/x509/certificate.py.
"""

import sys

from pkiaudit.x509.certificate import parse_certificate


def certificate_lines(label: str, cert_bytes: bytes) -> list[str]:
    """Writes the four output lines for one certificate."""
    cert = parse_certificate(cert_bytes)
    width = 2 * cert.curve.byte_length
    x, y = cert.public_key
    pathlen = "none" if cert.pathlen is None else str(cert.pathlen)
    return [
        f"cert {label} {cert.subject_cn} {cert.issuer_cn}",
        f"validity {cert.not_before} {cert.not_after}",
        f"key {cert.curve.name} {x:0{width}x} {y:0{width}x}",
        f"ca {'true' if cert.ca else 'false'} {pathlen}",
    ]


def main(input_path: str, output_path: str) -> None:
    """Writes the fields of each `cert <label> <hex>` line."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if words and words[0] == "cert":
                lines.extend(certificate_lines(words[1], bytes.fromhex(words[2])))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
