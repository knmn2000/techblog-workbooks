# Checkpoint 04 - Verify an ECDSA signature
#
# Problem:  problems/04-ecdsa-verify.md (also in the web problem book)
# Check:    ./check.sh 04
#
# Only your program's output is checked, so you can structure it however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you can
# focus on verify().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys

P = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffeffffffff0000000000000000ffffffff
A = P - 3
GX = 0xaa87ca22be8b05378eb1c71ef320ad746e1d3b628ba79b9859f741e082542a385502f25dbf55296c3a545e3872760ab7
GY = 0x3617de4a96262c6f5d9e98bf9292dc29f8f41dbd289a147ce9da3113b5f0b8c00a60b1ce1d7e819d7a431d7c90ea0e5f
N = 0xffffffffffffffffffffffffffffffffffffffffffffffffc7634d81f4372ddf581a0db248b0a77aecec196accc52973
G = (GX, GY)


def verify(pubx, puby, zhash, r, s):
    """Return True if the public key (pubx, puby) validly signed the 48-byte hash value zhash
    with signature (r, s); False otherwise. All five arguments are already-parsed integers."""
    # TODO: reject out-of-range r or s immediately (1 <= r <= n-1, 1 <= s <= n-1). Otherwise
    # compute w = s^-1 mod n, u1 = z*w mod n, u2 = r*w mod n, and the point u1*G + u2*Q (Q is the
    # public key). Invalid if that point is infinity; otherwise valid iff its x mod n equals r.
    raise NotImplementedError("verify")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            # verify <pubx> <puby> <hash> <r> <s>, all hex
            pubx, puby, zhash, r, s = (int(w, 16) for w in words[1:6])
            lines.append("valid" if verify(pubx, puby, zhash, r, s) else "invalid")
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
