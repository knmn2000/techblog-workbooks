# Reference solution - checkpoint 09 (Validate a certificate chain). SPOILERS: try it
# yourself first.
#
# Combines checkpoint 06's field reading and checkpoint 08's signature check into RFC 5280's
# core path-validation idea, simplified: walk the chain leaf to root, checking (in order) that
# every signature really chains up to a trust anchor, that every signer was allowed to sign
# (CA:true), that no path length constraint is violated, and that every certificate's validity
# window covers "now".

import sys

from common.certlib import parse_certificate, verify_ecdsa_sha384

REASONS = ("bad-signature", "unknown-anchor", "not-a-ca", "path-too-long", "expired")


def validate_chain(now: str, anchors: list, cert_bytes_list: list):
    """anchors: list of (curve, x, y). cert_bytes_list: leaf first, most-senior intermediate
    last. Returns (True, None) or (False, reason), reason one of REASONS."""
    certs = [parse_certificate(b) for b in cert_bytes_list]

    # 1. Signatures: each certificate but the last is signed by the next one up; the last is
    # signed by one of the trust anchors directly (no root certificate is given, just its key).
    for i in range(len(certs) - 1):
        signer = certs[i + 1]
        leaf = certs[i]
        if not verify_ecdsa_sha384(signer.curve, signer.pubx, signer.puby, leaf.tbs_bytes, leaf.sig_r, leaf.sig_s):
            return False, "bad-signature"
    top = certs[-1]
    if not any(verify_ecdsa_sha384(curve, x, y, top.tbs_bytes, top.sig_r, top.sig_s) for curve, x, y in anchors):
        return False, "unknown-anchor"

    # 2. Every signer (everything except the leaf) must be allowed to sign: CA:true.
    for c in certs[1:]:
        if not c.ca:
            return False, "not-a-ca"

    # 3. A signer's path length constraint bounds how many MORE intermediates may appear
    # between it and the leaf (not counting the leaf itself).
    for i in range(1, len(certs)):
        intermediates_below = i - 1
        if certs[i].pathlen is not None and intermediates_below > certs[i].pathlen:
            return False, "path-too-long"

    # 4. Every certificate's validity window must cover "now" (plain string comparison: every
    # time in this checkpoint is the same format, so this is exactly a chronological order).
    for c in certs:
        if not (c.not_before <= now <= c.not_after):
            return False, "expired"

    return True, None


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
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
