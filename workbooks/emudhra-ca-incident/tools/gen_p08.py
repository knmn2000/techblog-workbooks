"""Test cases for assignment 08 (check a certificate's signature).

Every certificate is built with `cryptography`'s CertificateBuilder, signed by a key this file
generates. The independent oracle is the `cryptography` library's own signature verification -
a different code path from the builder that created the bytes, and a different one again from
this workbook's hand-rolled modular-arithmetic reference: `issuer_public_key.verify(signature,
tbs_bytes, ec.ECDSA(hashes.SHA384()))`, catching InvalidSignature. `cert.tbs_certificate_bytes`
and `cert.signature` are read back from the parsed object, not computed by this file.

    python3 -P tools/gen_p08.py                                  # tests/08 (seed 1)
    python3 -P tools/gen_p08.py --seed 777 --out build/fresh/08  # what `check 08 -Fresh` runs
"""

import datetime
import random
import sys
from pathlib import Path

import cryptography
from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.x509.oid import NameOID

sys.path.insert(0, str(Path(__file__).resolve().parent))
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = f"cryptography {cryptography.__version__}: public_key.verify(signature, tbs_bytes, ec.ECDSA(hashes.SHA384())), independent of this workbook's modular-arithmetic reference"

REQUIREMENTS = [
    ("R1", "A self-signed certificate, verified against its own public key, is valid"),
    ("R2", "A certificate verified against the wrong issuer key is invalid"),
    ("R3", "A certificate whose signature bytes have been tampered with (one flipped bit in r or s) is invalid"),
    ("R4", "The TBS bytes are re-extracted correctly even when the certificate has v3 extensions (a non-trivial TBS structure)"),
    ("E2E", "A small set of certificates mixing valid, wrong-key and tampered signatures"),
]
EXPLAIN = "_lines=R1 valid=R2 invalid=R3"


def build_cert(subject_cn: str, issuer_cn: str, signing_key, subject_key=None, serial=1,
               extensions=False, not_before=datetime.datetime(2025, 1, 1), not_after=datetime.datetime(2026, 1, 1)):
    """Signs a P-384 certificate with `signing_key` (the alleged issuer's private key). If
    `subject_key` is omitted, the certificate is self-signed (subject key == signing key)."""
    subject_key = subject_key or signing_key
    builder = (x509.CertificateBuilder()
               .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)]))
               .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn)]))
               .public_key(subject_key.public_key())
               .serial_number(serial).not_valid_before(not_before).not_valid_after(not_after))
    if extensions:
        builder = builder.add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
    return builder.sign(signing_key, hashes.SHA384())


def flip_signature_bit(cert) -> bytes:
    """The certificate's DER bytes with one bit flipped inside signatureValue's content (the r,s
    bytes), leaving everything else - including the length fields - untouched."""
    data = bytearray(cert.public_bytes(Encoding.DER))
    sig = cert.signature  # the raw (r, s) DER bytes, read back from the parsed object
    at = data.rfind(bytes(sig))
    assert at != -1, "could not find the signature bytes to tamper with"
    data[at + len(sig) - 1] ^= 0x01  # flip the low bit of the signature's very last byte
    return bytes(data)


def oracle_valid(cert_bytes: bytes, issuer_public_key) -> bool:
    cert = x509.load_der_x509_certificate(cert_bytes)
    try:
        issuer_public_key.verify(cert.signature, cert.tbs_certificate_bytes, ec.ECDSA(hashes.SHA384()))
        return True
    except InvalidSignature:
        return False


