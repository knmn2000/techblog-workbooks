"""Test cases for assignment 09 (validate a certificate chain).

Every chain is built with `cryptography`'s CertificateBuilder. The independent oracle is
`openssl verify`: each chain is also written out as a small PEM trust store (a self-signed root
certificate wrapping the same key the test exposes only as a bare public key, since this
assignment's input never gives a root certificate, only its key) plus an "untrusted" bundle of
intermediates and the leaf, and

    openssl verify -attime <epoch> -CAfile root.pem -untrusted untrusted.pem leaf.pem

is run exactly as a real verifier would. OpenSSL's own numbered verify errors map onto this
assignment's reason vocabulary: 7 (signature failure) -> bad-signature, 20 (unable to get local
issuer certificate) -> unknown-anchor, 79 (invalid CA certificate) -> not-a-ca, 25 (path length
constraint exceeded) -> path-too-long, 9/10 (not yet valid / expired) -> expired.

    python3 -P tools/gen_p09.py                                  # tests/09 (seed 1)
    python3 -P tools/gen_p09.py --seed 777 --out build/fresh/09  # what `check 09 -Fresh` runs
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

LIB = f"openssl verify -attime <epoch> -CAfile <root> -untrusted <intermediates> <leaf> (OpenSSL's own path validation, independent of this workbook's reference)"

REQUIREMENTS = [
    ("R1", "A valid 2-level chain: the leaf is signed directly by a trust anchor"),
    ("R2", "A valid 3-level chain: leaf, one intermediate, then a trust anchor"),
    ("R3", "The last certificate's issuer key isn't one of the given trust anchors: unknown-anchor"),
    ("R4", "A certificate in the chain was not really signed by the next one up: bad-signature"),
    ("R5", "An intermediate in the chain lacks CA:true: not-a-ca"),
    ("R6", "An intermediate's path length constraint is violated by how many more intermediates follow it: path-too-long"),
    ("R7", "A certificate's validity window does not cover `now`: expired"),
    ("E2E", "A realistic small set of chains, mirroring what let browsers reject paths through the revoked eMudhra intermediates"),
]
EXPLAIN = "_lines=R1 trusted=R3 untrusted=R3"

EPOCH = datetime.datetime(2025, 6, 1)  # "now" for every chain in this assignment, unless R7 overrides it
ATTIME = int(EPOCH.timestamp())


def fmt_time(dt: datetime.datetime) -> str:
    """UTCTime text (YYMMDDHHMMSSZ), the form `cryptography` writes for any date in 1950-2049 -
    cross-checked once in main() against OpenSSL's own ASN.1 decoder."""
    return dt.strftime("%y%m%d%H%M%SZ")


def make_key():
    return ec.generate_private_key(ec.SECP384R1())


def make_cert(subject_cn, issuer_cn, pub_key, signing_key, ca=None, pathlen=None,
              not_before=None, not_after=None, serial=1):
    not_before = not_before or EPOCH - datetime.timedelta(days=30)
    not_after = not_after or EPOCH + datetime.timedelta(days=365)
    builder = (x509.CertificateBuilder()
               .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)]))
               .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn)]))
               .public_key(pub_key).serial_number(serial)
               .not_valid_before(not_before).not_valid_after(not_after))
    if ca is not None:
        builder = builder.add_extension(x509.BasicConstraints(ca=ca, path_length=pathlen), critical=True)
    return builder.sign(signing_key, hashes.SHA384())


ERROR_CODE_TO_REASON = {7: "bad-signature", 20: "unknown-anchor", 79: "not-a-ca",
                        25: "path-too-long", 9: "expired", 10: "expired"}
ERROR_RE = re.compile(r"error (\d+) at \d+ depth lookup")


