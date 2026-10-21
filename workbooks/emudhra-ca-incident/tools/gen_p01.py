"""Test cases for assignment 01 (modular arithmetic).

Expected values come from Python's own built-in `pow(base, exp, mod)` and `pow(a, -1, mod)`,
which is CPython's C-level bignum routine - independent of the reference solution, which must
implement square-and-multiply and extended Euclid itself rather than calling `pow`. The "none"
cases are cross-checked with `math.gcd`, a second independent routine.

    python3 -P tools/gen_p01.py                                  # tests/01 (seed 1)
    python3 -P tools/gen_p01.py --seed 777 --out build/fresh/01  # what `check 01 -Fresh` runs
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import curves  # noqa: E402
import wbcore  # noqa: E402

LIB = "Python's built-in pow(base, exp, mod) and pow(a, -1, mod), cross-checked with math.gcd"

REQUIREMENTS = [
    ("R1", "One output line per input line, in order: `modexp <result>` or `modinv <result>`/`modinv none`"),
    ("R2", "exp = 0 gives 1 mod m (even if base = 0), except mod = 1 always gives 0"),
    ("R3", "exp = 1 gives base mod m"),
    ("R4", "Exponents hundreds of bits long finish well under the time limit (square-and-multiply, not a loop of `exp` multiplications)"),
    ("R5", "base >= mod is reduced mod m before exponentiating"),
    ("R6", "modinv returns the inverse when gcd(a, mod) = 1"),
    ("R7", "modinv returns `none` when gcd(a, mod) != 1, including a = 0 and a sharing a prime factor with mod"),
    ("R8", "mod = 1: modexp is always 0, and by convention modinv mod 1 is also 0"),
    ("E2E", "A real curve prime (P-384's p) used for one modexp and one modinv"),
]
EXPLAIN = "_lines=R1"


def modexp_line(base, exp, mod):
    """One `modexp` input/expected pair. The oracle is Python's own pow(base, exp, mod)."""
    expected = pow(base, exp, mod)
    assert 0 <= expected < mod or mod == 1 and expected == 0
    return f"modexp {base} {exp} {mod}", f"modexp {expected}"


def modinv_line(a, mod):
    """One `modinv` input/expected pair. The oracle is pow(a, -1, mod); math.gcd confirms `none`."""
    try:
        inv = pow(a, -1, mod)
    except ValueError:
        inv = None
    g = math.gcd(a, mod)
    if mod == 1:
        assert inv == 0, "mod 1: every value is 0, so pow(a, -1, 1) is 0 by convention"
    elif inv is None:
        assert g != 1, f"pow() says a={a} mod={mod} has no inverse, but gcd is 1"
    else:
        assert g == 1, f"pow() found an inverse for a={a} mod={mod}, but gcd is {g}"
        assert (a * inv) % mod == 1, "the returned value isn't actually an inverse"
    return f"modinv {a} {mod}", ("modinv none" if inv is None else f"modinv {inv}")


def build(lines_and_expected):
    """lines_and_expected: list of (input_line, expected_line) pairs, in order."""
    inputs = [l for l, _ in lines_and_expected]
    expected = [e for _, e in lines_and_expected]
    return inputs, expected


