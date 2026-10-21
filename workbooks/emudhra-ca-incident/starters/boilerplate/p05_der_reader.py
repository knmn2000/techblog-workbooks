# Checkpoint 05 - Read DER
#
# Problem:  problems/05-der-reader.md (also in the web problem book)
# Check:    ./check.sh 05
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on der_to_lines().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys


def der_to_lines(hex_str: str) -> list:
    """Parse the DER bytes given as `hex_str` and return one output line per TLV node
    encountered in a depth-first, document-order walk. See the problem page for the exact
    tag/length/class rules and the output format."""
    # TODO: walk the bytes as tag-length-value nodes, recursing into constructed nodes
    # (SEQUENCE, SET, context-specific [n] wrappers), and format each node's line.
    raise NotImplementedError("der_to_lines")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "der":  # der <hex>: one or more DER-encoded values, concatenated
                lines.extend(der_to_lines(words[1]))
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
