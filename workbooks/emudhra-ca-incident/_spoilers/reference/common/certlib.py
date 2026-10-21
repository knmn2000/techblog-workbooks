"""Hand-written X.509 certificate reading and ECDSA verification, built on common/der.py.
Shared by the reference solutions for checkpoints 06-09. SPOILERS: try the checkpoints yourself
first.

No `cryptography.x509` parsing and no library ECDSA verification here: every field is read with
common/der.py's TLV walker, and signatures are checked with plain modular arithmetic (the same
point-addition formulas checkpoint 10 uses, run the other direction: multiply instead of search).
The curve constants (p, n, Gx, Gy) are reused from tools/curves.py rather than retyped.
"""

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

from . import der

# tools/curves.py holds the OpenSSL-verified curve constants; reuse its numbers instead of
# retyping them (the generators already prove them correct via curves.verify()).
_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_ROOT / "tools"))
import curves as _curves  # noqa: E402

CURVES = {name: {"p": c["p"], "n": c["n"], "gx": c["gx"], "gy": c["gy"]} for name, c in _curves.CURVES.items()}

ID_EC_PUBLIC_KEY = "1.2.840.10045.2.1"
CURVE_OIDS = {"1.2.840.10045.3.1.7": "P-256", "1.3.132.0.34": "P-384"}
COMMON_NAME_OID = "2.5.4.3"
BASIC_CONSTRAINTS_OID = "2.5.29.19"
ECDSA_SHA384_OID = "1.2.840.10045.4.3.3"


# ---- Reading one field at a time (each takes the relevant DER node) --------------------------

def read_name_cn(name_node: der.Node):
    """Name ::= SEQUENCE OF RelativeDistinguishedName (SET OF {type, value}). Returns the
    commonName attribute's value as text, or None if the name has no commonName."""
    for rdn in name_node.children:                 # RelativeDistinguishedName: SET OF ...
        for atv in rdn.children:                    # AttributeTypeAndValue: SEQUENCE { type, value }
            attr_type, value = atv.children
            if der.decode_oid(attr_type.content) == COMMON_NAME_OID:
                return value.content.decode("utf-8")
    return None


def read_validity(validity_node: der.Node):
    """Validity ::= SEQUENCE { notBefore Time, notAfter Time }. Time is UTCTime or
    GeneralizedTime; both are printed here exactly as they appear (this isn't a date checkpoint)."""
    not_before, not_after = validity_node.children
    return not_before.content.decode("ascii"), not_after.content.decode("ascii")


def read_spki(spki_node: der.Node):
    """SubjectPublicKeyInfo ::= SEQUENCE { algorithm AlgorithmIdentifier, subjectPublicKey BIT
    STRING }. Returns (curve name, x, y) for an uncompressed EC point (0x04 || x || y)."""
    algorithm, public_key_bits = spki_node.children
    alg_oid_node, curve_oid_node = algorithm.children
    if der.decode_oid(alg_oid_node.content) != ID_EC_PUBLIC_KEY:
        raise ValueError("subjectPublicKeyInfo algorithm is not id-ecPublicKey")
    curve_oid = der.decode_oid(curve_oid_node.content)
    if curve_oid not in CURVE_OIDS:
        raise ValueError(f"unrecognised curve OID {curve_oid}")
    curve = CURVE_OIDS[curve_oid]
    _unused, point = der.decode_bit_string(public_key_bits.content)
    if not point or point[0] != 0x04:
        raise ValueError("expected an uncompressed EC point (0x04 || x || y)")
    coord_len = (len(point) - 1) // 2
    x = int.from_bytes(point[1:1 + coord_len], "big")
    y = int.from_bytes(point[1 + coord_len:], "big")
    return curve, x, y


def find_spki(cert_bytes: bytes) -> der.Node:
    """The raw subjectPublicKeyInfo node of a certificate, untouched (checkpoint 07 hashes its
    exact original bytes - the whole nested SEQUENCE, not just the key bytes inside it)."""
    top = der.parse_all(cert_bytes)
    tbs = top[0].children[0]
    children = tbs.children
    i = 1 if children and children[0].cls == "context" and children[0].tag == 0 else 0
    return children[i + 5]  # serialNumber, signature, issuer, validity, subject, then spki


def read_basic_constraints(extensions_wrapper: der.Node):
    """extensions_wrapper is the [3] EXPLICIT context node wrapping `Extensions ::= SEQUENCE OF
    Extension`. Returns (ca, pathlen). Extension ::= SEQUENCE { extnID, critical BOOLEAN DEFAULT
    FALSE OPTIONAL, extnValue OCTET STRING }, so extnValue is always the extension's last field."""
    extensions_seq = extensions_wrapper.children[0]
    for extension in extensions_seq.children:
        extn_id = der.decode_oid(extension.children[0].content)
        if extn_id != BASIC_CONSTRAINTS_OID:
            continue
        extn_value = extension.children[-1]          # OCTET STRING: itself DER-encoded again
        bc_seq = der.parse_all(extn_value.content)[0]  # BasicConstraints ::= SEQUENCE { cA, pathLen }
        ca, idx = False, 0
        if bc_seq.children and bc_seq.children[0].tag == der.BOOLEAN:
            ca = bc_seq.children[0].content[0] != 0
            idx = 1
        pathlen = der.decode_integer(bc_seq.children[idx].content) if len(bc_seq.children) > idx else None
        return ca, pathlen
    return False, None  # BasicConstraints absent: RFC 5280 4.2.1.9 default is "not a CA"


