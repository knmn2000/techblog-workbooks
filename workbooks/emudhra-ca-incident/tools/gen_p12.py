"""Test cases for assignment 12 (validate and generate a private key).

Every expected answer comes from plain Python integers and the published curve orders (SEC 2 /
FIPS 186-5, held in tools/curves.py and proved against OpenSSL by curves.verify()), never from
the reference solution:

- `out-of-range` is 1 <= d <= n - 1 failing. For values up to n, the generator also asks OpenSSL
  (`derive_private_key`), which refuses exactly 0 and n.
- `weak` is "d or n - d has at most L/2 bits" (L = the bit length of n), a bit-length
  formulation that differs from the reference's comparison with 2^(L/2). For every weak value
  the generator also asks OpenSSL for the public keys of d and n - d and checks that they are
  each other's negation (same x, y values adding up to p), which is why n - d counts as weak.
- Every value a case expects to be accepted is checked against the same two rules, so a mistake
  in the test data stops the generator, not the learner.

    python3 -P tools/gen_p12.py                                  # tests/12 (seed 1)
    python3 -P tools/gen_p12.py --seed 777 --out build/fresh/12  # what `check 12 -Fresh` runs
"""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = ("Python integers and the published curve orders (SEC 2 / FIPS 186-5); OpenSSL (cryptography) confirms the "
       "order, and that d and n - d give negated public keys")

REQUIREMENTS = [
    ("R1", "A key from B to n - B, both ends included, gets `ok`"),
    ("R2", "Zero and any value of n or more get `out-of-range`; zero gets it although it is also below B"),
    ("R3", "A key below B gets `weak`, including the eight values from the incident; B - 1 is the largest of them"),
    ("R4", "A key above n - B gets `weak`, because d and n - d are as easy to guess as each other; n - 1 is the largest of them"),
    ("R5", "Each curve uses its own order, byte length and bound B (2^128 for P-256, 2^192 for P-384)"),
    ("R6", "For a `draw` line, the generator draws, validates and redraws after every rejection, whatever its reason, and the answer is the first block that passes"),
    ("E2E", "One input mixes validate and draw lines on both curves, with every verdict"),
]
EXPLAIN = ""

INCIDENT_P384 = [4, 56, 66, 115, 155, 156, 230, 237]  # P-384 private keys of the incident, all below 256


def order(curve):
    return curves.CURVES[curve]["n"]


def bits(curve):
    return curves.CURVES[curve]["bits"]


