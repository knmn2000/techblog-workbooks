"""Arithmetic modulo a number: powers and inverses (assignment 01).

Every curve operation in the project divides by a number mod p, and ECDSA divides mod n. Both
divisions are a multiplication by the inverse that `modinv` finds.
"""


def modexp(base: int, exp: int, mod: int) -> int:
    """Returns base ** exp mod `mod`, by square-and-multiply (mod >= 1, exp >= 0, base >= 0)."""
    if mod == 1:
        return 0
    base %= mod
    result = 1
    # Walk exp's bits from the lowest: `base` runs through base^1, base^2, base^4, ... and each
    # 1 bit multiplies its power into the result. That costs about log2(exp) multiplications.
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


def modinv(a: int, mod: int) -> int | None:
    """Returns the x in [0, mod) with a * x = 1 mod `mod`, or None when gcd(a, mod) is not 1."""
    if mod == 1:
        return 0
    # Extended Euclid: the same remainders as gcd(a, mod), with each remainder r also written as
    # s * a (mod `mod`). When the remainder reaches 1, its s is the inverse.
    old_r, r = a % mod, mod
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    if old_r != 1:  # a and mod share a factor: there is no inverse
        return None
    return old_s % mod