# ---- A whole certificate -----------------------------------------------------------------

@dataclass
class Certificate:
    tbs_bytes: bytes          # the exact original bytes of tbsCertificate, for re-hashing
    serial: int
    issuer_cn: str
    subject_cn: str
    not_before: str
    not_after: str
    curve: str
    pubx: int
    puby: int
    ca: bool
    pathlen: object           # int, or None if there is no path length constraint
    sig_alg_oid: str
    sig_r: int
    sig_s: int


def parse_certificate(cert_bytes: bytes) -> Certificate:
    """Certificate ::= SEQUENCE { tbsCertificate, signatureAlgorithm, signatureValue }."""
    top = der.parse_all(cert_bytes)
    if len(top) != 1 or top[0].tag != der.SEQUENCE or not top[0].constructed:
        raise ValueError("a certificate is exactly one top-level SEQUENCE")
    cert = top[0]
    if len(cert.children) != 3:
        raise ValueError("a Certificate has exactly 3 fields: tbsCertificate, "
                          "signatureAlgorithm, signatureValue")
    tbs_node, sig_alg_node, sig_value_node = cert.children
    tbs_bytes = cert_bytes[tbs_node.start: tbs_node.start + tbs_node.total_len]

    children = tbs_node.children
    i = 0
    if children and children[i].cls == "context" and children[i].tag == 0:
        i += 1  # version [0] EXPLICIT INTEGER; every certificate here is v3, so its value is fixed
    serial = der.decode_integer(children[i].content); i += 1
    i += 1  # signature: AlgorithmIdentifier, repeating the outer signatureAlgorithm; not needed again
    issuer_cn = read_name_cn(children[i]); i += 1
    not_before, not_after = read_validity(children[i]); i += 1
    subject_cn = read_name_cn(children[i]); i += 1
    curve, pubx, puby = read_spki(children[i]); i += 1
    ca, pathlen = False, None
    if i < len(children) and children[i].cls == "context" and children[i].tag == 3:
        ca, pathlen = read_basic_constraints(children[i])

    sig_alg_oid = der.decode_oid(sig_alg_node.children[0].content)
    _unused, sig_der_bytes = der.decode_bit_string(sig_value_node.content)
    sig_seq = der.parse_all(sig_der_bytes)[0]          # ECDSA-Sig-Value ::= SEQUENCE { r, s }
    sig_r = der.decode_integer(sig_seq.children[0].content)
    sig_s = der.decode_integer(sig_seq.children[1].content)

    return Certificate(tbs_bytes, serial, issuer_cn, subject_cn, not_before, not_after,
                        curve, pubx, puby, ca, pathlen, sig_alg_oid, sig_r, sig_s)


# ---- Elliptic-curve point arithmetic and ECDSA verification (hand modular arithmetic) --------

def point_add(p: int, a: int, point, other):
    """Affine point addition on y^2 = x^3 + a*x + b (mod p). Either point may be None (the
    point at infinity, the addition identity)."""
    if point is None:
        return other
    if other is None:
        return point
    x1, y1 = point
    x2, y2 = other
    if x1 == x2:
        if (y1 + y2) % p == 0:
            return None  # point and its negation: the sum is the point at infinity
        slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p  # tangent slope (doubling)
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, p) % p          # chord slope
    x3 = (slope * slope - x1 - x2) % p
    y3 = (slope * (x1 - x3) - y1) % p
    return x3, y3


def scalar_mult(p: int, a: int, n: int, k: int, point):
    """k * point, by double-and-add. point may be None (gives None back)."""
    k %= n
    if k == 0 or point is None:
        return None
    result = None
    addend = point
    while k:
        if k & 1:
            result = point_add(p, a, result, addend)
        addend = point_add(p, a, addend, addend)
        k >>= 1
    return result


def verify_ecdsa_sha384(curve_name: str, pubx: int, puby: int, message: bytes, r: int, s: int) -> bool:
    """Checks an ECDSA signature (r, s) over SHA-384(message) against public key (pubx, puby).
    This workbook's incident uses P-384 keys with ecdsa-with-SHA384 throughout, so the hash is
    fixed here; a P-256 certificate would use SHA-256 instead (out of scope for this checkpoint)."""
    c = CURVES[curve_name]
    p, a, n, gx, gy = c["p"], c["p"] - 3, c["n"], c["gx"], c["gy"]
    if not (1 <= r < n and 1 <= s < n):
        return False
    digest = hashlib.sha384(message).digest()
    z = int.from_bytes(digest, "big")
    n_bits = n.bit_length()
    if 8 * len(digest) > n_bits:
        z >>= 8 * len(digest) - n_bits
    w = pow(s, -1, n)
    u1, u2 = (z * w) % n, (r * w) % n
    point = point_add(p, a, scalar_mult(p, a, n, u1, (gx, gy)), scalar_mult(p, a, n, u2, (pubx, puby)))
    if point is None:
        return False
    x, _y = point
    return x % n == r
