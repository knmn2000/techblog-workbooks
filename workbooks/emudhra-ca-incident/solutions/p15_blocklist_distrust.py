# Checkpoint 15 - Block and distrust
#
# Problem:  problems/15-blocklist-distrust.md (also in the web problem book)
# Check:    ./check.sh 15
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on classify_chain().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys


def classify_chain(certs, blocked_spki, distrusted_roots):
    """certs: a list of (role, spki_hash, root_id) tuples, leaf to root (root_id is "-" for a
    leaf or intermediate cert). blocked_spki: a set of blocklisted SPKI hashes. distrusted_roots:
    a set of distrusted root ids.

    Return one of:
      ("trusted",)
      ("blocked", "spki", role)      the first cert (leaf to root) whose SPKI hash is blocklisted
      ("blocked", "root", root_id)   the chain's root id is in the distrusted set
    """
    # TODO: check every cert's SPKI hash against the blocklist first (in chain order, leaf to
    # root); only if none match, check the root's own id against the distrust set.
    raise NotImplementedError("classify_chain")


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
    except Exception as e:  # report the problem; the checker shows the message
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
