# Checkpoint 14 - Check a key ceremony
#
# Problem:  problems/14-ceremony-checker.md (also in the web problem book)
# Check:    ./check.sh 14
#
# Only your program's output is checked, so structure this however you like, or use another
# language or library (see README.md). The input/output code at the bottom is provided so you
# can focus on process_ceremony().
#
# Your own code that other checkpoints could reuse goes in solutions/common/ and is imported
# with `import common.<module>`.

import sys


def process_ceremony(steps):
    """steps: the ceremony log, one step per line, each already split into words
    (e.g. ["generate", "k1", "P-384"], ["fingerprint", "k1", "<hex>"], ["publish", "k1b"]).

    Return the list of output lines, in the order they should appear:
      "duplicate <label>"                a label was reused by a second `generate` step
      "publish <label> ok"               the published key's fingerprint matches its origin's
      "publish <label> MISMATCH <origin>"    it doesn't: something changed the key in between
      "publish <label> undefined"        the label was never generated, wrapped, or unwrapped
    """
    # TODO: track, for each label, which `generate` step it currently traces back to (its origin)
    # and the most recently recorded fingerprint for that exact label. Every `generate` step
    # starts its OWN new origin, even when it reuses a label an earlier `generate` already used
    # (don't let it overwrite the earlier one's attested fingerprint: a key already wrapped away
    # under the old identity must keep resolving to it). `wrap` and `unwrap` carry the current
    # origin forward to their target label; `fingerprint` records a label's current fingerprint,
    # and also records the origin's attested fingerprint the first time a label is fingerprinted
    # right after its own `generate` step.
    raise NotImplementedError("process_ceremony")


# ---- Input/output (provided) -------------------------------------------------


def main(input_path, output_path):
    steps = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if words:
                steps.append(words)
    out_lines = process_ceremony(steps)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines) + "\n")


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
