"""Test cases for assignment 07 (hash the public key / SPKI).

Every certificate is built with `cryptography`'s CertificateBuilder. The expected hash comes
from the exact OpenSSL pipeline this assignment's output has to match bit for bit:

    openssl x509 -pubkey -noout -inform DER -in cert.der
        | openssl pkey -pubin -outform DER
        | openssl dgst -sha256

That is three independent OpenSSL commands chained together, nothing from this workbook's own
code.

    python3 -P tools/gen_p07.py                                  # tests/07 (seed 1)
    python3 -P tools/gen_p07.py --seed 777 --out build/fresh/07  # what `check 07 -Fresh` runs
"""

import datetime
import random
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
import wbcore  # noqa: E402

LIB = "openssl x509 -pubkey | openssl pkey -pubin -outform DER | openssl dgst -sha256 (three independent OpenSSL commands)"

REQUIREMENTS = [
    ("R1", "The SPKI hash is correct for several P-256 certificates"),
    ("R2", "The SPKI hash is correct for several P-384 certificates"),
    ("R3", "Two different certificates (different subject, different validity) that share the same public key hash the same - the hash survives reissuance"),
    ("E2E", "A small set of certificates mixing both curves and a reissued key, matching OpenSSL's own pipeline bit for bit"),
]
EXPLAIN = "_lines=R1"

LIB_EC = {"P-256": ec.SECP256R1, "P-384": ec.SECP384R1}


def build_cert(subject_cn: str, curve: str, key=None, serial=1,
               not_before=datetime.datetime(2025, 1, 1), not_after=datetime.datetime(2026, 1, 1)):
    """One self-signed DER certificate. Reuses `key` if given (to test reissuance with the same
    key), otherwise generates a fresh one."""
    key = key or ec.generate_private_key(LIB_EC[curve]())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)])
    cert = (x509.CertificateBuilder()
            .subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(serial).not_valid_before(not_before).not_valid_after(not_after)
            .sign(key, hashes.SHA384() if curve == "P-384" else hashes.SHA256()))
    return cert.public_bytes(Encoding.DER), key


def openssl_spki_hash(der_bytes: bytes) -> str:
    """The exact pipeline described above, as the independent oracle."""
    with tempfile.NamedTemporaryFile(suffix=".der") as f:
        f.write(der_bytes)
        f.flush()
        pubkey = subprocess.run(["openssl", "x509", "-pubkey", "-noout", "-inform", "DER", "-in", f.name],
                                 capture_output=True, check=True).stdout
    spki_der = subprocess.run(["openssl", "pkey", "-pubin", "-outform", "DER"], input=pubkey,
                               capture_output=True, check=True).stdout
    digest = subprocess.run(["openssl", "dgst", "-sha256"], input=spki_der, capture_output=True, check=True).stdout
    # "SHA2-256(stdin)= <hex>\n" or "(stdin)= <hex>\n" depending on OpenSSL version
    return digest.decode().strip().rsplit("=", 1)[1].strip()


def main():
    args = wbcore.parse_args("07")
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records spki=hash", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, certs):
        """certs: list of (label, der_bytes)."""
        input_lines = [f"cert {label} {data.hex()}" for label, data in certs]
        expected = [f"spki {label} {openssl_spki_hash(data)}" for label, data in certs]
        cases.add(case_id, req, title, input_lines, expected)

    # R1 - P-256, several certificates
    certs = [(f"c{i}", build_cert(f"Spki-256-{i}", "P-256", serial=i + 1)[0]) for i in range(3)]
    add("07-R1-p256-several", "R1", "three different P-256 certificates, three different keys", certs)

    # R2 - P-384, several certificates
    certs = [(f"c{i}", build_cert(f"Spki-384-{i}", "P-384", serial=i + 1)[0]) for i in range(3)]
    add("07-R2-p384-several", "R2", "three different P-384 certificates, three different keys", certs)

    # R3 - same key, different certificates (different subject and validity)
    data1, key = build_cert("Reissued-V1", "P-384", serial=1,
                             not_before=datetime.datetime(2024, 1, 1), not_after=datetime.datetime(2025, 1, 1))
    data2, _ = build_cert("Reissued-V2-Different-Name", "P-384", key=key, serial=2,
                           not_before=datetime.datetime(2025, 6, 1), not_after=datetime.datetime(2026, 6, 1))
    add("07-R3-same-key-reissued", "R3",
        "two certificates with different subject names and different validity periods, same public key",
        [("original", data1), ("reissued", data2)])

    data3, key2 = build_cert("Same-Key-A", "P-256", serial=5)
    data4, _ = build_cert("Same-Key-B", "P-256", key=key2, serial=6,
                           not_before=datetime.datetime(2026, 1, 1), not_after=datetime.datetime(2027, 1, 1))
    add("07-R3-same-key-p256", "R3", "the same trick on P-256: same key, different everything else",
        [("a", data3), ("b", data4)])

    # Random mix, both curves, fresh with -Fresh
    certs = []
    for i in range(4):
        curve = rng.choice(["P-256", "P-384"])
        certs.append((f"r{i}", build_cert(f"Random-{args.seed}-{i}", curve, serial=100 + i)[0]))
    add(f"07-E2E-random-s{args.seed}", "E2E", f"four random certificates, both curves (seed {args.seed})", certs)

    # E2E - a reissued key mixed in with fresh ones, both curves in one input
    fresh_a, _ = build_cert("Mixed-Fresh-A", "P-256", serial=10)
    fresh_b, _ = build_cert("Mixed-Fresh-B", "P-384", serial=11)
    reissued_a, rkey = build_cert("Mixed-Reissue-V1", "P-384", serial=12)
    reissued_b, _ = build_cert("Mixed-Reissue-V2", "P-384", key=rkey, serial=13,
                                not_before=datetime.datetime(2027, 1, 1), not_after=datetime.datetime(2028, 1, 1))
    add("07-E2E-mixed-set", "E2E",
        "two fresh certificates (both curves) and two reissues of the same key, in one input",
        [("fresh-a", fresh_a), ("fresh-b", fresh_b), ("reissue-v1", reissued_a), ("reissue-v2", reissued_b)])

    cases.save()


if __name__ == "__main__":
    main()
