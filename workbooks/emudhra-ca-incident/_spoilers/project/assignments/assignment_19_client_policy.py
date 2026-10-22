"""Assignment 19 (client policy): says which clients accept each `chain` block of a test input.

The checker runs `assignment_19_client_policy.py <input-file> <output-file>`. The rules are in
src/pkiaudit/pki/client_policy.py.
"""

import sys

from pkiaudit.pki.client_policy import ClientPolicy, Facts, decide
from pkiaudit.pki.trust import ChainCert


def read_client(words: list[str]) -> tuple[str, ClientPolicy]:
    """`client <name> key=value ...`: the four switches come in any order."""
    switches = dict(word.split("=", 1) for word in words[2:])
    return words[1], ClientPolicy(revocation=switches["revocation"],
                                  blocklist=switches["blocklist"] == "yes",
                                  ct_required=switches["ct"] == "required",
                                  bundle_updated=switches["bundle"] == "updated")


def main(input_path: str, output_path: str) -> None:
    """Writes `verdict <chain-id> <client> accept` or `... reject <reason> [<what>]` for each
    chain, and within a chain for each client in the order the input declares them."""
    clients: list[tuple[str, ClientPolicy]] = []
    facts = Facts(set(), set(), set(), set())
    fact_sets = {"blocked-spki": facts.blocked_spki, "distrusted-root": facts.distrusted_roots,
                 "revoked": facts.revoked, "logged": facts.logged}
    lines = []
    chain_id, names, certs = None, [], []

    def finish() -> None:
        """Decides the chain read so far, with the facts as they stand before the next line."""
        nonlocal chain_id
        if chain_id is None:
            return
        for name, client in clients:
            reject = decide(certs, names, client, facts)
            verdict = "accept" if reject is None else " ".join(filter(None, ("reject", reject.reason, reject.what)))
            lines.append(f"verdict {chain_id} {name} {verdict}")
        chain_id = None

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "cert":  # cert <role> <name> <spki-hash> <root-id>, leaf first
                names.append(words[2])
                certs.append(ChainCert(words[1], words[3], words[4]))
                continue
            finish()  # any other line ends the current chain, so a fact after it doesn't reach it
            if words[0] == "client":
                clients.append(read_client(words))
            elif words[0] in fact_sets:  # blocked-spki, distrusted-root, revoked or logged
                fact_sets[words[0]].add(words[1])
            elif words[0] == "chain":  # chain <id>: starts a new chain
                chain_id, names, certs = words[1], [], []
    finish()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
