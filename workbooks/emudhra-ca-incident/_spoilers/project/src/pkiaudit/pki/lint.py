"""Linting a public key before a CA trusts or publishes it (assignment 13).

Three checks run from cheapest to most expensive, and the first that fails names the problem:

| Check | Finding |
|---|---|
| The point satisfies the curve's equation | off-curve |
| The key is not on the blocklist of known-compromised keys | known-compromised |
| The private key is not d or n - d for any d up to the bound | weak |

Any one of them, run by the CA, would have caught the incident's keys.
"""

from pkiaudit.attack.weak_key import find_private_key
from pkiaudit.ecc.curve import Curve

WEAK_BOUND = 4096  # how far the weak-key search goes, for both signs (the problem page explains the size)


def on_curve(curve: Curve, point: tuple[int, int]) -> bool:
    """Returns True when the point's coordinates are in [0, p) and satisfy y^2 = x^3 + a*x + b."""
    x, y = point
    p = curve.p
    if not (0 <= x < p and 0 <= y < p):
        return False
    return (y * y - (x ** 3 + curve.a * x + curve.b)) % p == 0


def lint_key(curve: Curve, public_key: tuple[int, int],
             blocklist: set[tuple[str, tuple[int, int]]]) -> str | None:
    """Returns the first finding ("off-curve", "known-compromised" or "weak"), or None for a good key."""
    # The blocklist holds (curve name, (x, y)) pairs.
    if not on_curve(curve, public_key):
        return "off-curve"
    if (curve.name, public_key) in blocklist:
        return "known-compromised"
    if find_private_key(curve, public_key, WEAK_BOUND) is not None:
        return "weak"
    return None
