"""Assignment 18 (verify a CRL's signature): checks each CRL of a test input against its issuer's
published key.

The checker runs `assignment_18_crl_signature.py <input-file> <output-file>`. Reading a CRL and
the per-issuer state are in src/pkiaudit/pki/crl.py.
"""

import sys

from pkiaudit.ecc.curves import CURVES
from pkiaudit.pki.crl import CrlWatch, read_crl


def main(input_path: str, output_path: str) -> None:
    """Writes `crl <label> ok` or `crl <label> halt <reason>` for each `crl` line, in input order."""
    watch = CrlWatch()
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "key":  # key <issuer> <curve> <x> <y>
                watch.set_key(words[1], CURVES[words[2]], (int(words[3], 16), int(words[4], 16)))
            elif words[0] == "crl":  # crl <label> <hex>
                reason = watch.check(read_crl(bytes.fromhex(words[2])))
                lines.append(f"crl {words[1]} ok" if reason is None else f"crl {words[1]} halt {reason}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
