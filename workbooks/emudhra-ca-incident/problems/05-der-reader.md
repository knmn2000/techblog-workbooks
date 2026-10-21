# 05 · Read DER

**Difficulty:** Medium · **Assignment** 5 of 16 · **Check:** `.\check 05`

**Tags**
- *Language:* bit manipulation · hex strings · recursion
- *Library:* none needed
- *Concepts:* ASN.1 · DER (Distinguished Encoding Rules) · tag-length-value encoding

## Read in the blog first

eMudhra's post doesn't cover this assignment: it's background for the rest of the workbook. Every
certificate here is a DER-encoded byte string, and assignments 06 to 09 all start by walking that
encoding the way this one does. For the full rules, read ITU-T X.690 section 8 ("Basic encoding
rules"), in particular 8.1 (the tag-length-value structure), 8.3 (INTEGER), 8.6 (BIT STRING) and
8.19 (OBJECT IDENTIFIER). The Source material section below links the document. You can pass
using this page alone.

## Source material

- ITU-T X.690, [Information technology - ASN.1 encoding rules: BER, CER and DER](https://www.itu.int/rec/T-REC-X.690), section 8 (the encoding this assignment reads)
- RFC 5280, [Internet X.509 Public Key Infrastructure Certificate and CRL Profile](https://www.rfc-editor.org/rfc/rfc5280), section 4.1 (where assignment 06 uses this TLV structure to read a real certificate)

## Where this fits

This is the first assignment that reads bytes, so it uses none of your earlier modules. Your
`asn1/der.py` turns bytes into a tree of nodes, and the certificate assignments read through it:
`x509/certificate.py` (assignment 06) reads a certificate's fields, `x509/spki.py` (07) hashes its
public key and `x509/signature.py` (08) checks its signature. Assignments 07 and 08 hash a node's
original bytes, so store in each node its start offset and its total size, header included.

## The problem

Write a program that reads DER-encoded bytes and prints every tag-length-value (TLV) node in them,
in the order each one starts, with its nesting depth, so that the output shows the shape of the
encoding.

### The tag-length-value structure

Every DER-encoded value is three parts, back to back:

- a **tag**: what kind of value this is;
- a **length**: how many bytes of content follow;
- the **content**: the value itself or, for a constructed value, more complete TLV nodes.

**The tag** is the first byte. Its bits mean:

| Bits | Meaning |
|---|---|
| 8-7 | tag class: `00` universal, `01` application, `10` context-specific, `11` private |
| 6 | `0` primitive (the content is the value), `1` constructed (the content is more TLV nodes) |
| 5-1 | tag number |

DER also has a multi-byte "high tag number" form for tag numbers 31 and above. No test uses it, so
every tag in this assignment fits in one byte.

**Universal** tags are ASN.1's built-in types: each number means the same type wherever it
appears. You need these:

| Tag number | Type | Form |
|---|---|---|
| 1 | BOOLEAN | primitive |
| 2 | INTEGER | primitive |
| 3 | BIT STRING | primitive (no test nests one) |
| 4 | OCTET STRING | primitive |
| 5 | NULL | primitive |
| 6 | OBJECT IDENTIFIER | primitive |
| 16 | SEQUENCE | constructed |
| 17 | SET | constructed |
| 23 | UTCTime | primitive |
| 24 | GeneralizedTime | primitive |

A **context-specific** tag ([0], [1], [2], [3], ...) means something different in each structure
that uses it. A certificate uses [0] for its version field and [3] for its extensions. Both wrap
another value, so both are constructed in this workbook. The tag number sits in the same bits 5-1
as a universal tag's; only the class bits differ.

**The length** follows the tag byte, in one of two forms:

- **Short form**: if the length byte's high bit is 0, the rest of that byte (0 to 127) is the
  length, and the length field is that one byte.
- **Long form**: if the length byte's high bit is 1, its low 7 bits say how many more bytes
  follow, and those bytes, read as one big-endian number, are the length. `0x81 0xC8` means "1
  more byte: 0xC8", a length of 200. `0x82 0x01 0x2C` means "2 more bytes: 0x01 0x2C", a length
  of 300.

A length of 127 is the largest short form, and 128 is the first length that needs the long form.

BER, the looser encoding that DER restricts, also allows an **indefinite length**: `0x80` with no
length at all, ended by two zero bytes. DER forbids it and no test uses it, so you don't need to
handle it.

**The content** is the next `length` bytes. For a primitive node, those bytes are the value,
decoded by type (below). For a constructed node, they are more complete TLV nodes, one after
another, each one level deeper than its parent.

### Decoding each type's content

A primitive node's value depends on its type:

| Type | Content bytes | Print |
|---|---|---|
| BOOLEAN | one byte: DER writes false as `0x00` and true as `0xFF` | `true` or `false` |
| NULL | none | `null` |
| OCTET STRING | the value | the bytes as lowercase hex |
| BIT STRING | the number of unused bits (0 to 7) at the end of the last byte, then the bytes that hold the bits | `<unused-bits>:<hex of the rest>`, e.g. `0:f0` |
| UTCTime, GeneralizedTime | ASCII text | the text unchanged, e.g. `251020120000Z` |
| INTEGER | a signed number (below) | the value in decimal |
| OBJECT IDENTIFIER | a list of numbers (below) | the dotted form, e.g. `1.2.840.10045.2.1` |
| any other type | | the bytes as lowercase hex, like OCTET STRING |

A BIT STRING with 0 unused bits and payload `0xF0` uses all 8 bits of that byte. With 4 unused
bits, only the top 4 count. You print the bytes the same way in both cases.

"Any other type" covers the string types you meet in real certificates, such as PrintableString
and UTF8String, which this assignment doesn't decode. It also covers a context-specific tag used
for **implicit tagging**: the tag replaces a value's own tag instead of wrapping another TLV, so
the node is primitive.

#### INTEGER

The content bytes are a **two's complement** number, most significant byte first:

- If the top bit of the first byte is 0, the value is the bytes read as an unsigned number.
- If that bit is 1, the value is negative: subtract `2^(8 * number of bytes)` from the unsigned
  reading.

DER puts an extra `0x00` byte in front of a positive value whose top bit would otherwise be set,
so that it doesn't read as negative. Keep that pad byte when you decode: it's what makes the value
positive.

Content `00 80` is two bytes with top byte `0x00`, so the value is positive: `0x0080 = 128`.
Content `80` alone has its top bit set, so the value is negative: 128 unsigned, minus `2^8 = 256`,
gives `-128`.

DER sets no size limit on an INTEGER, and one test has a 20-byte value, the size of a certificate
serial number. Python's `int` holds it; in another language, use a big-integer type.

#### OBJECT IDENTIFIER

An object identifier is a list of numbers called **arcs**, printed with dots between them, such as
`1.2.840.10045.2.1`. The encoding packs the first two arcs into one value, `40 * arc1 + arc2` (arc1
is 0, 1 or 2), and gives each later arc a value of its own.

Each value takes one or more bytes in **base 128**: 7 bits per byte, most significant group first,
with the top bit set on every byte of the value except its last. To decode:

1. Start the current value at 0. For each byte, shift the value left 7 bits and OR in the byte's
   low 7 bits.
2. A byte whose top bit is 0 ends the value. The next byte starts a new one.
3. Split the first value `v` into two arcs: `v < 40` gives `0, v`; `v < 80` gives `1, v - 40`;
   a larger `v` gives `2, v - 80`.

The first value follows the same base-128 rule as the others, so it can take more than one byte
too.

Worked example: bytes `2a 86 48 ce 3d 04 03 03`.

| Bytes | Value | Arcs |
|---|---|---|
| `2a` | 42, which is `40*1 + 2` | `1.2` |
| `86 48` | `0x86` has its top bit set, so the value goes on: 6 so far. `0x48` (top bit clear) ends it: `6*128 + 72 = 840` | `840` |
| `ce 3d` | the same way: 10045 | `10045` |
| `04`, `03`, `03` | one byte each: 4, 3, 3 | `4`, `3`, `3` |

The full OID is `1.2.840.10045.4.3.3`.

### Input

The checker runs your program from the workbook folder as `<program> <input-file> <output-file>`.
The input file contains one kind of line:

| Line | Meaning |
|---|---|
| `der <hex>` | DER bytes, as lowercase hex with no spaces. A line can hold several complete top-level TLV nodes back to back, with nothing wrapping them: walk all of them. |

### Output

Walk every node of every `der` line depth first, in document order: a constructed node's line comes
before its children's lines, and a node's children come before its next sibling. Write one line per
node:

```
node <depth> <class> <primitive-or-constructed> <tag> <length> <value>
```

- `<depth>`: `0` for a top-level node, `1` for its children, and so on.
- `<class>`: `universal`, `application`, `context` or `private`.
- `<primitive-or-constructed>`: the word `primitive` or `constructed`.
- `<tag>`: the tag number, in decimal.
- `<length>`: the number of content bytes, in decimal, not counting the tag and length fields.
- `<value>`: for a primitive node, its value as "Decoding each type's content" prints it, or `-`
  when a value printed as hex has no bytes (an empty OCTET STRING, for example). For a
  constructed node, the three characters `...`: its children follow on their own lines.

The checker ignores extra whitespace.

## Requirements

Each test checks one of these requirements. If tests fail, the checker's report shows how many
pass for each requirement, and it may add a `likely cause` line that names the requirement the
difference points to.

- **R1** BOOLEAN, NULL, OCTET STRING and BIT STRING values print as the table says, including a
  BIT STRING's unused-bits byte, and an input with several top-level nodes gets lines for all of
  them, in order.
- **R2** INTEGER is two's complement: a value with a leading `0x00` pad byte decodes to the right
  positive number, and a negative value decodes to the right negative number.
- **R3** OBJECT IDENTIFIER decodes from base-128 values to dotted arcs, including arcs (and the
  combined first value) that take more than one byte.
- **R4** SEQUENCE, SET and context-specific tags are constructed: their content is more TLV nodes,
  each one level deeper than its parent, through several levels.
- **R5** Both length forms work: the short form, and the long form with one or more length bytes,
  including 127 and 128, the lengths on either side of the boundary.

## Examples

### Example 1: a BIT STRING with unused bits (test `05-R1-bit-string-unused`)

```
input:   der 030205a0

output:  node 0 universal primitive 3 2 5:a0
```

Tag byte `0x03`: class bits `00` (universal), constructed bit `0` (primitive), tag number `3`
(BIT STRING). Length byte `0x02`: short form, 2 content bytes. Content `05 a0`: the first byte,
`0x05`, is the unused-bit count, and the rest, `a0`, holds the bits. Output value: `5:a0`.

### Example 2: INTEGER needing a pad byte, next to one that doesn't (test `05-R2-int-side-by-side`)

```
input:   der 02020080020180

output:  node 0 universal primitive 2 2 128
         node 0 universal primitive 2 1 -128
```

The first value has tag `02` (INTEGER), length `02` and content `00 80`. The leading `00` makes it
positive: `0x0080 = 128`. The second value has tag `02`, length `01` and content `80`. Its top bit
is set and no pad byte comes first, so it's negative: 128 unsigned, minus 256, gives `-128`. The
same byte `80` reads as 128 with a pad byte in front and as -128 without one.

### Example 3: nesting with a context-specific tag (test `05-R4-context-explicit`)

```
input:   der a003020102

output:  node 0 context constructed 0 3 ...
         node 1 universal primitive 2 1 2
```

Tag byte `0xa0` is `1010_0000`: class bits `10` (context-specific), constructed bit `1`, tag
number `0`. A certificate wraps its version field this way: `[0]` constructed, holding one
INTEGER. The outer node's value is `...` because its content is a TLV node (the INTEGER `2`),
which appears on the next line, one level deeper.

## Constraints

- Every `der` line holds complete, well-formed DER: no truncated nodes, no indefinite lengths and
  no tag number of 31 or above.
- Depths in the tests go no deeper than 4.
- Each case has a 10-second limit.
- There are 47 tests: 9 for R1 (two of them with several top-level nodes), 13 for R2, 8 for R3,
  8 for R4 (two of them random), 6 for R5, and 3 end-to-end cases that combine several node types
  and levels of nesting in one structure shaped like a slice of a real certificate. Part of the
  set is random and changes with `-Fresh`.

## Hints

<details><summary>Hint 1: where to start</summary>

Write one function that reads a single TLV node starting at a byte offset and returns the node
(its tag fields, length and content) and the offset after it: `read_tlv` in your `asn1/der.py`.
Build the depth-first walk and the value formatting around calls to it.
</details>

<details><summary>Hint 2: the approach</summary>

The tag byte gives the class, the constructed bit and the tag number by bit masking (`>> 6`,
`& 0x20`, `& 0x1F`). The length byte tells you whether the length is that byte (short form) or
the next N bytes (long form). A primitive node's value comes from decoding its content bytes by
type. A constructed node's content is more TLV nodes: read them one after another with the same
function, from the start of its content, until you have used up its length.
</details>

<details><summary>Hint 3: the traps</summary>

- An INTEGER's leading `0x00` byte belongs to the value: it makes a number whose high bit is set
  read as positive. Apply the two's complement rule to the bytes as given, pad byte included.
- An OBJECT IDENTIFIER's first value, `40*arc1 + arc2`, follows the same base-128 rule as the
  later arcs, so it takes more than one byte when it's large.
- A child is one level deeper than its parent. Pass the depth down as you recurse.
- The long form can take one, two or more length bytes. A length of 127 is the last short form,
  and 128 is the first long form.
- A context-specific tag keeps its number in the same five low bits as a universal tag; only the
  two class bits differ. Check the class before you decode by tag number: context-specific [1]
  isn't a BOOLEAN, though universal tag 1 is.
- One `der` line can hold several top-level nodes with nothing around them. Keep reading until
  the bytes run out.
</details>

<details><summary>Hint 4: pseudocode</summary>

```
read_tlv(data, i, depth):
    first = data[i]
    cls = (first >> 6) & 0b11
    constructed = (first & 0x20) != 0
    tag = first & 0x1F

    length_byte = data[i+1]
    if high bit of length_byte is 0:
        length = length_byte
        content_start = i + 2
    else:
        n = length_byte & 0x7F
        length = big-endian value of the next n bytes
        content_start = i + 2 + n

    content = data[content_start : content_start + length]
    node = {cls, constructed, tag, length, content, depth, children: [],
            start: i, total_len: content_start + length - i}
    if constructed:
        k = content_start
        while k < content_start + length:
            child, k = read_tlv(data, k, depth + 1)
            node.children.append(child)
    return node, content_start + length

visit(node):
    print one line for node (value "..." if constructed, else decoded by type)
    for child in node.children:
        visit(child)
```
</details>

## Checking your solution

```
.\check 05                                 run every test
.\check 05 -Case 05-R2-int-side-by-side    one test, showing its full input, expected output and your output
.\check 05 -Fresh                          a new set of tests (new random seed), to confirm on data you haven't seen
.\check 05 -Dispute <id> "why"             set aside a test you believe is wrong; you won't be blocked
```

A failing test looks like this:

```
  R2  INTEGER is two's complement: a value needing a leading 0x00 pad b...    12 / 13  FAILED
      x 05-R2-int-neg-128  INTEGER -128 (negative, two's complement)
          node[0]: expected (depth=0, cls=universal, pc=primitive, tag=2, length=1, value=-128), got (depth=0, cls=universal, pc=primitive, tag=2, length=1, value=128) - differs in value
          likely cause: R2 - INTEGER is two's complement: a value needing a leading 0x00 pad byte is still read correctly, and so is a negative value
          expected values from: openssl asn1parse (OpenSSL 3.x): independently decodes tag class, constructed/primitive, depth and length from the same bytes
          reproduce: py -P tools/run_py.py solutions 05 build/cases/05/05-R2-int-neg-128.in build/cases/05/05-R2-int-neg-128.out
```

## After you pass: compare with the post

eMudhra's post has no code for this, so there is no author's version to compare. The reference
`asn1/der.py` has one small function, `read_tlv`, that calls itself for each child, and one
decoder each for INTEGER, OBJECT IDENTIFIER and BIT STRING. The program's `format_value` has one
branch per type.

**Something to look for:** the reference decodes an OBJECT IDENTIFIER's first value with the same
base-128 loop as the other arcs, with no special case for a single byte. Compare how it handles an
arc pair whose combined value is large with the code you wrote for the later arcs.
