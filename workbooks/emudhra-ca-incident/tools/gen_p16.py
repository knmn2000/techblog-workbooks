"""Test cases for assignment 16 (audit a PKI), the capstone.

Three independent checks feed this assignment's three kinds of output line:
- `key`: on-curve via curves.on_curve (OpenSSL), weak-key existence via curves.public_point
  (OpenSSL) confirming the planted small d really is the key, known-compromised is definitional
  (exact match against the blocklist this generator wrote).
- `chain`: `openssl verify`, exactly as assignment 09's oracle does (a self-signed cert stands in
  for each bare anchor key).
- `exposed`: a second, differently-shaped computation of the same graph fact (a dict built by
  one pass per chain here, cross-checked against the main nested-loop style the reference uses),
  so this isn't just the reference's own logic re-run.

    python3 -P tools/gen_p16.py                                  # tests/16 (seed 1)
    python3 -P tools/gen_p16.py --seed 777 --out build/fresh/16  # what `check 16 -Fresh` runs
"""

import datetime
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID

sys.path.insert(0, str(Path(__file__).resolve().parent))
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = (f"cryptography {cryptography.__version__} / OpenSSL (key checks and openssl verify): "
       "independent of this assignment's own lint, chain and blast-radius logic")

REQUIREMENTS = [
    ("R1", "Every key is linted (anchors included), in input order: off-curve, known-compromised, "
           "weak or ok, in that priority - same rules as assignment 13"),
    ("R2", "Every chain is validated in input order: trusted, or untrusted with a reason - same "
           "rules as assignment 09"),
    ("R3", "Every key that signs at least one other certificate gets an `exposed` line listing "
           "every chain that depends on it; a key that only ever appears as a leaf gets none"),
    ("R4", "A key shared by two chains (the same intermediate signs both) is exposed by both - "
           "the actual blast-radius lesson: one compromised key can threaten more than one chain"),
    ("R5", "Both curves work, for anchors and certs alike"),
    ("E2E", "A small PKI shaped like the real incident: one root, several intermediates - one of "
            "them with the recovered weak key - and several leaf chains, some through the weak "
            "intermediate and some not"),
]
EXPLAIN = "_lines=R1 key=R1 chain=R2 exposed=R3"

EPOCH = datetime.datetime(2025, 6, 1)
ATTIME = int(EPOCH.timestamp())
ERROR_CODE_TO_REASON = {7: "bad-signature", 20: "unknown-anchor", 79: "not-a-ca", 25: "path-too-long",
                        9: "expired", 10: "expired"}
ERROR_RE = re.compile(r"error (\d+) at \d+ depth lookup")


def fmt_time(dt):
    return dt.strftime("%y%m%d%H%M%SZ")


def make_key(curve="P-384"):
    return ec.generate_private_key(ec.SECP384R1() if curve == "P-384" else ec.SECP256R1())


def make_cert(subject_cn, issuer_cn, pub_key, signing_key, ca=None, pathlen=None, serial=1):
    not_before = EPOCH - datetime.timedelta(days=30)
    not_after = EPOCH + datetime.timedelta(days=365)
    builder = (x509.CertificateBuilder()
               .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)]))
               .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn)]))
               .public_key(pub_key).serial_number(serial)
               .not_valid_before(not_before).not_valid_after(not_after))
    if ca is not None:
        builder = builder.add_extension(x509.BasicConstraints(ca=ca, path_length=pathlen), critical=True)
    sig_hash = hashes.SHA384() if isinstance(signing_key.public_key().curve, ec.SECP384R1) else hashes.SHA256()
    return builder.sign(signing_key, sig_hash)


def der_hex(cert) -> str:
    return cert.public_bytes(Encoding.DER).hex()


def pubnum(key):
    n = key.public_key().public_numbers()
    return n.x, n.y


