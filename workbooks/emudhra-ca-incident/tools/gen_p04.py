"""Test cases for checkpoint 04 (verify an ECDSA signature, P-384 + SHA-384 only).

Expected verdicts come from the `cryptography` library's own ECDSA verification (OpenSSL), with
`ec.ECDSA(utils.Prehashed(hashes.SHA384()))` so the exact 48-byte digest is under our control -
independent of the reference solution, which must implement the verification equation itself
(modular inverse and point add/double, in the same style as checkpoint 10's reference) rather than
calling the library.

Two boundary cases (r == n-1 and s == n-1, both as genuinely valid signatures) can't be reached by
just signing random messages with random nonces - the odds of hitting that one value by chance are
about 1 in 2^384. Both are instead constructed so the library confirms them as real passes; see
`s_boundary_case` and `r_boundary_case` below for exactly how, and why no discrete-log step is
needed to build them.

    python3 -P tools/gen_p04.py                                  # tests/04 (seed 1)
    python3 -P tools/gen_p04.py --seed 777 --out build/fresh/04  # what `check 04 -Fresh` runs
"""

import os
import random
import sys
from pathlib import Path

import cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = (f"cryptography {cryptography.__version__} (OpenSSL): ec.ECDSA(utils.Prehashed(hashes.SHA384())), "
       "the library's own verification")

REQUIREMENTS = [
    ("R1", "A genuinely valid signature verifies as `valid`"),
    ("R2", "r or s outside [1, n-1] is `invalid` without needing the point computation (0, and n or larger); "
           "and a signature where the recomputed point is itself the point at infinity is `invalid`"),
    ("R3", "Changing the signature by 1 - in r, in s, or in the signed hash - flips a valid signature to `invalid`"),
    ("R4", "A signature checked against a different public key than the one that made it is `invalid`"),
    ("R5", "r == n-1 or s == n-1 (the top of the legal range) verifies `valid` when the signature is otherwise genuine"),
    ("E2E", "A mixed batch of signatures: some valid, some altered, some out of range, some wrong key"),
]
EXPLAIN = "_lines=R1"

CURVE = curves.CURVES["P-384"]
P, A, B, N = CURVE["p"], CURVE["a"], CURVE["b"], CURVE["n"]
G = (CURVE["gx"], CURVE["gy"])
HEXLEN = CURVE["hexlen"]  # 96 hex chars = 48 bytes, for pubx, puby and the hash


def add(p1, p2):
    """Point addition/doubling, mod P - used only to build and sanity-check test data, not as
    part of the reference's own verification (which is a separate, hand-written implementation)."""
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        slope = (3 * x1 * x1 + A) * pow(2 * y1, -1, P) % P
    else:
        slope = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (slope * slope - x1 - x2) % P
    return x3, (slope * (x1 - x3) - y1) % P


def scalar_mult(d, point=G):
    result = None
    addend = point
    while d > 0:
        if d & 1:
            result = add(result, addend)
        addend = add(addend, addend)
        d >>= 1
    return result


def hexpt(pt):
    return f"{pt[0]:0{HEXLEN}x} {pt[1]:0{HEXLEN}x}"


def lib_verify(pub, zhash_bytes, r, s):
    """The independent oracle: ask OpenSSL (through `cryptography`) whether (pub, hash, r, s)
    is a valid ECDSA signature, by actually constructing and verifying it."""
    numbers = ec.EllipticCurvePublicNumbers(pub[0], pub[1], ec.SECP384R1())
    pubkey = numbers.public_key()
    sig = utils.encode_dss_signature(r, s)
    try:
        pubkey.verify(sig, zhash_bytes, ec.ECDSA(utils.Prehashed(hashes.SHA384())))
        return True
    except Exception:
        return False


def verify_line(pub, zhash, r, s):
    """One `verify` input/expected pair, cross-checked against the library oracle."""
    zbytes = zhash.to_bytes(48, "big")
    verdict = "valid" if lib_verify(pub, zbytes, r, s) else "invalid"
    line = f"verify {pub[0]:0{HEXLEN}x} {pub[1]:0{HEXLEN}x} {zhash:0{HEXLEN}x} {r:x} {s:x}"
    return line, verdict


