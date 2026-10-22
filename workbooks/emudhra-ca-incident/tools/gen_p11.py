"""Test cases for assignment 11 (sign a certificate with a recovered key).

This assignment stays entirely inside the workbook's own synthetic test keys and names
(forged.example and the like): there is no real certificate authority, domain or infrastructure
anywhere here. Every private key is either a toy value or a key this workbook generated for itself.

For the `sign` cases, expected r is computed by curves.public_point (an independent, OpenSSL-backed
scalar multiplication, not the reference's own point-doubling code). Expected s follows directly
from the ECDSA formula using Python's native modular inverse. Every case is then double-checked by
building the real public key and verifying the produced signature with the `cryptography` library -
a code path entirely separate from how either r or s was computed - so a case is never written
unless it is a genuine, verifiable ECDSA signature for the stated key and hash.

For the `forge` cases, the tbsCertificate, the intermediate certificate and the trust anchor come
from `cryptography`'s CertificateBuilder. The forged signature's r and s are computed the same
independent way as the `sign` cases, and the certificate's bytes are assembled with a DER writer
written here, not taken from the reference. Each forged certificate is then checked two independent
ways: `verify_directly_issued_by` confirms the intermediate signed the forged leaf and the root
signed the intermediate, and `openssl verify -CAfile <root> -untrusted <intermediate> <leaf>` runs
a real path validation. A forge case is never written unless both accept the forged chain.

    python3 -P tools/gen_p11.py                                  # tests/11 (seed 1)
    python3 -P tools/gen_p11.py --seed 777 --out build/fresh/11  # what `check 11 -Fresh` runs
"""

import datetime
import hashlib
import random
import subprocess
import sys
import tempfile
from pathlib import Path

import cryptography
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID

sys.path.insert(0, str(Path(__file__).resolve().parent))
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = f"cryptography {cryptography.__version__} (OpenSSL): r from scalar multiplication, the signature confirmed by verifying it"
FORGE_LIB = f"cryptography {cryptography.__version__} and openssl verify: the forged certificate assembled independently and accepted by both"
HEXLEN = {"P-256": 64, "P-384": 96}
LIB_CURVE = {"P-256": ec.SECP256R1, "P-384": ec.SECP384R1}
DIGEST_BYTES = {"P-256": 32, "P-384": 48}

# ecdsa-with-SHA384: the AlgorithmIdentifier the forged P-384 certificate carries.
ECDSA_WITH_SHA384 = bytes.fromhex("300a06082a8648ce3d040303")
# A fixed, clearly fictitious time window for every forged certificate (no real validity dates).
FORGE_EPOCH = datetime.datetime(2026, 1, 1)

REQUIREMENTS = [
    ("R1", "One output line per input, in order: `signature <id> <r> <s>`, in lowercase hex"),
    ("R2", "Both curves work: P-256 and P-384 each use their own p, a, G and n"),
    ("R3", "Every nonce k works, including k = 1, k = 2, k = n - 1, and a large random k, so the "
           "answer must come from double-and-add, not a loop that runs k times"),
    ("R4", "The private key can be any value, including the recovered incident value d = 4: the formula is the same however small or large d is"),
    ("R5", "The hash z can be any value in range, including 0 and n - 1"),
    ("R6", "A forged certificate signed with the weak key, assembled into DER, is accepted by your own validate_chain from assignment 09"),
]
# A wrong signature's r or s could come from almost any part of the formula, so there is no
# single requirement a content difference reliably points to (see authoring-guide.md: only map
# where a location really does localise the mistake). Only a missing line is mapped; each case's
# own requirement is the fallback cause.
EXPLAIN = "_lines=R1"


# ---- DER writers (independent of the reference's own) -----------------------------------------

def der_length(length):
    if length < 0x80:
        return bytes([length])
    body = length.to_bytes((length.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(body)]) + body


