"""Test cases for assignment 18 (verify a CRL's signature).

Every CRL is DER that the `cryptography` package wrote (CertificateRevocationListBuilder), or, for
the v1 case that the builder can't write, DER from the small writer below signed with
`key.sign(tbs, ec.ECDSA(hashes.SHA384()))`. Before a case is written, the generator loads every
CRL with `x509.load_der_x509_crl` and checks two independent facts about it:

  - whether the issuer's published key verifies it: `crl.is_signature_valid(public_key)`, and
    `openssl crl -inform DER -noout -CAfile <issuer certificate>` printing `verify OK` or
    `verify failure`. The two must agree.
  - which issuer it names: the commonName of the library's `crl.issuer`.

Whether a published key is weak is known by construction: the generator derives every key from
its private value d, and assignment 13 calls a key weak when d <= 4096. Strong keys are drawn far
from both 0 and n, so no strong key is the negation of a small one either.

The verdict comes from those facts and an explicit table of (issuer state, event) to (verdict, next
state), written separately from the reference's `CrlWatch`.

    python3 -P tools/gen_p18.py                                  # tests/18 (seed 1)
    python3 -P tools/gen_p18.py --seed 777 --out build/fresh/18  # what `check 18 -Fresh` runs
"""

import datetime
import random
import shutil
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

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = (f"cryptography {cryptography.__version__}: crl.is_signature_valid(issuer_key), cross-checked with "
       "`openssl crl -CAfile`; weak keys by their known private value (d <= 4096); verdicts from the page's "
       "four rules as a state table")

WEAK_BOUND = 4096  # assignment 13's bound
N = curves.CURVES["P-384"]["n"]
MAX_CRLS = 6  # per input
MAX_STRONG_LINTS = 3  # `ok` verdicts per input: each costs a 4096-step weak-key search

REQUIREMENTS = [
    ("R1", "A CRL that the issuer's published, strong key signed is `ok`"),
    ("R2", "A CRL whose signature does not verify under the issuer's published key is `halt signature-failed`, even when that key is weak"),
    ("R3", "A CRL that verifies under a key with d <= 4096 is `halt weak-key`; d = 4097 is `ok`"),
    ("R4", "After a halt, the issuer's CRLs are `halt issuer-halted` until a `key` line gives it a different key; other issuers are unaffected"),
    ("R5", "The issuer is read right in every CRL shape: v1 without a version, extensions, GeneralizedTime, a multi-attribute name"),
    ("E2E", "Several issuers, key changes, failures and weak keys in one input"),
]
# A difference that involves `issuer-halted` is about the state (R4). Any other difference points
# to the requirement its case targets: the checker sees the words of both lines, not which is which,
# so mapping `ok` or `weak-key` would blame R1 for a skipped weak-key lint.
EXPLAIN = "_lines=R1 crl~issuer-halted=R4"

THIS_UPDATE = datetime.datetime(2026, 5, 1)
NEXT_UPDATE = datetime.datetime(2026, 5, 8)
REVOKED_AT = datetime.datetime(2026, 4, 20)


# ---- Keys ----------------------------------------------------------------------------------

class Key:
    """A P-384 key and its private value d, so the generator knows whether it is weak."""

    def __init__(self, d: int):
        assert 1 <= d < N
        self.d = d
        self.private = ec.derive_private_key(d, ec.SECP384R1())
        numbers = self.private.public_key().public_numbers()
        self.point = (numbers.x, numbers.y)

    @property
    def weak(self) -> bool:
        return self.d <= WEAK_BOUND

    def hex(self) -> str:
        return f"{self.point[0]:096x} {self.point[1]:096x}"


def strong_key(rng) -> Key:
    """A key far from 0 and from n, so neither it nor its negation is near the weak bound."""
    return Key(rng.randrange(2 ** 64, N - 2 ** 64))


# ---- CRLs -----------------------------------------------------------------------------------

