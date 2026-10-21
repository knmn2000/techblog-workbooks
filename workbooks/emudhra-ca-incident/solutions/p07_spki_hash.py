# Checkpoint 07 - Hash the public key (SPKI)
#
# Problem:  problems/07-spki-hash.md (also in the web problem book)
# Check:    ./check.sh 07
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on spki_hash().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys


def spki_hash(cert_bytes: bytes) -> str:
    """SHA-256 of the exact original bytes of the certificate's subjectPublicKeyInfo SEQUENCE
    (algorithm identifier + BIT STRING, not just the raw key bytes), as 64 lowercase hex chars."""
    # TODO: find subjectPublicKeyInfo the way checkpoint 06 does (it's a fixed-position child of
    # tbsCertificate), slice out its exact original bytes, and hash them.
    raise NotImplementedError("spki_hash")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "cert":  # cert <label> <hex>: a full DER-encoded certificate
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
    except Exception as e:  # report the problem; the checker shows the message
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