def bound(curve):
    """The bound B = 2^(L/2) from the page, L being the bit length of n."""
    return 1 << (bits(curve) // 2)


def block(curve, value):
    """A candidate as hex text, zero-padded to the curve's byte length."""
    c = curves.CURVES[curve]
    assert 0 <= value < (1 << c["bits"]), f"{value:#x} does not fit in {c['bits']} bits"
    return f"{value:0{c['hexlen']}x}"


def verdict(curve, d):
    """The expected verdict, from integer rules and OpenSSL: None, 'out-of-range' or 'weak'."""
    n, half = order(curve), bits(curve) // 2
    if d < 1 or d >= n:
        if d <= n:  # OpenSSL reduces larger values mod n, so it only judges 0 and n
            assert not curves_accepts(curve, d), f"OpenSSL accepts {d:#x} on {curve}, the test data says out of range"
        return "out-of-range"
    assert curves_accepts(curve, d), f"OpenSSL refuses {d:#x} on {curve}"
    if d.bit_length() <= half or (n - d).bit_length() <= half:
        x1, y1 = curves.public_point(curve, d)
        x2, y2 = curves.public_point(curve, n - d)
        assert x1 == x2 and (y1 + y2) % curves.CURVES[curve]["p"] == 0, "d and n - d are not each other's negation"
        return "weak"
    return None


def curves_accepts(curve, d):
    from cryptography.hazmat.primitives.asymmetric import ec
    try:
        ec.derive_private_key(d, curves.CURVES[curve]["lib"]())
        return True
    except ValueError:
        return False


def expect(curve, d, want):
    assert verdict(curve, d) == want, f"{d:#x} on {curve} is {verdict(curve, d)}, not {want}"
    return d


def strong(rng, curve):
    """A plausible real key: uniform in the accepted range B .. n - B."""
    return expect(curve, rng.randrange(bound(curve), order(curve) - bound(curve) + 1), None)


def small(rng, curve):
    """A weak value below the threshold, with a random bit length so that tiny and large ones both appear."""
    return expect(curve, rng.getrandbits(rng.randint(1, bits(curve) // 2)) or 1, "weak")


def above_n(rng, curve):
    """A value of n or more that still fits in the curve's byte length."""
    return expect(curve, rng.randint(order(curve), (1 << bits(curve)) - 1), "out-of-range")


def tag(curve):
    return curve.lower().replace("-", "")


def validate_case(cases, case_id, req, title, curve, values):
    """One case with a `validate` line per value (label v0, v1, ...)."""
    lines, out = [], []
    for i, d in enumerate(values):
        lines.append(f"validate v{i} {curve} {block(curve, d)}")
        why = verdict(curve, d)
        out.append(f"ok v{i}" if why is None else f"reject v{i} {why}")
    cases.add(case_id, req, title, lines, out)


def draw_case(cases, case_id, req, title, curve, rejects, accept, label="k"):
    """One case with a `draw` line: every value in `rejects` must be rejected, `accept` must pass."""
    for r in rejects:
        assert verdict(curve, r) is not None, f"{r:#x} on {curve} would be accepted"
    assert verdict(curve, accept) is None, f"{accept:#x} on {curve} would be rejected"
    blocks = [block(curve, v) for v in rejects + [accept]]
    cases.add(case_id, req, title, [f"draw {label} {curve} " + " ".join(blocks)],
              f"key {label} {block(curve, accept)}")


def main():
    args = wbcore.parse_args("12")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    # R1 - accepted keys: random ones, and the exact edges of the accepted range.
    for curve in curves.CURVES:
        n, b = order(curve), bound(curve)
        validate_case(cases, f"12-R1-random-{tag(curve)}", "R1",
                      f"{curve}: three random keys from the accepted range", curve, [strong(rng, curve) for _ in range(3)])
        validate_case(cases, f"12-R1-low-edge-{tag(curve)}", "R1",
                      f"{curve}: d = B (2^{bits(curve) // 2}), the smallest accepted key", curve, [expect(curve, b, None)])
        validate_case(cases, f"12-R1-high-edge-{tag(curve)}", "R1",
                      f"{curve}: d = n - B, the largest accepted key", curve, [expect(curve, n - b, None)])

    # R2 - out of range: zero, n, and everything above.
    for curve in curves.CURVES:
        n = order(curve)
        validate_case(cases, f"12-R2-zero-{tag(curve)}", "R2",
                      f"{curve}: d = 0 is out-of-range (it is also below the weak threshold)", curve, [expect(curve, 0, "out-of-range")])
        validate_case(cases, f"12-R2-n-{tag(curve)}", "R2",
                      f"{curve}: d = n and n + 1 are out-of-range", curve, [expect(curve, n, "out-of-range"), expect(curve, n + 1, "out-of-range")])
        validate_case(cases, f"12-R2-above-n-{tag(curve)}", "R2",
                      f"{curve}: all-ff bits and a random value above n are out-of-range", curve,
                      [expect(curve, (1 << bits(curve)) - 1, "out-of-range"), above_n(rng, curve)])

    # R3 - weak keys below the threshold, with the incident's own values.
    validate_case(cases, "12-R3-incident-values-p384", "R3",
                  "P-384: the eight private keys of the incident (4, 56, 66, 115, 155, 156, 230, 237)", "P-384",
                  [expect("P-384", d, "weak") for d in INCIDENT_P384])
    validate_case(cases, "12-R3-d4-p384", "R3", "P-384: d = 4, the smallest private key reported in the incident", "P-384",
                  [expect("P-384", 4, "weak")])
    for curve in curves.CURVES:
        b = bound(curve)
        validate_case(cases, f"12-R3-one-{tag(curve)}", "R3", f"{curve}: d = 1 is weak", curve, [expect(curve, 1, "weak")])
        validate_case(cases, f"12-R3-just-below-{tag(curve)}", "R3",
                      f"{curve}: d = B - 1 is the largest weak key below the threshold", curve, [expect(curve, b - 1, "weak")])
        validate_case(cases, f"12-R3-random-s{args.seed}-{tag(curve)}", "R3",
                      f"{curve}: three random keys below the threshold, of different sizes (seed {args.seed})", curve,
                      [small(rng, curve) for _ in range(3)])

    # R4 - weak keys above n - threshold: the negations of the small ones.
    for curve in curves.CURVES:
        n, b = order(curve), bound(curve)
        validate_case(cases, f"12-R4-n-minus-1-{tag(curve)}", "R4",
                      f"{curve}: d = n - 1 (the public key is -G) is weak", curve, [expect(curve, n - 1, "weak")])
        validate_case(cases, f"12-R4-just-above-{tag(curve)}", "R4",
                      f"{curve}: d = n - B + 1 is the smallest weak key above the threshold", curve, [expect(curve, n - b + 1, "weak")])
        validate_case(cases, f"12-R4-random-s{args.seed}-{tag(curve)}", "R4",
                      f"{curve}: n minus three random small values is weak (seed {args.seed})", curve,
                      [expect(curve, n - small(rng, curve), "weak") for _ in range(3)])
    validate_case(cases, "12-R4-incident-negations-p384", "R4",
                  "P-384: n - 4, n - 56 and n - 237 are weak like 4, 56 and 237", "P-384",
                  [expect("P-384", order("P-384") - d, "weak") for d in (4, 56, 237)])

    # R5 - each curve has its own threshold.
    both = [("P-256", 1 << 150, None), ("P-384", 1 << 150, "weak")]
    cases.add("12-R5-same-value-both-curves", "R5",
              "the same number, 2^150, is ok as a P-256 key and weak as a P-384 key",
              [f"validate v{i} {curve} {block(curve, expect(curve, d, want))}" for i, (curve, d, want) in enumerate(both)],
              ["ok v0", "reject v1 weak"])
    validate_case(cases, "12-R5-p384-above-p256-bound", "R5",
                  "P-384: d = 2^128 and 2^128 + 1 are weak (they pass P-256's threshold, not P-384's)", "P-384",
                  [expect("P-384", (1 << 128), "weak"), expect("P-384", (1 << 128) + 1, "weak")])
    validate_case(cases, "12-R5-p384-edge-192", "R5",
                  "P-384: d = 2^192 - 1 is weak and d = 2^192 is ok", "P-384",
                  [expect("P-384", (1 << 192) - 1, "weak"), expect("P-384", 1 << 192, None)])
    validate_case(cases, "12-R5-p256-between-bounds", "R5",
                  "P-256: d = 2^130 and 2^190 are ok (P-384's threshold would reject them)", "P-256",
                  [expect("P-256", 1 << 130, None), expect("P-256", 1 << 190, None)])

    # R6 - the generator redraws after every kind of rejection.
    for curve in curves.CURVES:
        n, b = order(curve), bound(curve)
        draw_case(cases, f"12-R6-first-draw-{tag(curve)}", "R6",
                  f"{curve}: the first block passes and becomes the key", curve, [], strong(rng, curve))
        draw_case(cases, f"12-R6-redraw-range-{tag(curve)}", "R6",
                  f"{curve}: the generator discards 0, n and all-ff, then takes a good key", curve,
                  [0, n, (1 << bits(curve)) - 1], strong(rng, curve))
        draw_case(cases, f"12-R6-redraw-weak-{tag(curve)}", "R6",
                  f"{curve}: the generator discards a tiny block, B - 1 and n - 1 as weak, then takes a good key", curve,
                  [small(rng, curve), b - 1, n - 1], strong(rng, curve))
        draw_case(cases, f"12-R6-accept-edge-{tag(curve)}", "R6",
                  f"{curve}: the generator discards B - 1 and takes B", curve, [b - 1], b)
        draw_case(cases, f"12-R6-mixed-rejects-{tag(curve)}", "R6",
                  f"{curve}: the generator discards six blocks of all kinds, then takes a good key", curve,
                  [0, small(rng, curve), n, n - small(rng, curve), above_n(rng, curve), 1], strong(rng, curve))

    # E2E - validate and draw lines together, both curves, every verdict.
    makers = [
        lambda curve: ("validate", strong(rng, curve)),
        lambda curve: ("validate", small(rng, curve)),
        lambda curve: ("validate", order(curve) - small(rng, curve)),
        lambda curve: ("validate", rng.choice([0, order(curve), above_n(rng, curve)])),
        lambda curve: ("draw", ([0, small(rng, curve), order(curve) - 1], strong(rng, curve))),
        lambda curve: ("draw", ([], strong(rng, curve))),
    ]
    lines, out = [], []
    names = list(curves.CURVES)
    for i in range(10):
        curve = names[i % 2]
        kind, payload = (makers[i % len(makers)] if i < 6 else rng.choice(makers))(curve)
        label = f"k{i}"
        if kind == "validate":
            lines.append(f"validate {label} {curve} {block(curve, payload)}")
            why = verdict(curve, payload)
            out.append(f"ok {label}" if why is None else f"reject {label} {why}")
        else:
            rejects, accept = payload
            assert all(verdict(curve, r) is not None for r in rejects) and verdict(curve, accept) is None
            lines.append(f"draw {label} {curve} " + " ".join(block(curve, v) for v in rejects + [accept]))
            out.append(f"key {label} {block(curve, accept)}")
    cases.add(f"12-E2E-ceremony-s{args.seed}", "E2E",
              f"ten lines across both curves, validate and draw, every verdict mixed (seed {args.seed})", lines, out)

    cases.save()


if __name__ == "__main__":
    main()