def oracle_chain_trusted(anchor_items, cert_pool, chain_certs):
    """anchor_items: list of (id, private key) for EVERY anchor declared in this PKI (not just
    one), named with the SAME id string a cert's issuer CN would use (so OpenSSL's own name
    chaining lines up with what this assignment's input says). Any of them verifying the topmost
    cert is enough, exactly like assignment 09's "try each" rule, just applied PKI-wide here
    instead of one chain at a time.
    cert_pool: every non-leaf cert in the chain (openssl just needs the pool).
    chain_certs: the actual leaf-to-topmost certs, leaf first."""
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        anchor_certs = [make_cert(aid, aid, k.public_key(), k, ca=True, serial=900 + i)
                        for i, (aid, k) in enumerate(anchor_items)] or [
            make_cert("Unrelated", "Unrelated", make_key().public_key(), make_key(), ca=True, serial=999)]
        (d / "root.pem").write_bytes(b"".join(c.public_bytes(Encoding.PEM) for c in anchor_certs))
        args = ["openssl", "verify", "-attime", str(ATTIME), "-CAfile", str(d / "root.pem")]
        if cert_pool:
            (d / "untrusted.pem").write_bytes(b"".join(c.public_bytes(Encoding.PEM) for c in cert_pool))
            args += ["-untrusted", str(d / "untrusted.pem")]
        (d / "leaf.pem").write_bytes(chain_certs[0].public_bytes(Encoding.PEM))
        proc = subprocess.run(args + [str(d / "leaf.pem")], capture_output=True, text=True)
    if proc.returncode == 0 and "OK" in proc.stdout:
        return True, None
    m = ERROR_RE.search(proc.stdout + proc.stderr)
    assert m, f"unrecognised openssl verify output:\n{proc.stdout}\n{proc.stderr}"
    return False, ERROR_CODE_TO_REASON[int(m.group(1))]


def oracle_matched_anchor(top_cert, anchor_items):
    """Which anchor (id, key) actually signed top_cert's TBS bytes, via the `cryptography`
    library's own verify - a different code path from the reference's hand modular arithmetic,
    and from oracle_chain_trusted's openssl-based path-building above."""
    from cryptography.exceptions import InvalidSignature
    for aid, key in anchor_items:
        try:
            key.public_key().verify(top_cert.signature, top_cert.tbs_certificate_bytes,
                                     ec.ECDSA(top_cert.signature_hash_algorithm))
            return aid
        except InvalidSignature:
            continue
    return None


def oracle_exposed(chains, matched_anchors):
    """A second computation of the blast-radius graph fact, structurally different from the
    reference's (a dict-of-lists built with setdefault per id as the chains are walked): here,
    for every candidate id, scan every chain's tail (a comprehension, not a shared mutable dict
    built incrementally) and collect the chains that contain it. matched_anchors: chain_id ->
    the anchor id that actually signed its topmost cert, or None (from oracle_matched_anchor)."""
    cert_ids = {i for _, ids in chains for i in ids[1:]}
    anchor_ids = {aid for aid in matched_anchors.values() if aid is not None}
    all_ids = sorted(cert_ids | anchor_ids)
    result = {}
    for i in all_ids:
        chains_for_i = [cid for cid, ids in chains if i in ids[1:]]
        chains_for_i += [cid for cid, aid in matched_anchors.items() if aid == i]
        if chains_for_i:
            result[i] = chains_for_i
    return result


class PKI:
    """Builds one small PKI: anchors (bare keys, by curve), certs (keyed by id, each with its
    issuer's signing key and curve), and chains (leaf-first CERT id lists - no anchor id among
    them; the topmost cert is checked against every declared anchor, not one named here)."""

    def __init__(self):
        self.anchor_keys = {}     # id -> private key
        self.anchor_curve = {}    # id -> "P-256" | "P-384"
        self.anchor_order = []
        self.certs = {}           # id -> (cryptography Certificate, curve)
        self.cert_order = []
        self.chains = []          # (chain_id, [ids])
        self._serial = 1

    def anchor(self, aid, curve="P-384"):
        self.anchor_keys[aid] = make_key(curve)
        self.anchor_curve[aid] = curve
        self.anchor_order.append(aid)
        return aid

    def cert(self, cid, issuer_id, curve="P-384", ca=None, pathlen=None, pub_key=None):
        issuer_key = self.anchor_keys.get(issuer_id) or self.certs[issuer_id][2]
        # Every subject name built here is the bare id string (see make_cert calls below and in
        # main()), so the matching issuer name is just that same bare id - not
        # Name.rfc4514_string(), which would come back "CN=<id>" and double-wrap into
        # "CN=CN=<id>" once fed back in as a raw CN value, breaking OpenSSL's name chaining.
        issuer_cn = issuer_id
        key = pub_key or make_key(curve)
        self._serial += 1
        cert = make_cert(cid, issuer_cn, key.public_key(), issuer_key, ca=ca, pathlen=pathlen, serial=self._serial)
        self.certs[cid] = (cert, curve, key)
        self.cert_order.append(cid)
        return cid

    def chain(self, chain_id, ids):
        self.chains.append((chain_id, ids))
        return chain_id

    def key_order(self):
        return self.anchor_order + self.cert_order

    def key_tuple(self, kid):
        if kid in self.anchor_keys:
            x, y = pubnum(self.anchor_keys[kid])
            return (self.anchor_curve[kid], x, y)
        cert, curve, key = self.certs[kid]
        x, y = pubnum(key)
        return (curve, x, y)

    def input_lines(self, blocklist, bound_overrides=None):
        lines = []
        for curve, x, y in blocklist:
            lines.append(f"blocklist {curve} {x:x} {y:x}")
        for aid in self.anchor_order:
            curve, x, y = self.key_tuple(aid)
            lines.append(f"anchor {aid} {curve} {x:x} {y:x}")
        for cid in self.cert_order:
            cert, _curve, _key = self.certs[cid]
            lines.append(f"cert {cid} {der_hex(cert)}")
        for chain_id, ids in self.chains:
            lines.append(f"chain {chain_id} " + " ".join(ids))
        return lines

    def expected_lines(self, blocklist, bound):
        lines = []
        for kid in self.key_order():
            curve, x, y = self.key_tuple(kid)
            if not curves.on_curve(curve, x, y):
                reason = "off-curve"
            elif (curve, x, y) in blocklist:
                reason = "known-compromised"
            else:
                d = next((d for d in range(1, bound + 1) if curves.public_point(curve, d) == (x, y)), None)
                reason = "weak" if d is not None else None
            lines.append(f"key {kid} {reason or 'ok'}")
        anchor_items = [(aid, self.anchor_keys[aid]) for aid in self.anchor_order]
        matched_anchors = {}
        for chain_id, ids in self.chains:
            cert_pool = [self.certs[i][0] for i in ids[1:]]
            chain_certs = [self.certs[i][0] for i in ids]
            ok, reason = oracle_chain_trusted(anchor_items, cert_pool, chain_certs)
            matched_anchors[chain_id] = oracle_matched_anchor(chain_certs[-1], anchor_items)
            lines.append(f"chain {chain_id} trusted" if ok else f"chain {chain_id} untrusted {reason}")
        exposed = oracle_exposed(self.chains, matched_anchors)
        for kid in self.key_order():
            if kid in exposed and exposed[kid]:
                lines.append(f"exposed {kid} " + " ".join(exposed[kid]))
        return lines


