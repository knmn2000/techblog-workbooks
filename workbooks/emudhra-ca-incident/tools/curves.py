"""The two NIST curves used by the workbook, and a check of these constants against OpenSSL.

The constants are typed in from the standards (SEC 2, NIST SP 800-186). `verify()` proves them
with the `cryptography` library, so a typo here stops the generators instead of shipping a wrong
test. Generators use the library for every expected public key; nothing here does curve maths.
"""

from cryptography.hazmat.primitives.asymmetric import ec

CURVES = {
    "P-256": dict(
        bits=256,
        p=0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff,
        b=0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b,
        gx=0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296,
        gy=0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5,
        n=0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551,
        lib=ec.SECP256R1,
    ),
    "P-384": dict(
        bits=384,
        p=0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff,
        b=0xb3312fa7e23ee7e4988e056be3f82d19181d9c6efe8141120314088f5013875ac656398d8a2ed19d2a85c8edd3ec2aef,
        gx=0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7,
        gy=0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f,
        n=0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973,
        lib=ec.SECP384R1,
    ),
}
for _c in CURVES.values():
    _c["a"] = _c["p"] - 3
    _c["hexlen"] = _c["bits"] // 4


def public_point(name: str, d: int):
    """(x, y) of d*G, computed by OpenSSL through the cryptography library."""
    c = CURVES[name]
    numbers = ec.derive_private_key(d, c["lib"]()).public_key().public_numbers()
    return numbers.x, numbers.y


def on_curve(name: str, x: int, y: int) -> bool:
    """Whether OpenSSL accepts (x, y) as a point of the curve."""
    c = CURVES[name]
    try:
        ec.EllipticCurvePublicNumbers(x, y, c["lib"]()).public_key()
        return True
    except ValueError:
        return False


def verify() -> None:
    """Stop if any constant above disagrees with the library."""
    for name, c in CURVES.items():
        gx, gy = public_point(name, 1)
        assert (gx, gy) == (c["gx"], c["gy"]), f"{name}: G differs from OpenSSL's"
        assert (gy * gy - (gx ** 3 + c["a"] * gx + c["b"])) % c["p"] == 0, f"{name}: G is not on y^2 = x^3 + ax + b"
        # (n-1)*G must be -G, which holds exactly when n is the order of G.
        mx, my = public_point(name, c["n"] - 1)
        assert (mx, my) == (c["gx"], c["p"] - c["gy"]), f"{name}: n is not the order of G"
        assert on_curve(name, gx, gy) and not on_curve(name, gx, gy + 1)