def real_signature(rng):
    """A genuine signature: real private key, real nonce, real random hash, signed by the
    library itself. Returns (pub, zhash, r, s, d, k)."""
    d = rng.randrange(1, N)
    k = rng.randrange(1, N)
    pub = scalar_mult(d)
    zhash = int.from_bytes(os.urandom(48), "big")
    r_pt = scalar_mult(k)
    r = r_pt[0] % N
    s = (pow(k, -1, N) * (zhash + r * d)) % N
    assert 1 <= r < N and 1 <= s < N
    # Cross-check against the library's own signing/verification, independent of this formula.
    priv = ec.derive_private_key(d, ec.SECP384R1())
    sig = priv.sign(zhash.to_bytes(48, "big"), ec.ECDSA(utils.Prehashed(hashes.SHA384())))
    lib_r, lib_s = utils.decode_dss_signature(sig)
    assert lib_verify(pub, zhash.to_bytes(48, "big"), r, s), "hand-built signature doesn't verify"
    assert lib_verify(pub, zhash.to_bytes(48, "big"), lib_r, lib_s), "library's own signature doesn't verify"
    return pub, zhash, r, s, d, k


def s_boundary_case(rng):
    """A genuine signature with s == n - 1 exactly. s is solved for directly: pick a real
    private key d and a real nonce k (so r is whatever (k*G).x mod n naturally is), then choose
    the hash z so that the signing equation s = k^-1 * (z + r*d) mod n comes out to n - 1. No
    discrete log is needed because z, not r or s, is the free variable here."""
    d = rng.randrange(1, N)
    k = rng.randrange(1, N)
    pub = scalar_mult(d)
    r = scalar_mult(k)[0] % N
    s = N - 1
    z = (s * k - r * d) % N
    assert lib_verify(pub, z.to_bytes(48, "big"), r, s)
    return pub, z, r, s


