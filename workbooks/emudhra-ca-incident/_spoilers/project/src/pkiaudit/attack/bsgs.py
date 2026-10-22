"""Finding a small private key in square-root time: baby-step giant-step (assignment 17).

Assignment 10's search spends one point addition per candidate. This one stores the m baby
steps 1*G .. m*G in a table keyed by x, then visits giant points Q - c*G for centres c that are
2m apart. A giant point with the x of j*G is j*G or -(j*G), so it gives e = c + j or e = c - j
for Q = e*G, and its y says which. Each giant point therefore covers the 2m + 1 keys from c - m
to c + m, and walking both ways from Q covers every key from -bound to bound with about
bound / m giant points.
"""

from math import isqrt

from pkiaudit.ecc.curve import Curve, Point, add_points, scalar_multiply


def plan(bound: int, table_limit: int | None = None) -> tuple[int, int]:
    """Returns (m, giant points) for a search of keys -bound .. bound with at most table_limit
    baby steps: m = min(ceil(sqrt(bound)), table_limit), and 2*g - 1 giant points, Q and g - 1
    on each side of it, with g = ceil((bound + m) / (2m))."""
    m = isqrt(bound - 1) + 1  # the smallest m with m*m >= bound, in exact integers
    if table_limit is not None:
        m = min(m, table_limit)
    per_side = (bound + m + 2 * m - 1) // (2 * m)  # the last centre, 2m*(g - 1), is within m of bound
    return m, 2 * per_side - 1


def build_baby_table(curve: Curve, m: int) -> dict[int, tuple[int, int]]:
    """Returns {x of j*G: (j, y of j*G)} for j = 1 .. m. The x values differ, because j*G and
    j'*G share an x only when j' = j or j' = n - j."""
    table = {}
    point = curve.g
    for j in range(1, m + 1):
        table[point[0]] = (j, point[1])
        point = add_points(curve, point, curve.g)
    return table


def find_private_key_bsgs(curve: Curve, public_key: tuple[int, int], bound: int,
                          table: dict[int, tuple[int, int]]) -> int | None:
    """Returns the e with 1 <= |e| <= bound and e*G == public_key, or None if there is none.
    `table` comes from build_baby_table(curve, m); a negative e means the key is -(|e|*G)."""
    m = len(table)
    _, giant = plan(bound, m)
    per_side = (giant + 1) // 2
    stride = scalar_multiply(curve, 2 * m, curve.g)
    minus_stride = (stride[0], curve.p - stride[1])
    # Walk down (Q, Q - 2m*G, ...: centres 0, 2m, 4m, ...), then up (Q + 2m*G, ...: centres
    # -2m, -4m, ...). The up walk starts one stride out, because the down walk already saw Q.
    for step, sign, first in ((minus_stride, 1, 0), (stride, -1, 1)):
        point: Point = public_key
        if first:
            point = add_points(curve, point, step)
        for k in range(first, per_side):
            centre = sign * 2 * m * k
            e = None
            if point is None:  # Q - centre*G is the point at infinity, so Q = centre*G
                e = centre
            elif point[0] in table:
                j, y = table[point[0]]
                e = centre + j if y == point[1] else centre - j
            if e is not None:
                # The keys a walk can reach lie far below n, so this e is the only candidate:
                # outside the bound means no key within it.
                return e if 1 <= abs(e) <= bound else None
            point = add_points(curve, point, step)
    return None