def oracle_validate(root_certs, intermediate_certs, leaf_cert, attime=ATTIME):
    """root_certs: self-signed certs for the trust anchors (CAfile). intermediate_certs: every
    chain certificate except the leaf, most-senior first (doesn't matter: openssl -untrusted
    just needs the pool). Returns (True, None) or (False, reason)."""
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        # An empty CAfile is a deliberate case (no anchors at all: everything is unknown-anchor).
        # OpenSSL needs at least one well-formed cert to parse a PEM bundle, so when there are
        # none, point -CAfile at an unrelated, throwaway self-signed cert instead of an empty
        # file (which OpenSSL refuses to read at all) - it still can't be the chain's real
        # signer, so the result is the same "unknown-anchor" outcome either way.
        anchor_certs = root_certs or [make_cert("Unrelated-Throwaway", "Unrelated-Throwaway",
                                                 make_key().public_key(), make_key(), ca=True, serial=999)]
        (d / "root.pem").write_bytes(b"".join(c.public_bytes(Encoding.PEM) for c in anchor_certs))
        args = ["openssl", "verify", "-attime", str(attime), "-CAfile", str(d / "root.pem")]
        if intermediate_certs:
            (d / "untrusted.pem").write_bytes(b"".join(c.public_bytes(Encoding.PEM) for c in intermediate_certs))
            args += ["-untrusted", str(d / "untrusted.pem")]
        (d / "leaf.pem").write_bytes(leaf_cert.public_bytes(Encoding.PEM))
        proc = subprocess.run(args + [str(d / "leaf.pem")], capture_output=True, text=True)
    if proc.returncode == 0 and "OK" in proc.stdout:
        return True, None
    m = ERROR_RE.search(proc.stdout + proc.stderr)
    assert m, f"unrecognised openssl verify output:\n{proc.stdout}\n{proc.stderr}"
    code = int(m.group(1))
    assert code in ERROR_CODE_TO_REASON, f"unmapped openssl verify error code {code}"
    return False, ERROR_CODE_TO_REASON[code]


def check_time_format(cert):
    """Confirms fmt_time()'s assumption against OpenSSL's own ASN.1 decoder, once."""
    with tempfile.NamedTemporaryFile(suffix=".der") as f:
        f.write(cert.public_bytes(Encoding.DER))
        f.flush()
        proc = subprocess.run(["openssl", "asn1parse", "-inform", "DER", "-in", f.name],
                              capture_output=True, text=True, check=True)
    times = re.findall(r"prim: UTCTIME\s*:(\S+)", proc.stdout)
    assert len(times) == 2
    assert times[0] == fmt_time(cert.not_valid_before), (times[0], fmt_time(cert.not_valid_before))


