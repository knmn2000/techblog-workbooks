# Checkpoint 09 - Validate a certificate chain
#
# Problem:  problems/09-validate-chain.md (also in the web problem book)
# Check:    ./check.sh 09
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on validate_chain().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys

REASONS = ("bad-signature", "unknown-anchor", "not-a-ca", "path-too-long", "expired")


def validate_chain(now: str, anchors: list, cert_bytes_list: list):
    """anchors: list of (curve, x, y) trust anchor public keys. cert_bytes_list: the chain's
    certificates, leaf first, most-senior intermediate last (no root certificate - the anchor
    IS the root's key, trusted directly). Returns (True, None) if trusted, else (False, reason)
    with reason one of REASONS. See the problem page for the exact rules and their order."""
    # TODO: check (in order) that signatures chain up to a trust anchor, that every signer has
    # CA:true, that no path length constraint is violated, and that every certificate's
    # validity window covers `now`. Reuse checkpoint 06's field-reading and checkpoint 08's
    # signature check.
    raise NotImplementedError("validate_chain")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    label, now, anchors, certs = None, None, [], []

    def finish():
        if label is None:
            return
        trusted, reason = validate_chain(now, anchors, certs)
        lines.append(f"chain {label} trusted" if trusted else f"chain {label} untrusted {reason}")

    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "chain":  # chain <label>: starts a new chain, resetting state
                finish()
                label, now, anchors, certs = words[1], None, [], []
            elif words[0] == "now":  # now <time-string>
                now = words[1]
            elif words[0] == "anchor":  # anchor <curve> <x> <y>: a trusted root public key
                anchors.append((words[1], int(words[2], 16), int(words[3], 16)))
            elif words[0] == "cert":  # cert <hex>: leaf first, most senior intermediate last
                certs.append(bytes.fromhex(words[1]))
    finish()
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
