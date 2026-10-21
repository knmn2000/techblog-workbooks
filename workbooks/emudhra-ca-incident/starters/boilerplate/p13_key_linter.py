# Checkpoint 13 - Lint a public key
#
# Problem:  problems/13-key-linter.md (also in the web problem book)
# Check:    ./check.sh 13
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on lint_key().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys

WEAK_BOUND = 4096  # see the problem page for why a toy linter uses a bound this small

# The curve constants are on the problem page. Fill these in from there.
CURVES = {
    "P-256": {"p": 0, "a": 0, "b": 0, "gx": 0, "gy": 0},
    "P-384": {"p": 0, "a": 0, "b": 0, "gx": 0, "gy": 0},
}


def lint_key(curve, x, y, blocklist):
    """blocklist: a set of (curve, x, y) tuples declared so far. Return None if the key passes
    every check, or one of "off-curve", "known-compromised", "weak" (first failing reason, in
    that priority order)."""
    # TODO:
    #   1. Is (x, y) actually on `curve`'s equation? If not: "off-curve".
    #   2. Is (curve, x, y) in `blocklist`? If so: "known-compromised".
    #   3. Is there a d with 1 <= d <= WEAK_BOUND such that d*G == (x, y)? If so: "weak".
    #   4. Otherwise: None (the key is ok).
    raise NotImplementedError("lint_key")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    blocklist = set()
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "blocklist":  # blocklist <curve> <x> <y>: applies to key lines after it
                curve, x, y = words[1], int(words[2], 16), int(words[3], 16)
                blocklist.add((curve, x, y))
            elif words[0] == "key":  # key <label> <curve> <x> <y>
                label, curve, x, y = words[1], words[2], int(words[3], 16), int(words[4], 16)
                reason = lint_key(curve, x, y, blocklist)
                lines.append(f"ok {label}" if reason is None else f"fail {label} {reason}")
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