def main():
    args = wbcore.parse_args("09")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)
    now_str = fmt_time(EPOCH)

    def pubnums(key):
        n = key.public_key().public_numbers()
        return n.x, n.y

    def add_chain(case_id, req, title, label, root_keys, root_certs, intermediates, leaf, now=now_str, attime=ATTIME):
        """root_keys: list of ec private keys (trust anchors). root_certs: matching self-signed
        certs, for the oracle only. intermediates: list of cryptography Certificate objects,
        leaf-adjacent first (i.e. the order the chain input expects, leaf excluded). leaf: the
        leaf Certificate."""
        trusted, reason = oracle_validate(root_certs, intermediates, leaf, attime)
        input_lines = [f"chain {label}", f"now {now}"]
        for key in root_keys:
            x, y = pubnums(key)
            c = curves.CURVES["P-384"]
            input_lines.append(f"anchor P-384 {x:0{c['hexlen']}x} {y:0{c['hexlen']}x}")
        for cert in [leaf] + intermediates:
            input_lines.append(f"cert {cert.public_bytes(Encoding.DER).hex()}")
        expected = f"chain {label} trusted" if trusted else f"chain {label} untrusted {reason}"
        cases.add(case_id, req, title, input_lines, expected)

    # --- R1: valid 2-level chain ---
    root_key = make_key()
    root_cert = make_cert("Root-1", "Root-1", root_key.public_key(), root_key, ca=True, serial=1)
    check_time_format(root_cert)
    leaf_key = make_key()
    leaf = make_cert("Leaf-1", "Root-1", leaf_key.public_key(), root_key, serial=2)
    add_chain("09-R1-two-level", "R1", "a leaf signed directly by a trust anchor", "c1",
              [root_key], [root_cert], [], leaf)

    # --- R2: valid 3-level chain ---
    root_key2 = make_key()
    root_cert2 = make_cert("Root-2", "Root-2", root_key2.public_key(), root_key2, ca=True, serial=1)
    int_key2 = make_key()
    intermediate2 = make_cert("Intermediate-2", "Root-2", int_key2.public_key(), root_key2, ca=True, serial=2)
    leaf_key2 = make_key()
    leaf2 = make_cert("Leaf-2", "Intermediate-2", leaf_key2.public_key(), int_key2, serial=3)
    add_chain("09-R2-three-level", "R2", "leaf, one intermediate, then a trust anchor", "c2",
              [root_key2], [root_cert2], [intermediate2], leaf2)

    # --- R3: unknown anchor (signed by a root NOT in the anchor list) ---
    real_root_key = make_key()
    real_root_cert = make_cert("Real-Root", "Real-Root", real_root_key.public_key(), real_root_key, ca=True, serial=1)
    unknown_root_key = make_key()  # this key signs the leaf, but is never offered as an anchor
    leaf3_key = make_key()
    leaf3 = make_cert("Leaf-3", "Unknown-Root", leaf3_key.public_key(), unknown_root_key, serial=1)
    add_chain("09-R3-unknown-anchor", "R3", "signed by a root that isn't one of the given trust anchors", "c3",
              [real_root_key], [real_root_cert], [], leaf3)

    # --- R4: bad signature (same issuer name, wrong signing key) ---
    root_key4 = make_key()
    root_cert4 = make_cert("Root-4", "Root-4", root_key4.public_key(), root_key4, ca=True, serial=1)
    int_key4 = make_key()
    intermediate4 = make_cert("Intermediate-4", "Root-4", int_key4.public_key(), root_key4, ca=True, serial=2)
    leaf4_key = make_key()
    wrong_key4 = make_key()  # the leaf claims Intermediate-4 as issuer, but isn't really signed by it
    leaf4 = make_cert("Leaf-4", "Intermediate-4", leaf4_key.public_key(), wrong_key4, serial=3)
    add_chain("09-R4-bad-signature", "R4", "a leaf that claims the right issuer but isn't really signed by it", "c4",
              [root_key4], [root_cert4], [intermediate4], leaf4)

    # --- R5: intermediate lacks CA:true ---
    root_key5 = make_key()
    root_cert5 = make_cert("Root-5", "Root-5", root_key5.public_key(), root_key5, ca=True, serial=1)
    int_key5 = make_key()
    intermediate5 = make_cert("Intermediate-5", "Root-5", int_key5.public_key(), root_key5, ca=False, serial=2)  # not a CA
    leaf5_key = make_key()
    leaf5 = make_cert("Leaf-5", "Intermediate-5", leaf5_key.public_key(), int_key5, serial=3)
    add_chain("09-R5-not-a-ca", "R5", "an intermediate that signed a leaf but is not marked CA:true", "c5",
              [root_key5], [root_cert5], [intermediate5], leaf5)

    # --- R6: path length violated (pathlen 0, but another intermediate follows) ---
    root_key6 = make_key()
    root_cert6 = make_cert("Root-6", "Root-6", root_key6.public_key(), root_key6, ca=True, serial=1)
    intA_key6 = make_key()
    intA6 = make_cert("IntA-6", "Root-6", intA_key6.public_key(), root_key6, ca=True, pathlen=0, serial=2)
    intB_key6 = make_key()
    intB6 = make_cert("IntB-6", "IntA-6", intB_key6.public_key(), intA_key6, ca=True, serial=3)
    leaf6_key = make_key()
    leaf6 = make_cert("Leaf-6", "IntB-6", leaf6_key.public_key(), intB_key6, serial=4)
    add_chain("09-R6-path-too-long", "R6", "IntA-6 asserts path length 0, but IntB-6 follows it before the leaf", "c6",
              [root_key6], [root_cert6], [intB6, intA6], leaf6)

    # a pathlen that's respected (pathlen 1 with exactly one intermediate below it): must be trusted
    root_key6b = make_key()
    root_cert6b = make_cert("Root-6b", "Root-6b", root_key6b.public_key(), root_key6b, ca=True, serial=1)
    intA_key6b = make_key()
    intA6b = make_cert("IntA-6b", "Root-6b", intA_key6b.public_key(), root_key6b, ca=True, pathlen=1, serial=2)
    intB_key6b = make_key()
    intB6b = make_cert("IntB-6b", "IntA-6b", intB_key6b.public_key(), intA_key6b, ca=True, serial=3)
    leaf6b_key = make_key()
    leaf6b = make_cert("Leaf-6b", "IntB-6b", leaf6b_key.public_key(), intB_key6b, serial=4)
    add_chain("09-R6-path-length-respected", "R6", "IntA-6b asserts path length 1, and exactly one intermediate follows it: trusted", "c6b",
              [root_key6b], [root_cert6b], [intB6b, intA6b], leaf6b)

    # --- R7: expired ---
    root_key7 = make_key()
    root_cert7 = make_cert("Root-7", "Root-7", root_key7.public_key(), root_key7, ca=True, serial=1,
                            not_before=EPOCH - datetime.timedelta(days=3650), not_after=EPOCH + datetime.timedelta(days=3650))
    leaf7_key = make_key()
    leaf7 = make_cert("Leaf-7", "Root-7", leaf7_key.public_key(), root_key7, serial=2,
                       not_before=EPOCH - datetime.timedelta(days=400), not_after=EPOCH - datetime.timedelta(days=30))  # already expired at EPOCH
    add_chain("09-R7-expired", "R7", "the leaf's own validity window ended before `now`", "c7",
              [root_key7], [root_cert7], [], leaf7)

    root_key7b = make_key()
    root_cert7b = make_cert("Root-7b", "Root-7b", root_key7b.public_key(), root_key7b, ca=True, serial=1,
                             not_before=EPOCH - datetime.timedelta(days=3650), not_after=EPOCH + datetime.timedelta(days=3650))
    leaf7b_key = make_key()
    leaf7b = make_cert("Leaf-7b", "Root-7b", leaf7b_key.public_key(), root_key7b, serial=2,
                        not_before=EPOCH + datetime.timedelta(days=30), not_after=EPOCH + datetime.timedelta(days=400))  # not yet valid at EPOCH
    add_chain("09-R7-not-yet-valid", "R7", "the leaf's validity window has not started yet at `now`", "c7b",
              [root_key7b], [root_cert7b], [], leaf7b)

    # --- Random valid/invalid 2- and 3-level chains, for -Fresh coverage ---
    for k in range(2):
        scenario = rng.choice(["valid2", "valid3", "bad-sig", "not-a-ca", "unknown-anchor"])
        rkey = make_key()
        rcert = make_cert(f"RRoot-{args.seed}-{k}", f"RRoot-{args.seed}-{k}", rkey.public_key(), rkey, ca=True, serial=1)
        if scenario == "valid2":
            lkey = make_key()
            leaf = make_cert(f"RLeaf-{args.seed}-{k}", f"RRoot-{args.seed}-{k}", lkey.public_key(), rkey, serial=2)
            add_chain(f"09-E2E-random-{scenario}-s{args.seed}-{k}", "E2E", f"random valid 2-level chain (seed {args.seed})",
                      f"r{k}", [rkey], [rcert], [], leaf)
        elif scenario == "valid3":
            ikey = make_key()
            icert = make_cert(f"RInt-{args.seed}-{k}", f"RRoot-{args.seed}-{k}", ikey.public_key(), rkey, ca=True, serial=2)
            lkey = make_key()
            leaf = make_cert(f"RLeaf-{args.seed}-{k}", f"RInt-{args.seed}-{k}", lkey.public_key(), ikey, serial=3)
            add_chain(f"09-E2E-random-{scenario}-s{args.seed}-{k}", "E2E", f"random valid 3-level chain (seed {args.seed})",
                      f"r{k}", [rkey], [rcert], [icert], leaf)
        elif scenario == "bad-sig":
            ikey = make_key()
            icert = make_cert(f"RInt-{args.seed}-{k}", f"RRoot-{args.seed}-{k}", ikey.public_key(), rkey, ca=True, serial=2)
            lkey = make_key()
            wrong = make_key()
            leaf = make_cert(f"RLeaf-{args.seed}-{k}", f"RInt-{args.seed}-{k}", lkey.public_key(), wrong, serial=3)
            add_chain(f"09-E2E-random-{scenario}-s{args.seed}-{k}", "E2E", f"random chain with a bad signature (seed {args.seed})",
                      f"r{k}", [rkey], [rcert], [icert], leaf)
        elif scenario == "not-a-ca":
            ikey = make_key()
            icert = make_cert(f"RInt-{args.seed}-{k}", f"RRoot-{args.seed}-{k}", ikey.public_key(), rkey, ca=False, serial=2)
            lkey = make_key()
            leaf = make_cert(f"RLeaf-{args.seed}-{k}", f"RInt-{args.seed}-{k}", lkey.public_key(), ikey, serial=3)
            add_chain(f"09-E2E-random-{scenario}-s{args.seed}-{k}", "E2E", f"random chain with a non-CA intermediate (seed {args.seed})",
                      f"r{k}", [rkey], [rcert], [icert], leaf)
        else:
            other_root = make_key()
            lkey = make_key()
            leaf = make_cert(f"RLeaf-{args.seed}-{k}", f"Unknown-{args.seed}-{k}", lkey.public_key(), other_root, serial=2)
            add_chain(f"09-E2E-random-{scenario}-s{args.seed}-{k}", "E2E", f"random chain signed by an unlisted root (seed {args.seed})",
                      f"r{k}", [rkey], [rcert], [], leaf)

    # --- E2E: the incident shape - a chain through an intermediate that would be an eMudhra-like
    # CA, once removed from the trust store its signer is no longer a recognised anchor ---
    root_keyE = make_key()
    root_certE = make_cert("Public-Root", "Public-Root", root_keyE.public_key(), root_keyE, ca=True, serial=1)
    compromised_key = make_key()  # stands in for a weak/compromised intermediate key
    compromised_cert = make_cert("Compromised-Intermediate", "Public-Root", compromised_key.public_key(), root_keyE, ca=True, serial=2)
    leafE_key = make_key()
    leafE_valid = make_cert("Leaf-Via-Compromised", "Compromised-Intermediate", leafE_key.public_key(), compromised_key, serial=3)
    add_chain("09-E2E-incident-before-distrust", "E2E",
              "before distrust: a leaf through the (still trusted) intermediate verifies", "before",
              [root_keyE], [root_certE], [compromised_cert], leafE_valid)
    # After the incident, the intermediate is removed from the trust store/root list entirely -
    # modelled here as the leaf no longer chaining to any given anchor.
    add_chain("09-E2E-incident-after-distrust", "E2E",
              "after distrust: the same leaf, but its issuing intermediate's signer is no longer an anchor", "after",
              [], [], [compromised_cert], leafE_valid)

    cases.save()


if __name__ == "__main__":
    main()
