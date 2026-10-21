"""Test cases for assignment 05 (read DER).

Every case is hand-built: this file's own tiny encoders turn Python values (an int, a bool, an
OID string, ...) into DER bytes, and the SAME Python values become the expected output lines
(no decoding needed there - the generator never has to invert its own encoding). What needs
checking is the byte layout: did the length field use the right form, does nesting really put
each child at the depth I intended? That is checked independently with `openssl asn1parse`,
which decodes tag class / constructed-or-not / depth / length straight from the bytes using its
own C ASN.1 code, with no reference to anything in this workbook. Every case asserts this match
before it is written.

    python3 -P tools/gen_p05.py                                  # tests/05 (seed 1)
    python3 -P tools/gen_p05.py --seed 777 --out build/fresh/05  # what `check 05 -Fresh` runs
"""

import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # python -P leaves the script's folder off the path
import wbcore  # noqa: E402

LIB = "openssl asn1parse (OpenSSL 3.x): independently decodes tag class, constructed/primitive, depth and length from the same bytes"

REQUIREMENTS = [
    ("R1", "BOOLEAN, NULL, OCTET STRING and BIT STRING (with its unused-bits byte) decode correctly"),
    ("R2", "INTEGER is two's complement: a value needing a leading 0x00 pad byte is still read correctly, and so is a negative value"),
    ("R3", "OBJECT IDENTIFIER decodes its base-128 arcs to dotted notation, including arcs that need more than one byte"),
    ("R4", "SEQUENCE, SET and context-specific tags ([0], [3], ...) are constructed and recurse, with the right depth for each child"),
    ("R5", "Both length forms work: short form (fits in one byte) and long form (length needs 2 or more bytes)"),
    ("E2E", "A structure shaped like a real certificate fragment, mixing every node type in one walk"),
]
EXPLAIN = "_lines=R1"


# ---- Tiny DER encoders: each returns (bytes, expected_value_text_or_None) ----------------

def der_len(n: int) -> bytes:
    if n < 0x80:
        return bytes([n])
    body = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([0x80 | len(body)]) + body


def tlv(tag_byte: int, content: bytes) -> bytes:
    return bytes([tag_byte]) + der_len(len(content)) + content


def der_boolean(value: bool):
    return tlv(0x01, b"\xff" if value else b"\x00"), "true" if value else "false"


def der_integer(value: int):
    if value == 0:
        content = b"\x00"
    else:
        n = 1
        while True:  # the smallest n for which `value` fits in n bytes, two's complement
            try:
                content = value.to_bytes(n, "big", signed=True)
                break
            except OverflowError:
                n += 1
    return tlv(0x02, content), str(value)


def der_null():
    return tlv(0x05, b""), "null"


def der_octet_string(data: bytes):
    return tlv(0x04, data), (data.hex() or "-")


def der_bit_string(unused: int, payload: bytes):
    return tlv(0x03, bytes([unused]) + payload), f"{unused}:{payload.hex()}"


def der_oid(dotted: str):
    arcs = [int(a) for a in dotted.split(".")]
    values = [arcs[0] * 40 + arcs[1]] + arcs[2:]  # the first two arcs are combined into one value
    body = bytearray()
    for v in values:                               # each value gets the same base-128 encoding
        chunk = [v & 0x7F]
        v >>= 7
        while v:
            chunk.append((v & 0x7F) | 0x80)
            v >>= 7
        body += bytes(reversed(chunk))
    return tlv(0x06, bytes(body)), dotted


def der_time(tag_byte: int, text: str):
    return tlv(tag_byte, text.encode("ascii")), text


def der_sequence(*children_bytes: bytes):
    return tlv(0x30, b"".join(children_bytes))


def der_set(*children_bytes: bytes):
    return tlv(0x31, b"".join(children_bytes))


def der_context(tag_num: int, constructed: bool, content: bytes):
    byte = 0x80 | (0x20 if constructed else 0) | tag_num
    return tlv(byte, content)


