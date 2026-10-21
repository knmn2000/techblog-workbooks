"""Test cases for checkpoint 06 (read a certificate).

Every certificate is built with `cryptography`'s CertificateBuilder from values this file
chooses itself (the common name strings, the validity datetimes, the key pair, whether it's a
CA and its path length) - those chosen values ARE the expected output, no decoding needed for
them. What's checked independently is that the bytes `cryptography` produced really round-trip:
this file re-parses every certificate with `cryptography.x509.load_der_x509_certificate` (a
different code path through the same library - building and parsing are not the same logic) and
asserts every field matches what was intended, before the case is written. The two UTCTime/
GeneralizedTime strings are read back with `openssl asn1parse`, independent of both.

    python3 -P tools/gen_p06.py                                  # tests/06 (seed 1)
    python3 -P tools/gen_p06.py --seed 777 --out build/fresh/06  # what `check 06 -Fresh` runs
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

LIB = f"cryptography {cryptography.__version__} (OpenSSL): fields are read back from the built certificate with a separate parse call, and validity strings with openssl asn1parse"

REQUIREMENTS = [
    ("R1", "A non-CA leaf certificate: subject, issuer, validity and the public key all read correctly"),
    ("R2", "A CA certificate (BasicConstraints CA:TRUE) with no path length constraint"),
    ("R3", "A CA certificate with an explicit path length constraint (0, 1, or a larger number)"),
    ("R4", "Both curves: P-256 and P-384 public keys read correctly"),
    ("R5", "Subject and issuer can be the same (self-signed) or different, independent of CA status"),
    ("R6", "A certificate with no BasicConstraints extension at all defaults to CA:false, no path length"),
    ("E2E", "A realistic small set of certificates mixing every rule above in one input"),
]
EXPLAIN = "_lines=R1"

LIB_EC = {"P-256": ec.SECP256R1, "P-384": ec.SECP384R1}


def make_cert(subject_cn: str, issuer_cn: str, curve: str, not_before: datetime.datetime,
              not_after: datetime.datetime, ca=None, pathlen=None, serial=1, other_extension=False):
    """Builds one DER certificate and returns (hex, expected fields), after checking the bytes
    really hold what was asked for (a separate `cryptography` parse, and openssl for the two
    time strings)."""
    key = ec.generate_private_key(LIB_EC[curve]())
    pubnums = key.public_key().public_numbers()
    builder = (x509.CertificateBuilder()
               .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject_cn)]))
               .issuer_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, issuer_cn)]))
               .public_key(key.public_key())
               .serial_number(serial)
               .not_valid_before(not_before)
               .not_valid_after(not_after))
    if ca is not None:
        builder = builder.add_extension(x509.BasicConstraints(ca=ca, path_length=pathlen), critical=True)
    if other_extension:
        # Some other extension present, but no BasicConstraints among them: RFC 5280 4.2.1.9's
        # "absent means not a CA" default must still apply, separately from the case where the
        # certificate has no extensions at all.
        builder = builder.add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
    cert = builder.sign(key, hashes.SHA384() if curve == "P-384" else hashes.SHA256())
    data = cert.public_bytes(Encoding.DER)

    # Independent check: parse the bytes back (a different `cryptography` code path than the
    # builder that just wrote them) and confirm every field matches what was asked for.
    parsed = x509.load_der_x509_certificate(data)
    assert parsed.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == subject_cn
    assert parsed.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value == issuer_cn
    assert parsed.not_valid_before == not_before
    assert parsed.not_valid_after == not_after
    pn = parsed.public_key().public_numbers()
    assert (pn.x, pn.y) == (pubnums.x, pubnums.y)
    try:
        bc = parsed.extensions.get_extension_for_class(x509.BasicConstraints).value
        got_ca, got_pathlen = bc.ca, bc.path_length
    except x509.ExtensionNotFound:
        got_ca, got_pathlen = False, None
    want_ca = bool(ca)
    assert got_ca == want_ca and got_pathlen == pathlen

    not_before_str, not_after_str = asn1parse_times(data)

    c = curves.CURVES[curve]
    lines = [
        f"cert ID {subject_cn} {issuer_cn}",
        f"validity {not_before_str} {not_after_str}",
        f"key {curve} {pubnums.x:0{c['hexlen']}x} {pubnums.y:0{c['hexlen']}x}",
        f"ca {'true' if want_ca else 'false'} {'none' if pathlen is None else pathlen}",
    ]
    return data.hex(), lines


TIME_RE = re.compile(r"prim: (UTCTIME|GENERALIZEDTIME)\s*:(\S+)")


def asn1parse_times(data: bytes):
    """The two Validity time strings, read back by OpenSSL's own ASN.1 decoder (independent of
    this workbook's DER reader), in the order they appear (notBefore, then notAfter)."""
    with tempfile.NamedTemporaryFile(suffix=".der") as f:
        f.write(data)
        f.flush()
        proc = subprocess.run(["openssl", "asn1parse", "-inform", "DER", "-in", f.name],
                               capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    times = [m.group(2) for m in TIME_RE.finditer(proc.stdout)]
    assert len(times) == 2, f"expected exactly 2 time fields, found {len(times)}"
    return times


def main():
    args = wbcore.parse_args("06")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records cert=id,subject,issuer validity=notBefore,notAfter key=curve,pubx,puby ca=ca,pathlen",
                         REQUIREMENTS, EXPLAIN, LIB)

    before = datetime.datetime(2025, 1, 1, 0, 0, 0)
    after = datetime.datetime(2026, 1, 1, 0, 0, 0)

    def add(case_id, req, title, certs):
        """certs: list of (label, kwargs for make_cert)."""
        input_lines, expected = [], []
        for label, kwargs in certs:
            hex_str, lines = make_cert(**kwargs)
            input_lines.append(f"cert {label} {hex_str}")
            expected += [lines[0].replace("ID", label)] + lines[1:]
        cases.add(case_id, req, title, input_lines, expected)

    # R1 - a basic non-CA leaf
    add("06-R1-leaf-basic", "R1", "a plain leaf certificate, not a CA, P-256", [
        ("leaf", dict(subject_cn="Example-Leaf", issuer_cn="Example-Issuer", curve="P-256",
                       not_before=before, not_after=after))])
    add("06-R1-leaf-p384", "R1", "a plain leaf certificate, not a CA, P-384", [
        ("leaf", dict(subject_cn="Example-Leaf-2", issuer_cn="Example-Issuer-2", curve="P-384",
                       not_before=before, not_after=after))])
    add("06-R1-leaf-explicit-ca-false", "R1", "a leaf with BasicConstraints present but CA:FALSE",
        [("leaf", dict(subject_cn="Example-Leaf-3", issuer_cn="Example-Issuer-3", curve="P-256",
                        not_before=before, not_after=after, ca=False))])

    # R2 - CA, no path length
    add("06-R2-ca-no-pathlen", "R2", "a CA certificate with no path length constraint", [
        ("ca", dict(subject_cn="Example-CA", issuer_cn="Example-Root", curve="P-384",
                     not_before=before, not_after=after, ca=True))])
    add("06-R2-ca-no-pathlen-p256", "R2", "a CA certificate with no path length constraint, P-256", [
        ("ca", dict(subject_cn="Example-CA-2", issuer_cn="Example-Root-2", curve="P-256",
                     not_before=before, not_after=after, ca=True))])

    # R3 - CA, explicit path length (0, 1, larger)
    for n in (0, 1, 5):
        add(f"06-R3-pathlen-{n}", "R3", f"a CA certificate with path length {n}", [
            ("ca", dict(subject_cn=f"Example-CA-Pathlen-{n}", issuer_cn="Example-Root", curve="P-384",
                         not_before=before, not_after=after, ca=True, pathlen=n))])

    # R4 - both curves (also covered incidentally above, but dedicated cases make it explicit)
    add("06-R4-p256", "R4", "a P-256 public key reads correctly", [
        ("k", dict(subject_cn="Curve-Check-256", issuer_cn="Curve-Check-256", curve="P-256",
                    not_before=before, not_after=after))])
    add("06-R4-p384", "R4", "a P-384 public key reads correctly", [
        ("k", dict(subject_cn="Curve-Check-384", issuer_cn="Curve-Check-384", curve="P-384",
                    not_before=before, not_after=after))])

    # R5 - same CN (self-signed) vs different CN
    add("06-R5-self-signed", "R5", "subject and issuer are the same common name", [
        ("self", dict(subject_cn="Same-Name", issuer_cn="Same-Name", curve="P-384",
                       not_before=before, not_after=after))])
    add("06-R5-different-names", "R5", "subject and issuer are different common names", [
        ("diff", dict(subject_cn="Child-Name", issuer_cn="Parent-Name", curve="P-384",
                       not_before=before, not_after=after))])

    # R6 - BasicConstraints absent entirely
    add("06-R6-no-basic-constraints", "R6", "no BasicConstraints extension at all: defaults to CA:false, no path length", [
        ("plain", dict(subject_cn="No-Extensions", issuer_cn="No-Extensions-Issuer", curve="P-256",
                        not_before=before, not_after=after))])
    add("06-R6-no-basic-constraints-p384", "R6", "no BasicConstraints extension at all, P-384", [
        ("plain", dict(subject_cn="No-Extensions-2", issuer_cn="No-Extensions-Issuer-2", curve="P-384",
                        not_before=before, not_after=after))])
    add("06-R6-other-extension-no-basic-constraints", "R6",
        "a different extension is present (SubjectKeyIdentifier), but BasicConstraints is not - still CA:false", [
        ("other", dict(subject_cn="Other-Ext-Only", issuer_cn="Other-Ext-Issuer", curve="P-256",
                        not_before=before, not_after=after, other_extension=True))])

    # Random mix: validity dates vary, CA/pathlen combinations vary
    def random_cert(i, seed_tag):
        curve = rng.choice(["P-256", "P-384"])
        yb = rng.randint(2020, 2030)
        nb = datetime.datetime(yb, rng.randint(1, 12), rng.randint(1, 28), rng.randint(0, 23), rng.randint(0, 59), rng.randint(0, 59))
        na = nb + datetime.timedelta(days=rng.randint(30, 3650))
        choice = rng.choice(["leaf", "ca-nolen", "ca-len"])
        kwargs = dict(subject_cn=f"Random-{seed_tag}-{i}", issuer_cn=f"Random-Issuer-{seed_tag}-{i}",
                       curve=curve, not_before=nb, not_after=na)
        if choice == "ca-nolen":
            kwargs.update(ca=True)
        elif choice == "ca-len":
            kwargs.update(ca=True, pathlen=rng.randint(0, 4))
        return f"r{i}", kwargs

    items = [random_cert(i, args.seed) for i in range(5)]
    add(f"06-E2E-random-mix-s{args.seed}", "E2E", f"five random certificates mixing curves, CA status and path lengths (seed {args.seed})", items)

    # E2E - a small realistic set: root, intermediate, leaf (shape of what checkpoint 09 chains)
    add("06-E2E-chain-shaped", "E2E", "a root (CA, no pathlen), an intermediate (CA, pathlen 0) and a leaf (not a CA), as a real chain would look", [
        ("root", dict(subject_cn="Workbook-Root", issuer_cn="Workbook-Root", curve="P-384",
                       not_before=before, not_after=after, ca=True)),
        ("intermediate", dict(subject_cn="Workbook-Intermediate", issuer_cn="Workbook-Root", curve="P-384",
                               not_before=before, not_after=after, ca=True, pathlen=0)),
        ("leaf", dict(subject_cn="Workbook-Leaf", issuer_cn="Workbook-Intermediate", curve="P-384",
                       not_before=before, not_after=after)),
    ])

    cases.save()


if __name__ == "__main__":
    main()