def r_boundary_case():
    """A genuine signature with r == n - 1 exactly. Forcing r to a specific value by picking a
    nonce k would need solving the discrete log for that x-coordinate - infeasible. Instead this
    builds the *point* first and works outward, needing no discrete log at all:

    1. x0 = n - 1 happens to be a valid x-coordinate on P-384 (checked directly: x0^3+ax0+b is a
       quadratic residue mod p, found by Euler's criterion, and p = 3 mod 4 makes the square root
       a single exponentiation - no search over points needed).
    2. Pick s freely; this fixes w = s^-1 mod n and u2 = r*w mod n (r = n - 1, the target).
    3. Set z = 0, so u1 = z*w = 0, and the verification point is just u2 * Q for whatever Q is.
    4. Define Q = (u2^-1 mod n) * target_point, computed by ordinary scalar multiplication (no
       discrete log needed: we're choosing Q to make the equation hold, not solving for it).
       Then u2 * Q = target_point exactly, so its x mod n is r by construction, and the signature
       verifies. Q is a perfectly ordinary-looking public key - every point is *some* private
       key's public key, we simply never find out which d it corresponds to, and don't need to.
    """
    r = N - 1
    rhs = (r * r * r + A * r + B) % P
    assert pow(rhs, (P - 1) // 2, P) == 1, "n - 1 isn't a valid x-coordinate on this curve"
    y0 = pow(rhs, (P + 1) // 4, P)  # P = 3 mod 4, so this is a square root of rhs mod P
    assert (y0 * y0 - rhs) % P == 0
    target = (r, y0)
    assert curves.on_curve("P-384", *target)
    s = 0x1234567890abcdef  # any value coprime to n works; n is prime, so any nonzero s does
    w = pow(s, -1, N)
    u2 = (r * w) % N
    pub = scalar_mult(pow(u2, -1, N), target)
    z = 0
    assert lib_verify(pub, z.to_bytes(48, "big"), r, s)
    return pub, z, r, s


def build(lines_and_expected):
    inputs = [l for l, _ in lines_and_expected]
    expected = [e for _, e in lines_and_expected]
    return inputs, expected


def main():
    args = wbcore.parse_args("04")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add_case(case_id, req, title, items):
        inputs, expected = build(items)
        cases.add(case_id, req, title, inputs, expected)

    # R1 - genuinely valid signatures
    sigs = [real_signature(rng) for _ in range(3)]
    add_case(f"04-R1-valid-s{args.seed}", "R1", f"three genuine signatures from three different keys (seed {args.seed})",
             [verify_line(pub, z, r, s) for pub, z, r, s, _, _ in sigs])

    # R2 - r or s out of range, rejected before any point computation
    pub0, z0, r0, s0, _, _ = sigs[0]
    add_case("04-R2-zero", "R2", "r = 0 and s = 0, each with an otherwise-genuine signature", [
        verify_line(pub0, z0, 0, s0), verify_line(pub0, z0, r0, 0)])
    add_case("04-R2-too-big", "R2", "r = n and s = n (one past the legal range)", [
        verify_line(pub0, z0, N, s0), verify_line(pub0, z0, r0, N)])
    add_case("04-R2-way-too-big", "R2", "r and s far larger than n", [
        verify_line(pub0, z0, N * 7 + 3, s0), verify_line(pub0, z0, r0, N * 11 + 9)])
    # r and s both in range, but chosen so u1*G + u2*Q lands exactly on infinity (z = -r mod n,
    # with Q = G): a signature that must be rejected only by the final "is it infinity" check,
    # not by the range check or the x-coordinate comparison.
    inf_r = rng.randrange(1, N)
    inf_s = rng.randrange(1, N)
    inf_z = (N - inf_r) % N
    add_case("04-R2-infinity-point", "R2", "r, s and hash chosen so the recomputed point is infinity",
             [verify_line(G, inf_z, inf_r, inf_s)])

    # R3 - altering the signature by 1 (in r, in s, in the hash) must flip valid to invalid
    pub1, z1, r1, s1, _, _ = sigs[1]
    add_case("04-R3-altered-r", "R3", "a genuine signature with r incremented by 1", [
        verify_line(pub1, z1, r1, s1), verify_line(pub1, z1, (r1 + 1) % N or 1, s1)])
    add_case("04-R3-altered-s", "R3", "a genuine signature with s incremented by 1", [
        verify_line(pub1, z1, r1, s1), verify_line(pub1, z1, r1, (s1 + 1) % N or 1)])
    add_case("04-R3-altered-hash", "R3", "a genuine signature checked against a hash incremented by 1", [
        verify_line(pub1, z1, r1, s1), verify_line(pub1, (z1 + 1) % (1 << 384), r1, s1)])

    # R4 - checked against a different public key
    pub2, z2, r2, s2, _, _ = sigs[2]
    other_pub = scalar_mult(rng.randrange(1, N))
    add_case("04-R4-wrong-key", "R4", "a genuine signature checked against an unrelated public key", [
        verify_line(pub2, z2, r2, s2), verify_line(other_pub, z2, r2, s2)])

    # R5 - r == n-1 and s == n-1, both as genuine signatures (see the docstrings above)
    pub_s, z_s, r_s, s_s = s_boundary_case(rng)
    assert s_s == N - 1
    add_case("04-R5-s-boundary", "R5", "a genuine signature with s == n - 1 exactly",
             [verify_line(pub_s, z_s, r_s, s_s)])
    pub_r, z_r, r_r, s_r = r_boundary_case()
    assert r_r == N - 1
    add_case("04-R5-r-boundary", "R5", "a genuine signature with r == n - 1 exactly",
             [verify_line(pub_r, z_r, r_r, s_r)])
    # and the companion failure mode: r/s one *past* n - 1 must still read as out of range
    add_case("04-R5-just-over", "R5", "r = n (one past the legal top) must still be rejected as out of range", [
        verify_line(pub_s, z_s, N, s_s)])

    # E2E - a mixed batch: some valid, some altered, some out of range, some wrong key - as a
    # verifier would actually see them checking a batch of certificates
    batch = []
    for pub, z, r, s, _, _ in sigs:
        batch.append(verify_line(pub, z, r, s))
    batch.append(verify_line(pub1, z1, (r1 + 5) % N or 1, s1))
    batch.append(verify_line(pub2, z2, 0, s2))
    batch.append(verify_line(other_pub, z2, r2, s2))
    batch.append(verify_line(pub_s, z_s, r_s, s_s))
    rng.shuffle(batch)
    add_case(f"04-E2E-batch-s{args.seed}", "E2E", f"eight signatures, a mix of valid and invalid (seed {args.seed})", batch)

    cases.save()


if __name__ == "__main__":
    main()
