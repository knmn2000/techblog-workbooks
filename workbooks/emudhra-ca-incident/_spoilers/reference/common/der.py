"""Hand-written DER (ITU-T X.690) tag-length-value reader, shared by checkpoints 05-09's
reference solutions. SPOILERS: try the checkpoint yourself first.

This is a plain from-scratch decoder: no ASN.1 library, no `cryptography.x509` calls. It covers
exactly the definite-length, low-tag-number subset that X.509 certificates use.
"""

from dataclasses import dataclass, field

CLASS_NAMES = {0: "universal", 1: "application", 2: "context", 3: "private"}

# Universal tag numbers this workbook needs (ITU-T X.690 section 8).
BOOLEAN, INTEGER, BIT_STRING, OCTET_STRING, NULL, OBJECT_IDENTIFIER = 1, 2, 3, 4, 5, 6
SEQUENCE, SET, UTCTIME, GENERALIZEDTIME = 16, 17, 23, 24


@dataclass
class Node:
    """One TLV node, after its header (tag + length) has been read.

    `start` and `total_len` are offsets into the ORIGINAL buffer passed to parse_all/read_tlv,
    not into `content` - they let a caller re-slice the exact original bytes of a node (the TBS
    certificate trick in checkpoint 08 needs this: DER is canonical, but re-encoding a structure
    yourself is an easy way to get subtly different bytes than the ones that were signed).
    """
    cls: str                 # "universal" | "application" | "context" | "private"
    constructed: bool
    tag: int
    length: int               # content length in bytes
    content: bytes            # the content bytes (header stripped)
    children: list = field(default_factory=list)  # child Nodes, for constructed nodes
    depth: int = 0
    start: int = 0            # offset of this node's first header byte, in the original buffer
    total_len: int = 0        # header + content length


def read_length(data: bytes, i: int):
    """Length field starting at data[i]. Returns (length, index of the first content byte)."""
    first = data[i]
    if first & 0x80 == 0:           # short form: the byte itself is the length (0-127)
        return first, i + 1
    count = first & 0x7F            # long form: this many following bytes hold the length
    if count == 0:
        raise ValueError("indefinite length is not supported (DER requires definite length)")
    if i + 1 + count > len(data):
        raise ValueError("truncated length field")
    length = int.from_bytes(data[i + 1:i + 1 + count], "big")
    return length, i + 1 + count


def read_tlv(data: bytes, i: int, depth: int = 0):
    """One TLV node starting at data[i]. Returns (Node, index just past it)."""
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
    content = data[content_start:content_end]
    node = Node(cls, constructed, tag, length, content, children, depth, start, content_end - start)
    return node, content_end


def parse_all(data: bytes):
    """Every top-level TLV in `data`, in document order."""
    nodes, i = [], 0
    while i < len(data):
        node, i = read_tlv(data, i, 0)
        nodes.append(node)
    return nodes


def decode_integer(content: bytes) -> int:
    """DER INTEGER content -> a signed Python int (two's complement, big-endian)."""
    if not content:
        raise ValueError("empty INTEGER")
    value = int.from_bytes(content, "big")
    if content[0] & 0x80:              # top bit of the first byte set: this is a negative number
        value -= 1 << (8 * len(content))
    return value


def decode_oid(content: bytes) -> str:
    """DER OBJECT IDENTIFIER content -> dotted decimal (e.g. "1.2.840.10045.2.1").

    Every arc (including the first two, which share one encoded value) is base-128: 7 bits per
    byte, high bit set on every byte but the last one of that arc. The first encoded value
    combines the first two arcs as 40*arc1 + arc2 - and that combined value can itself need more
    than one byte, the same as any other arc.
    """
    if not content:
        raise ValueError("empty OBJECT IDENTIFIER")
    values, value = [], 0
    for b in content:
        value = (value << 7) | (b & 0x7F)   # base-128, big-endian, high bit = "more bytes follow"
        if not (b & 0x80):
            values.append(value)
            value = 0
    if value:
        raise ValueError("truncated OBJECT IDENTIFIER (last byte has the continuation bit set)")
    first = values[0]
    if first < 40:
        arc1, arc2 = 0, first
    elif first < 80:
        arc1, arc2 = 1, first - 40
    else:
        arc1, arc2 = 2, first - 80
    arcs = [arc1, arc2] + values[1:]
    return ".".join(str(a) for a in arcs)


def decode_bit_string(content: bytes):
    """DER BIT STRING content -> (number of unused bits in the last byte, the bit bytes)."""
    if not content:
        raise ValueError("empty BIT STRING (even zero bits needs the unused-bits byte)")
    return content[0], content[1:]


def find_child(node: Node, cls: str, tag: int) -> Node:
    """The first direct child with this class and tag number, or None."""
    return next((c for c in node.children if c.cls == cls and c.tag == tag), None)
