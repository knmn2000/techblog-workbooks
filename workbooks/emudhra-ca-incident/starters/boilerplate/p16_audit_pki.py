# Checkpoint 16 - Audit a PKI
#
# Problem:  problems/16-audit-pki.md (also in the web problem book)
# Check:    ./check.sh 16
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on the four functions above it.
#
# Your own code from earlier checkpoints can go in solutions/common/ and is imported with
# `import common.<module>`. This is the capstone: everything you need is in checkpoints 5-15.

import sys

CURVES = {
    "P-256": {},
    "P-384": {},
}
WEAK_BOUND = 4096


def lint_key(curve, x, y, blocklist):
    """Return None if the key is fine, or one of "off-curve", "known-compromised", "weak" (the
    first that applies, in that priority order). blocklist: a set of (curve, x, y) tuples."""
    # TODO: on-curve check (checkpoint 2's curve equation), then the blocklist, then checkpoint
    # 10's bounded search for a small private key.
    raise NotImplementedError("lint_key")


def parse_certificate(cert_bytes):
    """Return an object with the fields checkpoint 6 reads (curve, pubx, puby, ca, pathlen,
    tbs_bytes, sig_r, sig_s) - reuse your own checkpoints 5/6/8 code."""
    raise NotImplementedError("parse_certificate")


def validate_chain(keys_by_id, cert_ids, anchor_ids):
    """keys_by_id: id -> (curve, x, y, cert-or-None). cert_ids: leaf-first, certs only (no
    anchor among them). anchor_ids: every anchor declared in this PKI - the topmost cert must be
    signed by ANY of them (checkpoint 9's "try each" rule). Return (True, None, matched_anchor)
    or (False, reason, matched_anchor-or-None) - checkpoint 9's rules, plus which anchor (if
    any) actually signed the topmost cert, for blast_radius to use."""
    # TODO: same checks as checkpoint 9, but the topmost cert's signer isn't one named id - try
    # every id in anchor_ids and take the first that verifies.
    raise NotImplementedError("validate_chain")


def blast_radius(chains, matched_anchors):
    """chains: list of (chain_id, [cert ids leaf-first]). matched_anchors: chain_id -> the
    anchor id that actually signed its topmost cert, or None. Return id -> list of chain ids
    that depend on it: a cert at position >= 1 in some chain's own list, or an anchor that
    actually verified some chain's topmost cert."""
    # TODO: for every cert id that appears at position >= 1 in some chain, and every anchor id
    # that matched_anchors names for some chain, collect every chain that depends on it.
    raise NotImplementedError("blast_radius")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    blocklist = set()
    keys_by_id = {}
    key_order = []
    chains = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            kw = words[0]
            if kw == "blocklist":
                blocklist.add((words[1], int(words[2], 16), int(words[3], 16)))
            elif kw == "anchor":
                _, aid, curve, x, y = words
                keys_by_id[aid] = (curve, int(x, 16), int(y, 16), None)
                key_order.append(aid)
            elif kw == "cert":
                _, cid, hexdata = words
                cert = parse_certificate(bytes.fromhex(hexdata))
                keys_by_id[cid] = (cert.curve, cert.pubx, cert.puby, cert)
                key_order.append(cid)
            elif kw == "chain":
                chains.append((words[1], words[2:]))

    anchor_ids = [kid for kid in key_order if keys_by_id[kid][3] is None]

    lines = []
    for kid in key_order:
        curve, x, y, _ = keys_by_id[kid]
        reason = lint_key(curve, x, y, blocklist)
        lines.append(f"key {kid} {reason or 'ok'}")
    matched_anchors = {}
    for chain_id, ids in chains:
        ok, reason, matched = validate_chain(keys_by_id, ids, anchor_ids)
        matched_anchors[chain_id] = matched
        lines.append(f"chain {chain_id} trusted" if ok else f"chain {chain_id} untrusted {reason}")
    exposed = blast_radius(chains, matched_anchors)
    for kid in key_order:
        if kid in exposed and exposed[kid]:
            lines.append(f"exposed {kid} " + " ".join(exposed[kid]))

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
