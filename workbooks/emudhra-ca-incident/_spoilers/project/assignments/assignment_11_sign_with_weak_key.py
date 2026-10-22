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
