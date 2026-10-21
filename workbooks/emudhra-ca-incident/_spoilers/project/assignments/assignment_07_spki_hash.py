"""Assignment 07 (SPKI hash): prints the SPKI hash of each `cert` line of a test input.

The checker runs `assignment_07_spki_hash.py <input-file> <output-file>`.
src/pkiaudit/x509/spki.py computes the hash.
"""

import sys

from pkiaudit.x509.spki import spki_hash


def main(input_path: str, output_path: str) -> None:
    """Writes `spki <label> <sha256-hex>` for each `cert <label> <hex>` line."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if words and words[0] == "cert":
                lines.append(f"spki {words[1]} {spki_hash(bytes.fromhex(words[2]))}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
