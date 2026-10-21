# ======================================================================================
# Assignment 12: Generate a key correctly
# Problem: problems/12-generate-key.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 12 as `python -P tools/run_py.py
#   solutions 12 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 12`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished: it reads the input, calls your code
#   and writes the answer. You fill in the TODOs in this assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/ecc/keys.py in this assignment; each one gives its job at
#   the top.
#   Earlier files you can use: src/pkiaudit/ecc/curve.py and src/pkiaudit/ecc/curves.py.
#   Import them as modules of your package, e.g. `from pkiaudit.ecc import keys`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 12 (generate a key): replays the recorded draws on each `draw` line of a test input.

The checker runs `assignment_12_generate_key.py <input-file> <output-file>`. The generator is in
src/pkiaudit/ecc/keys.py. This program hands it the recorded blocks in place of a random source,
so the test knows which key it must accept.
"""

import sys
from collections.abc import Callable

from pkiaudit.ecc.curves import CURVES
from pkiaudit.ecc.keys import generate_private_key


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
    """Writes `key <label> <d>` for each `draw <label> <curve> <hex-block> ...` line."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if not words or words[0] != "draw":
                continue
            label, curve = words[1], CURVES[words[2]]
            d = generate_private_key(curve, replay([bytes.fromhex(block) for block in words[3:]]))
            lines.append(f"key {label} {d:0{2 * curve.byte_length}x}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
