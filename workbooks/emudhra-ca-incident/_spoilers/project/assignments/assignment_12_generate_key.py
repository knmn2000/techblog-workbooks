"""Assignment 12 (validate and generate a key): answers the `validate` and `draw` lines of a test input.

The checker runs `assignment_12_generate_key.py <input-file> <output-file>`. The checks and the
generator are in src/pkiaudit/ecc/keys.py. For a `draw` line this program hands the generator the
recorded blocks in place of a random source, so the test knows which key it must accept.
"""

import sys
from collections.abc import Callable

from pkiaudit.ecc.curves import CURVES
from pkiaudit.ecc.keys import generate_private_key, validate_private_key


def replay(blocks: list[bytes]) -> Callable[[int], bytes]:
    """Returns a random source that hands out `blocks` in order, whatever count the generator asks for."""
    draws = iter(blocks)

    def random_bytes(_count: int) -> bytes:
        block = next(draws, None)
        if block is None:
            raise ValueError(f"no accepted draw among {len(blocks)} candidates")
        return block

    return random_bytes


def main(input_path: str, output_path: str) -> None:
    """Writes `ok` or `reject` for each `validate` line and `key` for each `draw` line, in input order."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words:
                continue
            label, curve = words[1], CURVES[words[2]]
            if words[0] == "validate":  # validate <label> <curve> <hex>
                reason = validate_private_key(curve, int(words[3], 16))
                lines.append(f"ok {label}" if reason is None else f"reject {label} {reason}")
            elif words[0] == "draw":  # draw <label> <curve> <hex-block> ...
                d = generate_private_key(curve, replay([bytes.fromhex(block) for block in words[3:]]))
                lines.append(f"key {label} {d:0{2 * curve.byte_length}x}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
