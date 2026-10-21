# Checkpoint 06 - Read a certificate
#
# Problem:  problems/06-read-certificate.md (also in the web problem book)
# Check:    ./check.sh 06
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on format_lines().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys


def format_lines(label: str, cert_bytes: bytes) -> list:
    """The four output lines for one certificate. See the problem page for the exact format
    and for the rules on reading each field (checkpoint 05's TLV walk is what you walk here)."""
    # TODO: walk cert_bytes as DER (like checkpoint 05), find tbsCertificate's subject, issuer,
    # validity, subjectPublicKeyInfo and (if present) the BasicConstraints extension.
    raise NotImplementedError("format_lines")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "cert":  # cert <label> <hex>: a full DER-encoded certificate
                lines.extend(format_lines(words[1], bytes.fromhex(words[2])))
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
