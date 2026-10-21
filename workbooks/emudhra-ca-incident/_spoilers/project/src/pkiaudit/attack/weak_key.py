"""Recovering a private key that is too small (assignment 10).

A public key is Q = d*G. When d is small, walking G, 2G, 3G, ... reaches Q after d steps. Each
step adds G to the point before it, so a search up to `bound` costs `bound` point additions. The
incident's intermediate keys fell to this search.
"""

from pkiaudit.ecc.curve import Curve, add_points


def find_private_key(curve: Curve, public_key: tuple[int, int], bound: int) -> int | None:
    """Returns the d in [1, bound] with d*G == public_key, or None if there is none."""
    point = curve.g  # 1*G
    for d in range(1, bound + 1):
        if point == public_key:
            return d
        point = add_points(curve, point, curve.g)
    return None