def name(cn: str, extra=()) -> x509.Name:
    return x509.Name([*extra, x509.NameAttribute(NameOID.COMMON_NAME, cn)])


def build_crl(issuer: x509.Name, key: Key, serials=(), this_update=THIS_UPDATE, next_update=NEXT_UPDATE,
              extensions=False) -> bytes:
    """A v2 CRL that `key` signs with ecdsa-with-SHA384, written by the cryptography package."""
    b = x509.CertificateRevocationListBuilder().issuer_name(issuer).last_update(this_update)
    b = b.next_update(next_update)
    for serial in serials:
        entry = x509.RevokedCertificateBuilder().serial_number(serial).revocation_date(REVOKED_AT)
        if extensions:
            entry = entry.add_extension(x509.CRLReason(x509.ReasonFlags.key_compromise), critical=False)
        b = b.add_revoked_certificate(entry.build())
    if extensions:
        b = b.add_extension(x509.CRLNumber(7), critical=False)
        b = b.add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(key.private.public_key()),
                            critical=False)
    return b.sign(key.private, hashes.SHA384()).public_bytes(Encoding.DER)


def _tlv(tag: int, content: bytes) -> bytes:
    """One DER TLV, with the short length form below 128 and the long form from 128 on."""
    n = len(content)
    if n < 128:
        return bytes([tag, n]) + content
    size = (n.bit_length() + 7) // 8
    return bytes([tag, 0x80 | size]) + n.to_bytes(size, "big") + content


def _seq(*parts: bytes) -> bytes:
    return _tlv(0x30, b"".join(parts))


