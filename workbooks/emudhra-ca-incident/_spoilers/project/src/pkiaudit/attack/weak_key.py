"""Recovering a private key that is too small (assignment 10).

A public key is Q = d*G. When d is small, walking G, 2G, 3G, ... reaches Q after d steps. Each
step adds G to the point before it, so a search up to `bound` costs `bound` point additions. The
incident's intermediate keys fell to this search.

The private key n - d gives -(d*G), the point d*G with y replaced by p - y. Comparing each step's
point with -Q as well as Q finds that key in the same walk, with no extra additions.
"""

from pkiaudit.ecc.curve import Curve, add_points


def find_private_key(curve: Curve, public_key: tuple[int, int], bound: int) -> int | None:
    """Returns d when public_key == d*G, or -d when public_key == -(d*G), for d in [1, bound].

    -d stands for the private key n - d, which equals -d mod n. Returns None if neither matches.
    """
    x, y = public_key
    negated = (x, (curve.p - y) % curve.p)  # -Q: Q == -(d*G) exactly when -Q == d*G
    point = curve.g  # 1*G
    for d in range(1, bound + 1):
        if point == public_key:  # checked first, so d wins if both ever matched
            return d
        if point == negated:
            return -d
        point = add_points(curve, point, curve.g)
    return None