def der_integer(value):
    body = value.to_bytes((value.bit_length() + 7) // 8 or 1, "big")
    if body[0] & 0x80:
        body = b"\x00" + body
    return b"\x02" + der_length(len(body)) + body


def der_sequence(content):
    return b"\x30" + der_length(len(content)) + content


def der_bit_string(content):
    body = b"\x00" + content
    return b"\x03" + der_length(len(body)) + body


# ---- `sign` cases: the signature (r, s) on a hash z -------------------------------------------

def signature(curve, d, z, k):
    """Returns (r, s), cross-checked against the cryptography library before it is used."""
    c = curves.CURVES[curve]
    n = c["n"]
    rx, _ = curves.public_point(curve, k)
    r = rx % n
    s = pow(k, -1, n) * (z + r * d) % n
    assert r != 0 and s != 0, "a real signer would redraw k here; choose a different k for this case"
    qx, qy = curves.public_point(curve, d)
    pubkey = ec.EllipticCurvePublicNumbers(qx, qy, LIB_CURVE[curve]()).public_key()
    pubkey.verify(utils.encode_dss_signature(r, s), z.to_bytes(DIGEST_BYTES[curve], "big"),
                  ec.ECDSA(utils.Prehashed(_prehashed(curve))))
    return r, s


def build(curve, d, z, k):
    r, s = signature(curve, d, z, k)
    w = HEXLEN[curve]
    return f"signature {{id}} {r:0{w}x} {s:0{w}x}", r, s


def _prehashed(curve):
    return hashes.SHA256() if curve == "P-256" else hashes.SHA384()


def line(curve, case_id, d, z, k):
    w = HEXLEN[curve]
    return f"sign {case_id} {curve} {d:0{w}x} {z:0{w}x} {k:0{w}x}"


def expected_line(case_id, curve, d, z, k):
    template, r, s = build(curve, d, z, k)
    return template.format(id=case_id), r, s


def fixed_digest(curve, text):
    """A hash standing in for a signed message: sha256/sha384 of fixed, clearly fictitious text,
    reduced to the curve's digest size. Never a real certificate's bytes."""
    h = hashlib.sha256(text.encode()) if curve == "P-256" else hashlib.sha384(text.encode())
    return int.from_bytes(h.digest(), "big")


# ---- `forge` cases: a certificate signed with the weak key ------------------------------------

def _p384_cert(subject_cn, issuer_cn, pub_key, signing_key, ca, pathlen, serial,
               not_before, not_after):
    builder = (x509.CertificateBuilder()
               .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)]))
               .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn)]))
               .public_key(pub_key).serial_number(serial)
               .not_valid_before(not_before).not_valid_after(not_after))
    if ca is not None:
        builder = builder.add_extension(x509.BasicConstraints(ca=ca, path_length=pathlen), critical=True)
    return builder.sign(signing_key, hashes.SHA384())


def forge_case(rng, case_id, req, title, d, k, leaf_cn, cases):
    """Builds the incident shape: a public root -> a weak intermediate (private key d) -> a leaf
    forged for `leaf_cn`. Assembles the forged certificate from tbs, the algorithm id and (r, s),
    checks it with the library and openssl, and writes the case."""
    n = curves.CURVES["P-384"]["n"]
    root_key = ec.derive_private_key(rng.randrange(2, n - 1), ec.SECP384R1())
    leaf_key = ec.derive_private_key(rng.randrange(2, n - 1), ec.SECP384R1())
    int_key = ec.derive_private_key(d, ec.SECP384R1())  # the weak key: the intermediate's own key

    root_cert = _p384_cert("Public Test Root", "Public Test Root", root_key.public_key(), root_key,
                           True, None, 1, FORGE_EPOCH - datetime.timedelta(days=3650),
                           FORGE_EPOCH + datetime.timedelta(days=3650))
    int_cert = _p384_cert("Weak Issuing CA", "Public Test Root", int_key.public_key(), root_key,
                          True, 0, 2, FORGE_EPOCH - datetime.timedelta(days=30),
                          FORGE_EPOCH + datetime.timedelta(days=365))
    leaf_tmp = _p384_cert(leaf_cn, "Weak Issuing CA", leaf_key.public_key(), int_key,
                          None, None, 0x1234, FORGE_EPOCH - datetime.timedelta(days=1),
                          FORGE_EPOCH + datetime.timedelta(days=365))
    tbs = leaf_tmp.tbs_certificate_bytes

    z = int.from_bytes(hashlib.sha384(tbs).digest(), "big")
    r, s = signature("P-384", d, z, k)
    forged = der_sequence(tbs + ECDSA_WITH_SHA384 + der_bit_string(der_sequence(der_integer(r) + der_integer(s))))

    forged_cert = x509.load_der_x509_certificate(forged)
    forged_cert.verify_directly_issued_by(int_cert)  # the weak key really signed the forged leaf
    int_cert.verify_directly_issued_by(root_cert)
    _openssl_accepts(root_cert, int_cert, forged_cert)

    root_nums = root_key.public_key().public_numbers()
    w = HEXLEN["P-384"]
    input_line = (f"forge {case_id} P-384 {d:0{w}x} {k:0{w}x} {tbs.hex()} "
                  f"{int_cert.public_bytes(Encoding.DER).hex()} {root_nums.x:0{w}x} {root_nums.y:0{w}x}")
    expected = f"forged {case_id} {forged.hex()} valid"
    cases.add(case_id, req, title, [input_line], expected, source=FORGE_LIB)


