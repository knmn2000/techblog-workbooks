"""Assignment 15 (blocklist and distrust): gives a verdict on each `chain` block of a test input.

The checker runs `assignment_15_blocklist_distrust.py <input-file> <output-file>`. The rules are in
src/pkiaudit/pki/trust.py.
"""

import sys

from pkiaudit.pki.trust import ChainCert, check_chain


def main(input_path: str, output_path: str) -> None:
    """Writes `chain <id> trusted` or `chain <id> blocked <spki|root> <what>` for each chain."""
    blocked_spki: set[str] = set()
    distrusted_roots: set[str] = set()
    lines = []
    chain_id, certs = None, []

    def finish() -> None:
        if chain_id is None:
            return
        block = check_chain(certs, blocked_spki, distrusted_roots)
        lines.append(f"chain {chain_id} trusted" if block is None
                     else f"chain {chain_id} blocked {block.mechanism} {block.what}")

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] in ("blocked-spki", "distrusted-root"):
                # An entry applies to the chains after it, so the chain before it is decided now.
                finish()
                chain_id = None
            if words[0] == "blocked-spki":  # blocked-spki <hash>
                blocked_spki.add(words[1])
            elif words[0] == "distrusted-root":  # distrusted-root <root-id>
                distrusted_roots.add(words[1])
            elif words[0] == "chain":  # chain <id>: starts a new chain
                finish()
                chain_id, certs = words[1], []
            elif words[0] == "cert":  # cert <role> <spki-hash> <root-id>, leaf first
                certs.append(ChainCert(words[1], words[2], words[3]))
    finish()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
