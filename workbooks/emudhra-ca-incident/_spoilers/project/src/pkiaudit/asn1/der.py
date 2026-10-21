"""A reader for DER, the tag-length-value encoding certificates use (assignment 05).

It covers the part of ITU-T X.690 that X.509 certificates need: definite lengths and tag numbers
below 31. `parse_all` turns bytes into a tree of `Node`s, and the decode functions read the
values of the primitive types.
"""

from dataclasses import dataclass, field

CLASS_NAMES = {0: "universal", 1: "application", 2: "context", 3: "private"}

# Universal tag numbers (ITU-T X.690 section 8).
BOOLEAN, INTEGER, BIT_STRING, OCTET_STRING, NULL, OBJECT_IDENTIFIER = 1, 2, 3, 4, 5, 6
SEQUENCE, SET, UTCTIME, GENERALIZEDTIME = 16, 17, 23, 24


@dataclass
class Node:
    """One TLV: its header fields, its content bytes and, if constructed, its children."""

    cls: str  # "universal", "application", "context" or "private"
    constructed: bool
    tag: int
    length: int  # content length in bytes
    content: bytes  # the content bytes, without the header
    children: list["Node"] = field(default_factory=list)
    depth: int = 0  # 0 for a top-level node
    start: int = 0  # offset of the first header byte in the buffer the parser read
    total_len: int = 0  # header and content together

    def encoding(self, data: bytes) -> bytes:
        """Returns this node's original bytes, header included, out of `data`, the buffer the parser read."""
        # Assignments 07 and 08 hash these bytes. Re-encoding the fields yourself can give
        # different bytes from the ones the issuer signed.
        return data[self.start:self.start + self.total_len]


def read_length(data: bytes, i: int) -> tuple[int, int]:
    """Reads the length field at data[i]; returns (length, index of the first content byte)."""
    first = data[i]
    if first & 0x80 == 0:  # short form: the byte is the length (0 to 127)
        return first, i + 1
    count = first & 0x7F  # long form: the next `count` bytes hold the length, big-endian
    if count == 0:
        raise ValueError("indefinite length is not supported (DER requires definite length)")
    if i + 1 + count > len(data):
        raise ValueError("truncated length field")
    length = int.from_bytes(data[i + 1:i + 1 + count], "big")
    return length, i + 1 + count


def read_tlv(data: bytes, i: int, depth: int = 0) -> tuple[Node, int]:
    """Reads the TLV that starts at data[i]; returns (node, index of the byte after it)."""
    start = i
    if i >= len(data):
        raise ValueError(f"expected a TLV at offset {i}, ran out of bytes")
    first = data[i]
    cls = CLASS_NAMES[(first >> 6) & 0x3]
    constructed = bool(first & 0x20)
    tag = first & 0x1F
    if tag == 0x1F:
        raise ValueError("high-tag-number form (tag number >= 31) is not supported")
    length, content_start = read_length(data, i + 1)
    content_end = content_start + length
    if content_end > len(data):
        raise ValueError(f"truncated TLV: wanted {length} content bytes, only "
                         f"{len(data) - content_start} available")
    children = []
    if constructed:
        k = content_start
        while k < content_end:
            child, k = read_tlv(data, k, depth + 1)
            children.append(child)
        if k != content_end:
            raise ValueError("a child TLV ran past its parent's length")
    node = Node(cls, constructed, tag, length, data[content_start:content_end], children, depth, start,
                content_end - start)
    return node, content_end


def parse_all(data: bytes) -> list[Node]:
    """Returns every top-level TLV in `data`, in order."""
    nodes, i = [], 0
    while i < len(data):
        node, i = read_tlv(data, i, 0)
        nodes.append(node)
    return nodes


def decode_integer(content: bytes) -> int:
    """Reads INTEGER content bytes as a signed, big-endian, two's complement number."""
    if not content:
        raise ValueError("empty INTEGER")
    value = int.from_bytes(content, "big")
    if content[0] & 0x80:  # the top bit of the first byte is the sign
        value -= 1 << (8 * len(content))
    return value


def decode_oid(content: bytes) -> str:
    """Reads OBJECT IDENTIFIER content bytes as dotted decimal, such as "1.2.840.10045.2.1"."""
    if not content:
        raise ValueError("empty OBJECT IDENTIFIER")
    # Each value is base 128, 7 bits per byte, with the high bit set on every byte but its last.
    values, value = [], 0
    for b in content:
        value = (value << 7) | (b & 0x7F)
        if not (b & 0x80):
            values.append(value)
            value = 0
    if value:
        raise ValueError("truncated OBJECT IDENTIFIER (last byte has the continuation bit set)")
    # The first value packs the first two arcs as 40 * arc1 + arc2, and may itself take more
    # than one byte.
    first = values[0]
    if first < 40:
        arc1, arc2 = 0, first
    elif first < 80:
        arc1, arc2 = 1, first - 40
    else:
        arc1, arc2 = 2, first - 80
    return ".".join(str(arc) for arc in [arc1, arc2] + values[1:])


def decode_bit_string(content: bytes) -> tuple[int, bytes]:
    """Reads BIT STRING content bytes as (unused bits in the last byte, the bytes that hold the bits)."""
    if not content:
        raise ValueError("empty BIT STRING (even zero bits needs the unused-bits byte)")
    return content[0], content[1:]