def main():
    args = wbcore.parse_args("08")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, checks):
        """checks: list of (label, cert_bytes, curve, issuer_x, issuer_y, expected_valid)."""
        input_lines, expected = [], []
        for label, data, curve, x, y, valid in checks:
            c = curves.CURVES[curve]
            input_lines.append(f"cert {label} {data.hex()}")
            input_lines.append(f"issuer_pubkey {label} {curve} {x:0{c['hexlen']}x} {y:0{c['hexlen']}x}")
            expected.append(f"signature {label} {'valid' if valid else 'invalid'}")
        cases.add(case_id, req, title, input_lines, expected)

    def pubnums(key):
        n = key.public_key().public_numbers()
        return n.x, n.y

    # R1 - genuinely self-signed
    for i in range(3):
        key = ec.generate_private_key(ec.SECP384R1())
        cert = build_cert(f"Self-{i}", f"Self-{i}", key, serial=i + 1)
        x, y = pubnums(key)
        data = cert.public_bytes(Encoding.DER)
        assert oracle_valid(data, key.public_key())
        add(f"08-R1-self-signed-{i}", "R1", f"self-signed certificate #{i}, verified against its own key",
            [(f"s{i}", data, "P-384", x, y, True)])

    # R2 - wrong issuer key
    key_a = ec.generate_private_key(ec.SECP384R1())
    key_b = ec.generate_private_key(ec.SECP384R1())
    cert = build_cert("Wrong-Key-Subject", "Wrong-Key-Issuer", key_a, serial=10)
    data = cert.public_bytes(Encoding.DER)
    wx, wy = pubnums(key_b)
    assert not oracle_valid(data, key_b.public_key())
    add("08-R2-wrong-key", "R2", "a certificate checked against an unrelated public key",
        [("w1", data, "P-384", wx, wy, False)])

    # The same certificate, checked against its REAL key too, so R2's case isn't the only one
    rx, ry = pubnums(key_a)
    assert oracle_valid(data, key_a.public_key())
    add("08-R2-right-key-for-contrast", "R2", "the same certificate as 08-R2-wrong-key, checked against its real key instead",
        [("w1-real", data, "P-384", rx, ry, True)])

    # R3 - tampered signature
    for i in range(2):
        key = ec.generate_private_key(ec.SECP384R1())
        cert = build_cert(f"Tamper-{i}", f"Tamper-{i}", key, serial=20 + i)
        tampered = flip_signature_bit(cert)
        x, y = pubnums(key)
        assert not oracle_valid(tampered, key.public_key())
        add(f"08-R3-tampered-{i}", "R3", f"a self-signed certificate #{i} with one bit of its signature flipped",
            [(f"t{i}", tampered, "P-384", x, y, False)])

    # R4 - TBS re-extraction with real v3 extensions present (non-trivial TBS)
    key = ec.generate_private_key(ec.SECP384R1())
    cert = build_cert("Extensions-Present", "Extensions-Present", key, serial=30, extensions=True)
    data = cert.public_bytes(Encoding.DER)
    x, y = pubnums(key)
    assert oracle_valid(data, key.public_key())
    add("08-R4-with-extensions", "R4", "a self-signed CA certificate with a BasicConstraints extension present",
        [("ext1", data, "P-384", x, y, True)])

    intermediate_key = ec.generate_private_key(ec.SECP384R1())
    root_key = ec.generate_private_key(ec.SECP384R1())
    cert = build_cert("Intermediate", "Root", root_key, subject_key=intermediate_key, serial=31, extensions=True)
    data = cert.public_bytes(Encoding.DER)
    rx2, ry2 = pubnums(root_key)
    assert oracle_valid(data, root_key.public_key())
    add("08-R4-issuer-not-subject", "R4", "an intermediate (with extensions) signed by a different key (the root's), verified against the root's key",
        [("int1", data, "P-384", rx2, ry2, True)])

    # E2E - a mixed set: valid, wrong key, tampered, all in one input
    items = []
    for i in range(2):
        key = ec.generate_private_key(ec.SECP384R1())
        cert = build_cert(f"Mix-Valid-{i}", f"Mix-Valid-{i}", key, serial=40 + i)
        data = cert.public_bytes(Encoding.DER)
        x, y = pubnums(key)
        assert oracle_valid(data, key.public_key())
        items.append((f"valid{i}", data, "P-384", x, y, True))
    key_c = ec.generate_private_key(ec.SECP384R1())
    key_d = ec.generate_private_key(ec.SECP384R1())
    cert = build_cert("Mix-Wrong", "Mix-Wrong", key_c, serial=42)
    data = cert.public_bytes(Encoding.DER)
    x, y = pubnums(key_d)
    assert not oracle_valid(data, key_d.public_key())
    items.append(("wrong", data, "P-384", x, y, False))
    key_e = ec.generate_private_key(ec.SECP384R1())
    cert = build_cert("Mix-Tampered", "Mix-Tampered", key_e, serial=43)
    tampered = flip_signature_bit(cert)
    x, y = pubnums(key_e)
    assert not oracle_valid(tampered, key_e.public_key())
    items.append(("tampered", tampered, "P-384", x, y, False))
    add(f"08-E2E-mixed-s{args.seed}", "E2E", f"two valid, one wrong-key, one tampered, in one input (seed {args.seed})", items)

    cases.save()


if __name__ == "__main__":
    main()