def der_printable_string(text: str):
    # Not one of assignment 05's required types; used only to build realistic Name fields for
    # the E2E case. Its value is printed as hex, the same fallback as OCTET STRING.
    content = text.encode("ascii")
    return tlv(0x13, content), content.hex()


# ---- The structural oracle: openssl asn1parse ------------------------------------------

TYPE_TO_TAG = {
    "SEQUENCE": ("universal", 16), "SET": ("universal", 17), "INTEGER": ("universal", 2),
    "BOOLEAN": ("universal", 1), "NULL": ("universal", 5), "OCTET STRING": ("universal", 4),
    "BIT STRING": ("universal", 3), "OBJECT": ("universal", 6), "UTCTIME": ("universal", 23),
    "GENERALIZEDTIME": ("universal", 24), "PRINTABLESTRING": ("universal", 19),
}
LINE_RE = re.compile(r"^\s*\d+:d=(\d+)\s+hl=\d+\s+l=\s*(-?\d+)\s+(cons|prim):\s*(.*?)\s*$")
CONTEXT_RE = re.compile(r"^(cont|appl|priv)\s*\[\s*(\d+)\s*\]")
CLASS_WORD = {"cont": "context", "appl": "application", "priv": "private"}


def asn1parse_structure(data: bytes):
    """[(depth, cls, constructed, tag, length), ...] in document order, from OpenSSL's own
    ASN.1 decoder - independent of this workbook's DER reader."""
    with tempfile.NamedTemporaryFile(suffix=".der") as f:
        f.write(data)
        f.flush()
        proc = subprocess.run(["openssl", "asn1parse", "-inform", "DER", "-in", f.name],
                               capture_output=True, text=True)
    assert proc.returncode == 0, f"openssl asn1parse failed: {proc.stderr}"
    out = []
    for line in proc.stdout.splitlines():
        m = LINE_RE.match(line)
        assert m, f"unrecognised asn1parse line: {line!r}"
        depth, length, pc, type_str = int(m.group(1)), int(m.group(2)), m.group(3) == "cons", m.group(4)
        cm = CONTEXT_RE.match(type_str)
        if cm:
            cls, tag = CLASS_WORD[cm.group(1)], int(cm.group(2))
        else:
            name = next((t for t in TYPE_TO_TAG if type_str.startswith(t)), None)
            assert name, f"unrecognised type in asn1parse output: {type_str!r}"
            cls, tag = TYPE_TO_TAG[name]
        out.append((depth, cls, pc, tag, length))
    return out


def expected_structure(nodes):
    """The same shape, from the tree this file is about to turn into bytes, for comparison
    with asn1parse_structure()."""
    out = []

    def visit(n):
        out.append((n["depth"], n["cls"], n["constructed"], n["tag"], n["length"]))
        for c in n.get("children", ()):
            visit(c)

    for n in nodes:
        visit(n)
    return out


# ---- Building one case: a list of (bytes, tree) top-level items -------------------------

class Node:
    """A node being built: its bytes, plus enough of its own shape to self-check and to
    produce its expected output line(s)."""

    def __init__(self, data: bytes, cls: str, constructed: bool, tag: int, length: int,
                 value: str = None, children=None, depth: int = 0):
        self.data, self.cls, self.constructed = data, cls, constructed
        self.tag, self.length, self.value, self.depth = tag, length, value, depth
        self.children = children or []
        for c in self.children:
            c.depth = self.depth + 1
            _reindex(c, self.depth + 1)

    def as_dict(self):
        return {"depth": self.depth, "cls": self.cls, "constructed": self.constructed,
                "tag": self.tag, "length": self.length, "children": [c.as_dict() for c in self.children]}

    def lines(self):
        out = [f"node {self.depth} {self.cls} {'constructed' if self.constructed else 'primitive'} "
               f"{self.tag} {self.length} {self.value if self.value is not None else '...'}"]
        for c in self.children:
            out += c.lines()
        return out


