# Reference solution - checkpoint 14 (Check a key ceremony). SPOILERS: try it yourself first.
#
# Every `generate` step starts a brand new identity, even when it reuses a label an earlier
# `generate` already used (that reuse is flagged on its own, as `duplicate`). A label is just the
# current name pointing at some identity; `wrap` and `unwrap` carry the identity its source label
# currently points at forward to the target label. Because identities are tracked by a number, not
# by label text, reusing a label for a new key can never retroactively change what an earlier
# `wrap`/`unwrap` chain, already pointed at the old identity, resolves to.
#
# fingerprint lines attach a fingerprint to whatever label they name; the first one attached to a
# label that was just generated becomes that identity's attested ground truth. At publish, a key
# is `ok` only if its current fingerprint still matches the ground truth of the identity its label
# currently points to; if not, something silently changed the key material in between, and the
# identity's own generate-label names where to look.

import sys


def process_ceremony(steps):
    known = set()
    points_at = {}        # label -> the identity id it currently refers to
    generated_as = {}      # identity id -> the label it was generated under (for MISMATCH messages)
    origin_fp = {}         # identity id -> the fingerprint attested at ITS OWN generation
    current_fp = {}        # label -> the most recently recorded fingerprint for this label
    awaiting_origin_fp = set()  # identity ids whose very next fingerprint line sets origin_fp
    next_id = 0

    out = []
    for words in steps:
        kind = words[0]
        if kind == "generate":
            label = words[1]
            if label in known:
                out.append(f"duplicate {label}")
            next_id += 1
            points_at[label] = next_id
            generated_as[next_id] = label
            awaiting_origin_fp.add(next_id)
            known.add(label)
        elif kind == "wrap":
            label, wrapped_label = words[1], words[2]
            points_at[wrapped_label] = points_at.get(label)
            known.add(wrapped_label)
        elif kind == "unwrap":
            wrapped_label, label = words[1], words[2]
            points_at[label] = points_at.get(wrapped_label)
            known.add(label)
        elif kind == "fingerprint":
            label, hexval = words[1], words[2]
            current_fp[label] = hexval
            identity = points_at.get(label)
            if identity in awaiting_origin_fp:
                origin_fp[identity] = hexval
                awaiting_origin_fp.discard(identity)
        elif kind == "publish":
            label = words[1]
            if label not in known:
                out.append(f"publish {label} undefined")
                continue
            identity = points_at[label]
            if current_fp.get(label) == origin_fp.get(identity):
                out.append(f"publish {label} ok")
            else:
                out.append(f"publish {label} MISMATCH {generated_as.get(identity)}")
    return out


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
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