def main():
    args = wbcore.parse_args("01")
    curves.verify()
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, items):
        inputs, expected = build(items)
        cases.add(case_id, req, title, inputs, expected)

    big_mod = (1 << 400) | 1  # an odd 401-bit modulus, large enough that exponents of similar size matter
    big_base = rng.randrange(2, big_mod)

    # R1 - order preserved across a mix of modexp and modinv lines
    add("01-R1-mixed", "R1", "five lines, modexp and modinv interleaved", [
        modexp_line(3, 5, 7), modinv_line(3, 7), modexp_line(10, 0, 13),
        modinv_line(6, 13), modexp_line(2, 10, 1000)])
    add("01-R1-all-modexp", "R1", "four modexp lines in a row", [
        modexp_line(2, 3, 5), modexp_line(5, 5, 11), modexp_line(7, 2, 13), modexp_line(9, 9, 17)])
    add("01-R1-all-modinv", "R1", "four modinv lines in a row, some invertible and some not", [
        modinv_line(3, 11), modinv_line(4, 8), modinv_line(5, 11), modinv_line(6, 8)])

    # R2 - exp = 0
    add("01-R2-base-nonzero", "R2", "exp = 0 with a nonzero base and mod > 1", [modexp_line(123, 0, 97)])
    add("01-R2-base-zero", "R2", "exp = 0 with base = 0 (still gives 1, not 0)", [modexp_line(0, 0, 97)])
    add("01-R2-base-large", "R2", "exp = 0 with a base already bigger than mod", [modexp_line(500, 0, 7)])

    # R3 - exp = 1
    add("01-R3-small", "R3", "exp = 1, base already less than mod", [modexp_line(5, 1, 97)])
    add("01-R3-zero-base", "R3", "exp = 1, base = 0", [modexp_line(0, 1, 97)])
    add("01-R3-large-base", "R3", "exp = 1, base bigger than mod (reduces first)", [modexp_line(250, 1, 97)])

    # R4 - exponents hundreds of bits long; only square-and-multiply finishes in time
    for i in range(3):
        base = rng.randrange(2, big_mod)
        exp = rng.getrandbits(380) | (1 << 379)  # force a ~380-bit exponent, not a short one
        mod = rng.getrandbits(384) | 1 | (1 << 383)
        add(f"01-R4-huge-{i}-s{args.seed}", "R4", f"a ~380-bit exponent and a ~384-bit modulus (seed {args.seed})",
            [modexp_line(base, exp, mod)])
    add("01-R4-all-ones-exp", "R4", "a 256-bit exponent that is all 1 bits (every doubling step folds in a multiply)",
        [modexp_line(7, (1 << 256) - 1, (1 << 255) | 1)])

    # R5 - base >= mod, reduced before exponentiating
    add("01-R5-base-double-mod", "R5", "base is exactly twice the modulus", [modexp_line(194, 10, 97)])
    add("01-R5-base-much-larger", "R5", "base is far larger than the modulus", [modexp_line(big_base, 3, 1000003)])
    add("01-R5-base-equal-mod", "R5", "base equals the modulus (reduces to 0)", [modexp_line(97, 5, 97)])

    # R6 - modinv exists
    add("01-R6-small-prime-mod", "R6", "a coprime to a small prime modulus", [modinv_line(3, 7)])
    add("01-R6-composite-mod", "R6", "a coprime to a composite modulus", [modinv_line(7, 15)])
    add("01-R6-large", "R6", "a coprime to a large modulus", [modinv_line(rng.randrange(2, big_mod), big_mod)])

    # R7 - modinv none
    add("01-R7-zero", "R7", "a = 0, mod > 1 (gcd is mod, never 1)", [modinv_line(0, 97)])
    add("01-R7-prime-factor", "R7", "a is a multiple of a prime factor of a composite mod", [modinv_line(21, 35)])
    add("01-R7-equal-mod", "R7", "a equals mod (reduces to 0, same as a = 0)", [modinv_line(15, 15)])
    add("01-R7-shared-even", "R7", "a and mod are both even (share the factor 2)", [modinv_line(14, 20)])

    # R8 - mod = 1
    add("01-R8-modexp", "R8", "modexp with mod = 1: always 0, whatever base and exp are", [
        modexp_line(999, 999, 1), modexp_line(0, 0, 1)])
    add("01-R8-modinv", "R8", "modinv with mod = 1: 0 by convention", [modinv_line(5, 1), modinv_line(0, 1)])

    # E2E - a real curve prime
    p384 = curves.CURVES["P-384"]["p"]
    e2e_base = rng.randrange(2, p384)
    e2e_exp = rng.getrandbits(380)
    e2e_a = rng.randrange(1, p384)  # nonzero and less than a prime modulus: always invertible
    add(f"01-E2E-p384-s{args.seed}", "E2E", "P-384's field prime: one modexp and one modinv (seed {})".format(args.seed), [
        modexp_line(e2e_base, e2e_exp, p384), modinv_line(e2e_a, p384)])
    add("01-E2E-p384-g", "E2E", "P-384's field prime: modexp of its generator's x-coordinate, and its modinv",
        [modexp_line(curves.CURVES["P-384"]["gx"], 3, p384), modinv_line(curves.CURVES["P-384"]["gx"], p384)])

    cases.save()


if __name__ == "__main__":
    main()
