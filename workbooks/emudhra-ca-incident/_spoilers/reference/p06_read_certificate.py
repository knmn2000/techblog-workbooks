# Reference solution - checkpoint 06 (Read a certificate). SPOILERS: try it yourself first.
#
# Builds on checkpoint 05's TLV walk: common/certlib.py reads the specific fields of an X.509
# certificate out of that walk (subject/issuer common name, validity, the EC public key, and
# the BasicConstraints extension). This file just formats what it returns.

import sys

from common.certlib import parse_certificate

HEXLEN = {"P-256": 64, "P-384": 96}  # coordinate width in hex digits (32 and 48 bytes)


def format_lines(label: str, cert_bytes: bytes) -> list:
    c = parse_certificate(cert_bytes)
    pathlen = "none" if c.pathlen is None else str(c.pathlen)
    n = HEXLEN[c.curve]
    return [
        f"cert {label} {c.subject_cn} {c.issuer_cn}",
        f"validity {c.not_before} {c.not_after}",
        f"key {c.curve} {c.pubx:0{n}x} {c.puby:0{n}x}",
        f"ca {'true' if c.ca else 'false'} {pathlen}",
    ]


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "cert":  # cert <label> <hex>
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
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
