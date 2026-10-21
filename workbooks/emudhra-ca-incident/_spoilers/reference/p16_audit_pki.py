# Reference solution - checkpoint 16 (Audit a PKI). SPOILERS: try it yourself first.
#
# This is the capstone: it combines checkpoint 13's key linting, checkpoint 9's chain
# validation, and one new idea, blast radius - for every key that signs something else in this
# PKI, which chains would stop being trusted if that key turned out to be compromised. That last
# question is exactly what eMudhra, Mozilla and Chrome all had to answer within hours of
# disclosure: not just "is this key bad," but "what does it reach."

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
import curves as _curves  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common.certlib import parse_certificate, verify_ecdsa_sha384  # noqa: E402

WEAK_BOUND = 4096  # same toy budget as checkpoint 13, for the same reason: see its problem page

CURVES = {name: {"p": c["p"], "a": c["p"] - 3, "gx": c["gx"], "gy": c["gy"]} for name, c in _curves.CURVES.items()}


def on_curve(curve, x, y):
    c = CURVES[curve]
    p, a, b = c["p"], c["a"], _curves.CURVES[curve]["b"]
    return (y * y - (x ** 3 + a * x + b)) % p == 0


def point_add(p, a, point, other):
    x1, y1 = point
    x2, y2 = other
    if (x1, y1) == (x2, y2):
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (slope * slope - x1 - x2) % p
    return x3, (slope * (x1 - x3) - y1) % p


def find_small_private_key(curve, x, y, bound):
    c = CURVES[curve]
    p, a = c["p"], c["a"]
    point = (c["gx"], c["gy"])
    target = (x, y)
    for d in range(1, bound + 1):
        if point == target:
            return d
        point = point_add(p, a, point, (c["gx"], c["gy"]))
    return None


def lint_key(curve, x, y, blocklist):
    """Same three checks and priority order as checkpoint 13, applied here to every key in the
    PKI, anchors included."""
    if not on_curve(curve, x, y):
        return "off-curve"
    if (curve, x, y) in blocklist:
        return "known-compromised"
    if find_small_private_key(curve, x, y, WEAK_BOUND) is not None:
        return "weak"
    return None


def validate_chain(keys_by_id, cert_ids, anchor_ids):
    """cert_ids: leaf-first, certs only (no anchor among them). anchor_ids: every anchor
    declared anywhere in this PKI - the topmost cert is checked against each of them, and any
    match is enough (checkpoint 9's "try each" rule, applied across the whole PKI instead of one
    chain at a time). keys_by_id: id -> (curve, x, y, cert-or-None).
    Returns (True, None, matched_anchor_id) or (False, reason, matched_anchor_id-or-None): the
    matched anchor is which one actually signed the topmost cert, for blast-radius purposes,
    even if a later check still rejects the chain."""
    certs = [keys_by_id[i] for i in cert_ids]
    for i in range(len(certs) - 1):
        signer_curve, signer_x, signer_y, _ = certs[i + 1]
        _, _, _, leaf_cert = certs[i]
        if not verify_ecdsa_sha384(signer_curve, signer_x, signer_y, leaf_cert.tbs_bytes,
                                    leaf_cert.sig_r, leaf_cert.sig_s):
            return False, "bad-signature", None
    _, _, _, top_cert = certs[-1]
    matched = next((aid for aid in anchor_ids
                     if verify_ecdsa_sha384(*keys_by_id[aid][:3], top_cert.tbs_bytes,
                                             top_cert.sig_r, top_cert.sig_s)), None)
    if matched is None:
        return False, "unknown-anchor", None
    for i in range(1, len(certs)):
        _, _, _, cert = certs[i]
        if not cert.ca:
            return False, "not-a-ca", matched
    for i in range(1, len(certs)):
        _, _, _, cert = certs[i]
        if cert.pathlen is not None and (i - 1) > cert.pathlen:
            return False, "path-too-long", matched
    return True, None, matched


def blast_radius(chains, matched_anchors):
    """chains: list of (chain_id, [cert ids leaf-first]). matched_anchors: chain_id -> the
    anchor id that actually signed its topmost cert, or None. Returns id -> sorted list of
    chain ids that depend on it: a cert at position >= 1 in some chain's own list (a signer,
    not the leaf), or an anchor that actually verified some chain's topmost cert."""
    exposed = {}
    for chain_id, ids in chains:
        for signer_id in ids[1:]:
            exposed.setdefault(signer_id, []).append(chain_id)
        anchor_id = matched_anchors.get(chain_id)
        if anchor_id is not None:
            exposed.setdefault(anchor_id, []).append(chain_id)
    return exposed


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    bound = WEAK_BOUND
    blocklist = set()
    keys_by_id = {}       # id -> (curve, x, y, Certificate-or-None)
    key_order = []        # ids in the order they were declared, for the `key` lines
    chains = []            # (chain_id, [ids])
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
        if kid in exposed:
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