def _openssl_accepts(root_cert, int_cert, leaf_cert):
    """Runs a real path validation, the same oracle assignment 09 uses."""
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "root.pem").write_bytes(root_cert.public_bytes(Encoding.PEM))
        (d / "unt.pem").write_bytes(int_cert.public_bytes(Encoding.PEM))
        (d / "leaf.pem").write_bytes(leaf_cert.public_bytes(Encoding.PEM))
        proc = subprocess.run(["openssl", "verify", "-CAfile", str(d / "root.pem"),
                               "-untrusted", str(d / "unt.pem"), str(d / "leaf.pem")],
                              capture_output=True, text=True)
    assert proc.returncode == 0 and "OK" in proc.stdout, f"openssl rejected the forged chain:\n{proc.stdout}\n{proc.stderr}"


def main():
    args = wbcore.parse_args("11")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, curve, d, z, k):
        inp = [line(curve, case_id, d, z, k)]
        exp, _, _ = expected_line(case_id, curve, d, z, k)
        cases.add(case_id, req, title, inp, exp)

    def rand_d(curve):
        return rng.randrange(2 ** 64, curves.CURVES[curve]["n"] - 1)

    def rand_z(curve):
        return rng.randrange(0, curves.CURVES[curve]["n"])

    def rand_k(curve):
        return rng.randrange(2, curves.CURVES[curve]["n"] - 1)

    # R1 - several signatures in one input, in order
    inputs, exp_lines = [], []
    for i, curve in enumerate(("P-256", "P-384", "P-256")):
        cid = f"mixed-{i}"
        d, z, k = rand_d(curve), rand_z(curve), rand_k(curve)
        inputs.append(line(curve, cid, d, z, k))
        e, _, _ = expected_line(cid, curve, d, z, k)
        exp_lines.append(e)
    cases.add("11-R1-three-signatures", "R1", "three signatures in one input, two curves", inputs, exp_lines)

    # R2 - both curves individually
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        add(f"11-R2-{tag}", "R2", f"{curve}: a random key, hash and nonce", curve,
            rand_d(curve), rand_z(curve), rand_k(curve))

    # R3 - nonce diversity
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        n = curves.CURVES[curve]["n"]
        add(f"11-R3-k1-{tag}", "R3", f"{curve}: k = 1, so R is G itself", curve, rand_d(curve), rand_z(curve), 1)
        add(f"11-R3-k2-{tag}", "R3", f"{curve}: k = 2, the first doubling", curve, rand_d(curve), rand_z(curve), 2)
        add(f"11-R3-kmax-{tag}", "R3", f"{curve}: k = n - 1, the largest valid nonce", curve,
            rand_d(curve), rand_z(curve), n - 1)
    for k in range(2):
        curve = ("P-256", "P-384")[k]
        add(f"11-R3-random-k-s{args.seed}-{k}", "R3", f"{curve}: a large random nonce (seed {args.seed})",
            curve, rand_d(curve), rand_z(curve), rand_k(curve))

    # R4 - the private key can be any value, including the recovered incident value
    add("11-R4-d4-p384", "R4", "P-384, d = 4: the value recovered for the real incident in assignment 10",
        "P-384", 4, fixed_digest("P-384", "TBS bytes for a test leaf certificate issued inside this workbook"), rand_k("P-384"))
    for d in (1, 2, 56, 115):
        add(f"11-R4-d{d}-p384", "R4", f"P-384, d = {d}: another small recovered value", "P-384", d,
            rand_z("P-384"), rand_k("P-384"))
    add("11-R4-large-d", "R4", "P-384: a large, properly generated private key", "P-384",
        rand_d("P-384"), rand_z("P-384"), rand_k("P-384"))

    # R5 - the hash can be any value in range
    for curve in curves.CURVES:
        tag = curve.lower().replace("-", "")
        n = curves.CURVES[curve]["n"]
        add(f"11-R5-z0-{tag}", "R5", f"{curve}: z = 0", curve, rand_d(curve), 0, rand_k(curve))
        add(f"11-R5-zmax-{tag}", "R5", f"{curve}: z = n - 1", curve, rand_d(curve), n - 1, rand_k(curve))

    # R6 - forge a certificate with the weak key and check it with validate_chain from assignment 09
    forge_case(rng, "11-R6-forge-d4", "R6",
               "forge forged.example with the incident key d = 4, then validate the chain", 4,
               rand_k("P-384"), "forged.example", cases)
    forge_case(rng, "11-R6-forge-d56", "R6",
               "forge a second name with another recovered value, d = 56", 56,
               rand_k("P-384"), "login.forged.example", cases)

    # E2E - the full narrative: recover d (10) -> sign (11) -> a certificate for any name that your
    # own validator accepts, with a random leaf key and nonce so it changes with -Fresh.
    forge_case(rng, f"11-E2E-forge-s{args.seed}", "E2E",
               f"forge api.forged.example with d = 4 and a random nonce (seed {args.seed})", 4,
               rand_k("P-384"), "api.forged.example", cases)

    cases.save()


if __name__ == "__main__":
    main()