def _reindex(node: "Node", depth: int):
    node.depth = depth
    for c in node.children:
        _reindex(c, depth + 1)


def leaf(encoder_result, tag: int, cls: str = "universal") -> Node:
    data, value = encoder_result
    # Re-derive the content length from the bytes themselves, not from the caller, so a bug in
    # an encoder's own length accounting would show up as a mismatch against asn1parse too.
    content_len = len(data) - _header_len(data)
    return Node(data, cls, False, tag, content_len, value)


def _header_len(data: bytes) -> int:
    if data[1] & 0x80 == 0:
        return 2
    return 2 + (data[1] & 0x7F)


def branch(data: bytes, cls: str, tag: int, children) -> Node:
    content_len = len(data) - _header_len(data)
    return Node(data, cls, True, tag, content_len, None, children)


def seq(children) -> Node:
    data = der_sequence(*[c.data for c in children])
    return branch(data, "universal", 16, children)


def sett(children) -> Node:
    data = der_set(*[c.data for c in children])
    return branch(data, "universal", 17, children)


def ctx(tag_num: int, child: Node = None, raw: bytes = None) -> Node:
    """A context-specific constructed [tag_num] wrapping one child (EXPLICIT tagging, as
    version and extensions use in a real certificate)."""
    if raw is not None:
        data = der_context(tag_num, False, raw)
        return Node(data, "context", False, tag_num, len(raw), raw.hex() or "-")
    data = der_context(tag_num, True, child.data)
    return branch(data, "context", tag_num, [child])


def check_and_build(case_items):
    """items: a list of Nodes (each a top-level value). Returns (hex, expected lines), after
    asserting the tree's own notion of its shape matches OpenSSL's independent parse."""
    all_bytes = b"".join(n.data for n in case_items)
    got = asn1parse_structure(all_bytes)
    want = expected_structure([n.as_dict() for n in case_items])
    assert got == want, f"asn1parse disagrees with the intended shape:\n  openssl: {got}\n  intended: {want}"
    lines = []
    for n in case_items:
        lines += n.lines()
    return all_bytes.hex(), lines