def _integer(v: int) -> bytes:
    return _tlv(0x02, v.to_bytes(v.bit_length() // 8 + 1, "big"))


ECDSA_WITH_SHA384 = _seq(_tlv(0x06, bytes.fromhex("2a8648ce3d040303")))  # 1.2.840.10045.4.3.3


def _utc(text: str) -> bytes:
    return _tlv(0x17, text.encode())


def v1_crl(issuer_cn: str, key: Key, serials) -> bytes:
    """A v1 CRL (no version field), which the builder never writes. The library parses and checks
    what this writes before any case uses it."""
    issuer = _seq(_tlv(0x31, _seq(_tlv(0x06, bytes.fromhex("550403")), _tlv(0x0C, issuer_cn.encode()))))
    revoked = [_seq(*[_seq(_integer(s), _utc("260420000000Z")) for s in serials])] if serials else []
    tbs = _seq(ECDSA_WITH_SHA384, issuer, _utc("260501000000Z"), _utc("260508000000Z"), *revoked)
    signature = key.private.sign(tbs, ec.ECDSA(hashes.SHA384()))
    return _seq(tbs, ECDSA_WITH_SHA384, _tlv(0x03, b"\x00" + signature))


def _signature_at(data: bytes) -> int:
    sig = x509.load_der_x509_crl(data).signature  # the (r, s) DER, read back by the library
    at = data.rfind(sig)
    assert at != -1 and at + len(sig) == len(data)
    return at


def flip_r(data: bytes) -> bytes:
    """One bit flipped in r (the low bit of its last byte); every length stays the same."""
    at = _signature_at(data)
    assert data[at] == 0x30 and data[at + 1] < 0x80 and data[at + 2] == 0x02
    r_len = data[at + 3]
    out = bytearray(data)
    out[at + 4 + r_len - 1] ^= 0x01
    return bytes(out)


def flip_s(data: bytes) -> bytes:
    """One bit flipped in s (the low bit of the CRL's last byte)."""
    _signature_at(data)
    out = bytearray(data)
    out[-1] ^= 0x01
    return bytes(out)


def replace_once(data: bytes, old: bytes, new: bytes) -> bytes:
    """`data` with the one occurrence of `old` replaced by `new` of the same length."""
    assert len(old) == len(new) and data.count(old) == 1
    return data.replace(old, new)


# ---- Oracles --------------------------------------------------------------------------------

def openssl_verifies(data: bytes, issuer: x509.Name, key: Key) -> bool:
    """Asks `openssl crl -CAfile` whether the key, in a CA certificate named as the issuer, verifies the CRL."""
    ca = (x509.CertificateBuilder().subject_name(issuer).issuer_name(issuer)
          .public_key(key.private.public_key()).serial_number(1)
          .not_valid_before(datetime.datetime(2026, 1, 1)).not_valid_after(datetime.datetime(2027, 1, 1))
          .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
          .sign(key.private, hashes.SHA384()))
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "ca.pem").write_bytes(ca.public_bytes(Encoding.PEM))
        (Path(tmp) / "crl.der").write_bytes(data)
        proc = subprocess.run(["openssl", "crl", "-inform", "DER", "-in", str(Path(tmp) / "crl.der"), "-noout",
                               "-CAfile", str(Path(tmp) / "ca.pem")], capture_output=True, text=True)
    said = (proc.stdout + proc.stderr)
    assert ("verify OK" in said) != ("verify failure" in said), f"unexpected openssl output: {said!r}"
    return "verify OK" in said


def facts(data: bytes, published: Key) -> tuple[str, bool]:
    """(issuer commonName, whether the published key verifies the CRL), from the library and openssl."""
    crl = x509.load_der_x509_crl(data)
    cn = crl.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    lib = crl.is_signature_valid(published.private.public_key())
    assert lib == openssl_verifies(data, crl.issuer, published), "the library and openssl disagree"
    return cn, lib


# (state, event) -> (verdict, next state). A key event is "new-key" (a different key, or the
# issuer's first) or "same-key"; a CRL event is what the oracles say about it.
TABLE = {
    ("released", "new-key"): (None, "released"),
    ("released", "same-key"): (None, "released"),
    ("halted", "new-key"): (None, "released"),
    ("halted", "same-key"): (None, "halted"),
    ("released", "fails"): ("halt signature-failed", "halted"),
    ("released", "verifies-weak"): ("halt weak-key", "halted"),
    ("released", "verifies-strong"): ("ok", "released"),
    ("halted", "fails"): ("halt issuer-halted", "halted"),
    ("halted", "verifies-weak"): ("halt issuer-halted", "halted"),
    ("halted", "verifies-strong"): ("halt issuer-halted", "halted"),
}


def expected_lines(events) -> list:
    """Runs the events through TABLE. Events: ("key", issuer cn, Key) or ("crl", label, issuer cn, der)."""
    state, published, out = {}, {}, []
    for event in events:
        if event[0] == "key":
            _, cn, key = event
            kind = "same-key" if cn in published and published[cn].point == key.point else "new-key"
            published[cn] = key
            _, state[cn] = TABLE[(state.get(cn, "released"), kind)]
        else:
            _, label, cn, data = event
            read_cn, verifies = facts(data, published[cn])
            assert read_cn == cn, f"the library reads issuer {read_cn!r}, the case says {cn!r}"
            kind = "fails" if not verifies else ("verifies-weak" if published[cn].weak else "verifies-strong")
            verdict, state[cn] = TABLE[(state.get(cn, "released"), kind)]
            out.append(f"crl {label} {verdict}")
    return out


def input_lines(events) -> list:
    return [f"key {e[1]} P-384 {e[2].hex()}" if e[0] == "key" else f"crl {e[1]} {e[3].hex()}" for e in events]


# ---- Cases ----------------------------------------------------------------------------------

def main():
    args = wbcore.parse_args("18")
    curves.verify()
    if shutil.which("openssl") is None:
        sys.exit("gen_p18 needs the openssl command for its second oracle")
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, events, expect=None):
        assert sum(e[0] == "crl" for e in events) <= MAX_CRLS
        expected = expected_lines(events)
        assert sum(line.endswith(" ok") for line in expected) <= MAX_STRONG_LINTS
        if expect is not None:  # the verdicts the page's text promises for this case
            assert expected == [f"crl {label} {v}" for label, v in expect], (case_id, expected)
        cases.add(case_id, req, title, input_lines(events), expected)

    A, B = "Synthetic-CA-A", "Synthetic-CA-B"
    ka, kb, other = strong_key(rng), strong_key(rng), strong_key(rng)
    weak4 = Key(4)
    na, nb = name(A), name(B)

    # R1 - signed by the published, strong key.
    add("18-R1-v2-no-entries", "R1", "a v2 CRL with no revoked entries, signed by the published key",
        [("key", A, ka), ("crl", "r1", A, build_crl(na, ka))], [("r1", "ok")])
    add("18-R1-v2-two-entries", "R1", "a v2 CRL with 2 revoked serials, signed by the published key",
        [("key", A, ka), ("crl", "r2", A, build_crl(na, ka, serials=(0x1001, 0x1002)))], [("r2", "ok")])
    mid = build_crl(na, ka, serials=range(0x2001, 0x2004))
    assert mid[1] == 0x82 and mid[4:6] == b"\x30\x81", "tbsCertList's length should take DER's one-byte long form (128 to 255)"
    add("18-R1-v2-one-byte-long-form", "R1", "a v2 CRL with 3 revoked serials (tbsCertList length 128 to 255)",
        [("key", A, ka), ("crl", "r3", A, mid)], [("r3", "ok")])
    big = [rng.randrange(1, 2 ** 64) for _ in range(300)]
    add("18-R1-v2-300-entries", "R1", "a v2 CRL with 300 revoked serials (tbsCertList over 6,000 bytes)",
        [("key", A, ka), ("crl", "r300", A, build_crl(na, ka, serials=big))], [("r300", "ok")])
    add("18-R1-two-good-lists", "R1", "two CRLs of one issuer, both signed by the published key",
        [("key", A, ka), ("crl", "w1", A, build_crl(na, ka)),
         ("crl", "w2", A, build_crl(na, ka, serials=(77,), this_update=datetime.datetime(2026, 5, 8),
                                     next_update=datetime.datetime(2026, 5, 15)))],
        [("w1", "ok"), ("w2", "ok")])

    # R2 - the signature does not verify under the published key.
    add("18-R2-wrong-key", "R2", "a CRL signed by a strong key other than the published one",
        [("key", A, ka), ("crl", "x1", A, build_crl(na, other))], [("x1", "halt signature-failed")])
    good = build_crl(na, ka, serials=(0x0ABCDEF1, 0x0ABCDEF2))
    add("18-R2-flip-r", "R2", "a CRL signed by the published key, with one bit of r flipped",
        [("key", A, ka), ("crl", "x2", A, flip_r(good))], [("x2", "halt signature-failed")])
    add("18-R2-flip-s", "R2", "a CRL signed by the published key, with one bit of s flipped",
        [("key", A, ka), ("crl", "x3", A, flip_s(good))], [("x3", "halt signature-failed")])
    changed = replace_once(good, bytes.fromhex("02040abcdef2"), bytes.fromhex("02040abcdef3"))
    add("18-R2-changed-serial", "R2", "a CRL whose second revoked serial was changed after signing",
        [("key", A, ka), ("crl", "x4", A, changed)], [("x4", "halt signature-failed")])
    changed = replace_once(good, b"260501000000Z", b"260502000000Z")
    add("18-R2-changed-this-update", "R2", "a CRL whose thisUpdate day was changed after signing",
        [("key", A, ka), ("crl", "x5", A, changed)], [("x5", "halt signature-failed")])
    add("18-R2-weak-published-strong-signer", "R2",
        "the published key is weak (d = 4) and a strong key signed the CRL: the signature check comes first",
        [("key", B, weak4), ("crl", "x6", B, build_crl(nb, other))], [("x6", "halt signature-failed")])

    # R3 - the signature verifies, under a weak key.
    for d in (4, 1, 237, WEAK_BOUND):
        weak = Key(d)
        add(f"18-R3-weak-d{d}", "R3", f"a CRL signed by the published key, whose private value is d = {d}",
            [("key", B, weak), ("crl", f"d{d}", B, build_crl(nb, weak))], [(f"d{d}", "halt weak-key")])
    past = Key(WEAK_BOUND + 1)
    add(f"18-R3-not-weak-d{WEAK_BOUND + 1}", "R3", f"a CRL signed by the published key with d = {WEAK_BOUND + 1}, one past the bound",
        [("key", B, past), ("crl", "e1", B, build_crl(nb, past))], [("e1", "ok")])

    # R4 - the state each issuer keeps.
    first = build_crl(na, ka)
    add("18-R4-fail-then-replay", "R4", "a good CRL, the same CRL with one bit of s flipped, then the good CRL again",
        [("key", A, ka), ("crl", "a1", A, first), ("crl", "a2", A, flip_s(first)), ("crl", "a3", A, first)],
        [("a1", "ok"), ("a2", "halt signature-failed"), ("a3", "halt issuer-halted")])
    add("18-R4-resign-with-weak-key", "R4",
        "published key d = 4: a CRL signed by another key fails, then one signed by the published weak key",
        [("key", B, weak4), ("crl", "c1", B, build_crl(nb, other)), ("crl", "c2", B, build_crl(nb, weak4))],
        [("c1", "halt signature-failed"), ("c2", "halt issuer-halted")])
    add("18-R4-resign-with-published-key", "R4",
        "a CRL signed by another key fails, then one signed by the published strong key",
        [("key", A, ka), ("crl", "p1", A, build_crl(na, other)), ("crl", "p2", A, build_crl(na, ka))],
        [("p1", "halt signature-failed"), ("p2", "halt issuer-halted")])
    add("18-R4-new-key-releases", "R4",
        "a CRL fails, then a key line publishes a different key, and a CRL signed by that key follows",
        [("key", A, ka), ("crl", "k1", A, build_crl(na, other)), ("key", A, other),
         ("crl", "k2", A, build_crl(na, other))],
        [("k1", "halt signature-failed"), ("k2", "ok")])
    add("18-R4-same-key-keeps-halt", "R4",
        "a CRL fails, then a key line repeats the same published key, and a correctly signed CRL follows",
        [("key", A, ka), ("crl", "s1", A, build_crl(na, other)), ("key", A, ka), ("crl", "s2", A, build_crl(na, ka))],
        [("s1", "halt signature-failed"), ("s2", "halt issuer-halted")])
    add("18-R4-two-issuers", "R4",
        "two issuers' keys, then CRLs of both: a failure halts only its own issuer",
        [("key", A, ka), ("key", B, kb), ("crl", "i1", A, build_crl(na, ka)), ("crl", "i2", B, build_crl(nb, other)),
         ("crl", "i3", A, build_crl(na, ka)), ("crl", "i4", B, build_crl(nb, kb))],
        [("i1", "ok"), ("i2", "halt signature-failed"), ("i3", "ok"), ("i4", "halt issuer-halted")])
    add("18-R4-weak-halt-then-new-key", "R4",
        "a weak published key halts the issuer, a second CRL is refused, then a new strong key releases it",
        [("key", B, weak4), ("crl", "h1", B, build_crl(nb, weak4)), ("crl", "h2", B, build_crl(nb, weak4)),
         ("crl", "h3", B, build_crl(nb, other)), ("key", B, kb), ("crl", "h4", B, build_crl(nb, kb))],
        [("h1", "halt weak-key"), ("h2", "halt issuer-halted"), ("h3", "halt issuer-halted"), ("h4", "ok")])

    # R5 - the issuer, wherever the CRL's shape puts it.
    add("18-R5-v1-no-version", "R5", "a v1 CRL (no version field, so the issuer is the second field), then a v2 CRL of another issuer",
        [("key", A, ka), ("key", B, kb), ("crl", "v1", A, v1_crl(A, ka, [11, 12])), ("crl", "v2", B, build_crl(nb, kb))],
        [("v1", "ok"), ("v2", "ok")])
    add("18-R5-extensions", "R5", "a v2 CRL with crlExtensions (CRL number, authority key id) and entry extensions",
        [("key", A, ka), ("crl", "ext", A, build_crl(na, ka, serials=(5, 6), extensions=True))], [("ext", "ok")])
    late = datetime.datetime(2050, 6, 1)
    add("18-R5-generalized-time", "R5", "a v2 CRL whose thisUpdate and nextUpdate are GeneralizedTime (year 2050)",
        [("key", B, kb), ("crl", "gt", B, build_crl(nb, kb, serials=(9,), this_update=late, next_update=late + datetime.timedelta(days=7)))],
        [("gt", "ok")])
    long_cn = "Synthetic-Issuing-CA-For-Revocation-G3C"
    full = name(long_cn, [x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
                          x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Synthetic Trust Services")])
    add("18-R5-multi-attribute-name", "R5",
        "an issuer Name with country and organization before a 39-character commonName, next to issuer A",
        [("key", A, ka), ("key", long_cn, kb), ("crl", "m1", long_cn, build_crl(full, kb)),
         ("crl", "m2", A, build_crl(na, kb))],
        [("m1", "ok"), ("m2", "halt signature-failed")])

    # E2E - a fixed mix, and a random one that changes with the seed.
    add("18-E2E-mixed", "E2E", "two issuers, a weak key, a failure, a replay and a key change in one input",
        [("key", A, ka), ("key", B, Key(56)), ("crl", "m1", A, first), ("crl", "m2", B, build_crl(nb, Key(56))),
         ("crl", "m3", A, build_crl(na, kb)), ("crl", "m4", A, first), ("key", A, other),
         ("crl", "m5", A, build_crl(na, other)), ("crl", "m6", B, build_crl(nb, Key(56)))],
        [("m1", "ok"), ("m2", "halt weak-key"), ("m3", "halt signature-failed"), ("m4", "halt issuer-halted"),
         ("m5", "ok"), ("m6", "halt issuer-halted")])
    add(f"18-E2E-random-s{args.seed}", "E2E", f"a random run of key and CRL lines for two issuers (seed {args.seed})",
        random_events(rng, A, B))

    cases.save()


def random_events(rng, a: str, b: str) -> list:
    """Two issuers, up to 4 key lines and 6 CRLs, signed by the published key, another key, or
    tampered. At most MAX_STRONG_LINTS CRLs reach the weak-key lint under a strong key."""
    weak = Key(rng.choice([4, 56, 66, 115, 155, 156, 230, 237]))
    pool = [strong_key(rng), strong_key(rng), strong_key(rng)]
    published = {a: rng.choice([pool[0], weak]), b: pool[1]}
    events = [("key", a, published[a]), ("key", b, published[b])]
    keys, labels = 2, iter(f"q{i}" for i in range(1, 99))
    while sum(e[0] == "crl" for e in events) < MAX_CRLS:
        cn = rng.choice([a, b])
        if keys < 4 and rng.random() < 0.25:
            published[cn] = rng.choice([published[cn], *pool])  # sometimes the same key again
            events.append(("key", cn, published[cn]))
            keys += 1
            continue
        roll = rng.random()
        signer = published[cn] if roll < 0.6 else rng.choice([k for k in pool if k is not published[cn]])
        data = build_crl(name(cn), signer, serials=[rng.randrange(1, 2 ** 32) for _ in range(rng.randrange(4))])
        if roll < 0.15:
            data = flip_s(data)
        events.append(("crl", next(labels), cn, data))
    expected = expected_lines(events)
    if sum(line.endswith(" ok") for line in expected) > MAX_STRONG_LINTS:
        return random_events(rng, a, b)  # draw again: too many strong-key lints for the time limit
    return events


if __name__ == "__main__":
    main()
