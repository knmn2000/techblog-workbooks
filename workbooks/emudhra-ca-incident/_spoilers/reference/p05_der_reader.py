# Reference solution - checkpoint 05 (Read DER). SPOILERS: try it yourself first.
#
# A depth-first, document-order walk of every TLV (tag-length-value) node, printing one line
# per node with enough detail (class, constructed/primitive, tag number, length, decoded value)
# to tell exactly which node and which field a difference is in.

import sys

from common.der import (
    BIT_STRING, BOOLEAN, GENERALIZEDTIME, INTEGER, NULL, OBJECT_IDENTIFIER, OCTET_STRING,
    UTCTIME, decode_bit_string, decode_integer, decode_oid, parse_all,
)


def format_value(node) -> str:
    """The value field for one node's output line. Constructed nodes carry no value of their
    own (their children are the next lines); DER never leaves a primitive value truly empty
    here (NULL has its own word), but an empty string is printed as '-' so every line has
    exactly six fields."""
    if node.constructed:
        return "..."
    if node.cls == "universal":
        if node.tag == BOOLEAN:
            return "true" if node.content and node.content[0] != 0 else "false"
        if node.tag == INTEGER:
            return str(decode_integer(node.content))
        if node.tag == NULL:
            return "null"
        if node.tag == OBJECT_IDENTIFIER:
            return decode_oid(node.content)
        if node.tag == BIT_STRING:
            unused, bits = decode_bit_string(node.content)
            return f"{unused}:{bits.hex()}"
        if node.tag in (UTCTIME, GENERALIZEDTIME):
            return node.content.decode("ascii")
        if node.tag == OCTET_STRING:
            return node.content.hex() or "-"
    # Any other primitive type (a context-specific tag used for implicit tagging, or a
    # universal type not listed above, e.g. PrintableString/UTF8String) is printed as hex,
    # the same as OCTET STRING.
    return node.content.hex() or "-"


def der_to_lines(hex_str: str) -> list:
    """Every TLV node in `hex_str` (DER bytes as hex text), depth-first, document order."""
    data = bytes.fromhex(hex_str)
    lines = []

    def visit(node):
        pc = "constructed" if node.constructed else "primitive"
        lines.append(f"node {node.depth} {node.cls} {pc} {node.tag} {node.length} {format_value(node)}")
        for child in node.children:
            visit(child)

    for top in parse_all(data):
        visit(top)
    return lines


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
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
