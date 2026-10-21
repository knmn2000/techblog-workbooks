# Reference solution - checkpoint 07 (Hash the public key). SPOILERS: try it yourself first.
#
# The SPKI hash is SHA-256 of the exact original bytes of subjectPublicKeyInfo - the whole
# nested SEQUENCE (algorithm identifier + BIT STRING), not just the raw key bytes. Finding that
# node is the same walk checkpoint 06 does; common/certlib.py's find_spki does only that much
# of it, since this checkpoint doesn't need the rest of the certificate's fields.

import hashlib
import sys

from common.certlib import find_spki


def spki_hash(cert_bytes: bytes) -> str:
    node = find_spki(cert_bytes)
    raw = cert_bytes[node.start: node.start + node.total_len]
    return hashlib.sha256(raw).hexdigest()


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "cert":  # cert <label> <hex>
                lines.append(f"spki {words[1]} {spki_hash(bytes.fromhex(words[2]))}")
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
