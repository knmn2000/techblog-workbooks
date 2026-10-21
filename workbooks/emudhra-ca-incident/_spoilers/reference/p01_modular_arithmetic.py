# Reference solution - checkpoint 01 (Modular arithmetic). SPOILERS: try it yourself first.
#
# Square-and-multiply walks exp one bit at a time (from the bottom): it squares a running base
# every step, and whenever the current bit is 1 it folds that squared base into the result. That
# takes about log2(exp) multiplications instead of exp of them.
#
# Extended Euclid runs the same divide-and-remainder steps as gcd(a, mod), but carries along a
# second pair of numbers that express the running remainder as (something) * a mod mod. When the
# remainder finally reaches 1, that "something" is the inverse.

import sys


def modexp(base, exp, mod):
    """base ** exp mod mod. mod >= 2, exp >= 0, base >= 0 (base may be >= mod)."""
    if mod == 1:
        return 0
    base %= mod
    result = 1
    while exp > 0:
        if exp & 1:
            result = (result * base) % mod
        base = (base * base) % mod
        exp >>= 1
    return result


def modinv(a, mod):
    """a's inverse mod mod, or None if gcd(a, mod) != 1. mod >= 2, a >= 0."""
    if mod == 1:
        return 0
    old_r, r = a % mod, mod
    old_s, s = 1, 0
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
    if old_r != 1:  # gcd(a, mod) != 1: no inverse
        return None
    return old_s % mod


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "modexp":  # modexp <base> <exp> <mod>
                base, exp, mod = int(words[1]), int(words[2]), int(words[3])
                lines.append(f"modexp {modexp(base, exp, mod)}")
            elif words[0] == "modinv":  # modinv <a> <mod>
                a, mod = int(words[1]), int(words[2])
                r = modinv(a, mod)
                lines.append("modinv none" if r is None else f"modinv {r}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"usage: {sys.argv[0]} <input-file> <output-file>", file=sys.stderr)
        sys.exit(2)
    try:
        main(sys.argv[1], sys.argv[2])
    except NotImplementedError as e:
        print(f"not implemented: {e}", file=sys.stderr)
        sys.exit(99)
    except Exception as e:  # report the problem; the checker shows the message
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
