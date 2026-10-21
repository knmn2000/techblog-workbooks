# Checkpoint 11 - Sign a certificate with a recovered key
#
# Problem:  problems/11-sign-with-weak-key.md (also in the web problem book)
# Check:    ./check.sh 11
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on sign().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys

CURVES = {
    "P-256": {},
    "P-384": {},
}
HEXLEN = {"P-256": 64, "P-384": 96}


def sign(curve, d, z, k):
    """Return (r, s), the ECDSA signature for private key d, hash z, and nonce k."""
    # TODO: R = k*G; r = R.x mod n; s = k^-1 * (z + r*d) mod n. The curve constants are on
    # the problem page.
    raise NotImplementedError("sign")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            # sign <id> <curve> <d> <z> <k>: d, z, k in hex
            _, case_id, curve, d, z, k = words
            r, s = sign(curve, int(d, 16), int(z, 16), int(k, 16))
            w = HEXLEN[curve]
            lines.append(f"signature {case_id} {r:0{w}x} {s:0{w}x}")
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
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
