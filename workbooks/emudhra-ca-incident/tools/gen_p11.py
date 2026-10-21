"""Test cases for assignment 11 (sign a certificate with a recovered key).

This assignment stays entirely inside the workbook's own synthetic test keys: there is no real
certificate authority, domain or infrastructure involved anywhere here. Every private key is
either a toy value or a key this workbook generated for itself.

Expected r is computed by curves.public_point (an independent, OpenSSL-backed scalar
multiplication, not the reference's own point-doubling code). Expected s follows directly from
the ECDSA formula using Python's native modular inverse. Every case is then double-checked by
building the real public key and verifying the produced signature with the `cryptography`
library - a code path entirely separate from how either r or s was computed - so a case is never
written unless it is a genuine, verifiable ECDSA signature for the stated key and hash.

    python3 -P tools/gen_p11.py                                  # tests/11 (seed 1)
    python3 -P tools/gen_p11.py --seed 777 --out build/fresh/11  # what `check 11 -Fresh` runs
"""

import random
import sys
from pathlib import Path

import cryptography
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.exceptions import InvalidSignature

sys.path.insert(0, str(Path(__file__).resolve().parent))
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = f"cryptography {cryptography.__version__} (OpenSSL): r from scalar multiplication, the signature confirmed by verifying it"
HEXLEN = {"P-256": 64, "P-384": 96}
LIB_CURVE = {"P-256": ec.SECP256R1, "P-384": ec.SECP384R1}
DIGEST_BYTES = {"P-256": 32, "P-384": 48}

REQUIREMENTS = [
    ("R1", "One output line per input, in order: `signature <id> <r> <s>`, in lowercase hex"),
    ("R2", "Both curves work: P-256 and P-384 each use their own p, a, G and n"),
    ("R3", "Every nonce k works, including k = 1, k = 2, k = n - 1, and a large random k, so the "
           "answer must come from double-and-add, not a loop that runs k times"),
    ("R4", "The private key can be any value, including the recovered incident value d = 4: the formula is the same however small or large d is"),
    ("R5", "The hash z can be any value in range, including 0 and n - 1"),
]
# A wrong signature's r or s could come from almost any part of the formula, so there is no
# single requirement a content difference reliably points to (see authoring-guide.md: only map
# where a location really does localise the mistake). Only a missing line is mapped.
EXPLAIN = "_lines=R1"


def build(curve, d, z, k):
    c = curves.CURVES[curve]
    p, a, n = c["p"], c["a"], c["n"]
    g = (c["gx"], c["gy"])

    def add(P, R):
        x1, y1 = P
        x2, y2 = R
        if P == R:
            slope = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
        else:
            slope = (y2 - y1) * pow(x2 - x1, -1, p) % p
        x3 = (slope * slope - x1 - x2) % p
        return x3, (slope * (x1 - x3) - y1) % p

    def mul(k, point):
        result, base = None, point
        while k:
            if k & 1:
                result = base if result is None else add(result, base)
            base = add(base, base)
            k >>= 1
        return result

    # r: an independent scalar multiplication (OpenSSL via the cryptography library), not the
    # hand-rolled double-and-add above (that's only used as a second, cross-checking path).
    rx, _ = curves.public_point(curve, k)
    r = rx % n
    assert r == mul(k, g)[0] % n, "the hand double-and-add disagrees with OpenSSL's scalar multiplication"
    s = pow(k, -1, n) * (z + r * d) % n
    assert r != 0 and s != 0, "a real signer would redraw k here; choose a different k for this case"

    # Validate: build the real public key and verify the produced signature with the library -
    # a code path that doesn't reuse how r or s above was computed.
    qx, qy = curves.public_point(curve, d)
    pubkey = ec.EllipticCurvePublicNumbers(qx, qy, LIB_CURVE[curve]()).public_key()
    der_sig = utils.encode_dss_signature(r, s)
    digest = z.to_bytes(DIGEST_BYTES[curve], "big")
    pubkey.verify(der_sig, digest, ec.ECDSA(utils.Prehashed(_prehashed(curve))))
    w = HEXLEN[curve]
    return f"signature {{id}} {r:0{w}x} {s:0{w}x}", r, s


def _prehashed(curve):
    from cryptography.hazmat.primitives import hashes
    return hashes.SHA256() if curve == "P-256" else hashes.SHA384()


def line(curve, case_id, d, z, k):
    w = HEXLEN[curve]
    return f"sign {case_id} {curve} {d:0{w}x} {z:0{w}x} {k:0{w}x}"


def expected_line(case_id, curve, d, z, k):
    template, r, s = build(curve, d, z, k)
    return template.format(id=case_id), r, s


def fixed_digest(curve, text):
    """A hash standing in for a signed message: sha256/sha384 of fixed, clearly fictitious text
    ("TBS bytes for a test leaf certificate issued inside this workbook"), reduced to the curve's
    digest size. Never a real certificate's bytes."""
    import hashlib
    h = hashlib.sha256(text.encode()) if curve == "P-256" else hashlib.sha384(text.encode())
    return int.from_bytes(h.digest(), "big")


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

    cases.save()


if __name__ == "__main__":
    main()
