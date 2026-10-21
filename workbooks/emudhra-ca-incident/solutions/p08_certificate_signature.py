# Checkpoint 08 - Check a certificate's signature
#
# Problem:  problems/08-certificate-signature.md (also in the web problem book)
# Check:    ./check.sh 08
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on check_signature().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys


def check_signature(cert_bytes: bytes, curve: str, issuer_x: int, issuer_y: int) -> bool:
    """True if cert_bytes was really signed by the private key matching (issuer_x, issuer_y)
    on `curve`. See the problem page for how to re-extract tbsCertificate's exact original
    bytes and for the ECDSA verification equation (P-384 with SHA-384, as in checkpoint 04)."""
    # TODO: find tbsCertificate's original bytes, the signatureValue's (r, s), hash the former
    # with SHA-384, and check it against (issuer_x, issuer_y) with the ECDSA verify equation.
    raise NotImplementedError("check_signature")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    pending_cert = None  # (label, cert_bytes), waiting for its issuer_pubkey line
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "cert":  # cert <label> <hex>: the certificate to check
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
    except Exception as e:  # report the problem; the checker shows the message
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
