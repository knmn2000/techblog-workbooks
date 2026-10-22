"""Assignment 17 (baby-step giant-step): searches each `key` line and costs each `plan` line.

The checker runs `assignment_17_baby_step_giant_step.py <input-file> <output-file>`. The search
is in src/pkiaudit/attack/bsgs.py.
"""

import sys

from pkiaudit.attack.bsgs import build_baby_table, find_private_key_bsgs, plan
from pkiaudit.ecc.curves import CURVES


def main(input_path: str, output_path: str) -> None:
    """Writes `weak`, `none` or `plan` lines, one per `key` or `plan` line, in input order."""
    bound, table_limit = 1, None
    tables = {}  # (curve name, m) -> baby table, so keys that share a bound share the work
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            if words[0] == "bound":  # bound <N>: applies to the key lines after it
                bound = int(words[1])
            elif words[0] == "table":  # table <M> or table none: applies to the key and plan lines after it
                table_limit = None if words[1] == "none" else int(words[1])
            elif words[0] == "key":  # key <label> <curve> <x> <y>, coordinates in hex
                label, curve = words[1], CURVES[words[2]]
                m, _ = plan(bound, table_limit)
                if (curve.name, m) not in tables:
                    tables[(curve.name, m)] = build_baby_table(curve, m)
                e = find_private_key_bsgs(curve, (int(words[3], 16), int(words[4], 16)), bound,
                                          tables[(curve.name, m)])
                lines.append(f"none {label}" if e is None else f"weak {label} {e}")
            elif words[0] == "plan":  # plan <label> <bits>: the cost of a search with bound 2^bits
                m, giant = plan(2 ** int(words[2]), table_limit)
                lines.append(f"plan {words[1]} baby {m} giant {giant}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
