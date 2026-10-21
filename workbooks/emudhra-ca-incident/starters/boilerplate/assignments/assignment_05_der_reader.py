# ======================================================================================
# Assignment 05: Read DER
# Problem: problems/05-der-reader.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   The checker runs this program for assignment 05 as `python -P tools/run_py.py
#   solutions 05 <input-file> <output-file>`. It reads a test input, calls your code and
#   writes the answer to the output file, and the checker compares that answer with the
#   expected one. Run `.\check 05`, or use Run and Submit in the book.
#
# Your job:
#   The Boilerplate gives you this program finished. You fill in the TODOs in this
#   assignment's other files.
#
# The other files of this assignment:
#   You also write src/pkiaudit/asn1/der.py in this assignment; each one gives its job at
#   the top.
#   Import them as modules of your package, e.g. `from pkiaudit.asn1 import der`.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

"""Assignment 05 (DER reader): lists every TLV node of each `der` line of a test input.

The checker runs `assignment_05_der_reader.py <input-file> <output-file>`. The DER reader is
src/pkiaudit/asn1/der.py; this program walks its tree and prints one line per node.
"""

import sys

from pkiaudit.asn1 import der


def format_value(node: der.Node) -> str:
    """Writes a node's value: `...` for a constructed node, else its decoded value or hex."""
    if node.constructed:
        return "..."  # its children follow on their own lines
    if node.cls == "universal":
        if node.tag == der.BOOLEAN:
            return "true" if node.content and node.content[0] != 0 else "false"
        if node.tag == der.INTEGER:
            return str(der.decode_integer(node.content))
        if node.tag == der.NULL:
            return "null"
        if node.tag == der.OBJECT_IDENTIFIER:
            return der.decode_oid(node.content)
        if node.tag == der.BIT_STRING:
            unused, bits = der.decode_bit_string(node.content)
            return f"{unused}:{bits.hex()}"
        if node.tag in (der.UTCTIME, der.GENERALIZEDTIME):
            return node.content.decode("ascii")
    # OCTET STRING, strings and context-specific primitives print as hex, and an empty value as
    # `-`, so every line has six fields.
    return node.content.hex() or "-"


def der_lines(data: bytes) -> list[str]:
    """Writes one line per TLV node in `data`, depth first, in document order."""
    lines = []

    def visit(node: der.Node) -> None:
        kind = "constructed" if node.constructed else "primitive"
        lines.append(f"node {node.depth} {node.cls} {kind} {node.tag} {node.length} {format_value(node)}")
        for child in node.children:
            visit(child)

    for top in der.parse_all(data):
        visit(top)
    return lines


def main(input_path: str, output_path: str) -> None:
    """Writes the node lines for each `der <hex>` line."""
    lines = []
    with open(input_path, encoding="utf-8") as f:
        for line in f:
            words = line.split()
            if words and words[0] == "der":  # der <hex>: one or more DER values, concatenated
                lines.extend(der_lines(bytes.fromhex(words[1])))
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <input-file> <output-file>")
    main(sys.argv[1], sys.argv[2])
