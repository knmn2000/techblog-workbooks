# ======================================================================================
# Assignment 05: Read DER
# Problem: problems/05-der-reader.md (and in the problem book, with its Start here card)
#
# Why this file exists:
#   This module reads DER, the tag-length-value encoding that holds every certificate in
#   the project, into a tree of nodes, and decodes INTEGER, OBJECT IDENTIFIER and BIT
#   STRING values. Your `x509/certificate.py` (assignment 06), `x509/spki.py` (07) and
#   `x509/signature.py` (08) read certificates through it.
#
# Your job:
#   Write a DER reader in `asn1/der.py` that turns bytes into a tree of tag-length-value
#   nodes, each with its class, constructed bit, tag number, length, content bytes,
#   children and depth. Read both length forms, and have each node record where it starts
#   in the buffer and how many bytes it takes with its header, for assignments 07 and 08.
#   Add decoders for INTEGER, OBJECT IDENTIFIER and BIT STRING content, as "Decoding each
#   type's content" describes. The Boilerplate gives you the declarations; fill in each
#   TODO.
#
# How to start:
#   This is the Boilerplate. To start from an empty file instead, choose From scratch in
#   the book (the empty files are in starters/blank/).
# ======================================================================================

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
    # TODO: the short form and the long form; see "The length" under "The tag-length-value
    # structure" on the problem page.
    raise NotImplementedError("read_length")


def read_tlv(data: bytes, i: int, depth: int = 0) -> tuple[Node, int]:
    """Reads the TLV that starts at data[i]; returns (node, index of the byte after it)."""
    # TODO: split the tag byte into class, constructed bit and tag number, read the length,
    # then the content; a constructed node's content is more TLVs, one level deeper. See "The
    # tag-length-value structure" on the problem page. Fill in `start` and `total_len` too:
    # assignments 07 and 08 slice a node's original bytes out with `encoding`.
    raise NotImplementedError("read_tlv")


def parse_all(data: bytes) -> list[Node]:
    """Returns every top-level TLV in `data`, in order."""
    # TODO: read TLVs back to back until the bytes run out; see the `der` line under "Input" on
    # the problem page.
    raise NotImplementedError("parse_all")


def decode_integer(content: bytes) -> int:
    """Reads INTEGER content bytes as a signed, big-endian, two's complement number."""
    # TODO: see "INTEGER" under "Decoding each type's content" on the problem page.
    raise NotImplementedError("decode_integer")


def decode_oid(content: bytes) -> str:
    """Reads OBJECT IDENTIFIER content bytes as dotted decimal, such as "1.2.840.10045.2.1"."""
    # TODO: see "OBJECT IDENTIFIER" under "Decoding each type's content" on the problem page.
    raise NotImplementedError("decode_oid")


def decode_bit_string(content: bytes) -> tuple[int, bytes]:
    """Reads BIT STRING content bytes as (unused bits in the last byte, the bytes that hold the bits)."""
    # TODO: see BIT STRING in the table under "Decoding each type's content" on the problem page.
    raise NotImplementedError("decode_bit_string")
