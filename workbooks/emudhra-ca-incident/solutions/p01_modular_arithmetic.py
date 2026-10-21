# Checkpoint 01 - Modular arithmetic
#
# Problem:  problems/01-modular-arithmetic.md (also in the web problem book)
# Check:    ./check.sh 01
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on modexp() and modinv().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys


def modexp(base, exp, mod):
    """Return base ** exp mod mod. mod >= 2, exp >= 0, base >= 0 (base may be >= mod)."""
    # TODO: square-and-multiply. Don't multiply `exp` times in a loop - it must finish on a
    # several-hundred-bit exponent well inside the time limit.
    raise NotImplementedError("modexp")


def modinv(a, mod):
    """Return a's inverse mod mod, or None if gcd(a, mod) != 1. mod >= 2, a >= 0."""
    # TODO: the extended Euclidean algorithm.
    raise NotImplementedError("modinv")


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