def weak_point(curve, d):
    return curves.public_point(curve, d)


def main():
    args = wbcore.parse_args("16")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)
    bound = 4096

    def add(case_id, req, title, pki, blocklist=()):
        blocklist = set(blocklist)
        cases.add(case_id, req, title, pki.input_lines(blocklist), pki.expected_lines(blocklist, bound))

    # R1 - lint covers every reason, including anchors
    p = PKI()
    p.anchor("root1")
    p.cert("leaf1", "root1")
    p.chain("c1", ["leaf1"])
    lines = p.input_lines(set())
    expected = p.expected_lines(set(), bound)
    # Add one more anchor, off-curve by construction (a real point's y shifted by 1), not used
    # by any chain - just to confirm R1 lints every declared key, anchors included.
    ocurve, ox, oy = p.key_tuple("root1")
    broken_y = (oy + 1) % curves.CURVES[ocurve]["p"]
    assert not curves.on_curve(ocurve, ox, broken_y)
    lines.insert(0, f"anchor off-curve-anchor {ocurve} {ox:x} {broken_y:x}")
    expected.insert(0, "key off-curve-anchor off-curve")
    cases.add("16-R1-off-curve", "R1", "an extra anchor key perturbed off the curve by 1, alongside a clean chain",
              lines, expected)

    p = PKI()
    p.anchor("root2")
    p.cert("int-weak", "root2", ca=True, pub_key=None)
    weak_key = ec.derive_private_key(4, ec.SECP384R1())
    p.certs["int-weak"] = (make_cert("int-weak", "root2", weak_key.public_key(), p.anchor_keys["root2"], ca=True,
                                      serial=p._serial), "P-384", weak_key)
    p.cert("leaf-under-weak", "int-weak")
    p.chain("c1", ["leaf-under-weak", "int-weak"])
    add("16-R1-weak-d4", "R1", "an intermediate whose private key is 4 (the incident's own value)", p)

    p = PKI()
    p.anchor("rootB")
    blocked = make_key()
    p.cert("blocked-int", "rootB", ca=True, pub_key=blocked)
    p.cert("leaf-b", "blocked-int")
    p.chain("c1", ["leaf-b", "blocked-int"])
    add("16-R1-known-compromised", "R1", "an intermediate whose key is on the blocklist",
        p, blocklist={("P-384", *pubnum(blocked))})

    p = PKI()
    p.anchor("rootB2")
    weak_and_blocked = ec.derive_private_key(56, ec.SECP384R1())
    p.cert("weak-and-blocked", "rootB2", ca=True, pub_key=weak_and_blocked)
    p.cert("leaf-b2", "weak-and-blocked")
    p.chain("c1", ["leaf-b2", "weak-and-blocked"])
    add("16-R1-priority", "R1",
        "a key that is both weak (d=56) and on the blocklist: known-compromised wins (checked first)",
        p, blocklist={("P-384", *pubnum(weak_and_blocked))})

    p = PKI()
    p.anchor("rootC")
    p.cert("okC", "rootC", ca=True)
    p.cert("leafC", "okC")
    p.chain("c1", ["leafC", "okC"])
    add("16-R1-all-ok", "R1", "a clean 3-level chain: every key lints ok", p)

    # R2 - every chain-9-style reason, through this assignment's own input shape
    p = PKI()
    p.anchor("rootD")
    p.cert("leafD", "rootD")  # leafD is not a CA; make a chain pretend it's an intermediate
    p.cert("leafD2", "leafD")
    p.chain("c-not-ca", ["leafD2", "leafD"])
    add("16-R2-not-a-ca", "R2", "an intermediate lacking CA:true", p)

    p = PKI()
    p.anchor("rootE")
    p.cert("intE", "rootE", ca=True, pathlen=0)
    p.cert("intE2", "intE", ca=True)
    p.cert("leafE", "intE2")
    p.chain("c-pathlen", ["leafE", "intE2", "intE"])
    add("16-R2-path-too-long", "R2", "an intermediate's path length constraint is violated", p)

    p = PKI()
    p.anchor("rootF")  # declared, but not the real signer below
    unrelated_key = make_key()  # never declared as an anchor anywhere in this PKI
    leaf_f_key = make_key()
    leaf_f = make_cert("leafF", "Unrelated-Root", leaf_f_key.public_key(), unrelated_key, serial=p._serial + 1)
    p.certs["leafF"] = (leaf_f, "P-384", leaf_f_key)
    p.cert_order.append("leafF")
    p.chain("c-unknown", ["leafF"])
    add("16-R2-unknown-anchor", "R2",
        "the leaf's real signer was never declared as an anchor in this PKI", p)

    # R3/R4 - exposed lines, including a key shared by two chains
    p = PKI()
    p.anchor("rootG")
    p.cert("sharedG", "rootG", ca=True)
    p.cert("leafG1", "sharedG")
    p.cert("leafG2", "sharedG")
    p.chain("c1", ["leafG1", "sharedG"])
    p.chain("c2", ["leafG2", "sharedG"])
    add("16-R3-R4-shared-intermediate", "R3", "one intermediate signs two leaf chains: both appear in its exposed line", p)

    p = PKI()
    p.anchor("rootH")
    p.cert("leafH", "rootH")
    p.chain("c1", ["leafH"])
    add("16-R3-leaf-not-exposed", "R3", "a 2-level chain: the leaf itself gets no exposed line", p)

    # R5 - both curves, for linting (chain validation in this assignment is P-384 only, matching
    # assignments 06-09's own scope: a P-256 certificate would need SHA-256 instead of SHA-384,
    # which this assignment's reused signature check doesn't cover - a P-256 key is linted here,
    # but not put in any chain)
    p = PKI()
    p.anchor("rootI", curve="P-256")
    p.anchor("rootI2")
    p.cert("leafI-p384", "rootI2")
    p.chain("c1", ["leafI-p384"])
    add("16-R5-p256", "R5", "a P-256 anchor (linted, not chained) alongside a normal P-384 chain", p)

    # E2E - shaped like the real incident
    p = PKI()
    p.anchor("root-e2e")
    weak_key2 = ec.derive_private_key(115, ec.SECP384R1())
    p.certs["weak-intermediate"] = (make_cert("weak-intermediate", "root-e2e", weak_key2.public_key(),
                                               p.anchor_keys["root-e2e"], ca=True, serial=1001), "P-384", weak_key2)
    p.cert_order.append("weak-intermediate")
    p.cert("strong-intermediate", "root-e2e", ca=True)
    p.cert("leaf-via-weak-1", "weak-intermediate")
    p.cert("leaf-via-weak-2", "weak-intermediate")
    p.cert("leaf-via-strong", "strong-intermediate")
    p.chain("via-weak-1", ["leaf-via-weak-1", "weak-intermediate"])
    p.chain("via-weak-2", ["leaf-via-weak-2", "weak-intermediate"])
    p.chain("via-strong", ["leaf-via-strong", "strong-intermediate"])
    add("16-E2E-incident-shape", "E2E",
        "one root, a weak intermediate (d=115) signing two leaves, a strong intermediate signing one", p)

    cases.save()


if __name__ == "__main__":
    main()
