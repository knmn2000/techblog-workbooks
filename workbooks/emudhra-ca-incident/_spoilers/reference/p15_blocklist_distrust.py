# Reference solution - checkpoint 15 (Block and distrust). SPOILERS: try it yourself first.
#
# Two separate mechanisms, checked in order. SPKI blocking is the finer-grained, faster one (it
# blocks one exact key, wherever it shows up, the moment it's known to be bad): check it first,
# scanning the chain leaf to root. Only if nothing in the chain is individually blocklisted does
# the coarser, precautionary mechanism apply: is the whole hierarchy under this root distrusted.

import sys


def classify_chain(certs, blocked_spki, distrusted_roots):
    """certs: a list of (role, spki_hash, root_id) tuples, leaf to root. Returns ("trusted",),
    ("blocked", "spki", role) or ("blocked", "root", root_id)."""
    for role, spki, _root_id in certs:
        if spki in blocked_spki:
            return ("blocked", "spki", role)
    for role, _spki, root_id in certs:
        if role == "root" and root_id in distrusted_roots:
            return ("blocked", "root", root_id)
    return ("trusted",)


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    blocked_spki = set()
    distrusted_roots = set()
    lines = []
    chain_id = None
    certs = []

    def flush():
        if chain_id is None:
            return
        verdict = classify_chain(certs, blocked_spki, distrusted_roots)
        if verdict[0] == "trusted":
            lines.append(f"chain {chain_id} trusted")
        else:
            lines.append(f"chain {chain_id} blocked {verdict[1]} {verdict[2]}")

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "blocked-spki":
                blocked_spki.add(words[1])
            elif words[0] == "distrusted-root":
                distrusted_roots.add(words[1])
            elif words[0] == "chain":
                flush()
                chain_id, certs = words[1], []
            elif words[0] == "cert":
                role, spki, root_id = words[1], words[2], words[3]
                certs.append((role, spki, root_id))
    flush()
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