def main():
    args = wbcore.parse_args("05")
    rng = random.Random(args.seed)
    cases = wbcore.Cases(args.out, args.seed, "records node=depth,cls,pc,tag,length,value", REQUIREMENTS, EXPLAIN, LIB)

    def add(case_id, req, title, items):
        hex_str, expected = check_and_build(items)
        cases.add(case_id, req, title, [f"der {hex_str}"], expected)

    # R1 - BOOLEAN, NULL, OCTET STRING, BIT STRING
    add("05-R1-boolean-true", "R1", "a single BOOLEAN TRUE", [leaf(der_boolean(True), 1)])
    add("05-R1-boolean-false", "R1", "a single BOOLEAN FALSE", [leaf(der_boolean(False), 1)])
    add("05-R1-null", "R1", "a single NULL", [leaf(der_null(), 5)])
    add("05-R1-octet-string", "R1", "an OCTET STRING of a few bytes", [leaf(der_octet_string(bytes.fromhex("0a0b0c0d")), 4)])
    add("05-R1-octet-string-empty", "R1", "an OCTET STRING with zero content bytes", [leaf(der_octet_string(b""), 4)])
    add("05-R1-bit-string-0-unused", "R1", "a BIT STRING with 0 unused bits", [leaf(der_bit_string(0, bytes.fromhex("f0")), 3)])
    add("05-R1-bit-string-unused", "R1", "a BIT STRING with 5 unused bits in the last byte", [leaf(der_bit_string(5, bytes.fromhex("a0")), 3)])

    # R2 - INTEGER, the two's complement trap
    for v in (0, 1, 127, 128, 255, 256, 65535):
        add(f"05-R2-int-{v}", "R2", f"INTEGER {v}: {'needs a 0x00 pad byte' if v in (128, 255, 65535) else 'fits without padding'}",
            [leaf(der_integer(v), 2)])
    for v in (-1, -128, -129, -32768):
        add(f"05-R2-int-neg-{-v}", "R2", f"INTEGER {v} (negative, two's complement)", [leaf(der_integer(v), 2)])
    add("05-R2-int-side-by-side", "R2", "128 (needs padding) next to -128 (does not), same length in bytes",
        [leaf(der_integer(128), 2), leaf(der_integer(-128), 2)])
    add("05-R2-int-large", "R2", "a serial-number-sized positive INTEGER (20 bytes, top bit set)",
        [leaf(der_integer(0x8A1B2C3D4E5F60718293A4B5C6D7E8F900112233), 2)])

    # R3 - OBJECT IDENTIFIER, base-128 arcs
    for name, dotted in [("ec-public-key", "1.2.840.10045.2.1"), ("ecdsa-sha384", "1.2.840.10045.4.3.3"),
                          ("p256", "1.2.840.10045.3.1.7"), ("p384", "1.3.132.0.34"),
                          ("basic-constraints", "2.5.29.19"), ("common-name", "2.5.4.3")]:
        add(f"05-R3-oid-{name}", "R3", f"OBJECT IDENTIFIER {dotted}", [leaf(der_oid(dotted), 6)])
    add("05-R3-oid-multibyte-arc", "R3", "an OID with an arc over 127 (needs a two-byte base-128 encoding)",
        [leaf(der_oid("1.2.840.113549.1.1.11"), 6)])
    add("05-R3-oid-big-arc", "R3", "an OID with an arc needing three base-128 bytes",
        [leaf(der_oid("2.999999.3"), 6)])

    # R4 - SEQUENCE, SET, context-specific tags, nesting depth
    add("05-R4-sequence-flat", "R4", "a SEQUENCE of three INTEGERs, no further nesting",
        [seq([leaf(der_integer(1), 2), leaf(der_integer(2), 2), leaf(der_integer(3), 2)])])
    add("05-R4-sequence-nested", "R4", "a SEQUENCE containing a SEQUENCE containing a SEQUENCE (depth 0, 1, 2)",
        [seq([seq([seq([leaf(der_boolean(True), 1)])])])])
    add("05-R4-set", "R4", "a SET OF two INTEGERs", [sett([leaf(der_integer(5), 2), leaf(der_integer(9), 2)])])
    add("05-R4-context-explicit", "R4", "a context-specific [0] wrapping an INTEGER, as a certificate's version field does",
        [ctx(0, leaf(der_integer(2), 2))])
    add("05-R4-context-implicit", "R4", "a context-specific [1], primitive (implicit tagging, not wrapping another TLV)",
        [ctx(1, raw=bytes.fromhex("0102"))])
    add("05-R4-context-in-sequence", "R4", "a SEQUENCE with a [0] version and a [3] extensions wrapper, like a certificate's shape",
        [seq([ctx(0, leaf(der_integer(2), 2)), leaf(der_integer(7), 2),
              ctx(3, seq([leaf(der_boolean(True), 1)]))])])

    # R5 - length forms
    add("05-R5-length-short", "R5", "an OCTET STRING of 100 bytes (short-form length, fits in one byte)",
        [leaf(der_octet_string(bytes(range(100))), 4)])
    add("05-R5-length-long-1byte", "R5", "an OCTET STRING of 200 bytes (long-form length, one length byte)",
        [leaf(der_octet_string(bytes((i % 256 for i in range(200)))), 4)])
    add("05-R5-length-long-2byte", "R5", "an OCTET STRING of 300 bytes (long-form length, two length bytes)",
        [leaf(der_octet_string(bytes((i % 256 for i in range(300)))), 4)])
    add("05-R5-length-boundary-127", "R5", "an OCTET STRING of exactly 127 bytes (the last short-form length)",
        [leaf(der_octet_string(bytes(range(127))), 4)])
    add("05-R5-length-boundary-128", "R5", "an OCTET STRING of exactly 128 bytes (the first long-form length)",
        [leaf(der_octet_string(bytes((i % 256 for i in range(128)))), 4)])
    add("05-R5-sequence-of-long-content", "R5", "a SEQUENCE whose own length needs the long form, wrapping a 150-byte OCTET STRING",
        [seq([leaf(der_octet_string(bytes((i % 256 for i in range(150)))), 4)])])

    # R1 - multiple top-level values in one input (concatenated, not wrapped in a SEQUENCE)
    add("05-R1-two-top-level", "R1", "two independent top-level values, concatenated (both at depth 0)",
        [leaf(der_integer(9), 2), leaf(der_boolean(False), 1)])
    add("05-R1-three-top-level-mixed", "R1", "three top-level values of different types",
        [leaf(der_null(), 5), leaf(der_octet_string(bytes.fromhex("ff00")), 4), leaf(der_oid("2.5.4.3"), 6)])

    # Random mixes of primitives inside nested SEQUENCEs, for both committed and fresh seeds
    def random_leaf():
        kind = rng.choice(["int", "bool", "oct", "oid", "bits"])
        if kind == "int":
            return leaf(der_integer(rng.choice([0, 1, -1, 127, 128, -128, 1000, -1000, rng.randint(-100000, 100000)])), 2)
        if kind == "bool":
            return leaf(der_boolean(rng.choice([True, False])), 1)
        if kind == "oct":
            return leaf(der_octet_string(bytes(rng.randrange(256) for _ in range(rng.randint(0, 6)))), 4)
        if kind == "oid":
            arc0 = rng.choice([0, 1, 2])
            arc1 = rng.randint(0, 39) if arc0 < 2 else rng.randint(0, 2000)  # arc0 in {0,1} caps arc1 at 39
            rest = [str(rng.randint(0, 200000)) for _ in range(rng.randint(0, 3))]
            return leaf(der_oid(".".join([str(arc0), str(arc1)] + rest)), 6)
        return leaf(der_bit_string(rng.randint(0, 7), bytes(rng.randrange(256) for _ in range(rng.randint(0, 4)))), 3)

    for k in range(2):
        leaves = [random_leaf() for _ in range(rng.randint(3, 6))]
        add(f"05-R4-random-s{args.seed}-{k}", "R4", f"a random SEQUENCE of primitive nodes (seed {args.seed})", [seq(leaves)])

    # E2E - a structure shaped like a slice of a real certificate: version, serial, a Name
    # (SEQUENCE OF SET OF {OID, string}), an algorithm identifier, and an extensions wrapper.
    name = seq([sett([seq([leaf(der_oid("2.5.4.3"), 6), leaf(der_printable_string("eMudhra Test CA"), 19)])])])
    alg_id = seq([leaf(der_oid("1.2.840.10045.4.3.3"), 6)])
    ext_wrapper = ctx(3, seq([seq([leaf(der_oid("2.5.29.19"), 6), leaf(der_boolean(True), 1),
                                   leaf(der_octet_string(bytes.fromhex("3003010100")), 4)])]))
    cert_like = seq([ctx(0, leaf(der_integer(2), 2)), leaf(der_integer(12345), 2), alg_id, name, ext_wrapper])
    add("05-E2E-certificate-shaped", "E2E", "version, serial, algorithm identifier, a Name and an extensions wrapper, all in one SEQUENCE", [cert_like])

    time_seq = seq([leaf(der_time(0x17, "251020120000Z"), 23), leaf(der_time(0x18, "20251020120000Z"), 24)])
    add("05-E2E-validity-times", "E2E", "a Validity-shaped SEQUENCE of a UTCTime and a GeneralizedTime", [time_seq])

    add(f"05-E2E-random-s{args.seed}", "E2E", f"a deeper random nesting of SEQUENCEs and primitives (seed {args.seed})",
        [seq([seq([random_leaf(), random_leaf()]), random_leaf(), seq([random_leaf()])])])

    cases.save()


if __name__ == "__main__":
    main()
