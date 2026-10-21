# Reference solution - checkpoint 08 (Check a certificate's signature). SPOILERS: try it
# yourself first.
#
# Re-extracts the exact original bytes of tbsCertificate (not a re-encoding of its fields -
# DER is canonical, but reconstructing it yourself is an easy way to get subtly different bytes
# than the ones that were actually signed), hashes them with SHA-384, and checks the signature's
# (r, s) against the alleged issuer's public key with the same modular-arithmetic ECDSA
# verification equation as checkpoint 04, reused here as common/certlib.py's
# verify_ecdsa_sha384 (this checkpoint's own self-contained copy of that logic).

import sys

from common.certlib import parse_certificate, verify_ecdsa_sha384


def check_signature(cert_bytes: bytes, curve: str, issuer_x: int, issuer_y: int) -> bool:
    cert = parse_certificate(cert_bytes)
    return verify_ecdsa_sha384(curve, issuer_x, issuer_y, cert.tbs_bytes, cert.sig_r, cert.sig_s)


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    pending_cert = None  # (label, cert_bytes), waiting for its issuer_pubkey line
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "cert":  # cert <label> <hex>
                pending_cert = (words[1], bytes.fromhex(words[2]))
            elif words[0] == "issuer_pubkey":  # issuer_pubkey <label> <curve> <x> <y>
                label, curve, x, y = words[1], words[2], int(words[3], 16), int(words[4], 16)
                assert pending_cert and pending_cert[0] == label, "issuer_pubkey must follow the cert with the same label"
                valid = check_signature(pending_cert[1], curve, x, y)
                lines.append(f"signature {label} {'valid' if valid else 'invalid'}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <input-file> <output-file>", file=sys.stderr)
        sys.exit(2)
    try:
        main(sys.argv[1], sys.argv[2])
    except NotImplementedError as e:
        print(f"not implemented: {e}", file=sys.stderr)
        sys.exit(99)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
