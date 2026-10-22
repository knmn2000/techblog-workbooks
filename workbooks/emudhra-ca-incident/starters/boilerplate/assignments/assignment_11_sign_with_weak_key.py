# ======================================================================================
# Assignment 11: Sign a certificate with a recovered key
# Problem: problems/11-sign-with-weak-key.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 11 as `python -P tools/run_py.py
#   solutions 11 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 11`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   It adds to src/pkiaudit/ecc/ecdsa.py, which you started earlier: Add ECDSA signing to
#   `ecc/ecdsa.py`, next to the verification you wrote in assignment 04: given a curve, a
#   private key, a message hash and a nonce, compute the signature pair (r, s). Build it
#   from your scalar multiplication in `ecc/curve.py` and your modular inverse in
#   `ecc/modmath.py`. The Boilerplate's `ecc/ecdsa.py` from assignment 04 already declares
#   it as `sign` under its assignment 11 marker; if you wrote the file your own way, add
#   the function now.
#   Earlier files you can use: src/pkiaudit/ecc/modmath.py, src/pkiaudit/ecc/curve.py,
#   src/pkiaudit/ecc/curves.py and src/pkiaudit/pki/chain.py.
#   Import them as modules of your package, e.g. `from pkiaudit.ecc import ecdsa`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 11 (sign with a weak key): signs hashes and forges certificates with a recovered key.

The checker runs `assignment_11_sign_with_weak_key.py <input-file> <output-file>`. Signing is in
src/pkiaudit/ecc/ecdsa.py, and the chain verdict comes from src/pkiaudit/pki/chain.py (assignment
09). The DER writers below assemble the certificate around the tbsCertificate the input gives.
"""

import hashlib
import sys

from pkiaudit.ecc.curves import CURVES
from pkiaudit.ecc.ecdsa import sign
from pkiaudit.pki.chain import Anchor, validate_chain

# ecdsa-with-SHA384, the AlgorithmIdentifier every P-384 issuer in this project signs with.
ECDSA_WITH_SHA384 = bytes.fromhex("300a06082a8648ce3d040303")


def der_length(length: int) -> bytes:
    """A DER length: the short form below 128, else 0x80 | byte-count followed by the bytes."""
    if length < 0x80:
        return bytes([length])
    body = length.to_bytes((length.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(body)]) + body


def der_integer(value: int) -> bytes:
    """A DER INTEGER: big-endian two's complement, with a leading 0x00 when the top bit is set."""
    body = value.to_bytes((value.bit_length() + 7) // 8 or 1, "big")
    if body[0] & 0x80:
        body = b"\x00" + body
    return b"\x02" + der_length(len(body)) + body


def der_sequence(content: bytes) -> bytes:
    return b"\x30" + der_length(len(content)) + content


def der_bit_string(content: bytes) -> bytes:
    """A DER BIT STRING whose content is a whole number of bytes: the 0x00 unused-bits byte first."""
    body = b"\x00" + content
    return b"\x03" + der_length(len(body)) + body


def forge_certificate(curve, d: int, k: int, tbs: bytes) -> bytes:
    """Signs the tbsCertificate with d and k, and wraps it in a full certificate's DER."""
    z = int.from_bytes(hashlib.sha384(tbs).digest(), "big")
    r, s = sign(curve, d, z, k)
    signature = der_bit_string(der_sequence(der_integer(r) + der_integer(s)))
    return der_sequence(tbs + ECDSA_WITH_SHA384 + signature)


def main(input_path: str, output_path: str) -> None:
    """Handles each `sign` line and each `forge` line (see the problem page's Input section)."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "sign":
                _, case_id, curve_name, d, z, k = words
                curve = CURVES[curve_name]
                r, s = sign(curve, int(d, 16), int(z, 16), int(k, 16))
                width = 2 * curve.byte_length
                lines.append(f"signature {case_id} {r:0{width}x} {s:0{width}x}")
            elif words[0] == "forge":
                _, case_id, curve_name, d, k, tbs_hex, int_hex, ax, ay = words
                curve = CURVES[curve_name]
                forged = forge_certificate(curve, int(d, 16), int(k, 16), bytes.fromhex(tbs_hex))
                anchor = Anchor(curve, (int(ax, 16), int(ay, 16)))
                result = validate_chain([forged, bytes.fromhex(int_hex)], [anchor])
                verdict = "valid" if result.trusted else f"untrusted {result.reason}"
                lines.append(f"forged {case_id} {forged.hex()} {verdict}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
